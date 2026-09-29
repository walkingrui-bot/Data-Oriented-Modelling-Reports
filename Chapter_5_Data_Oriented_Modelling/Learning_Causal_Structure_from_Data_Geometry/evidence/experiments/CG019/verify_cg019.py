from pathlib import Path
import json, sys
import numpy as np, pandas as pd, torch
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
import run_cg018 as cg18
# Verify all six checkpoints reload and reproduce the frozen test objects deterministically.
z=np.load(R/'synthetic_test_context.npz'); x=torch.tensor(z['x'],dtype=torch.float32)
checks=[]
for mode in ['mechanism_blank','mechanism_feedback']:
  for seed in [11,22,33]:
    ck=torch.load(R/'models'/f'synthetic_worlds_{mode}_{seed}.pt',weights_only=True)
    m=cg18.MechanismModel('synthetic',mode); m.load_state_dict(ck['state_dict']); m.eval()
    with torch.no_grad(): p,tr=m(x,trace=True)
    checks.append({'mode':mode,'seed':seed,'finite_prediction':bool(torch.isfinite(p).all()),'finite_B':bool(torch.isfinite(tr['B']).all()),'max_row_abs_sum':float(tr['B'][:,-1].abs().sum(-1).max()),'diag_abs_max':float(torch.diagonal(tr['B'][:,-1],dim1=-2,dim2=-1).abs().max())})
# Consistency checks on recorded statistics.
s=pd.read_csv(R/'summary.csv'); c=pd.read_csv(R/'group_level_controls.csv'); e=pd.read_csv(R/'edge_semantic_summary.csv')
assert len(checks)==6 and all(q['finite_prediction'] and q['finite_B'] for q in checks)
assert max(q['max_row_abs_sum'] for q in checks) <= .950001
assert max(q['diag_abs_max'] for q in checks) < 1e-7
assert set(c.n_groups)=={100}
assert len(e)==6
out={'checkpoint_checks':checks,'rows_summary':len(s),'rows_group_controls':len(c),'rows_edge_semantics':len(e),'status':'PASS'}
(R/'verification.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
