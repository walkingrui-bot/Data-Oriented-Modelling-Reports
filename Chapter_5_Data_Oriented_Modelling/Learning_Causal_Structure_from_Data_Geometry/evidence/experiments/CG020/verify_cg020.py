from pathlib import Path
import json, numpy as np, pandas as pd, torch
import run_cg020_object_state as r
ROOT=Path(__file__).resolve().parent
z=np.load(ROOT/'synthetic_data.npz');ii=z['split']==2;x=torch.tensor(z['x'][ii],dtype=torch.float32);y=torch.tensor(z['y'][ii],dtype=torch.float32)
checks=[]
for seed in [11,22]:
 ck=torch.load(ROOT/'models'/f'world4_3_{seed}.pt',weights_only=True);m=r.ObjectWorldModel(3,1);m.load_state_dict(ck['state_dict']);m.eval()
 with torch.no_grad():
  p4,t4=m(x,4,trace=True);_,t2=m(x,2,trace=True);pcont=m(x,2,start_state=(t2['B'][:,-1],t2['logits'][:,-1]))
 checks.append({'seed':seed,'replay_max_abs':float((p4-pcont).abs().max()),'diag_max_abs':float(torch.diagonal(t4['B'][:,-1],dim1=-2,dim2=-1).abs().max()),'row_abs_sum_max':float(t4['B'][:,-1].abs().sum(-1).max()),'nll':float(r.loss(p4,y))})
res=pd.read_csv(ROOT/'results.csv'); ok=len(res)==8 and set(res.variant)==set(r.VARIANTS) and all(c['replay_max_abs']==0 for c in checks) and all(c['diag_max_abs']==0 for c in checks) and all(c['row_abs_sum_max']<=.950001 for c in checks)
out={'ok':bool(ok),'checkpoints':checks,'n_result_rows':len(res)};(ROOT/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2));assert ok
