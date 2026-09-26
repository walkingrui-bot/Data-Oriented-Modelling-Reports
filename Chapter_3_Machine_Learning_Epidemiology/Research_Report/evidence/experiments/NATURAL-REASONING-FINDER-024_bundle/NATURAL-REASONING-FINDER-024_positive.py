#!/usr/bin/env python3
# Positive control: same fixed visible CoT, but auxiliary hidden-state objectives force natural-like staged reasoning.
from pathlib import Path
import random, hashlib, json
import numpy as np, pandas as pd, torch, torch.nn as nn, torch.nn.functional as F
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, adjusted_mutual_info_score
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
OUT=Path('/mnt/data'); SEED=2404
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED); torch.set_num_threads(4)
N=5; OPS=['P1','P2','D2','NEG']
def ap(x,o): return {'P1':(x+1)%N,'P2':(x+2)%N,'D2':(2*x)%N,'NEG':(-x)%N}[o]
def di(x,g): d=(x-g)%N; return min(d,N-d)
def latent(g,x,m,c):
 main=ap(x,m); branch=ap(x,c); dm,db=di(main,g),di(branch,g); cmp=0 if db<dm else (1 if db==dm else 2); ans=branch if cmp==0 else main; return main,branch,cmp,ans,int(ans!=main)
TOK=['<BOS>','ALT','<SEP>','THINK','CHECK','FINAL','<EOS>']+[f'G{i}' for i in range(N)]+[f'X{i}' for i in range(N)]+OPS+[f'Y{i}' for i in range(N)]
stoi={t:i for i,t in enumerate(TOK)}; V=len(TOK)
seqs=[]; rows=[]
for g in range(N):
 for x in range(N):
  for m in OPS:
   for c in OPS:
    ma,br,cm,an,co=latent(g,x,m,c); seqs.append([stoi[t] for t in ['<BOS>',f'G{g}',f'X{x}',m,'ALT',c,'<SEP>','THINK','CHECK','FINAL',f'Y{an}','<EOS>']]); rows.append((g,x,m,c,ma,br,cm,an,co))
seq=torch.tensor(seqs); meta=pd.DataFrame(rows,columns=['goal','start','main_op','cf_op','main','branch','cmp','answer','corrected'])
probe_train=np.array([int(hashlib.sha1(str(r).encode()).hexdigest()[:8],16)%5!=0 for r in rows]); probe_test=~probe_train
class M(nn.Module):
 def __init__(self):
  super().__init__(); self.emb=nn.Embedding(V,24); self.cells=nn.ModuleList([nn.GRUCell(24,48),nn.GRUCell(48,48),nn.GRUCell(48,48)]); self.head=nn.Linear(48,V); self.mainh=nn.Linear(48,N); self.brh=nn.Linear(48,N); self.cmph=nn.Linear(48,3)
 def zero(self,B): return [torch.zeros(B,48) for _ in range(3)]
 def step(self,t,h):
  x=self.emb(t); n=[]
  for i,c in enumerate(self.cells): q=c(x,h[i]); n.append(q); x=q
  return self.head(n[-1]),n
 def forward(self,t,ret=False):
  h=self.zero(len(t)); O=[]; S=[[] for _ in range(3)]
  for k in range(t.shape[1]):
   o,h=self.step(t[:,k],h); O.append(o)
   for l in range(3): S[l].append(h[l])
  return (torch.stack(O,1),[torch.stack(s,1) for s in S],h) if ret else torch.stack(O,1)
 def state_after(self,t):
  h=self.zero(len(t))
  for k in range(t.shape[1]): _,h=self.step(t[:,k],h)
  return [q.clone() for q in h]
 def cont(self,h,s):
  O=[]
  for k in range(s.shape[1]): o,h=self.step(s[:,k],h); O.append(o)
  return (torch.stack(O,1) if O else None),h
m=M(); opt=torch.optim.AdamW(m.parameters(),lr=.01,weight_decay=1e-5)
yma=torch.tensor(meta.main.values); ybr=torch.tensor(meta.branch.values); ycm=torch.tensor(meta.cmp.values)
for ep in range(500):
 o,S,_=m(seq[:,:10],ret=True)
 # THINK pos7: candidates retained; CHECK pos8: comparison state; FINAL pos9: answer token
 loss=F.cross_entropy(o[:,9],seq[:,10]) + 1.5*F.cross_entropy(m.mainh(S[2][:,7]),yma)+1.5*F.cross_entropy(m.brh(S[2][:,7]),ybr)+2.0*F.cross_entropy(m.cmph(S[2][:,8]),ycm)
 opt.zero_grad(); loss.backward(); opt.step()
 if ep%25==0:
  with torch.no_grad(): acc=(o[:,9].argmax(-1)==seq[:,10]).float().mean().item(); ma=(m.mainh(S[2][:,7]).argmax(-1)==yma).float().mean().item(); br=(m.brh(S[2][:,7]).argmax(-1)==ybr).float().mean().item(); cm=(m.cmph(S[2][:,8]).argmax(-1)==ycm).float().mean().item()
  print(ep,acc,ma,br,cm,flush=True)
  if min(acc,ma,br,cm)>.999: break
with torch.no_grad(): o,S,_=m(seq[:,:10],ret=True); answer_acc=float((o[:,9].argmax(-1)==seq[:,10]).float().mean())
acts={(l+1,n):S[l][:,p,:].numpy() for l in range(3) for n,p in {'SEP':6,'THINK':7,'CHECK':8,'FINAL':9}.items()}; labels={'main':meta.main.values,'branch':meta.branch.values,'cmp':meta.cmp.values,'answer':meta.answer.values}
# label-free future-control tomography
ansids=[stoi[f'Y{k}'] for k in range(N)]; testids=np.where(probe_test)[0]; fm=[]
for n,pos in [('THINK',7),('CHECK',8),('FINAL',9)]:
 for l in range(1,4):
  A=acts[(l,n)]; dirs=PCA(n_components=5,random_state=SEED).fit(A[probe_train]).components_; eps=.25; SS=[]
  for ii in testids:
   with torch.no_grad(): hs0=m.state_after(seq[ii:ii+1,:pos+1]); base=hs0[l-1][0].clone()
   R=[]
   for delta in [torch.zeros_like(base)]+[sgn*eps*torch.tensor(d,dtype=base.dtype) for d in dirs for sgn in (1.,-1.)]:
    hs=[q.clone() for q in hs0]; hs[l-1]=(base+delta)[None,:]; suf=seq[ii:ii+1,pos+1:10]
    with torch.no_grad():
     oo,_=m.cont(hs,suf); z=(oo[0,-1] if suf.shape[1] else m.head(hs[-1])[0])[ansids].numpy()
    R.append(z)
   sig=list(R[0]);
   for q in range(5): sig+=list((R[1+2*q]-R[2+2*q])/(2*eps))
   SS.append(sig)
  Z=np.array(SS); Z=(Z-Z.mean(0))/(Z.std(0)+1e-6); pc=PCA(n_components=min(8,len(Z)-1,Z.shape[1]),random_state=SEED).fit_transform(Z)
  for t,k in [('cmp',3),('branch',5),('answer',5)]:
   km=KMeans(n_clusters=k,n_init=50,random_state=SEED).fit(pc); fm.append((n,l,t,adjusted_mutual_info_score(labels[t][testids],km.labels_)))
fm=pd.DataFrame(fm,columns=['checkpoint','layer','target','AMI']); fm.to_csv(OUT/'NATURAL-REASONING-FINDER-024_positive_control.csv',index=False)
print('answer',answer_acc); print(fm.to_string(index=False));
torch.save({'state_dict':m.state_dict(),'vocab':TOK},OUT/'NATURAL-REASONING-FINDER-024_positive_model.pt')
