import numpy as np,pandas as pd,torch
import run_cg020_object_state as r
z=np.load('synthetic_data.npz');ii=np.flatnonzero(z['split']==2);x=torch.tensor(z['x'][ii],dtype=torch.float32);y=torch.tensor(z['y'][ii],dtype=torch.float32);support=z['support'][ii];query=z['query'][ii];groups=z['group'][ii]
torch.set_num_threads(4);rows=[];traj=[]

def pred_from_state(m,x,B,L):
 s=m.sim_all(B);q=x[:,-3:].argmax(-1);mus=s[torch.arange(len(x))[:,None],torch.arange(3)[None,:],q[:,None]];return torch.cat([mus.reshape(len(x),9),L],-1)

def donor_indices():
 d=np.arange(len(x));
 for sp in [0,1]:
  for q in [0,1,2]:
   ix=np.flatnonzero((support==sp)&(query==q));
   # ensure donor differs in group: rotate until no same group
   for pos,i in enumerate(ix):
    for k in range(1,len(ix)):
     j=ix[(pos+k)%len(ix)]
     if groups[j]!=groups[i]:d[i]=j;break
 return torch.tensor(d)
donor=donor_indices()
for seed in [11,22]:
 ck=torch.load(f'models/world4_3_{seed}.pt',weights_only=True);m=r.ObjectWorldModel(3,1);m.load_state_dict(ck['state_dict']);m.eval()
 with torch.no_grad():
  pfull,t4=m(x,4,trace=True);p2,t2=m(x,2,trace=True);B2=t2['B'][:,-1].clone();L2=t2['logits'][:,-1].clone()
  base_states=[]
  for k in [2,3,4]:
   pk,tk=m(x,k,trace=True);base_states.append((pk,tk['B'][:,-1],tk['logits'][:,-1]))
  # erase explicit state at step2
  ze=(torch.zeros_like(B2),torch.zeros_like(L2));perase=m(x,2,start_state=ze)
  # transplant explicit state, context remains recipient context
  pt=m(x,2,start_state=(B2[donor],L2[donor]))
  # edge flip at step2
  Be=B2.clone();best=L2.argmax(-1);flat=Be[torch.arange(len(x)),best].abs().reshape(len(x),-1).argmax(-1);rr=flat//3;ss=flat%3;Be[torch.arange(len(x)),best,rr,ss]*=-1
  pe2=pred_from_state(m,x,Be,L2);pe3=m(x,1,start_state=(Be,L2));pe4=m(x,2,start_state=(Be,L2))
  for name,p in [('baseline',pfull),('erase_step2',perase),('transplant_step2',pt),('flip_step2_then2',pe4)]:
   rows.append({'seed':seed,'condition':name,'nll':float(r.loss(p,y)),'mse':float((r.expected(p)-y).square().mean()),'prediction_rms_vs_base':float((r.expected(p)-r.expected(pfull)).square().mean().sqrt())})
  for stage,pedit,pbase in [(2,pe2,base_states[0][0]),(3,pe3,base_states[1][0]),(4,pe4,base_states[2][0])]:
   traj.append({'seed':seed,'stage':stage,'prediction_rms':float((r.expected(pedit)-r.expected(pbase)).square().mean().sqrt())})
pd.DataFrame(rows).to_csv('object_interventions.csv',index=False);pd.DataFrame(traj).to_csv('object_edit_trajectory.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False));print('\ntrajectory');print(pd.DataFrame(traj).to_string(index=False))
