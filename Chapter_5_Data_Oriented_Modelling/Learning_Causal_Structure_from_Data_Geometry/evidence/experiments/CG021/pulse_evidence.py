from pathlib import Path
import importlib.util, numpy as np, pandas as pd, torch, math
spec=importlib.util.spec_from_file_location('cg','/mnt/data/cg021_work/run_cg021_free_pool.py');cg=importlib.util.module_from_spec(spec);spec.loader.exec_module(cg)
ROOT=Path('/mnt/data/cg021_work/CAUSAL_GEOMETRY_021');z=np.load(cg.DATA);ix=z['split']==2
x=torch.tensor(z['x'][ix],dtype=torch.float32);y=torch.tensor(z['y'][ix],dtype=torch.float32);sup=z['support'][ix];truth=z['all_query_truth'][ix]
rows=[]
for K in [3,8]:
  for seed in [11,22]:
    ck=torch.load(ROOT/'models'/f'pool{K}_{seed}.pt',map_location='cpu');m=cg.FreePool(K);m.load_state_dict(ck['state_dict']);m.eval()
    outs={};states={}
    with torch.no_grad():
      for mode in ['never','pulse','normal']:
        B=torch.zeros(len(x),K,3,3);lg=torch.zeros(len(x),K);Bs=[]
        for t in range(1,5):
          reveal=(mode=='normal' and t>=3) or (mode=='pulse' and t==3)
          B,lg=m.transition(m.ctx_tokens(x,reveal),B,lg);Bs.append(B.clone())
        sims=m.sim_all(B);q=x[:,-3:].argmax(-1);mus=sims[torch.arange(len(x))[:,None],torch.arange(K)[None,:],q[:,None]];p=torch.cat([mus.reshape(len(x),K*3),lg],-1)
        outs[mode]=p;states[mode]=torch.stack(Bs,1)
    sid=np.flatnonzero(sup==1);sidt=torch.tensor(sid)
    for mode in ['never','pulse','normal']:
      p=outs[mode][sidt];single=float(cg.loss(p,y[sidt],K));B=states[mode][sidt,-1].numpy();lg=outs[mode][sidt,K*3:].numpy();aq=float(cg.allq(B,lg,truth[sid]).mean());pred=cg.expected(p,K).numpy();outs[mode+'_pred']=pred
      rows.append({'variant':f'pool{K}','seed':seed,'mode':mode,'support_single_query_nll':single,'support_allq_nll':aq})
    # evidence imprint: pulse vs never after reveal step 3 and after support is removed at step 4
    b3=float((states['pulse'][sidt,2]-states['never'][sidt,2]).square().mean().sqrt());b4=float((states['pulse'][sidt,3]-states['never'][sidt,3]).square().mean().sqrt())
    pred_p=outs['pulse_pred'];pred_n=outs['never_pred'];pred_o=outs['normal_pred']
    sh_pn=float(np.sqrt(((pred_p-pred_n)**2).mean(1)).mean());sh_po=float(np.sqrt(((pred_p-pred_o)**2).mean(1)).mean())
    rows.append({'variant':f'pool{K}','seed':seed,'mode':'memory_summary','support_single_query_nll':np.nan,'support_allq_nll':np.nan,'B_imprint_step3':b3,'B_imprint_step4_after_removal':b4,'prediction_shift_pulse_vs_never':sh_pn,'prediction_shift_pulse_vs_normal':sh_po,'retained_B_fraction':b4/b3 if b3 else np.nan})
pd.DataFrame(rows).to_csv(ROOT/'pulse_evidence.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
