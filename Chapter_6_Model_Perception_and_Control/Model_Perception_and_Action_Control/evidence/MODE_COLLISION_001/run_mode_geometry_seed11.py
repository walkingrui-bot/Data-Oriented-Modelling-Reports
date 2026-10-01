import json, math, copy, random, time
import numpy as np, pandas as pd, torch, torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import pairwise_distances
PAIRS=json.load(open('mode_collision_pairs.json'))
train_pairs=[i for i in range(len(PAIRS)) if i%5!=0]; test_pairs=[i for i in range(len(PAIRS)) if i%5==0]
samples=[]
for pi,(text,act) in enumerate(PAIRS): samples += [(pi,0,text),(pi,1,act)]
PAD=0;BOS=1;BYTE0=2;VOCAB=258;MAXLEN=128

def enc(s):
 raw=list(s.encode()); b=raw if len(raw)<=127 else raw[:80]+raw[-47:]; return [BOS]+[x+2 for x in b]
def batch(items):
 x=torch.zeros(len(items),MAXLEN,dtype=torch.long); l=torch.zeros(len(items),dtype=torch.long); y=torch.zeros(len(items),dtype=torch.long)
 for i,(_,lab,s) in enumerate(items):
  z=enc(s);x[i,:len(z)]=torch.tensor(z);l[i]=len(z);y[i]=lab
 return x,l,y
tr=[s for s in samples if s[0] in train_pairs]; te=[s for s in samples if s[0] in test_pairs]
Xtr,Ltr,Ytr=batch(tr);Xte,Lte,Yte=batch(te)
torch.set_num_threads(4)
class M(nn.Module):
 def __init__(self):
  super().__init__();d=24;self.emb=nn.Embedding(VOCAB,d,padding_idx=0);self.pos=nn.Embedding(MAXLEN,d)
  base=nn.TransformerEncoderLayer(d,4,64,dropout=0,batch_first=True,norm_first=True,activation='gelu')
  self.layers=nn.ModuleList([copy.deepcopy(base) for _ in range(8)]);self.norm=nn.LayerNorm(d);self.head=nn.Linear(d,2)
  self.register_buffer('mask',torch.triu(torch.full((MAXLEN,MAXLEN),float('-inf')),1),persistent=False)
 def forward(self,x,l,ret=False):
  h=self.emb(x)+self.pos(torch.arange(x.shape[1])[None,:]); hs=[h];pad=x==0
  for z in self.layers: h=z(h,src_mask=self.mask,src_key_padding_mask=pad,is_causal=True);hs.append(h)
  idx=l-1; last=self.norm(h)[torch.arange(len(x)),idx];out=self.head(last)
  if ret:return out,[self.norm(z) for z in hs]
  return out

def metrics(Ztr,Zte):
 ytr=Ytr.numpy();y=Yte.numpy();
 clf=LogisticRegression(max_iter=1000,solver='liblinear').fit(Ztr,ytr);probe=(clf.predict(Zte)==y).mean()
 A=Zte[y==0];B=Zte[y==1];mu0=A.mean(0);mu1=B.mean(0);diff=mu1-mu0
 var=((A-mu0)**2).sum()/max(1,len(A)-1)+((B-mu1)**2).sum()/max(1,len(B)-1);f=(diff@diff)/(var+1e-12)
 D=pairwise_distances(Zte);np.fill_diagonal(D,np.inf);idx=np.argpartition(D,5,axis=1)[:,:5];mix=(y[idx]!=y[:,None]).mean()
 s=np.linalg.svd(Zte-Zte.mean(0),compute_uv=False);e=s*s;stable=e.sum()/(e.max()+1e-12);p=e/(e.sum()+1e-12);eff=np.exp(-(p[p>0]*np.log(p[p>0])).sum())
 return probe,f,mix,stable,eff
rows=[]
for seed in [11]:
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed);m=M();opt=torch.optim.AdamW(m.parameters(),lr=2e-3,weight_decay=1e-3);lossf=nn.CrossEntropyLoss();
 for ep in range(1,41):
  order=torch.randperm(len(tr));m.train()
  for st in range(0,len(tr),28):
   ii=order[st:st+28];opt.zero_grad();loss=lossf(m(Xtr[ii],Ltr[ii]),Ytr[ii]);loss.backward();torch.nn.utils.clip_grad_norm_(m.parameters(),1);opt.step()
 def ext(x,l):
  m.eval();
  with torch.no_grad():o,hs=m(x,l,True)
  last=[];mean=[]
  for h in hs:
   a=h.numpy();last.append(np.stack([a[i,l[i]-1] for i in range(len(l))]));mean.append(np.stack([a[i,:l[i]].mean(0) for i in range(len(l))]))
  return o.numpy(),last,mean
 outtr,ltr,mtr=ext(Xtr,Ltr);outte,lte,mte=ext(Xte,Lte)
 trainacc=(outtr.argmax(1)==Ytr.numpy()).mean();testacc=(outte.argmax(1)==Yte.numpy()).mean()
 for li in range(9):
  for rep,Ztr,Zte in [('last',ltr[li],lte[li]),('mean',mtr[li],mte[li])]:
   probe,f,mix,stable,eff=metrics(Ztr,Zte);rows.append(dict(seed=seed,layer=li,representation=rep,train_acc=trainacc,test_acc=testacc,probe_acc=probe,fisher_ratio=f,knn_cross_mix=mix,stable_rank=stable,effective_rank=eff))
pd.DataFrame(rows).to_csv('MODE_COLLISION_001_seed11_geometry.csv',index=False)
print(pd.DataFrame(rows).groupby(['representation','layer'])[['probe_acc','fisher_ratio','knn_cross_mix']].agg(['mean','std']).to_string())
