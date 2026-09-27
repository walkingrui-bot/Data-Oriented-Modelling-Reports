#!/usr/bin/env python3
"""Reproduce RELATIONAL-ROUTER-008 from local pinned UD test files.

Usage:
  python reproduce_relational_router.py --ud-dir /path/to/ud_files --out out.json

The directory must contain the exact filenames in source_manifest.csv.
Dependencies: numpy, pandas.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

ROLES=["nsubj","csubj","obj","iobj","ccomp","xcomp","obl"]
RI={r:i for i,r in enumerate(ROLES)}
SUBORD={"ccomp","xcomp","advcl","acl","parataxis","conj"}

def br(s): return s.split(":")[0]

def parse_conllu(path: Path):
    out=[]; cur=[]
    for ln in path.read_text(encoding="utf-8").splitlines():
        if not ln.strip():
            if cur: out.append(cur); cur=[]
            continue
        if ln.startswith("#"): continue
        f=ln.split("\t")
        if len(f)<8 or "-" in f[0] or "." in f[0]: continue
        cur.append({"id":int(f[0]),"upos":f[3],"head":int(f[6]),"rel":br(f[7])})
    if cur: out.append(cur)
    return out

def sentence_row(sent, lang):
    by={t["id"]:t for t in sent}; child={}
    for t in sent: child.setdefault(t["head"],[]).append(t)
    preds=[]
    for t in sent:
        ch=child.get(t["id"],[])
        cop=any(x["rel"]=="cop" for x in ch)
        hp=any(x["rel"] in RI for x in ch)
        is_pred=(t["upos"]=="VERB" or (t["upos"] in {"ADJ","NOUN","PROPN"} and cop) or (t["upos"]=="AUX" and hp))
        if not is_pred: continue
        c=np.zeros(7); dr=np.zeros(7); di=np.zeros(7)
        for x in ch:
            j=RI.get(x["rel"])
            if j is None: continue
            c[j]+=1; dr[j]+=np.sign(x["id"]-t["id"]); di[j]+=abs(x["id"]-t["id"])
        v=np.r_[c, np.divide(dr,c,out=np.zeros(7),where=c>0), np.divide(np.log1p(di/c),1,out=np.zeros(7),where=c>0)]
        preds.append({"id":t["id"],"head":t["head"],"rel":t["rel"],"v":v})
    if not preds: return None
    pids={p["id"] for p in preds}
    for p in preds:
        x=p["head"]; pa=0; nest=0; seen=set()
        while x and x in by and x not in seen:
            seen.add(x)
            if x in pids:
                if not pa: pa=x
                nest+=1
            x=by[x]["head"]
        p["parent"]=pa; p["nest"]=nest
    preds.sort(key=lambda p:p["id"])
    memo={}
    def depth(i,seen=None):
        if i==0:return 0
        if i in memo:return memo[i]
        if seen is None: seen=set()
        if i in seen or i not in by:return 0
        seen.add(i); d=1+depth(by[i]["head"],seen); memo[i]=d; return d
    tree_depth=max(depth(t["id"]) for t in sent)
    deps=[t for t in sent if t["head"]>0]
    mean_dep=np.mean([abs(t["id"]-t["head"]) for t in deps]) if deps else 0.0
    max_nest=max(p["nest"] for p in preds)
    def ancestors(i):
        a=[i]; seen=set(); x=i
        while x and x in by and x not in seen:
            seen.add(x); x=by[x]["head"]
            if x:a.append(x)
        return a
    def tdist(a,b):
        A=ancestors(a); pos={x:i for i,x in enumerate(A)}
        for j,x in enumerate(ancestors(b)):
            if x in pos:return pos[x]+j
        return len(A)+len(ancestors(b))
    pp=[tdist(preds[i]["id"],preds[j]["id"]) for i in range(len(preds)) for j in range(i+1,len(preds))]
    pred_pair=np.mean(pp) if pp else 0.0
    arcs=[(min(t["id"],t["head"]),max(t["id"],t["head"]),t["id"],t["head"]) for t in deps]
    cross=0
    for i,a in enumerate(arcs):
        for b in arcs[i+1:]:
            if len({a[2],a[3],b[2],b[3]})<4: continue
            if (a[0]<b[0]<a[1]<b[1]) or (b[0]<a[0]<b[1]<a[1]): cross+=1
    sub=sum(p["rel"] in SUBORD for p in preds)
    return {"lang":lang,"n":len(sent),"preds":preds,"y":np.array([tree_depth,mean_dep,max_nest,pred_pair,sub,cross],float)}

def local_pca(rows, train, k=8):
    X=np.vstack([p["v"] for i in train for p in rows[i]["preds"]])
    mu=X.mean(0); sd=X.std(0); sd[sd<1e-8]=1
    Z=(X-mu)/sd; _,_,vt=np.linalg.svd(Z,full_matrices=False); W=vt[:k].T
    def enc(v):return ((v-mu)/sd)@W
    return enc

def features(row,enc,mode):
    P=[dict(p,e=enc(p["v"])) for p in row["preds"]]; E=np.vstack([p["e"] for p in P])
    base=np.r_[E.mean(0),E.std(0),E.max(0),E.min(0),np.log1p(len(P))]
    pairs=[]
    if mode=="hier":
        m={p["id"]:p for p in P}
        pairs=[(m[p["parent"]],p) for p in P if p["parent"] in m]
    elif mode=="shuffle":
        for i in range(1,len(P)):
            j=(i*3+1)%len(P)
            if j==i:j=(j+1)%len(P)
            pairs.append((P[j],P[i]))
    else:
        pairs=list(zip(P[:-1],P[1:]))
    if pairs:
        A=np.vstack([np.abs(a["e"]-b["e"]) for a,b in pairs]).mean(0)
        B=np.vstack([a["e"]*b["e"] for a,b in pairs]).mean(0)
    else:
        A=np.zeros(8);B=np.zeros(8)
    return np.r_[base,A,B]

def ridge_fit(X,Y,train,lam=5):
    Xtr=X[train];Ytr=Y[train]
    mx=Xtr.mean(0);sx=Xtr.std(0);sx[sx<1e-8]=1
    my=Ytr.mean(0);sy=Ytr.std(0);sy[sy<1e-8]=1
    Z=(Xtr-mx)/sx; T=(Ytr-my)/sy; Z=np.c_[Z,np.ones(len(Z))]
    I=np.eye(Z.shape[1]);I[-1,-1]=0
    W=np.linalg.solve(Z.T@Z+lam*I,Z.T@T)
    def pred(A): return (np.c_[((A-mx)/sx),np.ones(len(A))]@W)*sy+my
    return pred,sy

def nrmse(pred,X,Y,idx,sy):
    P=pred(X[idx]);E=(P-Y[idx])/sy
    return float(np.sqrt(np.mean(E**2))),np.sqrt(np.mean(E**2,axis=0))

def run(rows,train,test):
    enc=local_pca(rows,train)
    XF=np.vstack([features(r,enc,"flat") for r in rows]);XH=np.vstack([features(r,enc,"hier") for r in rows]);XS=np.vstack([features(r,enc,"shuffle") for r in rows]);Y=np.vstack([r["y"] for r in rows])
    pf,sf=ridge_fit(XF,Y,train);ph,sh=ridge_fit(XH,Y,train);ps,ss=ridge_fit(XS,Y,train)
    ef,_=nrmse(pf,XF,Y,test,sf);eh,_=nrmse(ph,XH,Y,test,sh);es,_=nrmse(ps,XS,Y,test,ss)
    # adaptive uses flat/hier predictions from the same fitted heads
    PF=pf(XF[test]);PH=ph(XH[test]);gate=np.array([len(rows[i]["preds"])>=3 or max(p["nest"] for p in rows[i]["preds"])>=2 for i in test])
    PA=np.where(gate[:,None],PH,PF); ea=float(np.sqrt(np.mean(((PA-Y[test])/sf)**2)))
    return ef,eh,ea,es,float(gate.mean())

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ud-dir',type=Path,required=True);ap.add_argument('--out',type=Path,default=Path('relational_router_008_reproduction.json'));args=ap.parse_args()
    manifest=pd.read_csv(Path(__file__).with_name('source_manifest.csv'))
    rows=[]
    for _,r in manifest.iterrows():
        for s in parse_conllu(args.ud_dir/r.file):
            x=sentence_row(s,r.language)
            if x is not None:rows.append(x)
    n=len(rows);rng=np.random.default_rng(20260927);idx=np.arange(n);rng.shuffle(idx);cut=int(.8*n);tr=idx[:cut];te=idx[cut:]
    ef,eh,ea,es,act=run(rows,tr,te)
    out={"sentences":n,"random_split":{"flat":ef,"hierarchical":eh,"adaptive":ea,"shuffled_edge":es,"adaptive_activation":act}}
    langs=sorted({r['lang'] for r in rows});fold=[]
    for L in langs:
        tr=np.array([i for i,r in enumerate(rows) if r['lang']!=L]);te=np.array([i for i,r in enumerate(rows) if r['lang']==L])
        f,h,a,s,act=run(rows,tr,te);fold.append({"language":L,"n":len(te),"flat":f,"hierarchical":h,"adaptive":a,"activation":act})
    out['leave_one_language_out']=fold
    args.out.write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps(out,indent=2))
if __name__=='__main__':main()
