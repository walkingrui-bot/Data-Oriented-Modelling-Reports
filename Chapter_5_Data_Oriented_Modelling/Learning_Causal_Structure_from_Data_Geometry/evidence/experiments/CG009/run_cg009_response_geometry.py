"""CG-009 response-geometry analysis.

Expected files in the same directory (public Sachs data):
  GroundTruth.csv
  cd3cd28.csv
  cd3cd28_g0076.csv
  cd3cd28_u0126.csv
  pma.csv
  b2camp.csv
  cd3cd28_aktinhib.csv
  cd3cd28_ly.csv

The script computes robust log-scale location, scale and shape response components,
within-intervention response ranks, descendant-vs-nondescendant AUCs and a
permutation test. It intentionally separates matched-background inhibitors from
alternate activator routes.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
BASE = pd.read_csv(ROOT / "cd3cd28.csv")
GT = pd.read_csv(ROOT / "GroundTruth.csv")
VARS = list(BASE.columns)
IDX = {v:i for i,v in enumerate(VARS)}
ADJ = {v:[] for v in VARS}
for a,b in GT[["from","to"]].itertuples(index=False):
    ADJ[a].append(b)

def distances(targets):
    d={v:np.inf for v in VARS}; q=[]
    for t in targets: d[t]=0; q.append(t)
    for u in q:
        for v in ADJ[u]:
            if d[v] > d[u]+1:
                d[v]=d[u]+1; q.append(v)
    return d

def q(x,p): return np.quantile(x,p)
def med(x): return float(np.median(x))
def iqr(x): return float(q(x,.75)-q(x,.25))

def response_components(a,b):
    a=np.log(np.maximum(np.asarray(a,float),1e-6)); b=np.log(np.maximum(np.asarray(b,float),1e-6))
    scale=max(.2,(iqr(a)+iqr(b))/2/1.349)
    loc=abs((med(b)-med(a))/scale)
    scl=abs(np.log((iqr(b)+1e-6)/(iqr(a)+1e-6)))
    ps=np.array([.05,.1,.2,.3,.4,.5,.6,.7,.8,.9,.95])
    qa=(np.quantile(a,ps)-med(a))/max(iqr(a),1e-6)
    qb=(np.quantile(b,ps)-med(b))/max(iqr(b),1e-6)
    shape=float(np.sqrt(np.mean((qb-qa)**2)))
    return dict(location=loc,scale=scl,shape=shape,total=float(np.sqrt(loc*loc+scl*scl+shape*shape)))

def ranks(x):
    return pd.Series(x).rank(method="average").to_numpy()/len(x)

def auc(pos,neg):
    pos=np.asarray(pos); neg=np.asarray(neg)
    return float(np.mean([(p>n)+.5*(p==n) for p in pos for n in neg]))

spec=[
    ("cd3cd28_g0076.csv", ["PKC"], "matched inhibitor"),
    ("cd3cd28_u0126.csv", ["Mek","Erk"], "matched inhibitor"),
    ("pma.csv", ["PKC"], "alternate activator"),
    ("b2camp.csv", ["PKA"], "alternate activator"),
]
rows=[]
for fn,targets,kind in spec:
    env=pd.read_csv(ROOT/fn); d=distances(targets)
    comps=[response_components(BASE[v],env[v]) for v in VARS]
    for key in ["location","scale","shape","total"]:
        rr=ranks([c[key] for c in comps])
        for v,r in zip(VARS,rr):
            rows.append(dict(condition=fn,target="+".join(targets),kind=kind,node=v,component=key,rank=r,
                             descendant=np.isfinite(d[v]) and d[v]>0,direct_child=d[v]==1,nondescendant=not np.isfinite(d[v])))
R=pd.DataFrame(rows)
out=[]
for key,g in R.groupby("component"):
    out.append(dict(component=key,
                    descendant_auc=auc(g[g.descendant]["rank"],g[g.nondescendant]["rank"]),
                    child_auc=auc(g[g.direct_child]["rank"],g[g.nondescendant]["rank"])))
pd.DataFrame(out).to_csv(ROOT/"cg009_recomputed_component_auc.csv",index=False)
print(pd.DataFrame(out).sort_values("component"))
