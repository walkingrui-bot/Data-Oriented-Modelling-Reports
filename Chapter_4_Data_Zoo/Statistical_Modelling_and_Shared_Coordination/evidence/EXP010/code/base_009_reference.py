import os,re,json,random,copy,math
from pathlib import Path
import numpy as np,pandas as pd,torch
from torch import nn
import torch.nn.functional as F
from sklearn.datasets import load_diabetes
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score
ROOT=Path('/mnt/data/INTERNAL_COORDINATION_009'); RES=ROOT/'results'; RES.mkdir(parents=True,exist_ok=True)
torch.set_num_threads(2); D=16; TAUS=torch.tensor([.1,.25,.5,.75,.9]); SEEDS=[0,1,2]; STEPS=800; CPS=[0,25,50,100,200,400,800]
# ----- real patient-state scaffold -----
raw=load_diabetes().data.astype(np.float32); ids=np.arange(len(raw)); tr,te=train_test_split(ids,test_size=.2,random_state=2026)
mu=raw[tr].mean(0); sd=raw[tr].std(0)+1e-6; Z=((raw-mu)/sd).astype(np.float32); ZT=torch.tensor(Z)
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
vocab={'<pad>':0,'<unk>':1}; enc=[]; maxl=0
for vv in texts:
 for t in vv:
  for w in re.findall(r'[a-z]+',t.lower()):
   if w not in vocab:vocab[w]=len(vocab)
for vv in texts:
 aa=[]
 for t in vv:
  q=[vocab.get(w,1) for w in re.findall(r'[a-z]+',t.lower())]; maxl=max(maxl,len(q)); aa.append(q)
 enc.append(aa)
TOK=torch.zeros((len(Z),4,maxl),dtype=torch.long); MSK=torch.zeros_like(TOK,dtype=torch.float32)
for i,aa in enumerate(enc):
 for v,q in enumerate(aa): TOK[i,v,:len(q)]=torch.tensor(q); MSK[i,v,:len(q)]=1
np.savez_compressed(RES/'data_arrays.npz',Z=Z,NUM_MU=NM.numpy(),NUM_SIG=NS.numpy(),labels=labs,thresholds=th,train_idx=tr,test_idx=te)
pd.DataFrame({'index':ids,'split':['train' if x in set(tr) else 'test' for x in ids]}).to_csv(RES/'split.csv',index=False)

class Net(nn.Module):
 def __init__(self,seed):
  super().__init__(); torch.manual_seed(seed); self.emb=nn.Embedding(len(vocab),24,padding_idx=0); self.txt=nn.Sequential(nn.Linear(24,32),nn.GELU(),nn.Linear(32,D)); self.num=nn.Sequential(nn.Linear(6,32),nn.GELU(),nn.Linear(32,D)); self.M=nn.Parameter(torch.eye(D)+.03*torch.randn(D,D)); self.b=nn.Parameter(torch.zeros(D)); self.nh=nn.Sequential(nn.Linear(D,32),nn.GELU(),nn.Linear(32,30)); self.lh=nn.Sequential(nn.Linear(D,32),nn.GELU(),nn.Linear(32,18))
 def et(self,x,m):
  e=self.emb(x); return self.txt((e*m[...,None]).sum(1)/(m.sum(1,keepdim=True)+1e-6))
 def state(self,num=None,txt=None,mask=None):
  p=[]
  if num is not None:p.append(self.num(num))
  if txt is not None:p.append(self.et(txt,mask))
  e=torch.stack(p).mean(0); return torch.tanh(e@self.M.T+self.b)
 def out(self,r):
  q=torch.sort(self.nh(r).view(-1,6,5),dim=-1).values; l=self.lh(r).view(-1,6,3); return q,l

def obs(ix,g):
 m=NM[ix]; s=NS[ix]; y=m+s*torch.randn(m.shape,generator=g); y=y.clone(); y[:,1]=torch.round(y[:,1]/.2)*.2; y[:,2]=torch.maximum(y[:,2],torch.tensor(-.9)); y[:,3]=torch.minimum(y[:,3],torch.tensor(1.2)); return y
def batch(ix,seed,randvar=True):
 g=torch.Generator().manual_seed(int(seed)); it=torch.tensor(ix); a=obs(it,g); b=obs(it,g); v=torch.randint(0,4,(len(ix),),generator=g) if randvar else torch.zeros(len(ix),dtype=torch.long); return it,a,b,TOK[it,v],MSK[it,v]
def pin(q,y):
 e=y[...,None]-q; return torch.maximum(TAUS*e,(TAUS-1)*e).mean()
def lloss(l,y):return F.cross_entropy(l.reshape(-1,3),y.reshape(-1))
def state(model,mode,y,t,m):return model.state(num=y if mode in ['num','both'] else None,txt=t if mode in ['text','both'] else None,mask=m if mode in ['text','both'] else None)
def effrank(A):
 s=torch.linalg.svdvals(A.detach()).numpy(); p=s/(s.sum()+1e-12); return float(np.exp(-(p*np.log(p+1e-12)).sum())),s

def fast_eval(model):
 model.eval(); ix,y,yt,t,m=batch(te,880001,False); out={}; st={}
 with torch.no_grad():
  for mode in ['num','text','both']:
   r=state(model,mode,y,t,m); q,l=model.out(r); out[f'num_pinball_{mode}']=float(pin(q,yt)); out[f'coverage80_{mode}']=float(((yt>=q[:,:,0])&(yt<=q[:,:,4])).float().mean()); out[f'lang_acc_{mode}']=float((l.argmax(-1)==LAB[ix]).float().mean()); st[mode]=r
  rn=F.normalize(st['num'],dim=1); rt=F.normalize(st['text'],dim=1); same=(rn*rt).sum(1); mis=(rn*rt[torch.roll(torch.arange(len(te)),1)]).sum(1); out['paired_cosine']=float(same.mean()); out['mismatch_cosine']=float(mis.mean()); out['paired_cosine_gap']=float((same-mis).mean())
 er,s=effrank(model.M); out['M_effective_rank']=er
 for i,v in enumerate(s[:8]):out[f'M_sv{i+1}']=float(v)
 return out

def probe(model,mode):
 model.eval()
 with torch.no_grad():
  _,y,_,t,m=batch(tr,777001,False); A=state(model,mode,y,t,m).numpy(); _,y,_,t,m=batch(te,777002,False); B=state(model,mode,y,t,m).numpy()
 return float(r2_score(Z[te],Ridge(alpha=1).fit(A,Z[tr]).predict(B),multioutput='uniform_average'))
def gdiag(model):
 model.train(); ix,y,yt,t,m=batch(tr,991001,False); r=model.state(num=y,txt=t,mask=m); q,l=model.out(r); a=pin(q,yt); b=lloss(l,LAB[ix]); ga=torch.autograd.grad(a,model.M,retain_graph=True)[0].reshape(-1); gb=torch.autograd.grad(b,model.M)[0].reshape(-1); return {'grad_cos_num_lang':float(F.cosine_similarity(ga,gb,dim=0)),'grad_rms_num':float(torch.sqrt((ga**2).mean())),'grad_rms_lang':float(torch.sqrt((gb**2).mean()))}
def step(model,opt,branch,s):
 ix,y,yt,t,m=batch(tr,1000003+s*101,True); opt.zero_grad()
 if branch=='numeric':r=model.state(num=y);q,l=model.out(r);loss=pin(q,yt)
 elif branch=='language':r=model.state(txt=t,mask=m);q,l=model.out(r);loss=lloss(l,LAB[ix])
 else:
  p=s%3; r=model.state(num=y if p!=1 else None,txt=t if p!=0 else None,mask=m if p!=0 else None);q,l=model.out(r);loss=pin(q,yt)+.35*lloss(l,LAB[ix])
 loss.backward();opt.step();return float(loss.detach())
def train(initial,seed,branch,capture=False,freezeM_from=None):
 model=Net(seed);model.load_state_dict(copy.deepcopy(initial));
 if freezeM_from==0:model.M.requires_grad_(False);model.b.requires_grad_(False)
 opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=2e-3,weight_decay=1e-4); hist=[]; snaps={}
 if capture:
  x=fast_eval(model);x.update({'seed':seed,'branch':branch,'step':0,'train_loss':np.nan});x.update(gdiag(model));x.update({f'probe_r2_{z}':probe(model,z) for z in ['num','text','both']});hist.append(x);snaps[0]=copy.deepcopy(model.state_dict())
 for s in range(1,STEPS+1):
  if freezeM_from is not None and freezeM_from>0 and s==freezeM_from+1:
   model.M.requires_grad_(False);model.b.requires_grad_(False);opt=torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],lr=2e-3,weight_decay=1e-4)
  loss=step(model,opt,branch,s)
  if capture and s in CPS[1:]:
   x=fast_eval(model);x.update({'seed':seed,'branch':branch,'step':s,'train_loss':loss});x.update(gdiag(model));x.update({f'probe_r2_{z}':probe(model,z) for z in ['num','text','both']});hist.append(x);snaps[s]=copy.deepcopy(model.state_dict())
 return model,pd.DataFrame(hist),snaps

def final_eval(model,seed,branch):
 x=fast_eval(model);x.update({f'probe_r2_{z}':probe(model,z) for z in ['num','text','both']});x.update({'seed':seed,'branch':branch});return x

def stress(model,kind,freezeM,steps=200):
 m=copy.deepcopy(model);M0=m.M.detach().clone();
 if freezeM:m.M.requires_grad_(False);m.b.requires_grad_(False)
 opt=torch.optim.AdamW([p for p in m.parameters() if p.requires_grad],lr=2e-3,weight_decay=1e-4)
 for s in range(1,steps+1):step(m,opt,kind,200000+s)
 e=fast_eval(m);e['M_move']=float(torch.linalg.norm(m.M.detach()-M0));return e

def lesion(model,M0,seed):
 d=model.M.detach()-M0;U,S,Vh=torch.linalg.svd(d,full_matrices=False);rows=[]
 for k in [0,1,2,4,8]:
  m=copy.deepcopy(model);norm=0
  if k:
   rem=(U[:,:k]*S[:k])@Vh[:k,:];norm=float(torch.linalg.norm(rem));m.M.data.copy_(model.M.detach()-rem)
  e=fast_eval(m);rows.append({'seed':seed,'type':'top_delta','k':k,'removed_norm':norm,'num_pinball_both':e['num_pinball_both'],'lang_acc_both':e['lang_acc_both'],'paired_cosine_gap':e['paired_cosine_gap']})
  if k:
   g=torch.Generator().manual_seed(9000+17*seed+k);R=torch.randn(d.shape,generator=g);R=R/(torch.linalg.norm(R)+1e-12)*norm;mr=copy.deepcopy(model);mr.M.data.copy_(model.M.detach()-R);er=fast_eval(mr);rows.append({'seed':seed,'type':'random_matched','k':k,'removed_norm':norm,'num_pinball_both':er['num_pinball_both'],'lang_acc_both':er['lang_acc_both'],'paired_cosine_gap':er['paired_cosine_gap']})
 return rows

history=[];finals=[];freeze=[];stressrows=[];lesions=[];geom=[];seed0_mats=[]
for seed in SEEDS:
 base=Net(seed);init=copy.deepcopy(base.state_dict());M0=init['M'].clone();mods={};deltas={};mixed200=None
 for br in ['numeric','language','mixed']:
  cap=(seed==0)
  mo,hi,sn=train(init,seed,br,capture=cap);mods[br]=mo;deltas[br]=(mo.M.detach()-M0).reshape(-1);finals.append(final_eval(mo,seed,br))
  if cap:
   history.append(hi)
   for st,ss in sn.items():
    d=ss['M']-M0;sv=torch.linalg.svdvals(d).numpy();seed0_mats.append({'branch':br,'step':st,'delta_norm':float(torch.linalg.norm(d)),'delta_effective_rank':effrank(d)[0],**{f'delta_sv{i+1}':float(x) for i,x in enumerate(sv[:10])}})
  if br=='mixed':
   # deterministic mixed checkpoint 200 for freeze experiment
   if seed==0:mixed200=sn[200]
   else:
    tm=Net(seed);tm.load_state_dict(copy.deepcopy(init));op=torch.optim.AdamW(tm.parameters(),lr=2e-3,weight_decay=1e-4)
    for s in range(1,201):step(tm,op,'mixed',s)
    mixed200=copy.deepcopy(tm.state_dict())
   fm=Net(seed);fm.load_state_dict(copy.deepcopy(mixed200));fm.M.requires_grad_(False);fm.b.requires_grad_(False);op=torch.optim.AdamW([p for p in fm.parameters() if p.requires_grad],lr=2e-3,weight_decay=1e-4)
   for s in range(201,STEPS+1):step(fm,op,'mixed',s)
   e=final_eval(fm,seed,'mixed_freeze200');freeze.append(e)
   basee=fast_eval(mo)
   for kind in ['numeric','language']:
    for fr in [False,True]:
     e=stress(mo,kind,fr);e.update({'seed':seed,'stress':kind,'M_frozen':fr,'base_num_pinball_both':basee['num_pinball_both'],'base_lang_acc_both':basee['lang_acc_both']});stressrows.append(e)
   lesions+=lesion(mo,M0,seed)
 def cs(a,b):return float(F.cosine_similarity(a,b,dim=0))
 geom.append({'seed':seed,'delta_norm_numeric':float(torch.linalg.norm(deltas['numeric'])),'delta_norm_language':float(torch.linalg.norm(deltas['language'])),'delta_norm_mixed':float(torch.linalg.norm(deltas['mixed'])),'cos_num_lang':cs(deltas['numeric'],deltas['language']),'cos_mixed_num':cs(deltas['mixed'],deltas['numeric']),'cos_mixed_lang':cs(deltas['mixed'],deltas['language'])})
 if seed==0:
  for br,mo in mods.items():torch.save(mo.state_dict(),RES/f'seed0_{br}_final.pt')

if history:pd.concat(history).to_csv(RES/'seed0_training_history.csv',index=False)
pd.DataFrame(seed0_mats).to_csv(RES/'seed0_matrix_trajectory.csv',index=False)
FDF=pd.DataFrame(finals);FDF.to_csv(RES/'final_branch_metrics.csv',index=False);FR=pd.DataFrame(freeze);FR.to_csv(RES/'freeze_after_200.csv',index=False);ST=pd.DataFrame(stressrows);ST.to_csv(RES/'modality_stress.csv',index=False);LE=pd.DataFrame(lesions);LE.to_csv(RES/'ganglion_lesions.csv',index=False);GE=pd.DataFrame(geom);GE.to_csv(RES/'ganglion_delta_geometry.csv',index=False)
summary={}
for br in ['numeric','language','mixed']:
 s=FDF[FDF.branch==br];summary[br]={k:float(s[k].median()) for k in ['num_pinball_num','num_pinball_text','num_pinball_both','coverage80_both','lang_acc_num','lang_acc_text','lang_acc_both','paired_cosine_gap','probe_r2_num','probe_r2_text','probe_r2_both','M_effective_rank']}
summary['freeze200']={k:float(FR[k].median()) for k in ['num_pinball_both','lang_acc_both','probe_r2_both','paired_cosine_gap']}
summary['geometry']={k:float(GE[k].median()) for k in GE.columns if k!='seed'}
for kind in ['numeric','language']:
 for fr in [False,True]:
  s=ST[(ST.stress==kind)&(ST.M_frozen==fr)];summary[f'stress_{kind}_freeze_{fr}']={k:float(s[k].median()) for k in ['num_pinball_both','lang_acc_both','M_move']}
with open(RES/'summary.json','w') as f:json.dump(summary,f,indent=2)
with open(ROOT/'protocol.json','w') as f:json.dump({'dataset':'sklearn diabetes, 442 real patient states','train':len(tr),'test':len(te),'shared_dim':16,'seeds':SEEDS,'steps':STEPS,'checkpoints':CPS,'numeric_target':'proper quantile prediction of an independent remeasurement; q10/q25/q50/q75/q90','language_target':'six 3-level semantic concepts; stochastic paraphrase observation; no exact sentence reproduction','mixed_training':'cycle numeric-only evidence, text-only evidence, both; every step predicts both target types','language_loss_weight':.35},f,indent=2)
print(json.dumps(summary,indent=2))
