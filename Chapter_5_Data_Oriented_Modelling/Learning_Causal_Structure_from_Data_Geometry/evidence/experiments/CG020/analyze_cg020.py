from pathlib import Path
import math,json
import numpy as np,pandas as pd, torch
from scipy.special import logsumexp
import run_cg020_object_state as r
ROOT=Path(__file__).resolve().parent; z=np.load(ROOT/'synthetic_data.npz');ix=np.flatnonzero(z['split']==2);groups=z['group'][ix];y=z['y'][ix];trueB=z['true_B'][ix];x=z['x'][ix]
SIGMA=.15

def inst_nll(pred,y):
 mus=pred[:,:9].reshape(-1,3,3); lp=pred[:,9:]-logsumexp(pred[:,9:],axis=1,keepdims=True);ld=-.5*((mus-y[:,None,:])/SIGMA)**2;ld=ld.sum(-1)-3*math.log(SIGMA*math.sqrt(2*math.pi));return -logsumexp(lp+ld,axis=1)
def inst_mse(pred,y):
 mus=pred[:,:9].reshape(-1,3,3);w=np.exp(pred[:,9:]-logsumexp(pred[:,9:],axis=1,keepdims=True));mean=(mus*w[:,:,None]).sum(1);return ((mean-y)**2).mean(-1)
def boot(v,seed=2020,B=10000):
 v=np.asarray(v);rg=np.random.default_rng(seed);m=np.array([rg.choice(v,len(v),replace=True).mean() for _ in range(B)]);return {'mean':float(v.mean()),'lo':float(np.quantile(m,.025)),'hi':float(np.quantile(m,.975)),'fraction_positive':float((v>0).mean())}
rows=[]
for variant in r.VARIANTS:
 for seed in [11,22]:
  a=np.load(ROOT/'predictions'/f'{variant}_{seed}.npz');pred=a['prediction'];
  for i,g in enumerate(groups):rows.append({'variant':variant,'seed':seed,'group':int(g),'nll':inst_nll(pred[i:i+1],y[i:i+1])[0],'mse':inst_mse(pred[i:i+1],y[i:i+1])[0]})
pd.DataFrame(rows).to_csv(ROOT/'instance_metrics.csv',index=False)
df=pd.DataFrame(rows)
controls=[]
for metric in ['nll','mse']:
 a=df[df.variant.eq('onepass3')].groupby(['seed','group'])[metric].mean()
 b=df[df.variant.eq('world4_3')].groupby(['seed','group'])[metric].mean()
 d=(a-b).groupby('group').mean() # positive = world4 better
 q=boot(d,2020+(0 if metric=='nll' else 1));q.update({'contrast':'onepass3_minus_world4_3','metric':metric,'n_groups':len(d)});controls.append(q)
# rollout aggregates
c=pd.read_csv(ROOT/'long_rollout.csv');agg=c.groupby('world_steps')[['nll','mse','B_step_rms','B_norm']].mean().reset_index();agg.to_csv(ROOT/'long_rollout_summary.csv',index=False)
# model-level summary
res=pd.read_csv(ROOT/'results.csv');summary=res.groupby('variant').agg(n_seeds=('seed','count'),parameters=('parameters','first'),nll=('nll','mean'),mse=('mse','mean'),coverage=('ambiguous_world_coverage','mean'),double_do_nll=('double_do_nll','mean'),edge_delete_nll=('edge_delete_nll','mean'),edge_ignore_nll=('edge_ignore_nll','mean'),wrong_edge_nll=('wrong_edge_nll','mean'),edge_delta_corr=('edge_delta_corr','mean'),edge_delta_sign=('edge_delta_sign','mean')).reset_index();summary.to_csv(ROOT/'summary.csv',index=False)
pd.DataFrame(controls).to_csv(ROOT/'group_controls.csv',index=False)
print(summary.to_string(index=False));print('\ncontrols');print(pd.DataFrame(controls).to_string(index=False));print('\nlong');print(agg.to_string(index=False))
