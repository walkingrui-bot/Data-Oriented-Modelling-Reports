#!/usr/bin/env python3
"""
Recompute HUMAN-SENSORIMOTOR-GEOMETRY-003 from local source files.

Usage:
  python recompute_geometry.py --mocap-root /path/to/subjects --corpus /path/to/language_corpus.txt --out /path/to/out

The motion root should contain subject folders 01, 02 and 03 with the selected .amc files.
"""
from pathlib import Path
from collections import Counter
import argparse, numpy as np, pandas as pd

SELECTED = {
"01":["01_01.amc","01_03.amc","01_06.amc","01_09.amc","01_12.amc","01_14.amc"],
"02":["02_01.amc","02_02.amc","02_03.amc","02_04.amc","02_05.amc","02_06.amc","02_07.amc","02_08.amc","02_09.amc","02_10.amc"],
"03":["03_01.amc","03_02.amc","03_03.amc","03_04.amc"]}

def parse_amc(path):
    frames=[]; cur=None
    for raw in Path(path).read_text(errors="ignore").splitlines():
        s=raw.strip()
        if not s or s.startswith("#") or s.startswith(":"): continue
        if s.isdigit():
            if cur is not None: frames.append(cur)
            cur=[]; continue
        if cur is None: continue
        parts=s.split(); joint=parts[0]
        if joint=="root" or "fingers" in joint or "thumb" in joint: continue
        cur.extend(float(x) for x in parts[1:])
    if cur is not None: frames.append(cur)
    p=min(map(len,frames))
    return np.asarray([r for r in frames if len(r)==p],float)

def unwrap_deg(X):
    Y=X.copy()
    for j in range(Y.shape[1]):
        Y[:,j]=np.rad2deg(np.unwrap(np.deg2rad(Y[:,j])))
    return Y

def moving_average(X,w=5):
    if w<=1: return X
    out=np.empty_like(X)
    h=w//2
    for i in range(len(X)):
        out[i]=X[max(0,i-h):min(len(X),i+h+1)].mean(axis=0)
    return out

def prep(X,balanced=False):
    X=X-X.mean(0,keepdims=True)
    sd=X.std(0,ddof=1)
    keep=sd>1e-8
    X=X[:,keep]
    if balanced: X=X/X.std(0,ddof=1,keepdims=True)
    return X

def metrics(X):
    vals=np.linalg.eigvalsh(np.cov(X,rowvar=False))[::-1]
    vals=np.clip(vals,0,None)
    S=vals.sum(); p=vals/S
    return dict(
        stable_rank=S/vals[0],
        participation_rank=S*S/np.square(vals).sum(),
        d80=int(np.searchsorted(np.cumsum(p),.80)+1),
        d95=int(np.searchsorted(np.cumsum(p),.95)+1),
        top4_var=float(p[:4].sum())
    )

def language_metrics(text):
    VOC=64
    cnt=Counter(text); chars=[c for c,_ in cnt.most_common(VOC-1)]
    c2i={c:i for i,c in enumerate(chars)}; unk=VOC-1
    ids=np.array([c2i.get(c,unk) for c in text],int)
    uni=np.bincount(ids,minlength=VOC).astype(float); pi=uni/uni.sum()
    bi=np.zeros((VOC,VOC),float)
    np.add.at(bi,(ids[:-1],ids[1:]),1)
    P=bi/np.maximum(bi.sum(1,keepdims=True),1)
    A=np.sqrt(pi)[:,None]*(P-pi[None,:])
    s=np.linalg.svd(A,compute_uv=False)
    bigram=metrics_from_energy(s*s)

    L=3; mind=10
    next_counts={}
    def key(a,b,c): return (int(a),int(b),int(c))
    for t in range(L-1,len(ids)-1):
        k=key(ids[t-2],ids[t-1],ids[t])
        if k not in next_counts: next_counts[k]=np.zeros(VOC,int)
        next_counts[k][ids[t+1]]+=1
    Q={k:v/v.sum() for k,v in next_counts.items() if v.sum()>=mind}
    weights={k:next_counts[k].sum() for k in Q}
    keys=list(Q)
    X=np.vstack([Q[k] for k in keys]); w=np.array([weights[k] for k in keys],float)
    state=weighted_metrics(X,w)
    diffs=[]; dw=[]
    pair={}
    for t in range(L-1,len(ids)-2):
        k1=key(ids[t-2],ids[t-1],ids[t]); k2=key(ids[t-1],ids[t],ids[t+1])
        if k1 in Q and k2 in Q: pair[(k1,k2)]=pair.get((k1,k2),0)+1
    for (k1,k2),ww in pair.items():
        diffs.append(Q[k2]-Q[k1]); dw.append(ww)
    movement=weighted_metrics(np.vstack(diffs),np.array(dw,float))
    return bigram,state,movement

def metrics_from_energy(e):
    e=np.clip(np.asarray(e,float),0,None); S=e.sum(); p=e/S
    return dict(stable_rank=S/e.max(),participation_rank=S*S/np.square(e).sum(),
                d80=int(np.searchsorted(np.cumsum(p),.8)+1),
                d95=int(np.searchsorted(np.cumsum(p),.95)+1),
                top4_var=float(p[:4].sum()))

def weighted_metrics(X,w):
    w=w/w.sum(); mu=(X*w[:,None]).sum(0); Z=X-mu
    C=(Z*w[:,None]).T@Z
    vals=np.linalg.eigvalsh(C)[::-1]
    return metrics_from_energy(vals)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--mocap-root",required=True)
    ap.add_argument("--corpus",required=True)
    ap.add_argument("--out",required=True)
    args=ap.parse_args()
    out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    rows=[]
    for subj,files in SELECTED.items():
        for fn in files:
            X=unwrap_deg(parse_amc(Path(args.mocap_root)/subj/fn))
            V=np.diff(X,axis=0)
            Xm=moving_average(X,5); Vm=np.diff(Xm,axis=0)
            r={"subject":subj,"file":fn,"frames":len(X)}
            for prefix,data in [("state_raw",prep(X,False)),("velocity_raw",prep(V,False)),
                                ("state_bal",prep(X,True)),("velocity_bal",prep(V,True)),
                                ("velocity_smooth5",prep(Vm,False))]:
                for k,v in metrics(data).items(): r[prefix+"_"+k]=v
            rows.append(r)
    pd.DataFrame(rows).to_csv(out/"motion_trial_geometry_recomputed.csv",index=False)
    bigram,state,movement=language_metrics(Path(args.corpus).read_text(encoding="utf-8"))
    pd.DataFrame([{"representation":"bigram",**bigram},{"representation":"L3 state",**state},{"representation":"L3 movement",**movement}]).to_csv(out/"language_geometry_recomputed.csv",index=False)
if __name__=="__main__": main()
