from pathlib import Path
import copy, json, math, os, time
import numpy as np
import pandas as pd
import torch
from torch import nn
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parent
DATA=ROOT/'synthetic_data.npz'
SIGMA=.15
SEEDS=[11,22]
K=8

# Finite local probe; operator supervision is consequence-only. True B is never model input.
def constrain_B(B):
    eye=torch.eye(3,device=B.device,dtype=B.dtype)
    B=B*(1-eye)
    den=torch.maximum(B.abs().sum(-1,keepdim=True),torch.ones_like(B[...,:1]))
    return .95*B/den

class Block(nn.Module):
    def __init__(self,d=32,heads=4,ff=64):
        super().__init__(); self.l1=nn.LayerNorm(d); self.a=nn.MultiheadAttention(d,heads,batch_first=True,dropout=0.); self.l2=nn.LayerNorm(d); self.f=nn.Sequential(nn.Linear(d,ff),nn.GELU(),nn.Linear(ff,d))
    def forward(self,x):
        y=self.l1(x); z,_=self.a(y,y,y,need_weights=False); x=x+z; return x+self.f(self.l2(x))

class WorldProgram(nn.Module):
    """Persistent state is explicit candidate relation systems + logits only; no GRU/RNN hidden state."""
    def __init__(self,K=8,d=32):
        super().__init__(); self.K=K
        self.ctx=nn.Linear(5,d); self.cand_in=nn.Linear(10,d); self.var=nn.Embedding(3,d); self.typ=nn.Embedding(2,d); self.seed=nn.Parameter(torch.randn(K,d)*.02)
        self.blocks=nn.ModuleList([Block(d) for _ in range(3)])
        self.cand_out=nn.Linear(d,10); self.edge_gain=nn.Parameter(torch.tensor(1.4)); self.w_gain=nn.Parameter(torch.tensor(1.4))
    def ctx_tokens(self,x,reveal=True):
        cov=x[:,:9].reshape(-1,3,3); sr=x[:,9:12]; st=x[:,12:15]
        if not reveal: sr=torch.zeros_like(sr); st=torch.zeros_like(st)
        feat=torch.cat([cov,sr[:,:,None],st[:,:,None]],-1)
        return self.ctx(feat)+self.var.weight[None]+self.typ.weight[0]
    def cand_tokens(self,B,lg):
        f=torch.cat([B.reshape(len(B),self.K,9),lg[:,:,None]],-1)
        return self.cand_in(f)+self.seed[None]+self.typ.weight[1]
    def transition(self,ctx,B,lg):
        h=torch.cat([self.cand_tokens(B,lg),ctx],1)
        for b in self.blocks: h=b(h)
        o=self.cand_out(h[:,:self.K]); prop=constrain_B(torch.tanh(o[:,:,:9].reshape(len(B),self.K,3,3))); lp=o[:,:,9]
        a=torch.sigmoid(self.edge_gain); Bn=constrain_B((1-a)*B+a*prop)
        g=torch.sigmoid(self.w_gain); ln=(1-g)*lg+g*lp; ln=ln-ln.mean(-1,keepdim=True)
        return Bn,ln
    def form_world(self,x,steps=4,trace=False,start_state=None,reveal_step=3):
        n=len(x)
        if start_state is None:
            B=torch.zeros(n,self.K,3,3,device=x.device); lg=torch.zeros(n,self.K,device=x.device)
        else:
            B,lg=start_state
        Bs=[]; Ls=[]
        for t in range(1,steps+1):
            B,lg=self.transition(self.ctx_tokens(x,t>=reveal_step),B,lg); Bs.append(B); Ls.append(lg)
        if trace:return B,lg,{'B':torch.stack(Bs,1),'logits':torch.stack(Ls,1)}
        return B,lg

def apply_operator(B, spec):
    # B: batch,K,3,3. spec is dict, same operator for batch.
    C=B.clone(); rhs=torch.zeros(B.shape[:-2]+(3,),device=B.device,dtype=B.dtype)
    typ=spec['type']
    if typ in ('edge_delete_do','edge_scale_do','edge_flip_do'):
        r,s=spec['edge']
        if typ=='edge_delete_do': C[...,r,s]=0
        elif typ=='edge_scale_do': C[...,r,s]*=spec['scale']
        else: C[...,r,s]*=-1
    for t,v in zip(spec['targets'],spec['values']):
        C[...,t,:]=0; rhs[...,t]=v
    A=torch.eye(3,device=B.device,dtype=B.dtype)-C
    return torch.linalg.solve(A,rhs[...,None]).squeeze(-1)

def apply_true(B, spec):
    bt=torch.tensor(B,dtype=torch.float32)
    # add K axis for shared helper then remove
    return apply_operator(bt[:,None],spec)[:,0]

def train_specs():
    out=[]
    for q in range(3):
        for v in (-1.,1.): out.append({'name':f'do{q}_{v:+g}','type':'do','targets':[q],'values':[v]})
    for a,b in [(0,1),(0,2),(1,2)]:
        for va,vb in [(1.,1.),(1.,-1.),(-1.,1.)]: out.append({'name':f'do{a}{va:+g}_{b}{vb:+g}','type':'double','targets':[a,b],'values':[va,vb]})
    for r in range(3):
        for s in range(3):
            if r!=s: out.append({'name':f'del{r}{s}_do{s}','type':'edge_delete_do','edge':(r,s),'targets':[s],'values':[1.]})
    return out

def heldout_specs():
    out=[]
    for q in range(3):
        for v in (-1.5,-.5,.5,1.5): out.append({'name':f'do{q}_{v:+g}','type':'do','targets':[q],'values':[v]})
    for a,b in [(0,1),(0,2),(1,2)]:
        for va,vb in [(-1.,-1.),(.5,-1.5)]: out.append({'name':f'do{a}{va:+g}_{b}{vb:+g}','type':'double','targets':[a,b],'values':[va,vb]})
    for r in range(3):
        for s in range(3):
            if r!=s:
                out.append({'name':f'half{r}{s}_do{s}','type':'edge_scale_do','edge':(r,s),'scale':.5,'targets':[s],'values':[1.]})
                out.append({'name':f'flip{r}{s}_do{s}','type':'edge_flip_do','edge':(r,s),'targets':[s],'values':[1.]})
    return out

TRAIN_SPECS=train_specs(); HELD_SPECS=heldout_specs()

def mix_nll(mus,lg,y):
    # mus B,K,3 ; y B,3
    ld=-.5*((mus-y[:,None,:])/SIGMA).square().sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi))
    return -torch.logsumexp(lg.log_softmax(-1)+ld,1)

def bank_loss(B,lg,trueB,specs):
    vals=[]
    for spec in specs:
        vals.append(mix_nll(apply_operator(B,spec),lg,apply_true(trueB,spec)))
    return torch.stack(vals,1).mean()

def original_query_loss(B,lg,x,y):
    q=x[:,-3:].argmax(-1); allmus=[]
    for qi in range(3): allmus.append(apply_operator(B,{'type':'do','targets':[qi],'values':[1.]}))
    sims=torch.stack(allmus,2) # B,K,Q,3
    mus=sims[torch.arange(len(B))[:,None],torch.arange(B.shape[1])[None,:],q[:,None]]
    return mix_nll(mus,lg,y).mean(), mus

def expected(mus,lg): return (mus*lg.softmax(-1)[:,:,None]).sum(1)

def evaluate(model,x,y,trueB,group,support,steps=4):
    with torch.no_grad(): B,lg,tr=model.form_world(x,steps=steps,trace=True)
    orig,_=original_query_loss(B,lg,x,y)
    train=bank_loss(B,lg,trueB,TRAIN_SPECS); held=bank_loss(B,lg,trueB,HELD_SPECS)
    rows=[]
    for label,specs in [('train_bank',TRAIN_SPECS),('heldout_bank',HELD_SPECS)]:
        for spec in specs:
            yn=apply_true(trueB,spec); mus=apply_operator(B,spec); nll=mix_nll(mus,lg,yn)
            pred=expected(mus,lg); mse=((pred-yn)**2).mean(1)
            for i in range(len(x)):
                rows.append({'bank':label,'operator':spec['name'],'group':int(group[i]),'support':int(support[i]),'instance':i,'nll':float(nll[i]),'mse':float(mse[i])})
    # mechanism distances only as evaluation diagnostics
    w=lg.softmax(-1).cpu().numpy(); bn=B.cpu().numpy(); tb=trueB.numpy(); d=np.sqrt(((bn-tb[:,None])**2).mean((2,3)))
    state={'weighted_B_dist':float((w*d).sum(1).mean()),'best_B_dist':float(d.min(1).mean()),'effective_worlds':float(np.exp(-(w*np.log(np.clip(w,1e-12,1))).sum(1)).mean())}
    return {'original_query_nll':float(orig),'train_bank_nll':float(train),'heldout_bank_nll':float(held),**state},pd.DataFrame(rows),tr

def fit(seed,train,dev,test,steps=450):
    torch.manual_seed(seed); rng=np.random.default_rng(seed+2222); model=WorldProgram(K); opt=torch.optim.Adam(model.parameters(),lr=.0015)
    x,y,tb=train; vx,vy,vtb=dev; tx,ty,ttb,group,support=test
    best=1e9; state=None; logs=[]; t0=time.time()
    for step in range(1,steps+1):
        ix=rng.integers(len(x),size=64); horizon=int(rng.integers(3,7)); # variable local scoring horizon
        opt.zero_grad(); B,lg=model.form_world(x[ix],steps=horizon); # sample a compact operator minibank
        picks=rng.choice(len(TRAIN_SPECS),size=6,replace=False); specs=[TRAIN_SPECS[j] for j in picks]
        l=bank_loss(B,lg,tb[ix],specs); l.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(),5); opt.step()
        if step%50==0:
            with torch.no_grad(): Bv,lv=model.form_world(vx,steps=4); vl=float(bank_loss(Bv,lv,vtb,TRAIN_SPECS))
            logs.append({'step':step,'train_operator_nll':float(l.detach()),'dev_operator_bank_nll':vl,'sampled_horizon':horizon})
            if vl<best: best=vl; state=copy.deepcopy(model.state_dict()); sel=step
    model.load_state_dict(state); model.eval()
    metrics,detail,tr=evaluate(model,tx,ty,ttb,group,support,4)
    # support-specific heldout improvement from paired support/no-support rows
    d=detail[detail.bank=='heldout_bank'].groupby(['group','support']).nll.mean().unstack()
    metrics['heldout_support_improvement']=float((d[0]-d[1]).mean())
    # state sufficiency replay from t=2
    with torch.no_grad():
        _,_,a=model.form_world(tx,steps=2,trace=True); st=(a['B'][:,-1].clone(),a['logits'][:,-1].clone()); Br,Lr=model.form_world(tx,steps=2,start_state=st); B4,L4=model.form_world(tx,steps=4)
        metrics['state_replay_B_max_abs']=float((Br-B4).abs().max()); metrics['state_replay_logit_max_abs']=float((Lr-L4).abs().max())
    # rollout curve to 20 steps on first 200 test instances, score heldout bank
    curve=[]; xc=tx[:200]; ybc=ttb[:200]
    with torch.no_grad():
        B=None; lg=None; prev=None
        for h in range(1,21):
            B,lg=model.form_world(xc,steps=1,start_state=None if h==1 else (B,lg),reveal_step=1 if h>=3 else 99)
            hn=float(bank_loss(B,lg,ybc,HELD_SPECS)); step_rms=np.nan if prev is None else float((B-prev).square().mean().sqrt()); prev=B.clone()
            curve.append({'seed':seed,'step':h,'heldout_bank_nll':hn,'B_step_rms':step_rms})
    ck={'state_dict':state,'seed':seed,'selected_step':sel,'K':K,'train_specs':TRAIN_SPECS,'held_specs':HELD_SPECS}
    torch.save(ck,ROOT/'models'/f'world_program_{seed}.pt')
    (ROOT/'models'/f'world_program_{seed}_training.json').write_text(json.dumps(logs,indent=2))
    np.savez_compressed(ROOT/'predictions'/f'world_program_{seed}.npz',B=tr['B'].numpy(),logits=tr['logits'].numpy())
    return {'seed':seed,'parameters':sum(p.numel() for p in model.parameters()),'selected_step':sel,'dev_operator_bank_nll':best,'seconds':time.time()-t0,**metrics},detail,pd.DataFrame(curve)

def load_cg021_baseline(test):
    # reuse frozen CG-021 pool8 checkpoints, score them on the same operator banks
    import sys
    sys.path.insert(0,'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021')
    import run_cg021_free_pool as old
    tx,ty,ttb,group,support=test; out=[]; details=[]
    for seed in SEEDS:
        ck=torch.load(f'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021/models/pool8_{seed}.pt',map_location='cpu',weights_only=False)
        m=old.FreePool(8); m.load_state_dict(ck['state_dict']); m.eval()
        with torch.no_grad(): B,lgtr=m(tx,trace=True); B=lgtr['B'][:,-1]; lg=lgtr['logits'][:,-1]
        orig,_=original_query_loss(B,lg,tx,ty); trn=bank_loss(B,lg,ttb,TRAIN_SPECS); held=bank_loss(B,lg,ttb,HELD_SPECS)
        out.append({'seed':seed,'variant':'cg021_pool8','original_query_nll':float(orig),'train_bank_nll':float(trn),'heldout_bank_nll':float(held)})
        rows=[]
        for label,specs in [('train_bank',TRAIN_SPECS),('heldout_bank',HELD_SPECS)]:
            for spec in specs:
                yn=apply_true(ttb,spec); mus=apply_operator(B,spec); nll=mix_nll(mus,lg,yn); mse=((expected(mus,lg)-yn)**2).mean(1)
                for i in range(len(tx)): rows.append({'seed':seed,'variant':'cg021_pool8','bank':label,'operator':spec['name'],'group':int(group[i]),'support':int(support[i]),'instance':i,'nll':float(nll[i]),'mse':float(mse[i])})
        details.append(pd.DataFrame(rows))
    return pd.DataFrame(out),pd.concat(details,ignore_index=True)

def main():
    torch.set_num_threads(4); z=np.load(DATA); spl=[]
    for s in range(3):
        ix=z['split']==s; spl.append((torch.tensor(z['x'][ix],dtype=torch.float32),torch.tensor(z['y'][ix],dtype=torch.float32),torch.tensor(z['true_B'][ix],dtype=torch.float32)))
    ix=z['split']==2; test=(*spl[2],z['group'][ix],z['support'][ix])
    base,bd=load_cg021_baseline(test); base.to_csv(ROOT/'baseline_cg021.csv',index=False); bd.to_csv(ROOT/'baseline_operator_detail.csv',index=False)
    res=[]; det=[]; curves=[]
    for seed in SEEDS:
        r,d,c=fit(seed,spl[0],spl[1],test); res.append(r); d['seed']=seed;d['variant']='cg022_world_program';det.append(d);curves.append(c); print(json.dumps(r),flush=True)
        pd.DataFrame(res).to_csv(ROOT/'results.csv',index=False);pd.concat(det,ignore_index=True).to_csv(ROOT/'operator_detail.csv',index=False);pd.concat(curves,ignore_index=True).to_csv(ROOT/'rollout.csv',index=False)
    print('COMPLETE',flush=True)
if __name__=='__main__':main()
