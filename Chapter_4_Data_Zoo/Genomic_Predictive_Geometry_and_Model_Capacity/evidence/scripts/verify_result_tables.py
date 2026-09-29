"""Verify released derived results without downloading provider observations.

Usage: python verify_result_tables.py [path/to/evidence]
Requires numpy, pandas, scipy. Writes numerical_verification.json under --out.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ap=argparse.ArgumentParser()
ap.add_argument('evidence',nargs='?',default=str(Path(__file__).resolve().parents[1]))
ap.add_argument('--out',default='numerical_verification.json')
a=ap.parse_args();root=Path(a.evidence)
files={p.name:p for p in root.rglob('*.csv')}
checks=[]
def read(name):return pd.read_csv(files[name])
def check(name,actual,expected,atol=1e-8):
    actual=float(actual);expected=float(expected)
    ok=bool(np.isclose(actual,expected,atol=atol,rtol=0))
    checks.append({'check':name,'actual':actual,'expected':expected,'absolute_tolerance':atol,'pass':ok})
    if not ok:raise AssertionError(checks[-1])

for name,N in [('EXP002_capacity_scan_960snp.csv',960),('EXP004_fixedN_window_vs_spread.csv',240)]:
    d=read(name);r=d['rank'] if 'rank' in d else d.best_rank;v=d['map_dof'] if 'map_dof' in d else d.best_dof
    check(name+' mapping DOF maximum error',np.max(abs(v-r*(N-r))),0)
for name in ['EXP003A_scale_scan_variable_targets.csv','EXP003B_scale_scan_fixed24_targets.csv']:
    d=read(name);check(name+' mapping DOF maximum error',np.max(abs(d.best_dof-d.best_rank*(d.snps-d.best_rank))),0)
d=read('EXP005_predictive_spectrum.csv');check('EXP005 r90 correlation',d.r90.corr(d.best_rank),.873,5e-4)
d=read('EXP006B_19window_capacity_rule.csv')
check('EXP006 LOO exact',sum(d.best_rank==d.loocv_pred_rank),18)
check('EXP006 block exact',sum(d.best_rank==d.blocked_pred_rank),15)
check('EXP006 label combinations',math.comb(19,8),75582)
check('EXP006 exact LOO p',3/math.comb(19,8),3.9691990156386444e-5)
check('EXP006 exact block p',576/math.comb(19,8),.0076208621100261964)
d=read('EXP007_chr22_external_blind_transfer.csv')
check('EXP007 rank MAE',np.mean(abs(d.selected_rank-d.predicted_rank)),16)
check('EXP007 mean test regret',d.test_regret.mean(),.0113,5e-5)
d=read('EXP008_sample_support_matched_downsample.csv')
check('EXP008 changed windows',sum(d.best_rank_n1505!=d.best_rank_n657),16)
check('EXP008 mean rank shift',np.mean(d.best_rank_n657-d.best_rank_n1505),-8)
d=read('EXP010_matched_support_posthoc.csv')
check('EXP010 original MAE',d.original_abs_error.mean(),16)
check('EXP010 matched MAE',d.matched_abs_error.mean(),8)
d=read('EXP011C_stability_vs_nearoptimal_capacity.csv');ratio=d['min_rank_within_0.005']/d.stable50_mean_two_splits
check('EXP011 pooled stability correlation',d.stable50_mean_two_splits.corr(d['min_rank_within_0.005']),.929,5e-4)
check('EXP011 ratio mean',ratio.mean(),1.2908524555153091)
check('EXP011 ratio min',ratio.min(),.9411764705882353)
check('EXP011 ratio max',ratio.max(),1.6)
d=read('EXP011E_shuffle_controls.csv')
for col,v in [('true_stable50',28.25),('within_superpop_stable50',4.25),('global_stable50',1.5)]:check('EXP011 '+col,d[col].mean(),v)
d=read('EXP012_capacity_curve.csv')
near=d.loc[d.val_R2>=d.val_R2.max()-.005,'rank'].min();check('EXP012 near-optimal rank',near,5)
check('EXP012 best validation rank',d.loc[d.val_R2.idxmax(),'rank'],5)

d=read('EXP013B_direction_records.csv') if 'EXP013B_direction_records.csv' in files else None
if d is None:
    name=next(n for n,p in files.items() if n.startswith('EXP013B') and 'holdout_reliability' in pd.read_csv(p,nrows=0).columns and 'split_one' in pd.read_csv(p,nrows=0).columns)
    d=read(name)
summary=read('EXP013B_estimator_comparison.csv')
predname=next(n for n,p in files.items() if n.startswith('EXP013B') and 'predicted_reliability' in pd.read_csv(p,nrows=0).columns)
pred=read(predname)
for _,s in summary.iterrows():
    m=s['method'];g=pred[pred.method==m]
    check('EXP013B '+m+' raw Spearman',spearmanr(d[m],d.holdout_reliability).statistic,s.spearman_raw)
    check('EXP013B '+m+' calibrated MAE',np.mean(abs(g.predicted_reliability-g.holdout_reliability)),s.direction_MAE_calibrated)
    counts=g.groupby(['outer_split','target_grid']).apply(lambda v:abs(sum(v.predicted_reliability>=.5)-sum(v.holdout_reliability>=.5)),include_groups=False)
    check('EXP013B '+m+' count MAE',counts.mean(),s.stable_count_MAE)
d=read('EXP013C_direction_blind_results.csv');s=read('EXP013C_estimator_blind_metrics.csv')
for _,row in s.iterrows():
    m=row['method'];check('EXP013C '+m+' MAE',np.mean(abs(d[m+'_cal']-d.reference_reliability)),row.direction_MAE,2e-8)
    check('EXP013C '+m+' ordering',spearmanr(d[m+'_raw'],d.reference_reliability).statistic,row.raw_spearman,2e-8)
d=read('EXP015B_same_gene_correlations_92.csv');x=d.same_gene_rna_protein_correlation
check('EXP015B symbols',len(x),92)
check('EXP015B mean same-gene correlation',x.mean(),.3958801811,1e-9)
check('EXP015B median same-gene correlation',x.median(),.3806424474,1e-9)
check('EXP015B positive fraction',(x>0).mean(),.9239130435,1e-9)
report={'scope':'Checks of released derived outputs; no provider observations downloaded and no original model fitting rerun.','checks':checks,'all_pass':all(x['pass'] for x in checks)}
Path(a.out).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'all_pass':report['all_pass']}))
