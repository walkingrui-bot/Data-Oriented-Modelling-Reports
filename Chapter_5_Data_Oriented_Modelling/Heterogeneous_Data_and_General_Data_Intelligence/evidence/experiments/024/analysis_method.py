#!/usr/bin/env python3
"""Core gap, state-matrix, spectral and continuity calculations for experiment 024.

Input: a local copy of email-Eu-core-temporal.txt with rows: SRC DST TS.
Source used for the archived experiment:
  official: https://snap.stanford.edu/data/email-Eu-core-temporal.html
  public mirror: SteveHuntsman/PathHomologyDataAndScripts/email-Eu-core-temporal.txt
  Git blob SHA: 6d864f3a7d511359c8fc19c6a83b4e2302741669

Core conventions:
1) detect the largest inter-event timestamp gap before temporal-window analysis;
2) use only COMPLETE, non-overlapping windows wholly inside the primary continuous segment;
3) node activity = total incident events (sent + received) per node per window;
4) relation activity = event count per DIRECTED dyad per window;
5) PCA is applied to sqrt(count), feature-centered matrices;
6) active-neighbour coverage uses undirected partners / long-run undirected static neighbours;
7) effective partners = inverse Herfindahl of event shares across a node's partners;
8) topology partition is a deterministic one-level modularity move used only as a structural probe.

The archived CSV files contain the recorded outputs. This script calculates the
gap, spectral summaries and consecutive-state cosines. Coverage, community and
bootstrap summaries are supplied as recorded results.
"""
from pathlib import Path
import sys, math
import numpy as np
import pandas as pd

DAY=86400.0

def load(path):
    df=pd.read_csv(path,sep=r'\s+',names=['src','dst','ts'],dtype={'src':int,'dst':int,'ts':np.int64})
    return df.sort_values('ts').reset_index(drop=True)

def largest_gap(df):
    ts=df.ts.to_numpy(); gaps=np.diff(ts); i=int(np.argmax(gaps))+1
    return {'after':int(ts[i-1]),'before':int(ts[i]),'gap':int(gaps[i-1])}

def full_primary_windows(df, days):
    g=largest_gap(df); t0=int(df.ts.iloc[0]); W=int(days*DAY)
    n=(g['after']-t0)//W
    limit=t0+n*W
    return df[df.ts < limit].copy(), int(n), t0, W

def state_matrices(df, days):
    x,n,t0,W=full_primary_windows(df,days)
    nodes=np.array(sorted(set(x.src)|set(x.dst))); ni={u:i for i,u in enumerate(nodes)}
    dys=list(dict.fromkeys(zip(x.src,x.dst))); di={e:i for i,e in enumerate(dys)}
    N=np.zeros((n,len(nodes)),float); D=np.zeros((n,len(dys)),float)
    for s,t,ts in x[['src','dst','ts']].itertuples(index=False,name=None):
        w=(int(ts)-t0)//W; N[w,ni[s]]+=1; N[w,ni[t]]+=1; D[w,di[(s,t)]]+=1
    return N,D

def spectral_summary(X):
    X=np.sqrt(X); X=X-X.mean(axis=0,keepdims=True)
    sv=np.linalg.svd(X,compute_uv=False); ev=sv*sv; p=ev/ev.sum()
    c=np.cumsum(p); r95=int(np.searchsorted(c,.95)+1)
    pr=float(1/(p*p).sum()); er=float(np.exp(-(p[p>0]*np.log(p[p>0])).sum()))
    return r95,pr,er,float(p[0])

def consecutive_cosines(X):
    X=np.sqrt(X); out=[]
    for a,b in zip(X[:-1],X[1:]): out.append(float(a@b/(np.linalg.norm(a)*np.linalg.norm(b))))
    return out

if __name__=='__main__':
    if len(sys.argv)<2:
        raise SystemExit('usage: analysis_method.py email-Eu-core-temporal.txt')
    df=load(sys.argv[1]); g=largest_gap(df)
    print('events',len(df),'nodes',len(set(df.src)|set(df.dst)))
    print('largest gap days',g['gap']/DAY,'after day',g['after']/DAY,'before day',g['before']/DAY)
    for days in [7,14,30,60,90]:
        N,D=state_matrices(df,days)
        print(days,'days node',spectral_summary(N),'dyad',spectral_summary(D),
              'cos',np.mean(consecutive_cosines(N)),np.mean(consecutive_cosines(D)))
