from pathlib import Path
import copy, json, math, time
import numpy as np, pandas as pd
import torch
from torch import nn
from scipy.special import logsumexp

ROOT=Path(__file__).resolve().parent
for q in ['models','predictions','figures']: (ROOT/q).mkdir(exist_ok=True)
SIGMA=.15; SEEDS=[11,22]
OFF=[(r,s) for r in range(3) for s in range(3) if r!=s]
VARIANTS={
 'onepass1':dict(n_layers=1,inner_repeat=1,train_world_steps=1),
 'onepass3':dict(n_layers=3,inner_repeat=1,train_world_steps=1),
 'tied6':dict(n_layers=1,inner_repeat=6,train_world_steps=1),
 'world4_3':dict(n_layers=3,inner_repeat=1,train_world_steps=4),
}

def constrain_B(B):
    eye=torch.eye(3,device=B.device,dtype=B.dtype)
    B=B*(1-eye); den=torch.maximum(B.abs().sum(-1,keepdim=True),torch.ones_like(B[...,:1])); return .95*B/den

class Block(nn.Module):
    def __init__(self,d=32,heads=4,ff=64):
        super().__init__();self.l1=nn.LayerNorm(d);self.a=nn.MultiheadAttention(d,heads,batch_first=True,dropout=0.0);self.l2=nn.LayerNorm(d);self.f=nn.Sequential(nn.Linear(d,ff),nn.GELU(),nn.Linear(ff,d))
    def forward(self,x):
        y=self.l1(x);z,_=self.a(y,y,y,need_weights=False);x=x+z;return x+self.f(self.l2(x))

class ObjectWorldModel(nn.Module):
    """The only persistent state across world updates is explicit B + candidate logits."""
    def __init__(self,n_layers=3,inner_repeat=1,d=32):
        super().__init__();self.inner_repeat=inner_repeat
        self.ctx=nn.Linear(5,d);self.obj=nn.Linear(4,d);self.var=nn.Embedding(3,d);self.cand=nn.Embedding(3,d);self.typ=nn.Embedding(2,d)
        self.blocks=nn.ModuleList([Block(d) for _ in range(n_layers)]);self.row_head=nn.Linear(d,3);self.w_head=nn.Linear(d,1)
        self.edge_gain=nn.Parameter(torch.tensor(1.4));self.w_gain=nn.Parameter(torch.tensor(1.4))
    def ctx_tokens(self,x):
        cov=x[:,:9].reshape(-1,3,3);sr=x[:,9:12];st=x[:,12:15]
        feat=torch.cat([cov,sr[:,:,None],st[:,:,None]],-1) # batch,var,5
        return self.ctx(feat)+self.var.weight[None]+self.typ.weight[0]
    def obj_tokens(self,B,logits):
        # one explicit equation-row token per candidate x response variable
        feat=torch.cat([B,logits[:,:,None,None].expand(-1,-1,3,1)],-1).reshape(len(B),9,4)
        c=torch.arange(3,device=B.device).repeat_interleave(3);r=torch.arange(3,device=B.device).repeat(3)
        return self.obj(feat)+self.cand(c)[None]+self.var(r)[None]+self.typ.weight[1]
    def transition(self,ctx,B,logits):
        h=torch.cat([self.obj_tokens(B,logits),ctx],1)
        if len(self.blocks)==1 and self.inner_repeat>1:
            for _ in range(self.inner_repeat):h=self.blocks[0](h)
        else:
            for b in self.blocks:h=b(h)
        o=h[:,:9].reshape(len(B),3,3,-1);proposal=constrain_B(torch.tanh(self.row_head(o)))
        alpha=torch.sigmoid(self.edge_gain);Bnew=constrain_B((1-alpha)*B+alpha*proposal)
        lp=self.w_head(o.mean(2)).squeeze(-1);beta=torch.sigmoid(self.w_gain);lnew=(1-beta)*logits+beta*lp;lnew=lnew-lnew.mean(-1,keepdim=True)
        return Bnew,lnew
    def sim_all(self,B):
        I=torch.eye(3,device=B.device,dtype=B.dtype);mask=1-I;A=I-B[:,:,None,:,:]*mask[None,None,:,:,None];rhs=I[None,None,:,:].expand(len(B),3,-1,-1)
        return torch.linalg.solve(A,rhs[...,None]).squeeze(-1)
    def forward(self,x,world_steps=1,trace=False,start_state=None,reset_each=False):
        c=self.ctx_tokens(x[:,:15]);n=len(x)
        if start_state is None:B=torch.zeros(n,3,3,3,device=x.device);logits=torch.zeros(n,3,device=x.device)
        else:B,logits=start_state
        Bs=[];Ls=[]
        for _ in range(world_steps):
            if reset_each:B=torch.zeros_like(B);logits=torch.zeros_like(logits)
            B,logits=self.transition(c,B,logits);Bs.append(B);Ls.append(logits)
        sims=self.sim_all(B);q=x[:,-3:].argmax(-1);mus=sims[torch.arange(n)[:,None],torch.arange(3,device=x.device)[None,:],q[:,None]];p=torch.cat([mus.reshape(n,9),logits],-1)
        if trace:return p,{'B':torch.stack(Bs,1),'logits':torch.stack(Ls,1),'sims':sims}
        return p

def loss(p,y):
    mus=p[:,:9].reshape(-1,3,3);lp=p[:,9:].log_softmax(-1);ld=-.5*((mus-y[:,None,:])/SIGMA).square().sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi));return -torch.logsumexp(lp+ld,1).mean()
def expected(p):return (p[:,:9].reshape(-1,3,3)*p[:,9:].softmax(-1)[:,:,None]).sum(1)
def metrics(p,y,worlds,support):
    mus=p[:,:9].reshape(-1,3,3);w=p[:,9:].softmax(-1);r={'nll':float(loss(p,y)),'mse':float((expected(p)-y).square().mean()),'best_candidate_mse':float((mus-y[:,None,:]).square().mean(-1).min(1).values.mean())}
    for v,name in [(0,'ambiguous'),(1,'support')]:ix=support==v;r[name+'_nll']=float(loss(p[ix],y[ix]));r[name+'_mse']=float((expected(p[ix])-y[ix]).square().mean())
    ix=support==0;dist=(mus[ix,:,None,:]-worlds[ix,None,:,:]).square().mean(-1).sqrt();r['ambiguous_world_coverage']=float((((dist<=.20)&(w[ix,:,None]>=.10)).any(1)).float().mean());return r

def solve(B,targets,values):
    B=np.asarray(B);C=B.copy();rhs=np.zeros(B.shape[:-2]+(3,))
    for t,v in zip(targets,values):C[...,t,:]=0;rhs[...,t]=v
    return np.linalg.solve(np.eye(3)-C,rhs[...,None])[...,0]
def qnll(mus,w,y):
    ld=-.5*np.square((mus-y[:,None,:])/SIGMA).sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi));return -logsumexp(np.log(np.clip(w,1e-12,1))+ld,axis=1)
def novel(B,logits,trueB):
    w=torch.softmax(torch.tensor(logits),-1).numpy();vals=[]
    for pair in [(0,1),(0,2),(1,2)]:
      for vv in [(1.,1.),(1.,-1.),(-1.,1.),(-1.,-1.)]:vals.append(qnll(solve(B,pair,vv),w,solve(trueB,pair,vv)))
    correct=[];ignore=[];wrong=[];td=[];pd=[]
    # vectorized by true-edge coordinate; each world has two true edges.
    for r,s in OFF:
      ix=np.flatnonzero(np.abs(trueB[:,r,s])>1e-9)
      if len(ix)==0:continue
      TB=trueB[ix]; BB=B[ix]; WW=w[ix]
      bt=TB.copy();bt[:,r,s]=0.;y=solve(bt,[s],[1]);y0=solve(TB,[s],[1]);pi=solve(BB,[s],[1]);bc=BB.copy();bc[:,:,r,s]=0.;pc=solve(bc,[s],[1])
      correct.extend(qnll(pc,WW,y));ignore.extend(qnll(pi,WW,y))
      # average four absent-coordinate delete controls per case
      wrong_mat=[]
      for rr,ss in OFF:
        valid=np.abs(TB[:,rr,ss])<1e-9
        bw=BB.copy();bw[:,:,rr,ss]=0.;pw=solve(bw,[s],[1]);qn=qnll(pw,WW,y);qn=np.where(valid,qn,np.nan);wrong_mat.append(qn)
      wrong.extend(np.nanmean(np.stack(wrong_mat),axis=0))
      m0=(pi*WW[:,:,None]).sum(1);mc=(pc*WW[:,:,None]).sum(1);td.extend(y[:,r]-y0[:,r]);pd.extend(mc[:,r]-m0[:,r])
    return {'double_do_nll':float(np.mean(vals)),'edge_delete_nll':float(np.mean(correct)),'edge_ignore_nll':float(np.mean(ignore)),'wrong_edge_nll':float(np.mean(wrong)),'edge_delta_corr':float(np.corrcoef(td,pd)[0,1]),'edge_delta_sign':float(np.mean(np.sign(td)==np.sign(pd)))}

def fit(name,cfg,seed,tr,dv,te,meta,steps=450):
    torch.manual_seed(seed);rng=np.random.default_rng(seed+2020);m=ObjectWorldModel(cfg['n_layers'],cfg['inner_repeat']);opt=torch.optim.Adam(m.parameters(),lr=.0015);x,y=tr;vx,vy=dv;tx,ty=te;best=1e9;state=None;logs=[];t=time.time()
    for step in range(1,steps+1):
      ix=rng.integers(len(x),size=64);opt.zero_grad();p=m(x[ix],cfg['train_world_steps']);l=loss(p,y[ix]);l.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),5);opt.step()
      if step%50==0:
        with torch.no_grad():vl=float(loss(m(vx,cfg['train_world_steps']),vy))
        logs.append({'step':step,'train_nll':float(l.detach()),'dev_nll':vl})
        if vl<best:best=vl;state=copy.deepcopy(m.state_dict());sel=step
    m.load_state_dict(state);m.eval()
    with torch.no_grad():p,t0=m(tx,cfg['train_world_steps'],trace=True)
    r={'variant':name,'seed':seed,'parameters':sum(v.numel() for v in m.parameters()),'selected_step':sel,'train_world_steps':cfg['train_world_steps'],'block_calls_per_world_step':cfg['n_layers']*cfg['inner_repeat'],'dev_nll':best,'seconds':time.time()-t};r.update(metrics(p,ty,meta['worlds'],meta['support']));B=t0['B'][:,-1].numpy();lg=t0['logits'][:,-1].numpy();r.update(novel(B,lg,meta['trueB']))
    # same-parameter reset control: repeat calls but erase explicit object between calls
    if name=='onepass3':
      with torch.no_grad():pr=m(tx,4,reset_each=True);r['reset4_nll']=float(loss(pr,ty));r['reset4_max_abs_vs_onepass']=float((pr-p).abs().max())
    else:r['reset4_nll']=np.nan;r['reset4_max_abs_vs_onepass']=np.nan
    # state sufficiency replay: only (B,logits)+fixed context survives.
    if name=='world4_3':
      with torch.no_grad():_,a=m(tx,2,trace=True);st=(a['B'][:,-1].clone(),a['logits'][:,-1].clone());pc=m(tx,2,start_state=st);pf=m(tx,4);r['state_replay_max_abs']=float((pc-pf).abs().max())
    else:r['state_replay_max_abs']=np.nan
    torch.save({'state_dict':state,'variant':name,'seed':seed,'cfg':cfg,'selected_step':sel},ROOT/'models'/f'{name}_{seed}.pt');(ROOT/'models'/f'{name}_{seed}_training.json').write_text(json.dumps(logs,indent=2));np.savez_compressed(ROOT/'predictions'/f'{name}_{seed}.npz',prediction=p.numpy(),B=B,logits=lg)
    curve=[]
    with torch.no_grad():
      xc=tx[:200];yc=ty[:200];_,ta=m(xc,8,trace=True);q=xc[:,-3:].argmax(-1)
      for k in range(1,9):
        Bk=ta['B'][:,k-1];lk=ta['logits'][:,k-1];sk=m.sim_all(Bk);mus=sk[torch.arange(len(xc))[:,None],torch.arange(3)[None,:],q[:,None]];pk=torch.cat([mus.reshape(len(xc),9),lk],-1)
        br=np.nan if k==1 else float((ta['B'][:,k-1]-ta['B'][:,k-2]).square().mean().sqrt())
        curve.append({'variant':name,'seed':seed,'world_steps':k,'nll':float(loss(pk,yc)),'mse':float((expected(pk)-yc).square().mean()),'B_step_rms':br})
    return r,curve

def main():
    torch.set_num_threads(4);z=np.load(ROOT/'synthetic_data.npz');spl=[]
    for s in range(3):ix=z['split']==s;spl.append((torch.tensor(z['x'][ix],dtype=torch.float32),torch.tensor(z['y'][ix],dtype=torch.float32)))
    ix=z['split']==2;meta={'worlds':torch.tensor(z['worlds'][ix],dtype=torch.float32),'support':torch.tensor(z['support'][ix]),'trueB':z['true_B'][ix]};res=[];cur=[]
    for seed in SEEDS:
      for name,cfg in VARIANTS.items():
        r,c=fit(name,cfg,seed,*spl,meta);res.append(r);cur+=c;pd.DataFrame(res).to_csv(ROOT/'results.csv',index=False);pd.DataFrame(cur).to_csv(ROOT/'rollout_curve.csv',index=False);print(json.dumps(r),flush=True)
    print('COMPLETE')
if __name__=='__main__':main()
