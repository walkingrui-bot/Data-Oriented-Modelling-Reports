import re,random,copy,json
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
import torch.nn.functional as F
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split

ROOT=Path('/mnt/data/INTERNAL_COORDINATION_010'); RES=ROOT/'results'; RES.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(2); D=16; TAUS=torch.tensor([.1,.25,.5,.75,.9]); SEEDS=[0,1,2]; BASE_STEPS=800; EXPERT_STEPS=1000
raw=load_diabetes().data.astype(np.float32); ids=np.arange(len(raw)); tr,te=train_test_split(ids,test_size=.2,random_state=2026)
mu=raw[tr].mean(0); sd=raw[tr].std(0)+1e-6; Z=((raw-mu)/sd).astype(np.float32)
def npars(z):
 m=np.stack([.9*z[:,2]+.25*z[:,3]+.15*z[:,0]*z[:,2],.7*z[:,3]-.25*z[:,1]+.2*np.tanh(z[:,4]),.5*z[:,4]+.5*z[:,5]-.2*z[:,7],-.4*z[:,6]+.55*z[:,8]+.25*z[:,2]*z[:,8],.45*z[:,0]+.3*z[:,9]+.25*z[:,2],.35*z[:,2]+.3*z[:,3]+.2*z[:,6]-.2*z[:,5]],1).astype(np.float32)
 s=(.16+.05*np.abs(m)+.04/(1+np.exp(-z[:,:6]))).astype(np.float32); return m,s
NM,NS=npars(Z); NM=torch.tensor(NM); NS=torch.tensor(NS)
sc=np.stack([Z[:,0],Z[:,2],Z[:,3],Z[:,4]+Z[:,5]-Z[:,6],.6*Z[:,2]+.4*Z[:,3]+.2*Z[:,8],Z[:,7]-Z[:,8]+.3*Z[:,6]],1)
th=np.quantile(sc[tr],[1/3,2/3],axis=0); labs=(sc>th[0]).astype(np.int64)+(sc>th[1]).astype(np.int64); LAB=torch.tensor(labs)
PH={0:{0:['age profile is younger','age lies in the lower range','the participant is relatively young'],1:['age profile is typical','age lies near the middle','the participant is middle range in age'],2:['age profile is older','age lies in the upper range','the participant is relatively old']},1:{0:['body mass is relatively low','body mass sits below the usual range','body mass is on the lower side'],1:['body mass is near the usual range','body mass looks typical','body mass is around the middle'],2:['body mass is relatively high','body mass sits above the usual range','body mass is on the upper side']},2:{0:['blood pressure is on the low side','pressure sits below the usual range','blood pressure is relatively low'],1:['blood pressure is near the middle range','pressure looks typical','blood pressure is around the middle'],2:['blood pressure is on the high side','pressure sits above the usual range','blood pressure is relatively high']},3:{0:['the lipid balance is lower','the serum lipid pattern is low','the lipid relation is on the lower side'],1:['the lipid balance is intermediate','the serum lipid pattern is typical','the lipid relation is moderate'],2:['the lipid balance is higher','the serum lipid pattern is high','the lipid relation is on the upper side']},4:{0:['overall metabolic burden is low','the metabolic profile is relatively light','the overall metabolic pattern is mild'],1:['overall metabolic burden is moderate','the metabolic profile is intermediate','the overall metabolic pattern is moderate'],2:['overall metabolic burden is high','the metabolic profile is relatively heavy','the overall metabolic pattern is strong']},5:{0:['the secondary serum pattern is low','the auxiliary serum balance is reduced','the serum contrast sits low'],1:['the secondary serum pattern is moderate','the auxiliary serum balance is typical','the serum contrast sits in the middle'],2:['the secondary serum pattern is high','the auxiliary serum balance is elevated','the serum contrast sits high']}}
texts=[]
for i in range(len(Z)):
 vv=[]
 for v in range(4):
  r=random.Random(i*7919+v*104729+31); parts=[r.choice(PH[j][int(labs[i,j])]) for j in range(6)]; r.shuffle(parts); vv.append(' ; '.join(parts))
 texts.append(vv)
vocab={'<pad>':0,'<unk>':1}; maxl=0
for vv in texts:
 for t in vv:
  for w in re.findall(r'[a-z]+',t.lower()):
   if w not in vocab:vocab[w]=len(vocab)
enc=[]
for vv in texts:
 aa=[]
 for t in vv:
  q=[vocab.get(w,1) for w in re.findall(r'[a-z]+',t.lower())]; maxl=max(maxl,len(q)); aa.append(q)
 enc.append(aa)
TOK=torch.zeros((len(Z),4,maxl),dtype=torch.long); MSK=torch.zeros_like(TOK,dtype=torch.float32)
for i,aa in enumerate(enc):
 for v,q in enumerate(aa): TOK[i,v,:len(q)]=torch.tensor(q); MSK[i,v,:len(q)]=1

class Net(nn.Module):
 def __init__(self,seed):
  super().__init__(); torch.manual_seed(seed); self.emb=nn.Embedding(len(vocab),24,padding_idx=0); self.txt=nn.Sequential(nn.Linear(24,32),nn.GELU(),nn.Linear(32,D)); self.num=nn.Sequential(nn.Linear(6,32),nn.GELU(),nn.Linear(32,D)); self.M=nn.Parameter(torch.eye(D)+.03*torch.randn(D,D)); self.b=nn.Parameter(torch.zeros(D)); self.nh=nn.Sequential(nn.Linear(D,32),nn.GELU(),nn.Linear(32,30)); self.lh=nn.Sequential(nn.Linear(D,32),nn.GELU(),nn.Linear(32,18))
 def pooled(self,x,m):
  e=self.emb(x); return (e*m[...,None]).sum(1)/(m.sum(1,keepdim=True)+1e-6)
 def et(self,x,m): return self.txt(self.pooled(x,m))
 def state(self,num=None,txt=None,mask=None):
  p=[]
  if num is not None:p.append(self.num(num))
  if txt is not None:p.append(self.et(txt,mask))
  return torch.tanh(torch.stack(p).mean(0)@self.M.T+self.b)
 def out(self,r):
  return torch.sort(self.nh(r).view(-1,6,5),dim=-1).values,self.lh(r).view(-1,6,3)

def obs(ix,g):
 m=NM[ix];s=NS[ix];y=m+s*torch.randn(m.shape,generator=g);y=y.clone();y[:,1]=torch.round(y[:,1]/.2)*.2;y[:,2]=torch.maximum(y[:,2],torch.tensor(-.9));y[:,3]=torch.minimum(y[:,3],torch.tensor(1.2));return y
def batch(ix,seed,randvar=True):
 g=torch.Generator().manual_seed(int(seed));it=torch.tensor(ix);a=obs(it,g);b=obs(it,g);v=torch.randint(0,4,(len(ix),),generator=g) if randvar else torch.zeros(len(ix),dtype=torch.long);return it,a,b,TOK[it,v],MSK[it,v]
def pin(q,y):
 e=y[...,None]-q;return torch.maximum(TAUS*e,(TAUS-1)*e).mean()
def lloss(l,y):return F.cross_entropy(l.reshape(-1,3),y.reshape(-1))
def base_step(model,opt,s,branch='mixed'):
 ix,y,yt,t,m=batch(tr,1000003+s*101,True);opt.zero_grad()
 if branch=='numeric':r=model.state(num=y);q,l=model.out(r);loss=pin(q,yt)
 elif branch=='language':r=model.state(txt=t,mask=m);q,l=model.out(r);loss=lloss(l,LAB[ix])
 else:
  p=s%3;r=model.state(num=y if p!=1 else None,txt=t if p!=0 else None,mask=m if p!=0 else None);q,l=model.out(r);loss=pin(q,yt)+.35*lloss(l,LAB[ix])
 loss.backward();opt.step()
def train_base(seed,branch='mixed'):
 m=Net(seed);o=torch.optim.AdamW(m.parameters(),lr=2e-3,weight_decay=1e-4)
 for s in range(1,BASE_STEPS+1):base_step(m,o,s,branch)
 return m

class NumExpert(nn.Module):
 def __init__(self,capacity):
  super().__init__();w={'small':8,'medium':16,'precision':32}[capacity]
  if capacity=='small':self.net=nn.Sequential(nn.Linear(6,w),nn.GELU(),nn.Linear(w,30))
  elif capacity=='medium':self.net=nn.Sequential(nn.Linear(6,w),nn.GELU(),nn.Linear(w,16),nn.GELU(),nn.Linear(16,30))
  else:self.net=nn.Sequential(nn.Linear(6,w),nn.GELU(),nn.Linear(w,16),nn.GELU(),nn.Linear(16,w),nn.GELU(),nn.Linear(w,30))
 def forward(self,x):return torch.sort(self.net(x).view(-1,6,5),dim=-1).values
class LangExpert(nn.Module):
 def __init__(self,base,capacity):
  super().__init__();self.base=base;w={'small':8,'medium':16,'precision':32}[capacity]
  if capacity=='small':self.net=nn.Sequential(nn.Linear(24,w),nn.GELU(),nn.Linear(w,18))
  elif capacity=='medium':self.net=nn.Sequential(nn.Linear(24,w),nn.GELU(),nn.Linear(w,16),nn.GELU(),nn.Linear(16,18))
  else:self.net=nn.Sequential(nn.Linear(24,w),nn.GELU(),nn.Linear(w,w),nn.GELU(),nn.Linear(w,18))
 def forward(self,t,m):
  with torch.no_grad():p=self.base.pooled(t,m)
  return self.net(p).view(-1,6,3)

def train_experts(base,capacity,seed,subtrain):
 torch.manual_seed(90000+seed);ne=NumExpert(capacity);le=LangExpert(base,capacity);o=torch.optim.AdamW(list(ne.parameters())+list(le.net.parameters()),lr=1e-3,weight_decay=1e-4)
 for s in range(1,EXPERT_STEPS+1):
  ix,y,yt,t,m=batch(subtrain,500000+seed*100000+s*97,True);o.zero_grad();loss=pin(ne(y),yt)+.35*lloss(le(t,m),LAB[ix]);loss.backward();o.step()
 return ne,le

def base_outputs(base,ix,seed=880001):
 ii,y,yt,t,m=batch(ix,seed,False);d={}
 with torch.no_grad():
  for mode in ['num','text','both']:
   r=base.state(num=y if mode in ['num','both'] else None,txt=t if mode in ['text','both'] else None,mask=m if mode in ['text','both'] else None);q,l=base.out(r);d[mode]=(q,l)
 return ii,y,yt,t,m,d

def blend_metrics(base,ne,le,ix,a_num,a_lang,seed=880001):
 ii,y,yt,t,m,d=base_outputs(base,ix,seed);rows={}
 with torch.no_grad():
  qloc=ne(y);lloc=le(t,m)
  for mode in ['num','text','both']:
   qb,lb=d[mode];q=qb;l=lb
   if mode in ['num','both']:q=torch.sort((1-a_num)*qb+a_num*qloc,dim=-1).values
   if mode in ['text','both']:
    p=(1-a_lang)*F.softmax(lb,dim=-1)+a_lang*F.softmax(lloc,dim=-1);l=torch.log(p+1e-9)
   rows[mode]={'num_pinball':float(pin(q,yt)),'lang_acc':float((l.argmax(-1)==LAB[ii]).float().mean())}
 return rows

def choose_alphas(base,ne,le,val):
 grid=[0,.25,.5,.75]
 # one alpha per channel, selected across both situations in which that channel is available
 bestn=min(grid,key=lambda a: np.mean([blend_metrics(base,ne,le,val,a,0,seed=770001)[m]['num_pinball'] for m in ['num','both']]))
 bestl=max(grid,key=lambda a: np.mean([blend_metrics(base,ne,le,val,0,a,seed=770001)[m]['lang_acc'] for m in ['text','both']]))
 return bestn,bestl

rows=[];crossdiff=[];special=[]
for seed in SEEDS:
 # reproduce matched base and specialists
 mixed=train_base(seed,'mixed'); numsp=train_base(seed,'numeric'); langsp=train_base(seed,'language')
 rng=np.random.default_rng(202610+seed);perm=rng.permutation(tr);nv=max(35,int(.1*len(perm)));val=perm[:nv];sub=perm[nv:]
 # specialist reference metrics on test
 spn=blend_metrics(numsp,NumExpert('small'),LangExpert(numsp,'small'),te,0,0)['num']['num_pinball']
 spl=blend_metrics(langsp,NumExpert('small'),LangExpert(langsp,'small'),te,0,0)['text']['lang_acc']
 special.append({'seed':seed,'numeric_specialist_pinball':spn,'language_specialist_acc':spl})
 base=blend_metrics(mixed,NumExpert('small'),LangExpert(mixed,'small'),te,0,0)
 rows.append({'seed':seed,'capacity':'none','alpha_num':0,'alpha_lang':0,**{f'{mode}_{k}':v for mode,z in base.items() for k,v in z.items()}})
 for cap in ['small','medium','precision']:
  ne,le=train_experts(mixed,cap,seed,sub);an,al=choose_alphas(mixed,ne,le,val);met=blend_metrics(mixed,ne,le,te,an,al)
  rec={'seed':seed,'capacity':cap,'alpha_num':an,'alpha_lang':al,**{f'{mode}_{k}':v for mode,z in met.items() for k,v in z.items()}}
  rec['expert_params']=sum(p.numel() for p in ne.parameters())+sum(p.numel() for p in le.net.parameters());rows.append(rec)
  # exact cross-modal invariance audit: text->numeric and numeric->language should equal base when missing local modality
  recbase=blend_metrics(mixed,ne,le,te,0,0)
  crossdiff.append({'seed':seed,'capacity':cap,'text_to_numeric_abs_diff':abs(met['text']['num_pinball']-recbase['text']['num_pinball']),'numeric_to_language_abs_diff':abs(met['num']['lang_acc']-recbase['num']['lang_acc'])})
  if seed==0 and cap=='precision':
   torch.save({'mixed':mixed.state_dict(),'num_expert':ne.state_dict(),'lang_expert':le.net.state_dict(),'alpha_num':an,'alpha_lang':al},RES/'seed0_precision_bundle.pt')

R=pd.DataFrame(rows);R.to_csv(RES/'precision_residual_results.csv',index=False);C=pd.DataFrame(crossdiff);C.to_csv(RES/'cross_modal_invariance.csv',index=False);S=pd.DataFrame(special);S.to_csv(RES/'specialist_references.csv',index=False)
summary={}
for cap in ['none','small','medium','precision']:
 q=R[R.capacity==cap];summary[cap]={c:float(q[c].median()) for c in ['alpha_num','alpha_lang','num_num_pinball','text_num_pinball','both_num_pinball','num_lang_acc','text_lang_acc','both_lang_acc'] if c in q}
 if cap!='none':summary[cap]['expert_params_median']=float(q.expert_params.median())
summary['specialists']={'numeric_pinball':float(S.numeric_specialist_pinball.median()),'language_acc':float(S.language_specialist_acc.median())}
summary['cross_modal_max_abs_diff']={'text_to_numeric':float(C.text_to_numeric_abs_diff.max()),'numeric_to_language':float(C.numeric_to_language_abs_diff.max())}
# gap recovery using same-modality and both-modality metrics
b=summary['none'];sp=summary['specialists']
for cap in ['small','medium','precision']:
 s=summary[cap]
 s['numeric_same_gap_recovery_pct']=100*(b['num_num_pinball']-s['num_num_pinball'])/(b['num_num_pinball']-sp['numeric_pinball']+1e-12)
 s['language_same_gap_recovery_pct']=100*(s['text_lang_acc']-b['text_lang_acc'])/(sp['language_acc']-b['text_lang_acc']+1e-12)
with open(RES/'summary.json','w') as f:json.dump(summary,f,indent=2)
with open(ROOT/'protocol.json','w') as f:json.dump({'experiment':'INTERNAL_COORDINATION_010 Precision Residual Upgrade','base':'matched Experiment 009 mixed ganglion, 16D, 800 steps','seeds':SEEDS,'expert_steps':EXPERT_STEPS,'capacities':['small','medium','precision'],'base_frozen':True,'ganglion_frozen':True,'local_expert_activation':'numeric expert only when numeric evidence is present; language expert only when text evidence is present','blend_alpha_grid':[0,.25,.5,.75],'alpha_selection':'10% validation subset of original train split; one alpha per channel across same-modal and both-evidence settings','test_split':'same held-out 20% as Experiment 009','numeric_target':'proper quantile distribution of independent remeasurement','language_target':'six semantic 3-class variables, no exact text reconstruction'},f,indent=2)
print(json.dumps(summary,indent=2))
