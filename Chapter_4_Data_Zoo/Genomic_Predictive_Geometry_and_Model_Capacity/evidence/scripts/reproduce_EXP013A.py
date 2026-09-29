from pathlib import Path
import json, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import argparse
ap=argparse.ArgumentParser()
ap.add_argument('--input-dir',required=True,help='Directory containing the EXP011 and EXP012 result CSVs')
ap.add_argument('--out',default='EXP013A_reproduced')
args=ap.parse_args()
BASE=Path(args.input_dir)
OUT=Path(args.out); OUT.mkdir(parents=True,exist_ok=True)

# Archived real-data results from EXP011/EXP012.
c = pd.read_csv(BASE/'EXP011C_stability_vs_nearoptimal_capacity.csv')
a = pd.read_csv(BASE/'EXP011A_chr21_operator_reliability_summary.csv')
b = pd.read_csv(BASE/'EXP011B_chr22_operator_reliability_summary.csv')
spec = pd.read_csv(BASE/'EXP011_mode_reliability_spectra.csv')
r012 = pd.read_csv(BASE/'EXP012_operator_reliability_runs.csv')
cap012 = pd.read_csv(BASE/'EXP012_capacity_curve.csv')

y = c['min_rank_within_0.005'].to_numpy(dtype=float)

# One archived per-direction spectrum exists for each of the 8 medium-n tasks.
rows = []
for (ds,w), g in spec.groupby(['dataset','window'], sort=False):
    rel = g.sort_values('mode')['reliability'].to_numpy(dtype=float)
    target = float(c[(c.dataset==ds)&(c.window==w)]['min_rank_within_0.005'].iloc[0])
    rows.append({
        'dataset': ds, 'window': w, 'nearopt_rank_005': target,
        'stable25': int((rel >= 0.25).sum()),
        'stable50': int((rel >= 0.50).sum()),
        'stable75': int((rel >= 0.75).sum()),
        'effective': float(rel.sum()),
        'sqrt_support': float(np.sqrt(rel).sum()),
        'power2_support': float((rel**2).sum()),
    })
medium = pd.DataFrame(rows)
medium.to_csv(OUT/'EXP013A_medium_task_features.csv', index=False)

# EXP012 uses four locked reliability runs (2 target grids x 2 partitions).
def features_from_rel(rel):
    rel=np.asarray(rel,float)
    return {
        'stable25': int((rel>=0.25).sum()),
        'stable50': int((rel>=0.50).sum()),
        'stable75': int((rel>=0.75).sum()),
        'effective': float(rel.sum()),
        'sqrt_support': float(np.sqrt(rel).sum()),
        'power2_support': float((rel**2).sum()),
    }
run_rows=[]
for (target_set, seed), g in r012.groupby(['target_set','partition_seed'], sort=False):
    d=features_from_rel(g.sort_values('direction')['reliability'].to_numpy())
    d.update({'target_set': int(target_set), 'partition_seed': int(seed)})
    run_rows.append(d)
small_runs=pd.DataFrame(run_rows)
small_runs.to_csv(OUT/'EXP013A_exp012_repeated_split_features.csv', index=False)
small_mean=small_runs[['stable25','stable50','stable75','effective','sqrt_support','power2_support']].mean()
true_small_rank=int(cap012.loc[cap012.val_R2 >= cap012.val_R2.max()-0.005,'rank'].min())

# Scale-only calibration. Scale is fit on 8 medium tasks; LOO estimates generalization error there.
def loo_scale(x, y):
    x=np.asarray(x,float); y=np.asarray(y,float)
    preds=[]
    for i in range(len(y)):
        mask=np.arange(len(y))!=i
        xt=x[mask]; yt=y[mask]
        scale=float((xt@yt)/(xt@xt)) if float(xt@xt)>0 else 0.0
        preds.append(scale*x[i])
    scale_all=float((x@y)/(x@x)) if float(x@x)>0 else 0.0
    preds=np.asarray(preds)
    return scale_all, float(np.mean(np.abs(preds-y))), preds

cal_rows=[]
for feature in ['stable25','stable50','stable75','effective','sqrt_support','power2_support']:
    scale, mae, preds = loo_scale(medium[feature].to_numpy(), medium.nearopt_rank_005.to_numpy())
    pred_small=float(scale*small_mean[feature])
    cal_rows.append({
        'estimator': feature,
        'medium_LOO_MAE_rank': mae,
        'scale_fit_all_8': scale,
        'EXP012_feature_mean': float(small_mean[feature]),
        'EXP012_predicted_rank_continuous': pred_small,
        'EXP012_predicted_rank_rounded': int(np.clip(np.rint(pred_small),1,9)),
        'EXP012_actual_nearopt_rank_005': true_small_rank,
        'EXP012_abs_rank_error_rounded': abs(int(np.clip(np.rint(pred_small),1,9))-true_small_rank),
    })
cal=pd.DataFrame(cal_rows)

# Exploratory threshold sweep on medium tasks only. EXP012 never selects tau.
sweep=[]
for tau in np.round(np.arange(0.05,0.801,0.01),2):
    vals=[]
    for (ds,w), g in spec.groupby(['dataset','window'], sort=False):
        vals.append(int((g['reliability'].to_numpy(dtype=float) >= tau).sum()))
    vals=np.asarray(vals,float)
    scale,mae,_=loo_scale(vals,y)
    # Same tau applied to each locked EXP012 run, then averaged.
    small_counts=[]
    for _,g in r012.groupby(['target_set','partition_seed'], sort=False):
        small_counts.append(int((g['reliability'].to_numpy(dtype=float)>=tau).sum()))
    small_feature=float(np.mean(small_counts))
    pred=float(scale*small_feature)
    sweep.append({
        'tau': float(tau), 'medium_LOO_MAE_rank': mae, 'scale_fit_all_8': scale,
        'EXP012_mean_count': small_feature, 'EXP012_predicted_rank_continuous': pred,
        'EXP012_predicted_rank_rounded': int(np.clip(np.rint(pred),1,9)),
        'EXP012_actual_nearopt_rank_005': true_small_rank,
    })
sweep=pd.DataFrame(sweep)
sweep.to_csv(OUT/'EXP013A_threshold_sweep_medium_only.csv', index=False)
best=sweep.loc[sweep.medium_LOO_MAE_rank.idxmin()].copy()
cal=pd.concat([cal, pd.DataFrame([{
    'estimator': f"threshold_sweep_tau_{best.tau:.2f}",
    'medium_LOO_MAE_rank': float(best.medium_LOO_MAE_rank),
    'scale_fit_all_8': float(best.scale_fit_all_8),
    'EXP012_feature_mean': float(best.EXP012_mean_count),
    'EXP012_predicted_rank_continuous': float(best.EXP012_predicted_rank_continuous),
    'EXP012_predicted_rank_rounded': int(best.EXP012_predicted_rank_rounded),
    'EXP012_actual_nearopt_rank_005': true_small_rank,
    'EXP012_abs_rank_error_rounded': abs(int(best.EXP012_predicted_rank_rounded)-true_small_rank),
}])], ignore_index=True)
cal.to_csv(OUT/'EXP013A_estimator_calibration.csv', index=False)

# Split-instability diagnostic from archived repeated splits.
inst=[]
for _,r in a.iterrows():
    vals=np.array([r.effective_split1,r.effective_split2],float)
    inst.append({'group':'EXP011_chr21_medium','task':f"chr21_{int(r.window_start)}",
                 'train_n':1505,'half_n':752.5,'effective_1':vals[0],'effective_2':vals[1],
                 'relative_split_gap':float(abs(vals[0]-vals[1])/vals.mean())})
for target_set,g in small_runs.groupby('target_set'):
    vals=g.sort_values('partition_seed')['effective'].to_numpy(dtype=float)
    inst.append({'group':'EXP012_small','task':f"target_set_{int(target_set)}",
                 'train_n':30,'half_n':15,'effective_1':vals[0],'effective_2':vals[1],
                 'relative_split_gap':float(abs(vals[0]-vals[1])/vals.mean())})
inst=pd.DataFrame(inst)
inst.to_csv(OUT/'EXP013A_split_instability.csv', index=False)
medium_gap_mean=float(inst[inst.group=='EXP011_chr21_medium'].relative_split_gap.mean())
medium_gap_max=float(inst[inst.group=='EXP011_chr21_medium'].relative_split_gap.max())
small_gap_mean=float(inst[inst.group=='EXP012_small'].relative_split_gap.mean())
small_gap_min=float(inst[inst.group=='EXP012_small'].relative_split_gap.min())

# Figures: separate charts, default matplotlib colors/styles.
fig,ax=plt.subplots(figsize=(8.0,4.8))
plotcal=cal.sort_values('EXP012_predicted_rank_continuous')
ax.barh(plotcal['estimator'], plotcal['EXP012_predicted_rank_continuous'])
ax.axvline(true_small_rank, linestyle='--', linewidth=1.5)
ax.set_xlabel('Predicted near-optimal rank on EXP012')
ax.set_ylabel('Estimator calibrated on EXP011 medium-n tasks')
ax.set_title('EXP013A: medium-n calibration does not rescue the small-n rank')
fig.tight_layout()
fig.savefig(OUT/'fig19_exp013a_estimator_predictions.png', dpi=180)
plt.close(fig)

fig,ax=plt.subplots(figsize=(7.6,4.6))
labels=inst['task'].tolist()
x=np.arange(len(labels))
ax.bar(x, inst['relative_split_gap']*100)
ax.set_xticks(x, labels, rotation=30, ha='right')
ax.set_ylabel('Effective-support split gap (%)')
ax.set_title('EXP013A: split instability separates medium-n from the 30-person stress test')
fig.tight_layout()
fig.savefig(OUT/'fig20_exp013a_split_instability.png', dpi=180)
plt.close(fig)

summary={
    'experiment':'SMALL-N-RELIABILITY-CALIBRATION-013A',
    'status':'post-hoc estimator calibration using archived real-data operator outputs; not a blind validation',
    'calibration_tasks':'8 real medium-n chr21/chr22 tasks from EXP011',
    'stress_task':'EXP012 real 50-sample 1000 Genomes task; train n=30; revealed near-optimal rank=5',
    'best_medium_threshold_tau':float(best.tau),
    'best_medium_threshold_LOO_MAE_rank':float(best.medium_LOO_MAE_rank),
    'best_medium_threshold_EXP012_prediction_continuous':float(best.EXP012_predicted_rank_continuous),
    'best_medium_threshold_EXP012_prediction_rounded':int(best.EXP012_predicted_rank_rounded),
    'best_fixed_soft_EXP012_prediction':{
        'estimator':'sqrt_support',
        'continuous':float(cal.loc[cal.estimator=='sqrt_support','EXP012_predicted_rank_continuous'].iloc[0]),
        'rounded':int(cal.loc[cal.estimator=='sqrt_support','EXP012_predicted_rank_rounded'].iloc[0]),
        'medium_LOO_MAE_rank':float(cal.loc[cal.estimator=='sqrt_support','medium_LOO_MAE_rank'].iloc[0])
    },
    'EXP012_actual_nearopt_rank_005':true_small_rank,
    'medium_chr21_relative_split_gap_mean':medium_gap_mean,
    'medium_chr21_relative_split_gap_max':medium_gap_max,
    'EXP012_relative_split_gap_mean':small_gap_mean,
    'EXP012_relative_split_gap_min':small_gap_min,
    'split_gap_mean_ratio_small_over_medium':small_gap_mean/medium_gap_mean,
    'finding':'Re-thresholding or scalar soft transforms of archived reliability spectra do not recover the small-n near-optimal rank. Repeated-split effective support is far less stable in EXP012, providing a direct resolution-warning observable.',
}
with open(OUT/'EXP013A_summary.json','w') as f: json.dump(summary,f,indent=2)

# Compact markdown record for evidence package.
with open(OUT/'EXP013A_PROTOCOL_AND_RESULTS.md','w') as f:
    f.write('# SMALL-N-RELIABILITY-CALIBRATION-013A\n\n')
    f.write('This is a post-hoc calibration/diagnostic experiment using archived real-data outputs from EXP011 and EXP012. No synthetic dataset is used. EXP012 capacity outcomes were already revealed before this experiment, so they are used only as a stress target, not as blind validation.\n\n')
    f.write('Calibration: six fixed scalar summaries plus an exploratory hard-threshold sweep are fit only on the eight medium-n EXP011 tasks using scale-only regression and leave-one-task-out MAE. The chosen threshold is then applied unchanged to the four locked EXP012 reliability runs.\n\n')
    f.write('Resolution diagnostic: repeated-split relative gap = |E1-E2| / mean(E1,E2), where E is continuous effective support. Four chr21 tasks provide two archived split estimates; EXP012 provides two partitions for each of two target grids.\n\n')
    f.write(json.dumps(summary, indent=2))

print(json.dumps(summary,indent=2))
print('\nCalibration table:\n',cal.to_string(index=False))
print('\nInstability table:\n',inst.to_string(index=False))
