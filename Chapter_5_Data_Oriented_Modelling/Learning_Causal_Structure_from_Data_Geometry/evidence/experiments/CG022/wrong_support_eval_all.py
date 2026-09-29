from pathlib import Path
import sys,json
import numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import run_cg022_engineered_world as core
z=np.load(ROOT/'synthetic_data.npz');ii=np.flatnonzero(z['split']==2);x=torch.tensor(z['x'][ii],dtype=torch.float32);y=torch.tensor(z['y'][ii],dtype=torch.float32);group=z['group'][ii];sup=z['support'][ii];trueB=torch.tensor(z['true_B'][ii],dtype=torch.float32)
# donor: next support-present world in same observational-equivalence group
donor=np.full(len(x),-1,int)
for g in np.unique(group):
 ids=np.flatnonzero((group==g)&(sup==1))
 if len(ids)==3:
  for j,i in enumerate(ids):donor[i]=ids[(j+1)%3]
ids=np.flatnonzero(donor>=0);ds=donor[ids]

def load(kind,seed):
 if kind=='baseline':
  sys.path.insert(0,'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021');import run_cg021_free_pool as old
  ck=torch.load(f'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021/models/pool8_{seed}.pt',map_location='cpu',weights_only=False);m=old.FreePool(8);m.load_state_dict(ck['state_dict']);return m,'old'
 ck=torch.load(ROOT/'models'/f'{"evidence_coupled" if kind=="evidence_coupled" else "balanced"}_{seed}.pt',map_location='cpu',weights_only=False);m=core.WorldProgram(8);m.load_state_dict(ck['state_dict']);return m,'new'

def orig_predict(kind,m,xx):
 if kind=='old':
  p,tr=m(xx,trace=True);B=tr['B'][:,-1];lg=tr['logits'][:,-1]
 else:B,lg=m.form_world(xx,steps=4)
 q=xx[:,-3:].argmax(-1);sims=[]
 for qi in range(3):sims.append(core.apply_operator(B,{'type':'do','targets':[qi],'values':[1.]}))
 S=torch.stack(sims,2);mus=S[torch.arange(len(B))[:,None],torch.arange(B.shape[1])[None,:],q[:,None]]
 return mus,lg,core.expected(mus,lg)
rows=[]
for variant in ['baseline','balanced','evidence_coupled']:
 for seed in [11,22]:
  m,k=load(variant,seed);m.eval();xs=x.clone();xs[ids,9:15]=x[ds,9:15]
  with torch.no_grad():
   mo,lo,po=orig_predict(k,m,x);mw,lw,pw=orig_predict(k,m,xs)
  own=core.mix_nll(mw[ids],lw[ids],y[ids]);don=core.mix_nll(mw[ids],lw[ids],y[ds]);base=core.mix_nll(mo[ids],lo[ids],y[ids]);shift=((pw[ids]-po[ids])**2).mean(1).sqrt()
  for j,i in enumerate(ids):rows.append({'variant':variant,'seed':seed,'group':int(group[i]),'receiver':int(i),'donor':int(ds[j]),'base_own_nll':float(base[j]),'wrong_own_nll':float(own[j]),'wrong_donor_nll':float(don[j]),'own_degradation':float(own[j]-base[j]),'donor_preferred':int(don[j]<own[j]),'prediction_rms_shift':float(shift[j])})
df=pd.DataFrame(rows);df.to_csv(ROOT/'wrong_support_eval.csv',index=False)
s=df.groupby('variant').agg(own_degradation=('own_degradation','mean'),donor_preferred=('donor_preferred','mean'),prediction_rms_shift=('prediction_rms_shift','mean')).reset_index();s.to_csv(ROOT/'wrong_support_summary.csv',index=False);print(s.to_string(index=False))
