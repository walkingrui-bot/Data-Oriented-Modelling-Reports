#!/usr/bin/env python3
"""Reproduce HUMAN-EMG-REACHING-GEOMETRY-004 from the fixed public DataSet.csv.

Usage:
  python reproduce_004.py --csv DataSet.csv --out results

If --csv is omitted, the script downloads the exact fixed Git blob.
"""
from pathlib import Path
import argparse, io, urllib.request
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

BLOB='44fa933e7d164aa7279c545047d42d6ee6aae5c4'
URL=f'https://raw.githubusercontent.com/tianshi-yu/UpperLimbReachingData_HRL_Unimelb/{BLOB}/DataSet.csv'
POSE=['Sfe','Saa','Scpr','Scde','Tfe','Tb']
KIN=['dSfe','dSaa','dScpr','dScde','dTfe','dTb']
EMG_RMS=['BSH_RMS','BLH_RMS','TLAH_RMS','TLH_RMS','DA_RMS','DM_RMS','DP_RMS']
EMG_MAV=['BSH_MAV','BLH_MAV','TLAH_MAV','TLH_MAV','DA_MAV','DM_MAV','DP_MAV']

def pr(e):
    e=np.asarray(e,float); s=e.sum(); q=np.square(e).sum()
    return float(s*s/q) if q>0 else 0.0

def geom(X):
    X=np.asarray(X,float)
    C=np.cov(X,rowvar=False,ddof=1)
    lam=np.linalg.eigvalsh(C)[::-1]
    lam=np.maximum(lam,0)
    tr=lam.sum(); sq=np.square(lam).sum()
    cum=np.cumsum(lam)/tr
    return dict(stable=tr/lam[0], participation=tr*tr/sq,
                d90=int(np.searchsorted(cum,.90)+1),
                d95=int(np.searchsorted(cum,.95)+1),
                top3=lam[:3].sum()/tr, top4=lam[:4].sum()/tr)

def bootstrap_median(x, B=20000, seed=20260927):
    x=np.asarray(x,float); rng=np.random.default_rng(seed)
    vals=np.median(x[rng.integers(0,len(x),size=(B,len(x)))],axis=1)
    return np.quantile(vals,[.025,.975])

def main(csv_path,outdir):
    outdir=Path(outdir); outdir.mkdir(parents=True,exist_ok=True)
    if csv_path:
        df=pd.read_csv(csv_path)
    else:
        with urllib.request.urlopen(URL) as r: df=pd.read_csv(io.BytesIO(r.read()))
    assert len(df)==21096
    assert df.Subject.nunique()==10

    # subject-wide scales
    sd={}; rms={}; mu={}
    for s,g in df.groupby('Subject'):
        sd[s]=g[POSE+KIN+EMG_RMS+EMG_MAV].std(ddof=1).replace(0,1)
        mu[s]=g[KIN+EMG_RMS].mean()
        rms[s]=np.sqrt((g[POSE+KIN+EMG_RMS+EMG_MAV]**2).mean()).replace(0,1)

    trials=[]
    for (s,it),g in df.groupby(['Subject','Iteration'],sort=True):
        g=g.reset_index(drop=True); q=max(1,min(3,len(g)//4))
        delta=(g[POSE].tail(q).mean()-g[POSE].head(q).mean())/sd[s][POSE]
        endpoint=pr(np.square(delta))
        kin_energy=pr(((g[KIN]/rms[s][KIN])**2).mean())
        emg_rms=pr(((g[EMG_RMS]/rms[s][EMG_RMS])**2).mean())
        emg_mav=pr(((g[EMG_MAV]/rms[s][EMG_MAV])**2).mean())
        kg=geom((g[KIN]-mu[s][KIN])/sd[s][KIN])
        eg=geom((g[EMG_RMS]-mu[s][EMG_RMS])/sd[s][EMG_RMS])
        trials.append(dict(Subject=s,Iteration=it,Loc=int(g.Loc.iloc[0]),LocO=int(g.LocO.iloc[0]),
            target_row=int(g.LocO.iloc[0])//3,n=len(g),endpoint_breadth=endpoint,
            kin_energy_breadth=kin_energy,emg_rms_energy_breadth=emg_rms,
            emg_mav_energy_breadth=emg_mav,kin_stable=kg['stable'],emg_stable=eg['stable'],
            kin_d90=kg['d90'],kin_d95=kg['d95'],emg_d90=eg['d90'],emg_d95=eg['d95']))
    tr=pd.DataFrame(trials); tr.to_csv(outdir/'trial_level_results.csv',index=False)

    subs=[]
    for s,g in tr.groupby('Subject'):
        g=g.sort_values('endpoint_breadth'); n=len(g)
        low=g.iloc[:n//3]; high=g.iloc[(2*n+2)//3:]
        def rho(a,b): return float(spearmanr(g[a],g[b]).statistic)
        subs.append(dict(subject=s,
          rho_endpoint_kin=rho('endpoint_breadth','kin_energy_breadth'),
          rho_endpoint_emg=rho('endpoint_breadth','emg_rms_energy_breadth'),
          rho_endpoint_emg_mav=rho('endpoint_breadth','emg_mav_energy_breadth'),
          rho_kin_emg=rho('kin_energy_breadth','emg_rms_energy_breadth'),
          high_low_kin_energy=high.kin_energy_breadth.median()-low.kin_energy_breadth.median(),
          high_low_emg_rms=high.emg_rms_energy_breadth.median()-low.emg_rms_energy_breadth.median(),
          high_low_emg_mav=high.emg_mav_energy_breadth.median()-low.emg_mav_energy_breadth.median(),
          high_low_kin_stable=high.kin_stable.median()-low.kin_stable.median(),
          high_low_emg_stable=high.emg_stable.median()-low.emg_stable.median()))
    sub=pd.DataFrame(subs); sub.to_csv(outdir/'subject_level_results.csv',index=False)
    print('median rho endpoint→kin',sub.rho_endpoint_kin.median(),bootstrap_median(sub.rho_endpoint_kin))
    print('median high-low kin breadth',sub.high_low_kin_energy.median(),bootstrap_median(sub.high_low_kin_energy))
    print('median high-low kin stable',sub.high_low_kin_stable.median(),bootstrap_median(sub.high_low_kin_stable))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--csv'); ap.add_argument('--out',default='results')
    a=ap.parse_args(); main(a.csv,a.out)
