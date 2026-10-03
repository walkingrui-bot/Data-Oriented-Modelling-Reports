import os, math, numpy as np, pandas as pd, torch
from torch import nn
ROOT='/mnt/data/INTERNAL_COORDINATION_008'; OUT=f'{ROOT}/results'; os.makedirs(OUT,exist_ok=True); torch.set_num_threads(1)
back=np.load(f'{ROOT}/data/diabetes_backbone.npz',allow_pickle=True); X=back['X'].astype(np.float32); tr=back['train_idx']; te=back['test_idx']
D=10; C=6; H=16; K=5; TAUS=torch.tensor([.1,.25,.5,.75,.9])
# training-data geometry used only to build controlled current-world trajectories
Xm=X[tr]-X[tr].mean(0,keepdims=True); _,_,Vt=np.linalg.svd(Xm,full_matrices=False); PCS=Vt[:4].astype(np.float32)

def draw(Xin,rng):
    s=np.linspace(.85,1.18,D); b=np.linspace(-.18,.18,D); o=[]
    o.append(np.clip(Xin*s+b+.025*rng.normal(size=Xin.shape),-4,4))
    step=np.linspace(.30,.55,D); o.append(np.clip(np.round((Xin+.08*rng.normal(size=Xin.shape))/step)*step+.03*rng.normal(size=Xin.shape),-4,4))
    lod=np.linspace(-.9,-.25,D); o.append(np.clip(np.maximum(Xin+.10*rng.normal(size=Xin.shape),lod),-4,4))
    cap=np.linspace(.9,1.7,D); o.append(np.clip(np.minimum(Xin+.08*rng.normal(size=Xin.shape),cap),-4,4))
    sig=.05+.16/(1+np.exp(-Xin)); o.append(np.clip(Xin+sig*rng.normal(size=Xin.shape),-4,4))
    gain=np.linspace(.85,1.20,D); off=np.linspace(.08,-.10,D); o.append(np.clip(np.tanh(gain*Xin+off)+.08*rng.normal(size=Xin.shape),-4,4))
    return np.stack(o,1).astype(np.float32)

def world_seq(ids,rng,dynamic=True,T=3):
    x0=X[ids].copy(); B=len(ids)
    if dynamic:
        a=rng.normal(0,.34,size=(B,3)).astype(np.float32)
        v=a@PCS[:3]
        b=rng.normal(0,.12,size=(B,1)).astype(np.float32)
        w=b*PCS[3][None,:]
    else:
        v=np.zeros_like(x0); w=np.zeros_like(x0)
    al=np.linspace(0,1,T,dtype=np.float32)
    seq=[]
    for q in al:
        xt=x0+q*v+np.sin(np.pi*q)*w
        seq.append(np.clip(xt,-4,4))
    return np.stack(seq,1).astype(np.float32)

class In(nn.Module):
    def __init__(self): super().__init__(); self.net=nn.Sequential(nn.Linear(D,32),nn.Tanh(),nn.Linear(32,H))
    def forward(self,x): return self.net(x)
class Out(nn.Module):
    def __init__(self): super().__init__(); self.net=nn.Sequential(nn.Linear(H,48),nn.Tanh(),nn.Linear(48,D*K))
    def forward(self,z):
        raw=self.net(z).view(-1,D,K); base=raw[:,:,:1]; inc=torch.nn.functional.softplus(raw[:,:,1:]); return torch.cat([base,base+torch.cumsum(inc,-1)],-1)
def orth(seed,scale=.75):
    g=torch.Generator().manual_seed(seed); a=torch.randn(H,H,generator=g); q,_=torch.linalg.qr(a); return scale*q
class Model(nn.Module):
    def __init__(self,seed,mode='aligned'):
        super().__init__(); self.ins=nn.ModuleList([In() for _ in range(C)]); self.outs=nn.ModuleList([Out() for _ in range(C)]); self.M=nn.Parameter(orth(100+seed)); self.mode=mode
    def slice_step(self,r,Bslice,chs,order=None):
        # Bslice: [B,C,D]. aligned = same-timestamp evidence is a commutative set.
        if self.mode=='aligned':
            es=torch.stack([self.ins[int(c)](Bslice[:,int(c)]) for c in chs],0).mean(0)
            return torch.tanh((r+es)@self.M.T)
        # event baseline: same-time items are treated as serial events
        if order is None: order=chs
        for c in order:
            r=torch.tanh((r+self.ins[int(c)](Bslice[:,int(c)]))@self.M.T)
        return r
    def q(self,r,c): return self.outs[int(c)](r)

def qloss(q,y):
    e=y[:,:,None]-q; t=TAUS[None,None,:]; return torch.maximum(t*e,(t-1)*e).mean()

def train(seed,mode,steps=420):
    torch.manual_seed(seed); rng=np.random.default_rng(1000+seed); m=Model(seed,mode); opt=torch.optim.Adam(m.parameters(),lr=.004)
    for st in range(steps):
        ids=rng.choice(tr,72,False); dynamic=(rng.random()>.25); ws=world_seq(ids,rng,dynamic=dynamic); src=np.stack([draw(ws[:,t],rng) for t in range(3)],1); tgt=np.stack([draw(ws[:,t],rng) for t in range(3)],1)
        B=torch.tensor(src); T=torch.tensor(tgt); r=torch.zeros(len(ids),H); losses=[]
        for t in range(3):
            n=int(rng.integers(2,C+1)); chs=rng.choice(C,size=n,replace=False)
            if mode=='aligned': r=m.slice_step(r,B[:,t],chs)
            else: r=m.slice_step(r,B[:,t],chs,order=rng.permutation(chs))
            for j in rng.choice(C,size=2,replace=False): losses.append(qloss(m.q(r,int(j)),T[:,t,int(j)]))
        loss=torch.stack(losses).mean(); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(),5.); opt.step()
    return m

def pin_cov(m,r,tg):
    pins=[]; cov=[]
    with torch.no_grad():
        for j in range(C):
            q=m.q(r,j).numpy(); y=tg[:,j]
            e=y[:,:,None]-q; tau=np.array([.1,.25,.5,.75,.9])[None,None,:]
            pins.append(np.maximum(tau*e,(tau-1)*e).mean()); cov.append(((y>=q[:,:,0])&(y<=q[:,:,-1])).mean())
    return float(np.mean(pins)),float(np.mean(cov))

def eval_seed(m,seed,mode,dynamic=True,reps=6):
    rng=np.random.default_rng(9000+seed+(0 if dynamic else 333)); ids=te; ws=world_seq(ids,rng,dynamic=dynamic); src=np.stack([draw(ws[:,t],rng) for t in range(3)],1); targets=np.stack([[draw(ws[:,t],rng) for t in range(3)] for _ in range(reps)],0) # [R,T,B,C,D]
    B=torch.tensor(src); full=[np.arange(C) for _ in range(3)]
    def run(groups, within_orders=None):
        r=torch.zeros(len(ids),H)
        with torch.no_grad():
            for kk,t in enumerate(groups):
                chs=full[t]
                if mode=='aligned': r=m.slice_step(r,B[:,t],chs)
                else:
                    oo=chs if within_orders is None else within_orders[kk]
                    r=m.slice_step(r,B[:,t],chs,order=oo)
        return r
    # correct chronology, target current t=2 independent repeats
    r_correct=run([0,1,2]); pins=[]; cov=[]
    for rr in range(reps):
        p,c=pin_cov(m,r_correct,targets[rr,2]); pins.append(p); cov.append(c)
    # reverse time slices; same evidence, wrong chronology; still score against true current t=2
    r_reverse=run([2,1,0]); rp=[]
    for rr in range(reps): rp.append(pin_cov(m,r_reverse,targets[rr,2])[0])
    # same-time within-slice permutation sensitivity: six orderings of channels per timestamp
    states=[]; meds=[]
    for oo in range(6):
        orders=[rng.permutation(C) for _ in range(3)]
        r=run([0,1,2],orders); states.append(r.numpy())
        with torch.no_grad(): meds.append(np.stack([m.q(r,j).numpy()[:,:,2] for j in range(C)],1))
    state_sd=float(np.stack(states).std(0).mean()); pred_sd=float(np.stack(meds).std(0).mean())
    # stale/misaligned: half of current channels are actually stale t=0 observations but are mislabeled as current t=2.
    r=torch.zeros(len(ids),H)
    with torch.no_grad():
        for t in [0,1]: r=m.slice_step(r,B[:,t],np.arange(C)) if mode=='aligned' else m.slice_step(r,B[:,t],np.arange(C),order=np.arange(C))
        Bbad=B[:,2].clone(); Bbad[:,:3]=B[:,0,:3]
        r=m.slice_step(r,Bbad,np.arange(C)) if mode=='aligned' else m.slice_step(r,Bbad,np.arange(C),order=np.arange(C))
    bp=[pin_cov(m,r,targets[rr,2])[0] for rr in range(reps)]
    return {'dynamic':int(dynamic),'correct_pinball':float(np.mean(pins)),'coverage80':float(np.mean(cov)),'reverse_time_pinball':float(np.mean(rp)),'reverse_state_distance':float(torch.linalg.norm(r_correct-r_reverse,dim=1).mean()),'within_slice_pred_sd':pred_sd,'within_slice_state_sd':state_sd,'stale_half_pinball':float(np.mean(bp)),'stale_half_state_distance':float(torch.linalg.norm(r_correct-r,dim=1).mean())}

def latent_audit(m,seed):
    # held-out current-state linear readout of actual X_t from r_t, fitted only on train episodes.
    def collect(ids,rng,nrep=2):
        RR=[]; YY=[]
        for z in range(nrep):
            ws=world_seq(ids,rng,True); src=np.stack([draw(ws[:,t],rng) for t in range(3)],1); B=torch.tensor(src); r=torch.zeros(len(ids),H)
            with torch.no_grad():
                for t in range(3): r=m.slice_step(r,B[:,t],np.arange(C)) if m.mode=='aligned' else m.slice_step(r,B[:,t],np.arange(C),order=np.arange(C))
            RR.append(r.numpy()); YY.append(ws[:,2])
        return np.concatenate(RR),np.concatenate(YY)
    rng=np.random.default_rng(12000+seed); A,Y=collect(tr,rng,1); B,Z=collect(te,rng,1); lam=1e-3; W=np.linalg.solve(A.T@A+lam*np.eye(H),A.T@Y); pr=B@W; ss=((Z-pr)**2).sum(); st=((Z-Z.mean(0))**2).sum(); return 1-float(ss/st)

if __name__=='__main__':
    rows=[]
    for mode in ['aligned','event']:
        for seed in range(5):
            m=train(seed,mode)
            for dyn in [True,False]: rows.append({'mode':mode,'seed':seed,**eval_seed(m,seed,mode,dyn)})
            rows[-2]['latent_R2']=latent_audit(m,seed); rows[-1]['latent_R2']=np.nan
            if mode=='aligned' and seed==0: torch.save(m.state_dict(),f'{OUT}/aligned_seed0.pt')
    df=pd.DataFrame(rows); df.to_csv(f'{OUT}/per_seed.csv',index=False)
    print(df.groupby(['mode','dynamic']).median(numeric_only=True).to_string())
