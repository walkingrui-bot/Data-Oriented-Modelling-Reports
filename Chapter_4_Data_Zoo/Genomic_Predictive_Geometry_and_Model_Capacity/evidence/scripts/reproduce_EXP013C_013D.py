#!/usr/bin/env python3
"""Reproduce EXP013C/013D from the locked MVP HapMap source.

Usage:
  python reproduce_EXP013C_013D.py --source /path/to/hapmap.txt --out ./out

Source identity locked in the experiment:
  shanwai1234/MVP demo.data/hapmap/hapmap.txt
  Git blob b8120641d506cd1ee55e46d8c345f313501c21ae

The outer EXP013C sample split uses the locked 32-bit LCG/Fisher-Yates rule.
Estimator resampling uses NumPy default_rng with the recorded seeds.
This script executes EXP013C; the EXP013D aggregate results are supplied
separately, and its complete sample-size scan is not implemented here.
"""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

TARGET=np.array([0,4,8,12,16,20,24,28,32])
COEFF={
 'split_mean':(0.1758859068108493,0.3751640383939799),
 'split_power_rel':(0.13353575498132267,0.7411990610766235),
 'bootstrap':(-0.1548643186307435,0.9025093552315956),
}
EPS=1e-12

def lcg_values(seed):
    s=seed & 0xffffffff
    while True:
        s=(1664525*s+1013904223)&0xffffffff
        yield s/2**32

def fisher_lcg(n,seed):
    a=list(range(n)); g=lcg_values(seed)
    for i in range(n-1,0,-1):
        j=int(next(g)*(i+1)); a[i],a[j]=a[j],a[i]
    return np.array(a,int)

def dosage(gt,alleles):
    if gt in ('NN','N','') or '-' in gt: return np.nan
    a=alleles.split('/')
    if len(a)!=2 or len(a[0])!=1 or len(a[1])!=1 or len(gt)!=2: return np.nan
    if any(c not in a for c in gt): return np.nan
    return float((gt[0]==a[1])+(gt[1]==a[1]))

def load_source(path):
    lines=Path(path).read_text().strip().splitlines()
    h=lines[0].split('\t'); samples=h[11:]
    rows=[x.split('\t') for x in lines[1:]]
    return samples,rows

def locked_panels(samples,rows):
    perm=fisher_lcg(len(samples),13013); tr=perm[:30]
    panels={}
    for chrom in ('1','2','3','4'):
        sel=[]
        for f in rows:
            if f[2]!=chrom: continue
            vals=np.array([dosage(f[11+i],f[1]) for i in tr],float)
            ok=np.isfinite(vals)
            if ok.sum()<27: continue
            af=vals[ok].sum()/(2*ok.sum()); maf=min(af,1-af)
            if maf<.05: continue
            sel.append((f[0],f[1],int(f[3]),f))
            if len(sel)==38: break
        if len(sel)!=38: raise RuntimeError(f'chromosome {chrom}: {len(sel)} locked markers')
        panels[chrom]=sel
    return perm,panels

def matrix(rowsel,idx):
    return np.array([[dosage(f[11+i],al) for _,al,_,f in rowsel] for i in idx],float)

def impute_and_standardize(train,ref):
    mu=np.nanmean(train,0)
    T=np.where(np.isfinite(train),train,mu)
    R=np.where(np.isfinite(ref),ref,mu)
    sd=T.std(0); sd=np.where(sd<1e-8,1.,sd)
    return (T-mu)/sd,(R-mu)/sd

def operator(Z):
    inp=np.setdiff1d(np.arange(Z.shape[1]),TARGET)
    return Z[:,inp].T@Z[:,TARGET]/len(Z),inp

def independent_reliability(Ctr,Cref):
    _,_,Vt=np.linalg.svd(Ctr,full_matrices=False); V=Vt.T
    out=[]
    for k in range(len(TARGET)):
        a=Ctr@V[:,k]; b=Cref@V[:,k]
        out.append(np.clip(2*np.dot(a,b)/(np.dot(a,a)+np.dot(b,b)+EPS),0,1))
    return np.array(out),V

def exp013c_estimator(T,chrom,K=30,B=200):
    # T is already train-imputed standardized.
    C,inp=operator(T); _,_,Vt=np.linalg.svd(C,full_matrices=False); V=Vt.T
    pa=np.array([np.sum((C@V[:,k])**2) for k in range(9)])
    rng=np.random.default_rng(513000+int(chrom)*100); rels=[]; pns=[]
    for _ in range(K):
        p=rng.permutation(len(T)); a=p[:len(T)//2]; b=p[len(T)//2:]
        CA=T[a][:,inp].T@T[a][:,TARGET]/len(a); CB=T[b][:,inp].T@T[b][:,TARGET]/len(b)
        N=(CA-CB)/2
        pn=np.array([np.sum((N@V[:,k])**2) for k in range(9)])
        pns.append(pn); rels.append(np.clip(1-pn/(pa+EPS),0,1))
    rels=np.array(rels); mp=np.mean(pns,0)
    power=np.maximum(pa-mp,0)/(pa+EPS)
    rng=np.random.default_rng(713000+int(chrom)*100); Z=[]
    for _ in range(B):
        ids=rng.integers(0,len(T),len(T)); Cb=T[ids][:,inp].T@T[ids][:,TARGET]/len(T)
        Z.append(np.stack([Cb@V[:,k] for k in range(9)]))
    Z=np.array(Z); zbar=Z.mean(0); noise=np.mean(np.sum((Z-zbar)**2,2),0)
    sobs=np.sum(zbar*zbar,1); sdeb=np.maximum(sobs-noise/B,0); boot=sdeb/(sdeb+noise+EPS)
    return {'split_mean':rels.mean(0),'split_power_rel':power,'bootstrap':boot}

def clipcal(method,x):
    a,b=COEFF[method]; return np.clip(a+b*x,0,1)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--out',required=True)
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    samples,rows=load_source(args.source); perm,panels=locked_panels(samples,rows)
    train=perm[:30]; ref=perm[150:]
    D=[]
    for chrom,sel in panels.items():
        Tr=matrix(sel,train); Rf=matrix(sel,ref); T,R=impute_and_standardize(Tr,Rf)
        Ctr,_=operator(T); Crf,_=operator(R); hold,V=independent_reliability(Ctr,Crf)
        est=exp013c_estimator(T,chrom)
        for k in range(9):
            D.append({'task':f'maize_chr{chrom}','direction':k+1,'hold':hold[k],**{m:est[m][k] for m in est},**{m+'_cal':clipcal(m,est[m])[k] for m in est}})
    d=pd.DataFrame(D); d.to_csv(out/'EXP013C_reproduced_directions.csv',index=False)
    met=[]
    for m in ('split_mean','split_power_rel','bootstrap'):
        y=d.hold.to_numpy(); p=d[m+'_cal'].to_numpy(); x=d[m].to_numpy()
        met.append({'method':m,'direction_MAE':np.mean(abs(p-y)),'raw_spearman':spearmanr(x,y).statistic})
    pd.DataFrame(met).to_csv(out/'EXP013C_reproduced_metrics.csv',index=False)
    # EXP013D: the report/evidence records exact aggregate results and the LCG seeds/design.
    print(pd.DataFrame(met).to_string(index=False))

if __name__=='__main__': main()
