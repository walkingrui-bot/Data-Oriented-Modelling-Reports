import numpy as np,pandas as pd,torch
import run_cg020_object_state as r
z=np.load('synthetic_data.npz');ix=np.flatnonzero(z['split']==2)[:200];x=torch.tensor(z['x'][ix],dtype=torch.float32);y=torch.tensor(z['y'][ix],dtype=torch.float32)
rows=[];torch.set_num_threads(4)
for seed in [11,22]:
 ck=torch.load(f'models/world4_3_{seed}.pt',weights_only=True);m=r.ObjectWorldModel(3,1);m.load_state_dict(ck['state_dict']);m.eval()
 with torch.no_grad():
  _,tr=m(x,20,trace=True);q=x[:,-3:].argmax(-1)
  for k in range(1,21):
   B=tr['B'][:,k-1];L=tr['logits'][:,k-1];s=m.sim_all(B);mus=s[torch.arange(len(x))[:,None],torch.arange(3)[None,:],q[:,None]];p=torch.cat([mus.reshape(len(x),9),L],-1)
   rows.append({'seed':seed,'world_steps':k,'nll':float(r.loss(p,y)),'mse':float((r.expected(p)-y).square().mean()),'B_step_rms':np.nan if k==1 else float((tr['B'][:,k-1]-tr['B'][:,k-2]).square().mean().sqrt()),'B_norm':float(B.square().mean().sqrt())})
pd.DataFrame(rows).to_csv('long_rollout.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
