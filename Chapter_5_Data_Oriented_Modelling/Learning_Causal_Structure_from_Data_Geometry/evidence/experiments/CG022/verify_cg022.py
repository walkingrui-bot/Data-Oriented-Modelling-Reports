from pathlib import Path
import json,sys
import numpy as np,torch,pandas as pd
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT));import run_cg022_engineered_world as core
z=np.load(ROOT/'synthetic_data.npz');ix=z['split']==2;x=torch.tensor(z['x'][ix],dtype=torch.float32);tb=torch.tensor(z['true_B'][ix],dtype=torch.float32)
checks=[];max_pred=0.;max_diag=0.;max_rowsum=0.
for stem in ['world_program','balanced','evidence_coupled']:
 for seed in [11,22]:
  ck=torch.load(ROOT/'models'/f'{stem}_{seed}.pt',map_location='cpu',weights_only=False);m=core.WorldProgram(8);m.load_state_dict(ck['state_dict']);m.eval()
  with torch.no_grad():B,lg,tr=m.form_world(x,steps=4,trace=True)
  saved=np.load(ROOT/'predictions'/f'{stem}_{seed}.npz');err=max(float(np.max(np.abs(saved['B']-tr['B'].numpy()))),float(np.max(np.abs(saved['logits']-tr['logits'].numpy()))));max_pred=max(max_pred,err)
  bn=tr['B'].numpy();max_diag=max(max_diag,float(np.max(np.abs(np.diagonal(bn,axis1=-2,axis2=-1)))));max_rowsum=max(max_rowsum,float(np.max(np.abs(bn).sum(-1))))
  checks.append({'model':stem,'seed':seed,'reload_trajectory_max_abs':err})
# exact state replay for final construction
replay=0.
for seed in [11,22]:
 ck=torch.load(ROOT/'models'/f'evidence_coupled_{seed}.pt',map_location='cpu',weights_only=False);m=core.WorldProgram(8);m.load_state_dict(ck['state_dict']);m.eval()
 with torch.no_grad():
  _,_,a=m.form_world(x,steps=2,trace=True);st=(a['B'][:,-1],a['logits'][:,-1]);Br,Lr=m.form_world(x,steps=2,start_state=st,reveal_step=1);B4,L4=m.form_world(x,steps=4);replay=max(replay,float((Br-B4).abs().max()),float((Lr-L4).abs().max()))
out={'checkpoint_checks':checks,'max_reload_trajectory_error':max_pred,'max_diagonal_error':max_diag,'max_row_abs_sum':max_rowsum,'final_state_replay_max_abs':replay,'n_new_checkpoints':len(checks),'status':'PASS' if max_pred==0 and max_diag==0 and max_rowsum<=.950001 and replay==0 else 'FAIL'}
(ROOT/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
