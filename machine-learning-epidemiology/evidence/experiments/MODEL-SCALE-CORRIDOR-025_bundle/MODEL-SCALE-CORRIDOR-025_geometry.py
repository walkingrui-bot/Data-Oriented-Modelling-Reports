#!/usr/bin/env python3
from pathlib import Path
import math, random, argparse
import numpy as np, pandas as pd
import torch, torch.nn as nn, torch.nn.functional as F
apg=argparse.ArgumentParser(); apg.add_argument('--coverage',type=float,required=True); apg.add_argument('--widths',type=str,default='8,16,32,64,128'); args=apg.parse_args()
OUT=Path('/mnt/data'); torch.set_num_threads(4)
N=5; OPS=['P1','P2','D2','NEG']
def ap(x,o): return {'P1':(x+1)%N,'P2':(x+2)%N,'D2':(2*x)%N,'NEG':(-x)%N}[o]
def di(x,g): d=(x-g)%N; return min(d,N-d)
def latent(g,x,m,c):
 main=ap(x,m); branch=ap(x,c); return main,branch,(branch if di(branch,g)<di(main,g) else main)
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']+[f'G{i}' for i in range(N)]+[f'X{i}' for i in range(N)]+OPS+[f'Y{i}' for i in range(N)]
stoi={t:i for i,t in enumerate(TOK)}; V=len(TOK); yids=torch.tensor([stoi[f'Y{i}'] for i in range(N)])
seqs=[]; rows=[]
for g in range(N):
 for x in range(N):
  for mi,m in enumerate(OPS):
   for ci,c in enumerate(OPS):
    main,branch,ans=latent(g,x,m,c); ts=['<BOS>',f'G{g}',f'X{x}',m,'ALT',c,'<SEP>','THINK','CHECK','FINAL',f'Y{ans}','<EOS>']
    seqs.append([stoi[t] for t in ts]); rows.append((g,x,mi,ci,ans))
SEQ=torch.tensor(seqs); truth=np.array([r[-1] for r in rows])
def mask(cov):
 k={.25:1,.5:2,1.:4}[cov]; out=[]
 for g,x,mi,ci,_ in rows:
  base=(g*5+x+mi)%4; out.append(ci in {(base+j)%4 for j in range(k)})
 return np.array(out)
class LM(nn.Module):
 def __init__(self,hid):
  super().__init__(); self.hid=hid; self.layers=2; self.emb=nn.Embedding(V,16); self.gru=nn.GRU(16,hid,2,batch_first=True); self.head=nn.Linear(hid,V)
 def forward(self,t,h0=None): o,h=self.gru(self.emb(t),h0); return self.head(o),h
 def state(self,t): return self.gru(self.emb(t))[1]
 def cont(self,h,t): o,h2=self.gru(self.emb(t),h); return self.head(o),h2
def params(m): return sum(p.numel() for p in m.parameters())
def train(hid,cov,seed):
 random.seed(seed); np.random.seed(seed); torch.manual_seed(seed); m=LM(hid); ids=np.where(mask(cov))[0]; t=SEQ[ids,:10]; y=SEQ[ids,10]; opt=torch.optim.AdamW(m.parameters(),lr=.012,weight_decay=1e-5); streak=0
 for ep in range(900):
  lg,_=m(t); loss=F.cross_entropy(lg[:,9],y); opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(m.parameters(),5); opt.step()
  if ep%10==0:
   with torch.no_grad(): a=(lg[:,9].argmax(-1)==y).float().mean().item()
   streak=streak+1 if a>.999 else 0
   if streak>=3: break
 with torch.no_grad(): lg,_=m(SEQ[:,:10]); pr=lg[:,9].argmax(-1); fa=float((pr==SEQ[:,10]).float().mean()); ta=float((pr[ids]==SEQ[ids,10]).float().mean())
 return m,dict(epochs=ep+1,train_acc=ta,full_acc=fa,params=params(m),n_train=len(ids))
def metric(m,info,hid,cov,seed):
 # all CHECK states define empirical geometry
 h=m.state(SEQ[:,:9]).detach(); H=m.layers*m.hid; X=h.permute(1,0,2).reshape(len(SEQ),-1).numpy(); Xc=X-X.mean(0,keepdims=True)
 # hidden-state spectrum
 s=np.linalg.svd(Xc/np.sqrt(len(X)-1),compute_uv=False); e=s*s; state_stable=float(e.sum()/e.max()); state_d95=int(np.searchsorted(np.cumsum(e/e.sum()),.95)+1)
 # whitened coordinates on modes covering 99% variance
 U,S,Vt=np.linalg.svd(Xc,full_matrices=False); ev=S*S; k99=int(np.searchsorted(np.cumsum(ev/ev.sum()),.99)+1); k99=max(k99,1); Z=U[:,:k99]*np.sqrt(len(X)-1) # whitened scores; covariance I
 # per-dim RMS nearest different answer in whitened metric
 sq=(Z*Z).sum(1); d2=(sq[:,None]+sq[None,:]-2*Z@Z.T)/k99; d2=np.maximum(d2,0); d=np.sqrt(d2); d[truth[:,None]==truth[None,:]]=np.inf; wcrowd=np.min(d,axis=1)
 # outputs + gradients for correct states
 z,_=m.cont(h,SEQ[:,9:10]); yz=z[:,-1][:,yids]; pred=yz.argmax(-1).numpy(); correct=np.where(pred==truth)[0]
 hc=m.state(SEQ[correct,:9]).detach().requires_grad_(True); zc,_=m.cont(hc,SEQ[correct,9:10]); yc=zc[:,-1][:,yids]; yy=torch.tensor(truth[correct]); tmp=yc.detach().clone(); tmp[torch.arange(len(correct)),yy]=-1e9; run=tmp.argmax(-1); margins=yc[torch.arange(len(correct)),yy]-yc[torch.arange(len(correct)),run]
 g=torch.autograd.grad(margins.sum(),hc)[0].permute(1,0,2).reshape(len(correct),-1).detach().numpy()
 # covariance-metric response std sqrt(g^T C g), C from fixed full-world state cloud
 # = ||Xc g|| / sqrt(n-1)
 resp_sd=np.sqrt(np.sum((Xc@g.T)**2,axis=0)/(len(X)-1)+1e-12); rgeo=margins.detach().numpy()/resp_sd
 # whitened gradient coordinates: gradient against PCA-whitened state coordinates
 # covariance-weighted gain is resp_sd
 # gradient direction diversity in whitened tangent metric: columns scores = g V diag(S/sqrt(n-1))
 Csqrt=Vt.T*(S/np.sqrt(len(X)-1))[None,:]
 Gw=g@Csqrt; ss=np.linalg.svd(Gw/np.sqrt(len(Gw)),compute_uv=False); ee=ss*ss; ctrl_stable=float(ee.sum()/ee.max()); ctrl_d95=int(np.searchsorted(np.cumsum(ee/ee.sum()),.95)+1)
 return dict(hidden=hid,coverage=cov,seed=seed,**info,n_correct=len(correct),median_geo_width=float(np.median(rgeo)),median_cov_gain=float(np.median(resp_sd)),median_whitened_crowding=float(np.median(wcrowd[correct])),state_stable_rank=state_stable,state_d95=state_d95,state_k99=k99,control_geo_stable_rank=ctrl_stable,control_geo_d95=ctrl_d95,median_margin=float(margins.median()))
rowsout=[]; cov=args.coverage
for hid in [int(x) for x in args.widths.split(',') if x]:
 for seed in [2501,2502]:
  m,info=train(hid,cov,seed); r=metric(m,info,hid,cov,seed); rowsout.append(r); print('DONE',r,flush=True)
pd.DataFrame(rowsout).to_csv(OUT/f'MODEL-SCALE-CORRIDOR-025_geo_cov{int(cov*100)}_{args.widths.replace(",","-")}.csv',index=False)
