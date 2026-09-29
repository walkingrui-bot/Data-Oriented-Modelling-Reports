from pathlib import Path
import importlib.util, json, numpy as np, torch, pandas as pd
spec=importlib.util.spec_from_file_location('cg','/mnt/data/cg021_work/CAUSAL_GEOMETRY_021/run_cg021_free_pool.py');cg=importlib.util.module_from_spec(spec);spec.loader.exec_module(cg)
R=Path('/mnt/data/cg021_work/CAUSAL_GEOMETRY_021');z=np.load(R/'synthetic_data.npz');ix=z['split']==2
x=torch.tensor(z['x'][ix],dtype=torch.float32);support=z['support'][ix];group=z['group'][ix]
out={'checkpoints':{},'pre_reveal_pair_max_B_diff':{},'pre_reveal_pair_max_logit_diff':{}}
for K in [3,8]:
  for seed in [11,22]:
    name=f'pool{K}_{seed}';ck=torch.load(R/'models'/f'{name}.pt',map_location='cpu');m=cg.FreePool(K);m.load_state_dict(ck['state_dict']);m.eval()
    with torch.no_grad():p,t=m(x,trace=True)
    saved=np.load(R/'predictions'/f'{name}.npz')
    pred_err=float(np.max(np.abs(p.numpy()-saved['prediction'])));B_err=float(np.max(np.abs(t['B'].numpy()-saved['B'])));lg_err=float(np.max(np.abs(t['logits'].numpy()-saved['logits'])))
    B=t['B'][:,-1];diag=float(B.diagonal(dim1=-2,dim2=-1).abs().max());rows=float(B.abs().sum(-1).max())
    out['checkpoints'][name]={'prediction_max_abs_error':pred_err,'trajectory_B_max_abs_error':B_err,'trajectory_logit_max_abs_error':lg_err,'max_abs_diagonal':diag,'max_row_abs_sum':rows}
    # support/no-support twins within each true world are consecutive in this fixed dataset; before reveal they must be identical.
    b2=t['B'][:,1].numpy();l2=t['logits'][:,1].numpy();db=[];dl=[]
    for g in np.unique(group):
      ids=np.flatnonzero(group==g)
      for a,b in [(ids[0],ids[1]),(ids[2],ids[3]),(ids[4],ids[5])]:db.append(np.max(np.abs(b2[a]-b2[b])));dl.append(np.max(np.abs(l2[a]-l2[b])))
    out['pre_reveal_pair_max_B_diff'][name]=float(max(db));out['pre_reveal_pair_max_logit_diff'][name]=float(max(dl))
# Evidence package claims
kf=json.loads((R/'key_findings.json').read_text());out['key_findings']=kf
ok=all(v['prediction_max_abs_error']==0 and v['trajectory_B_max_abs_error']==0 and v['trajectory_logit_max_abs_error']==0 and v['max_abs_diagonal']==0 and v['max_row_abs_sum']<=.950001 for v in out['checkpoints'].values()) and all(v==0 for v in out['pre_reveal_pair_max_B_diff'].values()) and all(v==0 for v in out['pre_reveal_pair_max_logit_diff'].values())
out['all_checks_pass']=bool(ok);(R/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
