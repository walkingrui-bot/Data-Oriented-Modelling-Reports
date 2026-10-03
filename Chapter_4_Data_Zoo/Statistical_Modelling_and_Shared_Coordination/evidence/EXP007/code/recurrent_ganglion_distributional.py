import os, math, numpy as np, pandas as pd, torch
from torch import nn
ROOT='/mnt/data/INTERNAL_COORDINATION_007'; OUT=f'{ROOT}/results_recurrent'; os.makedirs(OUT,exist_ok=True); torch.set_num_threads(1)
back=np.load(f'{ROOT}/data/diabetes_backbone.npz',allow_pickle=True); X=back['X'].astype(np.float32); tr=back['train_idx']; te=back['test_idx']; D=10; C=6; K=5; taus=torch.tensor([.1,.25,.5,.75,.9])
def draw(Xin,rng):
 s=np.linspace(.85,1.18,D); b=np.linspace(-.18,.18,D); o=[]; o.append(np.clip(Xin*s+b+.025*rng.normal(size=Xin.shape),-4,4)); step=np.linspace(.30,.55,D); o.append(np.clip(np.round((Xin+.08*rng.normal(size=Xin.shape))/step)*step+.03*rng.normal(size=Xin.shape),-4,4)); lod=np.linspace(-.9,-.25,D); o.append(np.clip(np.maximum(Xin+.10*rng.normal(size=Xin.shape),lod),-4,4)); cap=np.linspace(.9,1.7,D); o.append(np.clip(np.minimum(Xin+.08*rng.normal(size=Xin.shape),cap),-4,4)); sig=.05+.16/(1+np.exp(-Xin)); o.append(np.clip(Xin+sig*rng.normal(size=Xin.shape),-4,4)); gain=np.linspace(.85,1.20,D); off=np.linspace(.08,-.10,D); o.append(np.clip(np.tanh(gain*Xin+off)+.08*rng.normal(size=Xin.shape),-4,4)); return np.stack(o,1).astype(np.float32)
class In(nn.Module):
 def __init__(self): super().__init__(); self.net=nn.Sequential(nn.Linear(D,32),nn.Tanh(),nn.Linear(32,16))
 def forward(self,x): return self.net(x)
class Out(nn.Module):
 def __init__(self): super().__init__(); self.net=nn.Sequential(nn.Linear(16,48),nn.Tanh(),nn.Linear(48,D*K))
 def forward(self,z):
  raw=self.net(z).view(-1,D,K); base=raw[:,:,:1]; inc=torch.nn.functional.softplus(raw[:,:,1:]); return torch.cat([base,base+torch.cumsum(inc,-1)],-1)
def orth(seed,scale=.75):
 g=torch.Generator().manual_seed(seed); a=torch.randn(16,16,generator=g); q,_=torch.linalg.qr(a); return scale*q
class Ganglion(nn.Module):
 def __init__(self,seed=0,mode='trainable'):
  super().__init__(); self.ins=nn.ModuleList([In() for _ in range(C)]); self.outs=nn.ModuleList([Out() for _ in range(C)]); self.M=nn.Parameter(orth(100+seed)); self.mode=mode
  if mode=='identity':
   with torch.no_grad(): self.M.copy_(torch.eye(16)*.75); self.M.requires_grad=False
  elif mode=='fixed_random': self.M.requires_grad=False
 def step(self,r,y,c): return torch.tanh(r@self.M.T + self.ins[c](y))
 def q(self,r,c): return self.outs[c](r)
def qloss(q,y):
 e=y[:,:,None]-q; t=taus[None,None,:]; return torch.maximum(t*e,(t-1)*e).mean()
def train(seed,mode,steps=450):
 torch.manual_seed(seed); rng=np.random.default_rng(1000+seed); m=Ganglion(seed,mode); opt=torch.optim.Adam([p for p in m.parameters() if p.requires_grad],lr=.004)
 for st in range(steps):
  ids=rng.choice(tr,80,False); src=draw(X[ids],rng); tgt=draw(X[ids],rng); B=torch.tensor(src); T=torch.tensor(tgt); order=rng.permutation(C); L=int(rng.integers(1,C+1)); r=torch.zeros(len(ids),16); losses=[]
  for kk,c in enumerate(order[:L]):
   r=m.step(r,B[:,c],int(c))
   # current-world distribution: score two random output channels after each evidence item
   for j in rng.choice(C,size=2,replace=False): losses.append(qloss(m.q(r,int(j)),T[:,j]))
  loss=torch.stack(losses).mean(); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(),5.); opt.step()
 return m
def score(m,seed,reps=8,orders=6):
 rng=np.random.default_rng(9000+seed); ids=te; src=draw(X[ids],rng); tg=np.stack([draw(X[ids],rng) for _ in range(reps)],0); B=torch.tensor(src); res=[]
 for nobs in [1,2,3,6]:
  pins=[]; cov=[]; states=[]; med_preds=[]
  # same source measurements, different orders
  ords=[]
  for oo in range(orders): ords.append(rng.permutation(C)[:nobs])
  with torch.no_grad():
   for order in ords:
    r=torch.zeros(len(ids),16)
    for c in order: r=m.step(r,B[:,int(c)],int(c))
    states.append(r.numpy())
    meds=[]
    for j in range(C):
     q=m.q(r,j).numpy(); meds.append(q[:,:,2]); y=tg[:,:,j]; e=y[:,:,:,None]-q[None]; tau=np.array([.1,.25,.5,.75,.9])[None,None,None,:]; pins.append(np.maximum(tau*e,(tau-1)*e).mean()); cov.append(((y>=q[:,:,0][None])&(y<=q[:,:,-1][None])).mean())
    med_preds.append(np.stack(meds,1))
  # order sensitivity: predictive median difference between orders
  P=np.stack(med_preds,0); order_pred_sd=float(P.std(0).mean()); S=np.stack(states,0); order_state_sd=float(S.std(0).mean())
  res.append({'nobs':nobs,'pinball':float(np.mean(pins)),'coverage80':float(np.mean(cov)),'order_pred_sd':order_pred_sd,'order_state_sd':order_state_sd})
 return res
def ablate(m,seed):
 orig=m.M.detach().clone(); out=[]
 for name,M in [('base',orig),('identity',torch.eye(16)*float(torch.linalg.svdvals(orig).mean())),('random',orth(7000+seed,float(torch.linalg.svdvals(orig).mean())) )]:
  with torch.no_grad(): m.M.copy_(M)
  x=score(m,seed,reps=5,orders=4); row=[z for z in x if z['nobs']==6][0]; out.append({'ablation':name,**row})
 U,S,Vh=torch.linalg.svd(orig)
 for rr in [2,4,8,12]:
  Mr=(U[:,:rr]*S[:rr])@Vh[:rr];
  with torch.no_grad(): m.M.copy_(Mr)
  row=[z for z in score(m,seed,reps=5,orders=4) if z['nobs']==6][0]; out.append({'ablation':f'rank{rr}',**row})
 with torch.no_grad(): m.M.copy_(orig)
 return out
rows=[]; abl=[]
for mode in ['trainable','identity','fixed_random']:
 for seed in range(3):
  m=train(seed,mode)
  for r in score(m,seed): rows.append({'mode':mode,'seed':seed,**r})
  if mode=='trainable':
   for a in ablate(m,seed): abl.append({'seed':seed,**a})
   if seed==0: torch.save(m.state_dict(),f'{OUT}/trainable_seed0.pt')
pd.DataFrame(rows).to_csv(f'{OUT}/per_seed_by_evidence.csv',index=False); pd.DataFrame(abl).to_csv(f'{OUT}/ablation.csv',index=False)
print('MAIN median')
print(pd.DataFrame(rows).groupby(['mode','nobs']).median(numeric_only=True).to_string())
print('\nABLATION median')
print(pd.DataFrame(abl).groupby('ablation').median(numeric_only=True).to_string())
