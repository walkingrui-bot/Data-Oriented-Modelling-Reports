"""Recompute published Phase 2 summaries from retained CSVs; standard library only.

This validates arithmetic and recorded relationships, not model retraining.
Bootstrap intervals are retained results, not resampled without source trajectories.
"""
from pathlib import Path
import csv,json,statistics,math
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'evidence/phase2'
def rows(path):
    with (BASE/path).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def close(a,b,tol=1e-6):
    if abs(a-b)>tol:raise AssertionError((a,b,tol))
def jaccard(a,b,c,d):
    x=set(range(int(a),int(b)+1));y=set(range(int(c),int(d)+1));return len(x&y)/len(x|y)
checks={}
# Round 1 uses macro means over independent training seeds; subset sizes differ.
r=rows('G1_generative_control/02_metric_comparison_correct_examples.csv')
means={k:statistics.mean(float(x[k]) for x in r) for k in r[0] if k not in ['seed','n_correct_examples']}
close(means['exact_future_influence_top1'],.905915,1e-6)
checks['GCM1_correct_subset_seed_macro_means']=means
r=rows('G2_future_instruments/02_metric_top1_by_seed.csv')
metric_map={'Train-selected raw attention':'raw_attention','Attention × future-gradient':'attention_futuregrad','Future gradient norm':'future_grad_norm','Directional future gradient':'directional_future_grad','3-point integrated directional future gradient':'integrated_directional_future_grad','Batched future-margin counterfactual':'batched_future_margin','Exact future causal influence (FCI)':'exact_fci'}
for m in rows('G2_future_instruments/01_metric_benchmark.csv'):
    v=statistics.mean(float(x[metric_map[m['metric']]]) for x in r);close(v,float(m['top1_relevant_history']))
checks['GCM2_seed_means']={'independent_models':len(r),'heldout_per_model':64,'all_exact_fci':all(float(x['exact_fci'])==1 for x in r)}
hard=rows('M0_content_mirror/results.csv');key='80轮后平均|p-0.5|'
v=[float(x[key]) for x in hard]
checks['hard_mirror_relative_reductions']={'versus_self':1-v[2]/v[0],'versus_neutral':1-v[2]/v[1]}
close(checks['hard_mirror_relative_reductions']['versus_self'],.9231184,1e-6)
mgc={x['condition']:x for x in rows('M1_state_mirror/01_long_run_summary.csv')}
checks['state_mirror_relative_reductions']={k:1-float(mgc['learned_mirror'][k])/float(mgc['free'][k]) for k in ['late_TV','late_KL']}
# The frequency scan retains all 72 trajectory means, permitting an actual aggregation check.
traj=rows('M2_dynamic_mirror/05_frequency_seed_level.csv');freq=rows('M2_dynamic_mirror/02_correction_frequency_stats.csv')
agg={}
for row in freq:
    vals=[float(x['late_tv']) for x in traj if x['condition']==row['condition']]
    assert len(vals)==12
    v=statistics.mean(vals);close(v,float(row['late_tv_mean']),1e-7);agg[row['condition']]=v
checks['frequency_scan_trajectory_means']=agg
dose=rows('V1_mechanism_tests/04_TMC_dose_matched_cadence.csv');active=[x for x in dose if x['condition']!='free']
for x in active:
    close(float(x['lambda_at_correction'])/float(x['interval_tokens']),.025,1e-12)
range_means=max(float(x['late_TV_mean']) for x in active)-min(float(x['late_TV_mean']) for x in active)
paired=rows('V1_mechanism_tests/05_TMC_dose_matched_paired_test.csv')[0]
close(range_means,float(paired['max_range_of_interval_means']),1e-7)
diff=float(active[0]['late_TV_mean'])-float(active[-1]['late_TV_mean']);close(diff,float(paired['mean_late_TV_difference']),1e-7)
checks['matched_dose']={'nominal_lambda_per_token':.025,'range_of_means_recomputed':range_means,'every1_minus_every16_from_rounded_means':diff,'bootstrap_CI_retained':[float(paired['bootstrap_95_lo']),float(paired['bootstrap_95_hi'])]}
neighborhood=rows('B1_causal_balance/04_balance_band_neighborhood.csv')
for x in neighborhood:close(jaccard(x['true_band_start'],x['true_band_end'],x['GCM_band_start'],x['GCM_band_end']),float(x['band_jaccard']),1e-12)
checks['balance_neighborhood']={'worlds':len(neighborhood),'mean_jaccard':statistics.mean(float(x['band_jaccard']) for x in neighborhood),'median_jaccard':statistics.median(float(x['band_jaccard']) for x in neighborhood)}
bands=rows('V1_mechanism_tests/07_balance_band_with_residual_gate.csv')
for x in bands:close(jaccard(x['near_opt_start'],x['near_opt_end'],x['extended_band_start'],x['extended_band_end']),float(x['extended_band_jaccard']),1e-12)
noise=next(x for x in bands if x['world']=='pure_noise')
checks['residual_band']={'pure_noise_jaccard':float(noise['extended_band_jaccard']),'bad_timepoints_called_balance':float(noise['fraction_bad_timepoints_still_called_balance'])}
result={'status':'passed','check_groups':len(checks),'model_training_rerun':False,'bootstrap_resampled':False,'checks':checks}
(ROOT/'audit/phase2_verification.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
