import sys, json, time, math, os
import numpy as np, pandas as pd, torch
from experiment import Model, make_data, objective, normalized_alignment, cross_rmse, self_rmse, linear_r2, seed_all, set_freeze

torch.set_num_threads(1)

def fast_run(seed, variant='switch', freeze=None, pre=250, bind=1200, lr=0.015):
    seed_all(seed)
    qtr,xtr,qte,xte=make_data()
    model=Model()
    opt=torch.optim.Adam(model.parameters(),lr=lr)
    if variant=='direct': pre=0
    for _ in range(pre):
        opt.zero_grad(); L,_,_,_=objective(model,xtr,'self'); L.backward(); opt.step()
    # pre metrics + snapshots
    with torch.no_grad():
        _,rpre,_,plpre=objective(model,xte,'binding')
        pre_m=dict(pre_cross=cross_rmse(plpre)[0], pre_align=normalized_alignment(rpre), pre_self=self_rmse(plpre), pre_r2=linear_r2(rpre,qte))
        theta_pre={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()}
    if variant=='self_only':
        return {**pre_m,'cross_test':pre_m['pre_cross'],'align_test':pre_m['pre_align'],'self_test':pre_m['pre_self'],'latent_r2_test':pre_m['pre_r2'],'worst_cross_test':cross_rmse(plpre)[1], 'd_core':0,'d_enc':0,'d_dec':0}
    if freeze:
        set_freeze(model,freeze)
        opt=torch.optim.Adam([p for p in model.parameters() if p.requires_grad],lr=lr)
    shuf=None
    if variant=='shuffled':
        rng=np.random.default_rng(seed+9000); n=xtr[0].shape[0]; shuf=[]
        for i in range(3):
            row=[]
            for j in range(3):
                if i==j: row.append(xtr[j])
                else:
                    perm=torch.tensor(rng.permutation(n),dtype=torch.long)
                    row.append(xtr[j][perm])
            shuf.append(row)
    for _ in range(bind):
        opt.zero_grad(); L,_,_,_=objective(model,xtr,'binding',shuf); L.backward(); opt.step()
    with torch.no_grad():
        _,rte,_,plte=objective(model,xte,'binding')
        post={k:v.detach().cpu().numpy().copy() for k,v in model.state_dict().items()}
    def block_delta(prefix):
        num=0.0; den=0.0
        for k in post:
            if k.startswith(prefix):
                d=post[k]-theta_pre[k]; num += float((d*d).sum()); den += float((theta_pre[k]*theta_pre[k]).sum())
        return math.sqrt(num), math.sqrt(den)
    dc,_=block_delta('core.'); de,_=block_delta('enc.'); dd,_=block_delta('dec.')
    return {**pre_m,'cross_test':cross_rmse(plte)[0],'worst_cross_test':cross_rmse(plte)[1],'align_test':normalized_alignment(rte),'self_test':self_rmse(plte),'latent_r2_test':linear_r2(rte,qte),'d_core':dc,'d_enc':de,'d_dec':dd}

