"""Recompute all selected-checkpoint predictions, without training."""
import json
import numpy as np
import pandas as pd
import torch
import run_cg017 as run

R=run.ROOT
a=np.load(R/'synthetic_data.npz');idx=a['split']==2
synthetic=(torch.tensor(a['x'][idx],dtype=torch.float32),torch.tensor(a['y'][idx],dtype=torch.float32),None)
sets={('synthetic','worlds'):synthetic}
for fold,tr,dv,te,meta in run.real_folds():sets[('real',fold)]=te
results=pd.read_csv(R/'results.csv');errors=[];loss_errors=[]
for _,row in results.iterrows():
    name=f'{row.task}_{row.fold}_{row["mode"]}_{row.seed}'
    ck=torch.load(R/'models'/f'{name}.pt',map_location='cpu',weights_only=True)
    model=run.Model(ck['input_dim'],ck['task'],ck['mode']);model.load_state_dict(ck['state_dict']);model.eval()
    x,y,m=sets[(row.task,row.fold)]
    with torch.no_grad():p=model(x);ll=float(run.loss(p,y,row.task,m))
    expected=np.load(R/'predictions'/f'{name}.npz')['prediction']
    errors.append(float(np.max(np.abs(p.numpy()-expected))));loss_errors.append(abs(ll-row.loss))
assert max(errors)<1e-6 and max(loss_errors)<1e-6
# Analytic equivalence of the three Gaussian SCM orientations.
a,b=.4,-.6;cov=np.array([[1,a,a*b],[a,1,b],[a*b,b,1.]])
cov_errors=[]
for kind in range(3):
 B=np.zeros((3,3))
 if kind==0:B[1,0]=a;B[2,1]=b
 elif kind==1:B[0,1]=a;B[2,1]=b
 else:B[0,1]=a;B[1,2]=b
 inv=np.linalg.inv(np.eye(3)-B);actual=inv@np.diag(1-(B**2).sum(1))@inv.T
 cov_errors.append(float(np.max(np.abs(actual-cov))))
assert max(cov_errors)<1e-12
report={'selected_checkpoints_verified':len(results),'max_prediction_abs_error':max(errors),'max_loss_abs_error':max(loss_errors),'max_analytic_covariance_error':max(cov_errors)}
(R/'verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
