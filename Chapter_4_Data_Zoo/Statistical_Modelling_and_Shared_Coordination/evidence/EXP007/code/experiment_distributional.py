import os, math, copy, json
import numpy as np, pandas as pd
import torch
from torch import nn
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

ROOT='/mnt/data/INTERNAL_COORDINATION_007'
os.makedirs(f'{ROOT}/results_dist',exist_ok=True)
torch.set_num_threads(1)
back=np.load(f'{ROOT}/data/diabetes_backbone.npz',allow_pickle=True)
X=back['X'].astype(np.float32); tr_idx=back['train_idx']; te_idx=back['test_idx']
D=X.shape[1]; C=6
TAUS=torch.tensor([0.1,0.25,0.5,0.75,0.9],dtype=torch.float32)
K=len(TAUS)

# Each call is a fresh measurement draw from the same latent patient state.
def channel_draw(Xin, rng):
    Xin=np.asarray(Xin,np.float32); out=[]
    s=np.linspace(0.85,1.18,D,dtype=np.float32); b=np.linspace(-0.18,0.18,D,dtype=np.float32)
    z=Xin*s+b + 0.025*rng.normal(size=Xin.shape); out.append(np.clip(z,-4,4))
    step=np.linspace(0.30,0.55,D,dtype=np.float32)
    z=np.round((Xin+0.08*rng.normal(size=Xin.shape))/step)*step + 0.03*rng.normal(size=Xin.shape); out.append(np.clip(z,-4,4))
    lod=np.linspace(-0.9,-0.25,D,dtype=np.float32)
    z=np.maximum(Xin+0.10*rng.normal(size=Xin.shape),lod); out.append(np.clip(z,-4,4))
    cap=np.linspace(0.9,1.7,D,dtype=np.float32)
    z=np.minimum(Xin+0.08*rng.normal(size=Xin.shape),cap); out.append(np.clip(z,-4,4))
    sigma=0.05+0.16/(1+np.exp(-Xin))
    z=Xin+sigma*rng.normal(size=Xin.shape); out.append(np.clip(z,-4,4))
    gain=np.linspace(0.85,1.20,D,dtype=np.float32); offset=np.linspace(0.08,-0.10,D,dtype=np.float32)
    z=np.tanh(gain*Xin+offset)+0.08*rng.normal(size=Xin.shape); out.append(np.clip(z,-4,4))
    return np.stack(out,axis=1).astype(np.float32)

class Pre(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Linear(D,32),nn.Tanh(),nn.Linear(32,16),nn.Tanh())
    def forward(self,x): return self.net(x)
class QPost(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Linear(16,48),nn.Tanh(),nn.Linear(48,D*K))
    def forward(self,z):
        raw=self.net(z).view(-1,D,K)
        base=raw[:,:,0:1]
        inc=torch.nn.functional.softplus(raw[:,:,1:])
        return torch.cat([base,base+torch.cumsum(inc,dim=-1)],dim=-1)

def orth(seed,scale=.9):
    g=torch.Generator().manual_seed(seed); a=torch.randn(16,16,generator=g); q,_=torch.linalg.qr(a); return q*scale

class Shared(nn.Module):
    def __init__(self,seed=0):
        super().__init__(); self.pre=nn.ModuleList([Pre() for _ in range(C)]); self.post=nn.ModuleList([QPost() for _ in range(C)]); self.M=nn.Parameter(orth(100+seed))
    def encode(self,x,c): return torch.tanh(self.pre[c](x)@self.M.T)
    def predict_q(self,z,c): return self.post[c](z)
class Identity(nn.Module):
    def __init__(self,seed=0):
        super().__init__(); self.pre=nn.ModuleList([Pre() for _ in range(C)]); self.post=nn.ModuleList([QPost() for _ in range(C)])
    def encode(self,x,c): return self.pre[c](x)
    def predict_q(self,z,c): return self.post[c](z)
class Private(nn.Module):
    def __init__(self,seed=0):
        super().__init__(); self.pre=nn.ModuleList([Pre() for _ in range(C)]); self.post=nn.ModuleList([QPost() for _ in range(C)]); self.M=nn.ParameterList([nn.Parameter(orth(200+seed*17+c)) for c in range(C)])
    def encode(self,x,c): return torch.tanh(self.pre[c](x)@self.M[c].T)
    def predict_q(self,z,c): return self.post[c](z)

def qloss(q,y):
    e=y[:,:,None]-q
    t=TAUS.to(q.device)[None,None,:]
    return torch.maximum(t*e,(t-1)*e).mean()

def train(seed,kind,steps=280):
    torch.manual_seed(seed); np.random.seed(seed)
    m={'shared':Shared,'identity':Identity,'private':Private}[kind](seed)
    opt=torch.optim.Adam(m.parameters(),lr=0.005)
    rng=np.random.default_rng(5000+seed)
    traj=[]
    for st in range(steps):
        ids=rng.choice(tr_idx,size=min(96,len(tr_idx)),replace=False)
        src=channel_draw(X[ids],rng); tgt=channel_draw(X[ids],rng) # independent measurement draws
        src=torch.tensor(src); tgt=torch.tensor(tgt)
        pairs=[(rng.integers(C),rng.integers(C)) for _ in range(14)]
        losses=[]; cache={}
        for i,j in pairs:
            if i not in cache: cache[i]=m.encode(src[:,i,:],int(i))
            losses.append(qloss(m.predict_q(cache[i],int(j)),tgt[:,j,:]))
        loss=torch.stack(losses).mean(); opt.zero_grad(); loss.backward(); opt.step()
        if st in [0,49,149,279]: traj.append((st+1,float(loss)))
    return m,traj

def evaluate(m,seed,audit_reps=10):
    rng=np.random.default_rng(20000+seed)
    ids=te_idx
    # one independent source draw; many independent target draws
    src=channel_draw(X[ids],rng)
    target_reps=np.stack([channel_draw(X[ids],rng) for _ in range(audit_reps)],axis=0) # R,N,C,D
    B=torch.tensor(src)
    pin=[]; cov=[]; width=[]; qerr=[]; zs=[]
    # empirical quantiles across target repetitions = audit-only distribution target
    empq=np.quantile(target_reps,[.1,.25,.5,.75,.9],axis=0).transpose(1,2,3,0) # N,C,D,K
    with torch.no_grad():
        for i in range(C):
            z=m.encode(B[:,i,:],i); zs.append(z.numpy())
            for j in range(C):
                q=m.predict_q(z,j).numpy()
                # score all independent heldout draws with pinball
                ys=target_reps[:,:,j,:] # R,N,D
                qq=q[None,:,:,:]
                e=ys[:,:,:,None]-qq
                tau=np.array([.1,.25,.5,.75,.9])[None,None,None,:]
                pin.append(np.maximum(tau*e,(tau-1)*e).mean())
                lo=q[:,:,0]; hi=q[:,:,-1]
                cov.append(((ys>=lo[None])&(ys<=hi[None])).mean())
                width.append((hi-lo).mean())
                qerr.append(np.abs(q-empq[:,j]).mean())
    Z=np.stack(zs,1)
    sd=Z.reshape(-1,16).std(0).mean()+1e-8
    d=[]
    for a in range(C):
        for b in range(a+1,C): d.append(np.linalg.norm(Z[:,a]-Z[:,b],axis=1).mean()/sd/math.sqrt(16))
    ret=[]
    for a in range(C):
        for b in range(C):
            if a==b: continue
            Dm=((Z[:,a,None,:]-Z[:,b][None,:,:])**2).sum(-1); ret.append((Dm.argmin(1)==np.arange(len(ids))).mean())
    return dict(pinball=float(np.mean(pin)),coverage80=float(np.mean(cov)),interval_width=float(np.mean(width)),quantile_mae=float(np.mean(qerr)),latent_dist=float(np.mean(d)),retrieval=float(np.mean(ret))),Z

def audit_x(m,seed):
    rng=np.random.default_rng(30000+seed)
    def pool(ids):
        arr=channel_draw(X[ids],rng); B=torch.tensor(arr)
        with torch.no_grad(): return np.mean(np.stack([m.encode(B[:,i,:],i).numpy() for i in range(C)],1),1)
    ztr=pool(tr_idx); zte=pool(te_idx); rg=Ridge(alpha=1.).fit(ztr,X[tr_idx]); return float(r2_score(X[te_idx],rg.predict(zte),multioutput='variance_weighted'))

def ablate_shared(m,seed):
    orig=m.M.detach().clone(); out=[]
    base,_=evaluate(m,seed); out.append({'ablation':'base',**base})
    s=torch.linalg.svdvals(orig); scale=float(s.mean())
    for name,M in [('identity',torch.eye(16)*scale),('random',orth(9000+seed,scale))]:
        with torch.no_grad(): m.M.copy_(M)
        e,_=evaluate(m,seed); out.append({'ablation':name,**e})
    U,S,Vh=torch.linalg.svd(orig)
    for r in [2,4,8,12]:
        Mr=(U[:,:r]*S[:r])@Vh[:r]
        with torch.no_grad(): m.M.copy_(Mr)
        e,_=evaluate(m,seed); out.append({'ablation':f'rank{r}',**e})
    with torch.no_grad(): m.M.copy_(orig)
    return out

rows=[]; abls=[]; tr=[]
models={}
for kind in ['shared','identity','private']:
    models[kind]={}
    for seed in range(3):
        m,t=train(seed,kind); models[kind][seed]=m
        e,Z=evaluate(m,seed); e['clean_state_r2']=audit_x(m,seed)
        rows.append({'kind':kind,'seed':seed,**e});
        tr += [{'kind':kind,'seed':seed,'step':s,'loss':l} for s,l in t]
        if kind=='shared':
            for x in ablate_shared(m,seed): abls.append({'seed':seed,**x})
        if seed==0:
            np.save(f'{ROOT}/results_dist/{kind}_seed0_latent.npy',Z); torch.save(m.state_dict(),f'{ROOT}/results_dist/{kind}_seed0.pt')

pd.DataFrame(rows).to_csv(f'{ROOT}/results_dist/per_seed.csv',index=False)
pd.DataFrame(abls).to_csv(f'{ROOT}/results_dist/matrix_ablation.csv',index=False)
pd.DataFrame(tr).to_csv(f'{ROOT}/results_dist/training_trace.csv',index=False)
print(pd.DataFrame(rows).groupby('kind').median(numeric_only=True).to_string())
print('\nABLATION')
print(pd.DataFrame(abls).groupby('ablation').median(numeric_only=True).to_string())
