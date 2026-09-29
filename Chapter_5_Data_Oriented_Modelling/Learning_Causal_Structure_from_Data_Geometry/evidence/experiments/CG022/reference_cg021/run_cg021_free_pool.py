from pathlib import Path
import copy, json, math, time, os
import numpy as np, pandas as pd
import torch
from torch import nn
from scipy.special import logsumexp

ROOT=Path('/mnt/data/cg021_work/CAUSAL_GEOMETRY_021')
DATA='/mnt/data/cg021_work/cg020/CAUSAL_GEOMETRY_020_Evidence/synthetic_data.npz'
SIGMA=.15; SEEDS=[11,22]; VARIANTS={'pool3':3,'pool8':8}

def constrain_B(B):
    eye=torch.eye(3,device=B.device,dtype=B.dtype);B=B*(1-eye)
    den=torch.maximum(B.abs().sum(-1,keepdim=True),torch.ones_like(B[...,:1]));return .95*B/den
class Block(nn.Module):
    def __init__(self,d=32,heads=4,ff=64):
        super().__init__();self.l1=nn.LayerNorm(d);self.a=nn.MultiheadAttention(d,heads,batch_first=True,dropout=0.);self.l2=nn.LayerNorm(d);self.f=nn.Sequential(nn.Linear(d,ff),nn.GELU(),nn.Linear(ff,d))
    def forward(self,x):
        y=self.l1(x);z,_=self.a(y,y,y,need_weights=False);x=x+z;return x+self.f(self.l2(x))
class FreePool(nn.Module):
    """Finite capacity, no discrete hypothesis-selection rule. Every candidate persists and can change continuously."""
    def __init__(self,K,d=32):
        super().__init__();self.K=K
        self.ctx=nn.Linear(5,d);self.cand_in=nn.Linear(10,d);self.var=nn.Embedding(3,d);self.typ=nn.Embedding(2,d)
        self.seed=nn.Parameter(torch.randn(K,d)*.02)
        self.blocks=nn.ModuleList([Block(d) for _ in range(3)])
        self.cand_out=nn.Linear(d,10);self.edge_gain=nn.Parameter(torch.tensor(1.4));self.w_gain=nn.Parameter(torch.tensor(1.4))
    def ctx_tokens(self,x,reveal):
        cov=x[:,:9].reshape(-1,3,3);sr=x[:,9:12];st=x[:,12:15]
        if not reveal:sr=torch.zeros_like(sr);st=torch.zeros_like(st)
        feat=torch.cat([cov,sr[:,:,None],st[:,:,None]],-1)
        return self.ctx(feat)+self.var.weight[None]+self.typ.weight[0]
    def cand_tokens(self,B,lg):
        f=torch.cat([B.reshape(len(B),self.K,9),lg[:,:,None]],-1)
        return self.cand_in(f)+self.seed[None]+self.typ.weight[1]
    def transition(self,ctx,B,lg):
        h=torch.cat([self.cand_tokens(B,lg),ctx],1)
        for b in self.blocks:h=b(h)
        o=self.cand_out(h[:,:self.K]);prop=constrain_B(torch.tanh(o[:,:,:9].reshape(len(B),self.K,3,3)));lp=o[:,:,9]
        a=torch.sigmoid(self.edge_gain);bn=constrain_B((1-a)*B+a*prop);g=torch.sigmoid(self.w_gain);ln=(1-g)*lg+g*lp;ln=ln-ln.mean(-1,keepdim=True)
        return bn,ln
    def sim_all(self,B):
        I=torch.eye(3,device=B.device,dtype=B.dtype);mask=1-I;A=I-B[:,:,None,:,:]*mask[None,None,:,:,None];rhs=I[None,None,:,:].expand(len(B),self.K,-1,-1)
        return torch.linalg.solve(A,rhs[...,None]).squeeze(-1)
    def forward(self,x,steps=4,trace=False,reveal_step=3):
        n=len(x);B=torch.zeros(n,self.K,3,3,device=x.device);lg=torch.zeros(n,self.K,device=x.device);Bs=[];Ls=[]
        for t in range(1,steps+1):
            B,lg=self.transition(self.ctx_tokens(x,t>=reveal_step),B,lg);Bs.append(B);Ls.append(lg)
        sims=self.sim_all(B);q=x[:,-3:].argmax(-1);mus=sims[torch.arange(n)[:,None],torch.arange(self.K,device=x.device)[None,:],q[:,None]];p=torch.cat([mus.reshape(n,self.K*3),lg],-1)
        if trace:return p,{'B':torch.stack(Bs,1),'logits':torch.stack(Ls,1)}
        return p

def unpack(p,K):return p[:,:K*3].reshape(-1,K,3),p[:,K*3:]
def loss(p,y,K):
    m,l=unpack(p,K);ld=-.5*((m-y[:,None,:])/SIGMA).square().sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi));return -torch.logsumexp(l.log_softmax(-1)+ld,1).mean()
def expected(p,K):
    m,l=unpack(p,K);return (m*l.softmax(-1)[:,:,None]).sum(1)
def qnll(m,w,y):
    ld=-.5*np.square((m-y[:,None,:])/SIGMA).sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi));return -logsumexp(np.log(np.clip(w,1e-12,1))+ld,axis=1)
def sims_np(B):
    bt=torch.tensor(B,dtype=torch.float32);n,K=bt.shape[:2];I=torch.eye(3);mask=1-I;A=I-bt[:,:,None,:,:]*mask[None,None,:,:,None];rhs=I[None,None,:,:].expand(n,K,-1,-1);return torch.linalg.solve(A,rhs[...,None]).squeeze(-1).numpy()
def allq(B,lg,truth):
    s=sims_np(B);w=torch.softmax(torch.tensor(lg),-1).numpy();return np.stack([qnll(s[:,:,q,:],w,truth[:,q,:]) for q in range(3)],1).mean(1)
def stats(B2,l2,B4,l4,trueB):
    w2=torch.softmax(torch.tensor(l2),-1).numpy();w4=torch.softmax(torch.tensor(l4),-1).numpy()
    d2=np.sqrt(((B2-trueB[:,None])**2).mean((2,3)));d4=np.sqrt(((B4-trueB[:,None])**2).mean((2,3)))
    H2=-(w2*np.log(np.clip(w2,1e-12,1))).sum(1);H4=-(w4*np.log(np.clip(w4,1e-12,1))).sum(1)
    def div(B,w):
        out=[]
        for i in range(len(B)):
            D=np.sqrt(((B[i,:,None]-B[i,None,:])**2).mean((2,3)));out.append((D*w[i,:,None]*w[i,None,:]).sum())
        return np.array(out)
    return dict(w2=w2,w4=w4,weightedB2=(w2*d2).sum(1),weightedB4=(w4*d4).sum(1),bestB2=d2.min(1),bestB4=d4.min(1),eff2=np.exp(H2),eff4=np.exp(H4),top2=w2.max(1),top4=w4.max(1),tv=.5*np.abs(w4-w2).sum(1),bmove=np.sqrt(((B4-B2)**2).mean((1,2,3))),div2=div(B2,w2),div4=div(B4,w4),topchange=np.argmax(w2,1)!=np.argmax(w4,1))

def fit(K,seed,tr,dv,te,meta,steps=450):
    torch.manual_seed(seed);rng=np.random.default_rng(seed+2121);m=FreePool(K);opt=torch.optim.Adam(m.parameters(),lr=.0015);x,y=tr;vx,vy=dv;tx,ty=te;best=1e9;state=None;logs=[];t0=time.time()
    for step in range(1,steps+1):
        ix=rng.integers(len(x),size=64);opt.zero_grad();p=m(x[ix]);l=loss(p,y[ix],K);l.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),5);opt.step()
        if step%50==0:
            with torch.no_grad():vl=float(loss(m(vx),vy,K))
            logs.append({'step':step,'train_nll':float(l.detach()),'dev_nll':vl})
            if vl<best:best=vl;state=copy.deepcopy(m.state_dict());sel=step
    m.load_state_dict(state);m.eval()
    with torch.no_grad():p,trc=m(tx,trace=True)
    B=trc['B'].numpy();lg=trc['logits'].numpy();B2,B4=B[:,1],B[:,3];l2,l4=lg[:,1],lg[:,3];sup=meta['support'];truth=meta['allq'];trueB=meta['trueB']
    pre=allq(B2,l2,truth);full=allq(B4,l4,truth);rw=allq(B2,l4,truth);rew=allq(B4,l2,truth);st=stats(B2,l2,B4,l4,trueB)
    rows=[]
    for i in range(len(tx)):
        rows.append({'variant':f'pool{K}','seed':seed,'instance':i,'group':int(meta['group'][i]),'support':int(sup[i]),'pre_allq_nll':pre[i],'final_allq_nll':full[i],'reweight_only_nll':rw[i],'rewrite_only_nll':rew[i],'weighted_B_dist_pre':st['weightedB2'][i],'weighted_B_dist_final':st['weightedB4'][i],'best_B_dist_pre':st['bestB2'][i],'best_B_dist_final':st['bestB4'][i],'effective_worlds_pre':st['eff2'][i],'effective_worlds_final':st['eff4'][i],'top_weight_pre':st['top2'][i],'top_weight_final':st['top4'][i],'weight_TV':st['tv'][i],'B_update_rms':st['bmove'][i],'weighted_diversity_pre':st['div2'][i],'weighted_diversity_final':st['div4'][i],'top_slot_changed':int(st['topchange'][i])})
    # transplant support from another real world in same group. No candidate is selected by us; only incoming evidence changes.
    xs=tx.clone();don=np.full(len(tx),-1,int)
    for g in np.unique(meta['group']):
        ids=np.flatnonzero((meta['group']==g)&(sup==1))
        if len(ids)==3:
            for j,ii in enumerate(ids):don[ii]=ids[(j+1)%3]
    ids=np.flatnonzero(don>=0);ds=don[ids];xs[ids,9:15]=tx[ds,9:15]
    with torch.no_grad():pp=m(xs)
    mm,ll=unpack(pp,K);ww=ll.softmax(-1).numpy();mm=mm.numpy();own=qnll(mm[ids],ww[ids],ty.numpy()[ids]);donl=qnll(mm[ids],ww[ids],ty.numpy()[ds]);origm=expected(p,K).numpy();newm=expected(pp,K).numpy();shift=np.sqrt(((newm[ids]-origm[ids])**2).mean(1))
    wrong=pd.DataFrame({'variant':f'pool{K}','seed':seed,'receiver_instance':ids,'donor_instance':ds,'group':meta['group'][ids],'own_nll_under_wrong_support':own,'donor_nll_under_wrong_support':donl,'donor_preferred':(donl<own).astype(int),'prediction_rms_shift':shift})
    r={'variant':f'pool{K}','K':K,'seed':seed,'parameters':sum(v.numel() for v in m.parameters()),'selected_step':sel,'dev_nll':best,'test_nll':float(loss(p,ty,K)),'test_mse':float((expected(p,K)-ty).square().mean()),'seconds':time.time()-t0}
    rdf=pd.DataFrame(rows)
    for flag,name in [(0,'no_support'),(1,'support')]:
        q=rdf[rdf.support==flag]
        for c in ['pre_allq_nll','final_allq_nll','reweight_only_nll','rewrite_only_nll','weighted_B_dist_pre','weighted_B_dist_final','effective_worlds_pre','effective_worlds_final','top_weight_pre','top_weight_final','weight_TV','B_update_rms','weighted_diversity_pre','weighted_diversity_final','top_slot_changed']:r[f'{name}_{c}']=float(q[c].mean())
    r['wrong_support_donor_preferred_rate']=float(wrong.donor_preferred.mean());r['wrong_support_prediction_shift']=float(wrong.prediction_rms_shift.mean());r['wrong_support_own_minus_donor_nll']=float((wrong.own_nll_under_wrong_support-wrong.donor_nll_under_wrong_support).mean())
    torch.save({'state_dict':state,'K':K,'seed':seed,'selected_step':sel},ROOT/'models'/f'pool{K}_{seed}.pt');(ROOT/'models'/f'pool{K}_{seed}_training.json').write_text(json.dumps(logs,indent=2));np.savez_compressed(ROOT/'predictions'/f'pool{K}_{seed}.npz',prediction=p.numpy(),B=B,logits=lg,donor_idx=don)
    return r,rdf,wrong

def main():
    torch.set_num_threads(4);z=np.load(DATA);spl=[]
    for s in range(3):
        ix=z['split']==s;spl.append((torch.tensor(z['x'][ix],dtype=torch.float32),torch.tensor(z['y'][ix],dtype=torch.float32)))
    ix=z['split']==2;meta={'group':z['group'][ix],'support':z['support'][ix],'trueB':z['true_B'][ix],'allq':z['all_query_truth'][ix]}
    onlys=os.environ.get('ONLY_SEED');onlyv=os.environ.get('ONLY_VARIANT')
    res=[];sd=[];wr=[]
    if (ROOT/'results.csv').exists():res=pd.read_csv(ROOT/'results.csv').to_dict('records')
    if (ROOT/'state_dynamics.csv').exists():sd=[pd.read_csv(ROOT/'state_dynamics.csv')]
    if (ROOT/'wrong_support.csv').exists():wr=[pd.read_csv(ROOT/'wrong_support.csv')]
    done={(str(r['variant']),int(r['seed'])) for r in res}
    for seed in SEEDS:
        if onlys and seed!=int(onlys):continue
        for name,K in VARIANTS.items():
            if onlyv and name!=onlyv:continue
            if (name,seed) in done:print(json.dumps({'skip':name,'seed':seed}),flush=True);continue
            r,d,w=fit(K,seed,*spl,meta);res.append(r);sd.append(d);wr.append(w);pd.DataFrame(res).to_csv(ROOT/'results.csv',index=False);pd.concat(sd,ignore_index=True).to_csv(ROOT/'state_dynamics.csv',index=False);pd.concat(wr,ignore_index=True).to_csv(ROOT/'wrong_support.csv',index=False);print(json.dumps(r),flush=True)
if __name__=='__main__':main()
