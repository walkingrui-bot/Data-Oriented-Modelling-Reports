#!/usr/bin/env python3
"""Recompute INTOX-GAIT-GEO-004 and INTOX-GAIT-ROBUST-005 from the report 4×6 matrix.

The public matrix is rounded to three decimals. Consequently, values derived from this
file can differ slightly from report values obtained from the higher-precision working
matrix. Report-recorded values are stored separately in this evidence package.
"""
from pathlib import Path
import argparse, numpy as np, pandas as pd

def load_matrix(path):
    df=pd.read_csv(path)
    labels=df.iloc[:,0].tolist(); feats=list(df.columns[1:]); X=df.iloc[:,1:].to_numpy(float)
    return labels,feats,X

def svd_metrics(X):
    s=np.linalg.svd(X,compute_uv=False); e=s*s; total=e.sum()
    return dict(pc1_energy= e[0]/total, top2_energy=e[:2].sum()/total,
                stable_rank=total/e[0], participation_rank=total*total/np.sum(e*e))

def feature_jackknife(X,feats):
    out=[]
    for j,f in enumerate(feats):
        d=svd_metrics(np.delete(X,j,axis=1)); d['omitted_feature']=f; out.append(d)
    return pd.DataFrame(out)

def subgroup_jackknife(X,labels):
    out=[]
    for i,l in enumerate(labels):
        d=svd_metrics(np.delete(X,i,axis=0)); d['omitted_subgroup']=l; out.append(d)
    return pd.DataFrame(out)

def controls(X):
    row=X/np.linalg.norm(X,axis=1,keepdims=True)
    rms=np.sqrt(np.mean(X*X,axis=0)); col=X/np.where(rms==0,1,rms)
    sign=np.sign(X)
    out=[]
    for name,A in [('base',X),('row_unit',row),('column_rms_equalized',col),('sign_only',sign)]:
        d=svd_metrics(A); d['construction']=name; out.append(d)
    return pd.DataFrame(out)

def hadamard(X):
    H=np.array([[1,1,1,1],[1,-1,1,-1],[1,1,-1,-1],[1,-1,-1,1]],float)/2
    C=H@X; e=np.sum(C*C,axis=1); names=['shared','sex','direction','sex_x_direction']
    return pd.DataFrame({'component':names,'energy_fraction':e/e.sum()})

def permutation_null(X,n=200000,seed=20260927):
    rng=np.random.default_rng(seed); obs=svd_metrics(X)['pc1_energy']; obs_sh=4*np.sum(X.mean(0)**2)/np.sum(X*X)
    pc=np.empty(n); sh=np.empty(n); chunk=10000
    for k in range(0,n,chunk):
        m=min(chunk,n-k)
        perm=np.argsort(rng.random((m,*X.shape)),axis=2)
        A=np.take_along_axis(np.broadcast_to(X,(m,*X.shape)),perm,axis=2)
        G=A@np.swapaxes(A,1,2); eig=np.linalg.eigvalsh(G)[:,::-1]
        pc[k:k+m]=eig[:,0]/eig.sum(1)
        mu=A.mean(1); sh[k:k+m]=4*np.sum(mu*mu,axis=1)/np.sum(A*A,axis=(1,2))
    return pd.DataFrame([
        {'test':'pc1','observed':obs,'null_mean':pc.mean(),'q95':np.quantile(pc,.95),'empirical_p':(np.sum(pc>=obs)+1)/(n+1)},
        {'test':'shared_factor','observed':obs_sh,'null_mean':sh.mean(),'q95':np.quantile(sh,.95),'empirical_p':(np.sum(sh>=obs_sh)+1)/(n+1)},
    ]),pd.DataFrame({'pc1_energy':pc,'shared_factor':sh})

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('matrix'); ap.add_argument('--outdir',default='gait_recompute'); ap.add_argument('--nperm',type=int,default=200000); ap.add_argument('--seed',type=int,default=20260927)
    a=ap.parse_args(); out=Path(a.outdir); out.mkdir(exist_ok=True)
    labels,feats,X=load_matrix(a.matrix)
    pd.DataFrame([svd_metrics(X)]).to_csv(out/'base_svd.csv',index=False)
    feature_jackknife(X,feats).to_csv(out/'feature_jackknife.csv',index=False)
    subgroup_jackknife(X,labels).to_csv(out/'subgroup_jackknife.csv',index=False)
    controls(X).to_csv(out/'scaling_controls.csv',index=False)
    hadamard(X).to_csv(out/'hadamard_factorization.csv',index=False)
    summ,null=permutation_null(X,a.nperm,a.seed); summ.to_csv(out/'permutation_summary.csv',index=False); null.to_csv(out/'permutation_null.csv',index=False)

if __name__=='__main__': main()
