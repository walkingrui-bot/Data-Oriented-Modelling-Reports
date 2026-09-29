from pathlib import Path
import sys, numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import run_cg023_coordinate_world as cg
import run_cg024_sequential_acceptance as r
OUT=Path('/mnt/data/cg024_final/CAUSAL_GEOMETRY_024');dat=np.load(ROOT/'world_data.npz');Ms,bs,eqbank,tmbank=dat['M'],dat['b'],dat['eqbank'],dat['tmbank'];te=np.arange(500,600);rr=[]
for seed in [11,22]:
 ck=torch.load(ROOT/'models'/f'cg023_{seed}.pt',map_location='cpu',weights_only=False);m=cg.WorldProgram();m.load_state_dict(ck['world']);m.eval();x=r.passive_panel(m,seed,Ms,bs,eqbank,tmbank,te);x['source']='cg023';rr.append(x)
pd.concat(rr,ignore_index=True).to_csv(OUT/'cg023_passive_same_panel.csv',index=False)
