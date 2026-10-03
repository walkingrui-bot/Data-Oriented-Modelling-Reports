from pathlib import Path
import os, json, math, hashlib
import numpy as np, pandas as pd
import torch
from torch import nn
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

ROOT=str(Path(__file__).resolve().parents[1])
os.makedirs(f'{ROOT}/results',exist_ok=True); os.makedirs(f'{ROOT}/data',exist_ok=True)
torch.set_num_threads(1)

# Real biomedical backbone: 442 diabetes patients, 10 baseline measurements.
Xraw,y=load_diabetes(return_X_y=True, scaled=False)
feature_names=load_diabetes().feature_names
idx=np.arange(len(Xraw))
tr_idx, te_idx=train_test_split(idx,test_size=0.30,random_state=20261001)
sc=StandardScaler().fit(Xraw[tr_idx])
X=sc.transform(Xraw).astype(np.float32)
np.savez_compressed(f'{ROOT}/data/diabetes_backbone.npz', Xraw=Xraw, X=X, y=y, train_idx=tr_idx, test_idx=te_idx, feature_names=np.array(feature_names,dtype=object))

# Deterministic, epidemiology-inspired measurement operators.
def fixed_noise(shape, seed):
    rng=np.random.default_rng(seed); return rng.normal(0,1,size=shape).astype(np.float32)

def channelize(X, drift=False):
    X=np.asarray(X,np.float32)
    out=[]
    # 0: calibration bias / proportional error
    s=np.linspace(0.85,1.18,X.shape[1],dtype=np.float32); b=np.linspace(-0.18,0.18,X.shape[1],dtype=np.float32)
    out.append(np.clip(X*s+b,-4,4))
    # 1: self-report style heaping/rounding + mild noise
    step=np.linspace(0.30,0.55,X.shape[1],dtype=np.float32)
    z=np.round(X/step)*step + 0.035*fixed_noise(X.shape,11)
    out.append(np.clip(z,-4,4))
    # 2: lower limit of detection + assay noise
    lod=np.linspace(-0.9,-0.25,X.shape[1],dtype=np.float32)
    z=np.maximum(X+0.06*fixed_noise(X.shape,22),lod)
    out.append(np.clip(z,-4,4))
    # 3: top-coding / saturation
    cap=np.linspace(0.9,1.7,X.shape[1],dtype=np.float32)
    z=np.minimum(X+0.04*fixed_noise(X.shape,33),cap)
    out.append(np.clip(z,-4,4))
    # 4: heteroscedastic measurement error
    eps=fixed_noise(X.shape,44)
    sigma=0.045+0.11/(1+np.exp(-X))
    z=X+sigma*eps
    out.append(np.clip(z,-4,4))
    # 5: nonlinear assay response; drift changes only this measurement mechanism
    if not drift:
        gain=np.linspace(0.85,1.20,X.shape[1],dtype=np.float32); offset=np.linspace(0.08,-0.10,X.shape[1],dtype=np.float32)
        z=np.tanh(gain*X+offset)+0.035*fixed_noise(X.shape,55)
    else:
        gain=np.linspace(1.15,1.55,X.shape[1],dtype=np.float32); offset=np.linspace(-0.28,0.24,X.shape[1],dtype=np.float32)
        z=0.68*np.tanh(1.35*gain*X+1.25*offset)+0.22*np.sin(2.0*X)+0.04*(X**2)*np.sign(X)+0.035*fixed_noise(X.shape,66)
    out.append(np.clip(z,-4,4))
    return np.stack(out,axis=1).astype(np.float32) # N x 6 x 10

Y_base=channelize(X,False); Y_drift=channelize(X,True)
np.savez_compressed(f'{ROOT}/data/measurement_channels.npz', base=Y_base, drift=Y_drift)

class SharedPerception(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Linear(10,32),nn.Tanh(),nn.Linear(32,16),nn.Tanh())
    def forward(self,x): return self.net(x)
class SharedGenerator(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Linear(16,32),nn.Tanh(),nn.Linear(32,10))
    def forward(self,z): return self.net(z)
class AffineAdapter(nn.Module):
    def __init__(self):
        super().__init__(); self.logscale=nn.Parameter(torch.zeros(16)); self.bias=nn.Parameter(torch.zeros(16))
    def forward(self,z): return z*torch.exp(self.logscale)+self.bias
class ResidualChannelNet(nn.Module):
    def __init__(self):
        super().__init__(); self.net=nn.Sequential(nn.Linear(16,32),nn.Tanh(),nn.Linear(32,16)); self.alpha=nn.Parameter(torch.tensor(0.15))
    def forward(self,z): return z+self.alpha*self.net(z)
class Model(nn.Module):
    def __init__(self,mode='affine'):
        super().__init__(); self.perc=SharedPerception(); self.core=nn.Linear(16,16); self.gen=SharedGenerator();
        A=AffineAdapter if mode=='affine' else ResidualChannelNet
        self.cin=nn.ModuleList([A() for _ in range(6)]); self.cout=nn.ModuleList([A() for _ in range(6)]); self.mode=mode
    def encode(self,x,c):
        h=self.perc(x); h=self.cin[c](h); return torch.tanh(self.core(h))
    def decode(self,z,c): return self.gen(self.cout[c](z))

def bind_loss(model,batch, pair_count=8):
    # stochastic coverage of the 6x6 binding field; all pairs recur over training
    pairs=torch.randint(0,36,(pair_count,)).tolist()
    losses=[]
    cache={}
    for p in pairs:
        i,j=divmod(p,6)
        if i not in cache: cache[i]=model.encode(batch[:,i,:],i)
        losses.append(((model.decode(cache[i],j)-batch[:,j,:])**2).mean())
    return torch.stack(losses).mean()

def focus_loss(model,batch,c=5):
    losses=[]; cache={}
    pairs=[]
    for j in range(6): pairs.append((c,j))
    for i in range(6):
        if i!=c: pairs.append((i,c))
    for i,j in pairs:
        if i not in cache: cache[i]=model.encode(batch[:,i,:],i)
        losses.append(((model.decode(cache[i],j)-batch[:,j,:])**2).mean())
    return torch.stack(losses).mean()

def eval_model(model, arr, ids):
    model.eval(); B=torch.tensor(arr[ids],dtype=torch.float32)
    mat=np.zeros((6,6)); zs=[]
    with torch.no_grad():
        for i in range(6):
            z=model.encode(B[:,i,:],i); zs.append(z.numpy())
            for j in range(6): mat[i,j]=torch.sqrt(((model.decode(z,j)-B[:,j,:])**2).mean()).item()
    Z=np.stack(zs,axis=1) # n x 6 x16
    cross=mat[~np.eye(6,dtype=bool)].mean(); selfrm=np.diag(mat).mean()
    fm=[]
    for i in range(6):
        for j in range(6):
            if i!=j and (i==5 or j==5): fm.append(mat[i,j])
    focus_cross=float(np.mean(fm))
    # within-scene latent distance normalized by latent sd
    sd=Z.reshape(-1,16).std(axis=0).mean()+1e-8
    d=[]
    for a in range(6):
        for b in range(a+1,6): d.append(np.linalg.norm(Z[:,a]-Z[:,b],axis=1).mean()/sd/math.sqrt(16))
    latent_dist=float(np.mean(d))
    # retrieval across all directed channel pairs
    retrieval=[]
    for a in range(6):
        Za=Z[:,a]
        for b in range(6):
            if a==b: continue
            Zb=Z[:,b]
            D=((Za[:,None,:]-Zb[None,:,:])**2).sum(-1)
            retrieval.append((D.argmin(1)==np.arange(len(ids))).mean())
    # audit: linear readout of clean reference X from pooled latent, heldout only fit on train separately elsewhere
    return dict(cross_rmse=float(cross),focus_cross_rmse=focus_cross,self_rmse=float(selfrm),latent_dist=latent_dist,retrieval=float(np.mean(retrieval))),mat,Z

def audit_clean(model, arr):
    model.eval()
    def pooled(ids):
        B=torch.tensor(arr[ids],dtype=torch.float32)
        with torch.no_grad(): return np.mean(np.stack([model.encode(B[:,i,:],i).numpy() for i in range(6)],1),1)
    Ztr,Zte=pooled(tr_idx),pooled(te_idx)
    rg=Ridge(alpha=1.0).fit(Ztr,X[tr_idx]); pred=rg.predict(Zte)
    return float(r2_score(X[te_idx],pred,multioutput='variance_weighted'))

def train(seed,mode,steps=300):
    torch.manual_seed(seed); np.random.seed(seed)
    m=Model(mode); opt=torch.optim.Adam(m.parameters(),lr=0.008)
    rng=np.random.default_rng(seed+1234)
    first_grad=None; traj=[]
    for step in range(steps):
        ids=rng.choice(tr_idx,size=min(64,len(tr_idx)),replace=False)
        b=torch.tensor(Y_base[ids],dtype=torch.float32)
        opt.zero_grad(); loss=bind_loss(m,b); loss.backward()
        if step==0:
            def gradrms(params):
                vals=[p.grad.detach().pow(2).mean().item() for p in params if p.grad is not None]
                return float(math.sqrt(np.mean(vals))) if vals else 0.
            first_grad={'perception':gradrms(m.perc.parameters()),'channel':gradrms(list(m.cin.parameters())+list(m.cout.parameters())),'core':gradrms(m.core.parameters()),'generator':gradrms(m.gen.parameters())}
        opt.step()
        if step in [0,9,49,149,299]:
            e,_,_=eval_model(m,Y_base,te_idx); traj.append({'step':step+1,'loss':float(loss.item()),**e})
    return m,first_grad,traj

def shifted_eval_array():
    Y=Y_base.copy(); Y[:,5,:]=Y_drift[:,5,:]; return Y
Y_shift=shifted_eval_array()

def adapt_channel_only(model,mode,seed,cal_n=48,steps=150):
    # update only channel-5 in/out modules; shared reality frozen
    for p in model.parameters(): p.requires_grad=False
    params=list(model.cin[5].parameters())+list(model.cout[5].parameters())
    for p in params: p.requires_grad=True
    opt=torch.optim.Adam(params,lr=0.01)
    rng=np.random.default_rng(seed+9000); cal=rng.choice(tr_idx,size=cal_n,replace=False)
    core0=torch.cat([p.detach().flatten() for p in model.core.parameters()]).clone()
    for _ in range(steps):
        ids=rng.choice(cal,size=min(48,len(cal)),replace=False); b=torch.tensor(Y_shift[ids],dtype=torch.float32)
        opt.zero_grad(); loss=focus_loss(model,b,5); loss.backward(); opt.step()
    core1=torch.cat([p.detach().flatten() for p in model.core.parameters()])
    return model,float(torch.norm(core1-core0).item())

def adapt_whole(model,seed,cal_n=48,steps=150):
    for p in model.parameters(): p.requires_grad=True
    opt=torch.optim.Adam(model.parameters(),lr=0.003)
    rng=np.random.default_rng(seed+9100); cal=rng.choice(tr_idx,size=cal_n,replace=False)
    core0=torch.cat([p.detach().flatten() for p in model.core.parameters()]).clone()
    for _ in range(steps):
        ids=rng.choice(cal,size=min(48,len(cal)),replace=False); b=torch.tensor(Y_shift[ids],dtype=torch.float32)
        opt.zero_grad(); loss=bind_loss(model,b); loss.backward(); opt.step()
    core1=torch.cat([p.detach().flatten() for p in model.core.parameters()])
    return model,float(torch.norm(core1-core0).item())

