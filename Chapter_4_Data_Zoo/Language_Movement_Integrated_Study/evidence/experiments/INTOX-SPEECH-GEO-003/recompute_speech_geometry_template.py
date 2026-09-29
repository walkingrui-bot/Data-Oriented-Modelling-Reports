#!/usr/bin/env python3
"""Recompute the INTOX-SPEECH-GEO-003 geometry when original KAISD segments are present.

Expected NPZ layout:
  sober: object array/list or numeric array of segments
  intoxicated: object array/list or numeric array of segments
Each segment may be (128,345) or (345,128); this script normalizes to (time,bands).
"""
import argparse, numpy as np, pandas as pd

def to_tb(seg):
    a=np.asarray(seg,float)
    if a.shape==(128,345): return a.T
    if a.shape==(345,128): return a
    raise ValueError(f"Unexpected segment shape {a.shape}")

def eig_metrics(X):
    X=np.asarray(X,float)
    C=np.cov(X,rowvar=False)
    lam=np.linalg.eigvalsh(C)[::-1]
    lam=np.clip(lam,0,None)
    s=lam.sum(); top=lam[0]
    stable=s/top if top>0 else np.nan
    pr=s*s/np.sum(lam*lam) if np.sum(lam*lam)>0 else np.nan
    d95=int(np.searchsorted(np.cumsum(lam)/s,.95)+1) if s>0 else 0
    top4=lam[:4].sum()/s if s>0 else np.nan
    return dict(stable_rank=stable,participation_rank=pr,d95=d95,top4=top4)

def standardize_shared(sober,intox):
    frames=np.concatenate([*sober,*intox],axis=0)
    mu=frames.mean(0); sd=frames.std(0,ddof=0); sd[sd==0]=1
    return [(x-mu)/sd for x in sober],[(x-mu)/sd for x in intox]

def movement(segs): return [np.diff(x,axis=0) for x in segs]

def trajectory_metrics(seg):
    d=np.diff(seg,axis=0)
    g=eig_metrics(d)
    norms=np.linalg.norm(d,axis=1)
    step=float(np.mean(norms))
    if len(d)>1:
        num=np.sum(d[:-1]*d[1:],axis=1)
        den=np.linalg.norm(d[:-1],axis=1)*np.linalg.norm(d[1:],axis=1)
        cos=np.nanmean(np.divide(num,den,out=np.full_like(num,np.nan),where=den>0))
    else: cos=np.nan
    path=norms.sum(); disp=np.linalg.norm(seg[-1]-seg[0]); tort=path/disp if disp>0 else np.nan
    energy=np.sum(d*d,axis=0); breadth=(energy.sum()**2/np.sum(energy*energy)) if np.sum(energy*energy)>0 else np.nan
    g.update(frame_step_norm=step,adjacent_direction_cosine=cos,tortuosity=tort,movement_band_breadth=breadth)
    return g

def pooled_metrics(segs,object_name):
    X=np.concatenate(segs,axis=0)
    d=eig_metrics(X); d['object']=object_name; return d

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('npz'); ap.add_argument('--out',default='speech_recomputed')
    a=ap.parse_args(); z=np.load(a.npz,allow_pickle=True)
    sober=[to_tb(x) for x in z['sober']]; intox=[to_tb(x) for x in z['intoxicated']]
    sober,intox=standardize_shared(sober,intox)
    rows=[]
    for label,segs in [('Sober',sober),('Intoxicated',intox)]:
        d=pooled_metrics(segs,'State cloud'); d['condition']=label; rows.append(d)
        d=pooled_metrics(movement(segs),'Temporal movement'); d['condition']=label; rows.append(d)
    pd.DataFrame(rows).to_csv(a.out+'_pooled.csv',index=False)
    sm=[]
    for label,segs in [('Sober',sober),('Intoxicated',intox)]:
        for i,s in enumerate(segs):
            d=trajectory_metrics(s); d.update(condition=label,segment=i); sm.append(d)
    pd.DataFrame(sm).to_csv(a.out+'_segment_metrics.csv',index=False)

if __name__=='__main__': main()
