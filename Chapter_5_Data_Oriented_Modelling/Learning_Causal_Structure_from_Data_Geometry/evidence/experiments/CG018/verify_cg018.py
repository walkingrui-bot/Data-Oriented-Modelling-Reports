import json
from pathlib import Path
import numpy as np
import pandas as pd
import torch
import run_cg018 as run
R=run.R
a=np.load(R/'synthetic_data.npz');idx=a['split']==2
sets={('synthetic','worlds'):(torch.tensor(a['x'][idx],dtype=torch.float32),torch.tensor(a['y'][idx],dtype=torch.float32),None)}
for fold,tr,dv,te,meta in run.base.real_folds():sets[('real',fold)]=te
rows=pd.read_csv(R/'results.csv');errors=[];loss_errors=[];qerrors=[];clamps=[]
for _,row in rows.iterrows():
 name=f'{row.task}_{row.fold}_{row["mode"]}_{row.seed}';ck=torch.load(R/'models'/f'{name}.pt',weights_only=True)
 m=run.MechanismModel(row.task,row['mode']);m.load_state_dict(ck['state_dict']);m.eval();x,y,mask=sets[(row.task,row.fold)]
 with torch.no_grad():p=m(x);ll=float(run.base.loss(p,y,row.task,mask))
 ref=np.load(R/'predictions'/f'{name}.npz')['prediction'];errors.append(float(np.abs(p.numpy()-ref).max()));loss_errors.append(abs(ll-row.loss))
 if row.task=='synthetic':
  with torch.no_grad():
   xx=x[:8].clone();xx[:,-3:]=torch.roll(xx[:,-3:],1,1);_,t1=m(x[:8],trace=True);_,t2=m(xx,trace=True)
  qerrors.append(float((t1['B']-t2['B']).abs().max()))
  sims=t1['simulations'];clamps.append(float((sims.diagonal(dim1=-2,dim2=-1)-1).abs().max()))
assert max(errors)<1e-6 and max(loss_errors)<1e-6 and max(qerrors)==0 and max(clamps)<1e-5
report={'checkpoints_verified':len(rows),'max_prediction_error':max(errors),'max_loss_error':max(loss_errors),'max_query_switch_relation_change':max(qerrors),'max_do_clamp_error':max(clamps)}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
