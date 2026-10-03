import numpy as np, pandas as pd, torch, os
from torch import nn
ROOT='/mnt/data/INTERNAL_COORDINATION_007'; torch.set_num_threads(1)
back=np.load(f'{ROOT}/data/diabetes_backbone.npz',allow_pickle=True); X=back['X'].astype(np.float32); tr=back['train_idx']; te=back['test_idx']; D=10; K=5; C=6
Q=np.load(f'{ROOT}/data/seventh_channel.npz')['Q'].astype(np.float32); taus=torch.tensor([.1,.25,.5,.75,.9])
def draw6(Xin,rng):
 s=np.linspace(.85,1.18,D); b=np.linspace(-.18,.18,D); out=[]; out.append(np.clip(Xin*s+b+.025*rng.normal(size=Xin.shape),-4,4)); step=np.linspace(.30,.55,D); out.append(np.clip(np.round((Xin+.08*rng.normal(size=Xin.shape))/step)*step+.03*rng.normal(size=Xin.shape),-4,4)); lod=np.linspace(-.9,-.25,D); out.append(np.clip(np.maximum(Xin+.10*rng.normal(size=Xin.shape),lod),-4,4)); cap=np.linspace(.9,1.7,D); out.append(np.clip(np.minimum(Xin+.08*rng.normal(size=Xin.shape),cap),-4,4)); sig=.05+.16/(1+np.exp(-Xin)); out.append(np.clip(Xin+sig*rng.normal(size=Xin.shape),-4,4)); gain=np.linspace(.85,1.20,D); off=np.linspace(.08,-.10,D); out.append(np.clip(np.tanh(gain*Xin+off)+.08*rng.normal(size=Xin.shape),-4,4)); return np.stack(out,1).astype(np.float32)
def draw7(Xin,rng):
 U=Xin@Q; z=.72*np.tanh(1.1*U)+.18*np.sin(1.7*U)+.08*np.sign(U)*(U**2)/(1+np.abs(U)); z+=.09*rng.normal(size=z.shape); return np.clip(z,-4,4).astype(np.float32)
class Pre(nn.Module):
 def __init__(self): super().__init__(); self.net=nn.Sequential(nn.Linear(D,32),nn.Tanh(),nn.Linear(32,16),nn.Tanh())
 def forward(self,x): return self.net(x)
class Post(nn.Module):
 def __init__(self): super().__init__(); self.net=nn.Sequential(nn.Linear(16,48),nn.Tanh(),nn.Linear(48,D*K))
 def forward(self,z):
  raw=self.net(z).view(-1,D,K); base=raw[:,:,:1]; inc=torch.nn.functional.softplus(raw[:,:,1:]); return torch.cat([base,base+torch.cumsum(inc,-1)],-1)
def orth(seed):
 g=torch.Generator().manual_seed(seed); a=torch.randn(16,16,generator=g); q,_=torch.linalg.qr(a); return .9*q
class M6(nn.Module):
 def __init__(self,seed): super().__init__(); self.pre=nn.ModuleList([Pre() for _ in range(6)]); self.post=nn.ModuleList([Post() for _ in range(6)]); self.M=nn.Parameter(orth(100+seed))
 def enc(self,x,c): return torch.tanh(self.pre[c](x)@self.M.T)
 def q(self,z,c): return self.post[c](z)
class M7(nn.Module):
 def __init__(self,base):
  super().__init__(); self.pre=nn.ModuleList([Pre() for _ in range(7)]); self.post=nn.ModuleList([Post() for _ in range(7)]); self.M=nn.Parameter(base.M.detach().clone())
  for c in range(6): self.pre[c].load_state_dict(base.pre[c].state_dict()); self.post[c].load_state_dict(base.post[c].state_dict())
 def enc(self,x,c): return torch.tanh(self.pre[c](x)@self.M.T)
 def q(self,z,c): return self.post[c](z)
def loss(q,y):
 e=y[:,:,None]-q; t=taus[None,None,:]; return torch.maximum(t*e,(t-1)*e).mean()
def base(seed,steps=220):
 torch.manual_seed(seed); rng=np.random.default_rng(1000+seed); m=M6(seed); opt=torch.optim.Adam(m.parameters(),lr=.005)
 for _ in range(steps):
  ids=rng.choice(tr,96,False); A=torch.tensor(draw6(X[ids],rng)); T=torch.tensor(draw6(X[ids],rng)); ls=[]; cache={}
  for __ in range(12):
   i=int(rng.integers(6)); j=int(rng.integers(6));
   if i not in cache: cache[i]=m.enc(A[:,i],i)
   ls.append(loss(m.q(cache[i],j),T[:,j]))
  L=torch.stack(ls).mean(); opt.zero_grad(); L.backward(); opt.step()
 return m
def score(m,seed,reps=4):
 rng=np.random.default_rng(8000+seed); A6=draw6(X[te],rng); A7=draw7(X[te],rng); A=np.concatenate([A6,A7[:,None]],1); B=torch.tensor(A); new=[]; old=[]
 tg=[]
 for _ in range(reps): tg.append(np.concatenate([draw6(X[te],rng),draw7(X[te],rng)[:,None]],1))
 tg=np.stack(tg)
 with torch.no_grad():
  for i in range(7):
   z=m.enc(B[:,i],i)
   for j in range(7):
    q=m.q(z,j).numpy(); y=tg[:,:,j]; e=y[:,:,:,None]-q[None]; tau=np.array([.1,.25,.5,.75,.9])[None,None,None,:]; v=np.maximum(tau*e,(tau-1)*e).mean(); (new if (i==6 or j==6) else old).append(v)
 return np.mean(new),np.mean(old)
def onboard(seed,adapt,steps=120):
 b=base(seed); m=M7(b); M0=m.M.detach().clone()
 for p in m.parameters(): p.requires_grad=False
 ps=list(m.pre[6].parameters())+list(m.post[6].parameters())
 for p in ps: p.requires_grad=True
 if adapt: m.M.requires_grad=True; ps+=[m.M]
 opt=torch.optim.Adam(ps,lr=.006); rng=np.random.default_rng(6000+seed); cal=rng.choice(tr,64,False)
 for _ in range(steps):
  ids=rng.choice(cal,64,True); A=np.concatenate([draw6(X[ids],rng),draw7(X[ids],rng)[:,None]],1); T=np.concatenate([draw6(X[ids],rng),draw7(X[ids],rng)[:,None]],1); A=torch.tensor(A); T=torch.tensor(T); ls=[]; z7=m.enc(A[:,6],6)
  for j in range(6): ls.append(loss(m.q(z7,j),T[:,j]))
  for i in range(6): ls.append(loss(m.q(m.enc(A[:,i],i),6),T[:,6]))
  ls.append(loss(m.q(z7,6),T[:,6])); L=torch.stack(ls).mean(); opt.zero_grad(); L.backward(); opt.step()
 n,o=score(m,seed); return {'seed':seed,'mode':'adapt_M' if adapt else 'frozen_M','new_pair_pinball':float(n),'legacy_pinball':float(o),'M_move':float(torch.norm(m.M.detach()-M0))}
rows=[]
for s in range(3): rows += [onboard(s,False),onboard(s,True)]
pd.DataFrame(rows).to_csv(f'{ROOT}/results_dist/onboarding.csv',index=False); print(pd.DataFrame(rows).groupby('mode').median(numeric_only=True).to_string())
