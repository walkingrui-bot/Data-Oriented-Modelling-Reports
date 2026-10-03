"""Post-run follow-up diagnostics after the 80-step experiment.

Longer optimisation resolves finite-budget versus representation effects.
Exact rank-one fits verify the linear layer's observed residual floor.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import experiment as ex

ROOT=ex.ROOT
rows=[]; references=[]; init_rows=[]
for noise in [0.,.03]:
    for seed in range(30):
        x,phi,observed,clean,true_theta,s,W_true,init=ex.create_data(seed,noise)
        teacher,_=ex.train_local(phi,observed,init)
        target=teacher@phi.T; centered=target-target.mean(0)
        u,sv,vt=np.linalg.svd(centered,full_matrices=False)
        best=target.mean(0)+(u[:,:1]*sv[:1])@vt[:1]
        references.append(dict(noise=noise,seed=seed,
            constant_rmse=np.sqrt(np.mean(centered**2)),
            exact_best_line_rmse=np.sqrt(np.mean((best-target)**2)),
            target_s1=sv[0],target_s2=sv[1],target_s3=sv[2]))
        for kind in ['geometry','random']:
            p=ex.initialize(teacher,2,seed,kind)
            a=ex.audit(p,2,phi,teacher,clean,true_theta,s)
            a.update(noise=noise,seed=seed,init=kind)
            init_rows.append(a)
        # Extended optimisation is explicitly a follow-up, reported separately.
        if noise==0. and seed<10:
            for kind in ['geometry','random']:
                for method,steps in [('joint_gradient',4000),('coupled_step',800)]:
                    old=ex.CONFIG['coordinator_steps'];ex.CONFIG['coordinator_steps']=steps
                    p,first,trace,snaps=ex.fit_coordinator(teacher,phi,2,seed,kind,method)
                    ex.CONFIG['coordinator_steps']=old
                    a=ex.audit(p,2,phi,teacher,clean,true_theta,s)
                    a.update(noise=noise,seed=seed,init=kind,update=method,steps=steps,
                             first_pass_step=first if first is not None else -1)
                    rows.append(a)
pd.DataFrame(rows).to_csv(ROOT/'results'/'extended_budget_controls.csv',index=False)
pd.DataFrame(references).to_csv(ROOT/'results'/'exact_representation_controls.csv',index=False)
pd.DataFrame(init_rows).to_csv(ROOT/'results'/'initial_state_audit.csv',index=False)
print(pd.DataFrame(rows).groupby(['init','update']).agg(n=('seed','size'),pass_rate=('all_sources_pass','mean'),median_rmse=('rmse_target','median'),first_pass=('first_pass_step','median')).to_string())
