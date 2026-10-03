import sys, os, math, json
import numpy as np, pandas as pd, torch
from experiment import Model, make_data, objective, normalized_alignment, cross_rmse, self_rmse, linear_r2, seed_all, grad_cosines

torch.set_num_threads(1)
seed=0; seed_all(seed)
qtr,xtr,qte,xte=make_data(); model=Model(); opt=torch.optim.Adam(model.parameters(),lr=0.015)
for _ in range(180):
    opt.zero_grad(); L,_,_,_=objective(model,xtr,'self'); L.backward(); opt.step()

base={k:v.detach().clone() for k,v in model.state_dict().items()}
prev={k:v.detach().clone() for k,v in model.state_dict().items()}

def vec_delta(state1,state0,prefix):
    ss=0.
    for k in state1:
        if k.startswith(prefix):
            d=(state1[k]-state0[k]).float(); ss += float((d*d).sum())
    return math.sqrt(ss)

def metrics(step):
    with torch.no_grad():
        _,rte,_,plte=objective(model,xte,'binding')
        cur={k:v.detach().clone() for k,v in model.state_dict().items()}
    cos=grad_cosines(model,xtr)
    return dict(bind_step=step,cross_test=cross_rmse(plte)[0],worst_cross_test=cross_rmse(plte)[1],self_test=self_rmse(plte),align_test=normalized_alignment(rte),latent_r2_test=linear_r2(rte,qte),cos_AB=cos[0],cos_AC=cos[1],cos_BC=cos[2],cum_core=vec_delta(cur,base,'core.'),cum_enc=vec_delta(cur,base,'enc.'),cum_dec=vec_delta(cur,base,'dec.'),step_core=vec_delta(cur,prev,'core.'),step_enc=vec_delta(cur,prev,'enc.'),step_dec=vec_delta(cur,prev,'dec.')),cur

rows=[]
r,cur=metrics(0); rows.append(r); prev=cur
for t in range(1,701):
    opt.zero_grad(); L,_,_,_=objective(model,xtr,'binding'); L.backward(); opt.step()
    if t<=20 or t in [25,30,40,50,75,100,150,200,300,400,500,600,700]:
        r,cur=metrics(t); rows.append(r); prev=cur
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
outdir = ROOT / 'reproduced_results'
outdir.mkdir(exist_ok=True)
pd.DataFrame(rows).to_csv(outdir / 'seed0_binding_trace.csv',index=False)
print(pd.DataFrame(rows).head(12).to_string(index=False))
print('\nTAIL')
print(pd.DataFrame(rows).tail(8).to_string(index=False))
