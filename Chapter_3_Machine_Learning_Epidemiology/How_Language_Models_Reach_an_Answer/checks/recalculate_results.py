"""Recalculate published numerical claims from included authored/derived tables.

Run from any directory: python checks/recalculate_results.py
Uses Python, NumPy and pandas. Reads local files only; no model calls or downloads.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RESULTS = []

def frame(unit, filename):
    return pd.read_csv(ROOT / 'evidence/experiments' / unit / filename)

def summary(unit, filename='summary.json'):
    return json.loads((ROOT/'evidence/experiments'/unit/filename).read_text())

def check(name, actual, expected, tolerance=1e-10):
    a=np.asarray(actual,dtype=float); e=np.asarray(expected,dtype=float)
    ok=a.shape==e.shape and np.allclose(a,e,rtol=0,atol=tolerance,equal_nan=True)
    diff=float(np.nanmax(np.abs(a-e))) if a.size and a.shape==e.shape else None
    RESULTS.append({'check':name,'passed':bool(ok),'max_absolute_difference':diff,'tolerance':tolerance})

def grouped(unit, rawfile, sumfile, keys, metrics):
    r=frame(unit,rawfile).groupby(keys,dropna=False)[metrics].mean().sort_index()
    s=frame(unit,sumfile).set_index(keys)[metrics].sort_index()
    common=r.index.intersection(s.index)
    check(f'{unit}: {rawfile} grouping coverage',len(common),len(s),0)
    check(f'{unit}: {sumfile} from run-level means',r.loc[common].values,s.loc[common].values)

def main():
    d=frame('021','dimension_performance.csv').set_index('d')
    check('021: held-out JS at D=3,10,16,24',d.loc[[3,10,16,24],'js_affine_bits'],[.4095,.3643,.3431,.3266],.00005)
    check('021: D=24 MSE reduction',1-d.loc[24,'mse_affine']/d.loc[24,'mse_reset'],.1458,.00005)
    m=frame('021','movement_spectrum_lowD.csv').set_index('D')
    check('021: D=10 movement spectrum',m.loc[10,['stable_rank','top3','d95']],[3.009,.6103,9],[.0005,.00005,0])
    r=frame('021','multistep_rollout.csv').query('d == 24').set_index('horizon')
    check('021: observed-action rollout JS',r.loc[[1,4,8],'js_bits'],[.3239,.3052,.2971],.00005)

    p=summary('022','pooled_summary.json'); d=frame('022','model_summary.csv')
    check('022: pooled states',d.states.sum(),545,0)
    for c in ['acc_language','acc_observation','acc_agent','nll_language','nll_observation','nll_agent','alpha','beta','actual_prob_gain']:
        check('022: state-weighted '+c,np.average(d[c],weights=d.states),p[c])
    d=frame('022','surface_form_summary.csv')
    check('022: surface-state denominator',d.states.sum(),423,0)
    for c in ['frame_action_only','frame_action_plus_obs','length_action_only','length_action_plus_obs']:
        check('022: surface weighted '+c,np.average(d[c],weights=d.states),p[c])

    s=summary('023')
    check('023: action consistency percentage-point gain',100*(s['generated_action_consistency_controlled']-s['generated_action_consistency_free']),38.71,.005)
    check('023: relative grounding gain',s['generated_grounding_fraction_controlled']/s['generated_grounding_fraction_free']-1,.352,.0005)
    s=summary('024')
    check('024: slot NLL reduction',1-s['refined_slot_nll']/s['broad_slot_nll'],s['slot_nll_reduction'])
    check('024: full NLL gap',s['refined_oracle_action_full_nll']-s['free_full_nll'],s['remaining_full_nll_gap'])
    d=frame('024','per_task_refined.csv');check('024: task wins',(d.delta_nll<0).sum(),5,0)
    s=summary('025');d=frame('025','object_source_anatomy.csv')
    check('025: retrieved mentions by source',d.rementioned_objects.sum(),164,0)
    check('025: retrievable fraction',164/203,s['retrievable_fraction'])
    d=frame('025','end_to_end_per_task.csv')
    check('025: held-out states',d.states.sum(),124,0)
    check('025: end-to-end task wins',(d.end_to_end_delta<0).sum(),9,0)
    check('025: end-to-end NLL improvement',s['free_full_nll']-s['end_to_end_nll'],s['end_to_end_improvement_nats'])

    s=summary('026A');d=frame('026A','reversal_symmetrization.csv')
    check('026A: reverse-pair mean displacement',d.reversal_midpoint_distance.mean(),s['reversal_midpoint_mean_distance'])
    check('026A: reversal reduction',1-d.reversal_midpoint_distance.mean()/d.raw_pair_mean_distance.mean(),s['reversal_reduction_fraction'])
    d=frame('026A','eta_regime_map.csv').set_index('eta')
    # eta_regime_map.csv reports this fraction to six decimal places.
    check('026A: main pair-order energy',d.loc[.002,'pairwise_field_energy_fraction'],s['pairwise_order_energy_fraction'],5e-7)
    d=frame('026B','raw_curriculum_runs.csv');s=frame('026B','curriculum_summary_by_eta.csv').set_index('eta')
    check('026B: qualified foundations',d.seed.nunique(),17,0)
    for eta,row in s.iterrows():
        q=d[d.eta==eta]
        block=q[q.microsteps==1].endpoint_accuracy.mean()
        micro=q[q.microsteps==16].endpoint_accuracy.mean()
        coupled=q[q.method=='COUPLED32'].endpoint_accuracy.mean()
        check(f'026B: endpoint means eta={eta}',[block,micro,coupled],row[['block_endpoint','micro16_endpoint','coupled_endpoint']])
        check(f'026B: order-penalty recovery eta={eta}',(micro-block)/(coupled-block),row.endpoint_order_penalty_recovered)

    grouped('026C','stability_100_microsteps.csv','stability_100_microsteps_summary.csv',['eta','mode'],['B_loss_gain','protected_survival','endpoint_accuracy','delta_ready_frac'])
    s=summary('026C','final_summary.json');d=frame('026C','protected_gradient_mechanism.csv')
    for c,k in [('n_protected','n_protected_prefixes_mean'),('protected_gradient_rank','protected_gradient_rank_mean'),('threatened_fraction','threatened_fraction_raw_B_update'),('first_order_B_learning_retained','first_order_B_learning_retained')]:
        check('026C: mechanism '+c,d[c].mean(),s[k])
    grouped('026D','confirm_raw.csv','confirm_summary.csv',['eta','method'],['B_loss_gain','survival','holes','endpoint_accuracy','delta_ready_frac'])
    d=frame('026D','protected_gradient_spectrum.csv');check('026D: stable rank mean',d.stable_rank.mean(),1.232,.0005)
    a=frame('026D','risk_span2_anchor_anatomy.csv');check('026D: anchor count',len(a),34,0)
    for level in ['002','005']:
        grouped('026E',f'intervention_eta{level}_raw.csv',f'intervention_eta{level}_summary.csv',['eta','method'],['B_loss_gain','survival','holes','endpoint_accuracy','delta_ready_frac'])
    d=frame('026E','proxy_selection_summary.csv').set_index('method')
    check('026E: two-step gradient energy',d.loc['resp2_span','grad_energy'],.882,.0005)
    for f,n in [('all_static_loss_summary.csv',29),('primal_dual_summary.csv',6)]:
        d=frame('026F',f);gate=(d.survival>=.99)&(d.endpoint_accuracy>=.98)&(d.B_loss_gain>0)
        check('026F: '+f+' settings',len(d),n,0);check('026F: '+f+' gate passes',gate.sum(),0,0)
    for pre in ['eta002','eta005','eta010_stress','eta020_stress']:
        grouped('026G',pre+'_raw.csv',pre+'_summary.csv',['eta','method'],['B_loss_gain','survival','holes','endpoint_accuracy','delta_ready_frac'])
    d=frame('026G','eta005_summary.csv').set_index('method')
    check('026G: rank-two/all-prefix learning ratio',d.loc['anchor_rank2','B_loss_gain']/d.loc['exact_all','B_loss_gain'],2.02,.005)

    d=frame('027A','risk_edges.csv');s=summary('027A')
    check('027A: candidate edges',len(d),2040,0);check('027A: pooled exit fraction',d.exit_bad.mean(),s['overall_risky_edge_rate'])
    d=frame('027A','canonical_edge_bypass.csv');bad=d[d.canonical_exit_bad==1]
    check('027A: canonical transitions and exits',[len(d),len(bad)],[352,125],0)
    check('027A: bypass opportunities',bad.has_safe_alternative.sum(),15,0)
    d=frame('027B','next_safe_region_recovery.csv');s=summary('027B')
    for c,k in [('canonical_returns','canonical_eventual_return_rate'),('recoverable_exact1','active_recovery_within_1'),('probe_recoverable_3','active_recovery_within_3'),('greedy_recovers_3','greedy_recovery_within_3')]:
        check('027B: '+c,d[c].mean(),s[k])
    check('027B: unrecoverable cases',(d.probe_recoverable_3==0).sum(),2,0)
    d=frame('027C','reset_all_canonical_exits.csv').groupby('variant').correct.mean()
    check('027C: reset success',d.loc[['prompt_restart','last_pair_projection','commitment_projection','last_safe_rollback']],[.864,.872,.952,1])
    d=frame('027C','level3_true_escalations.csv').groupby('variant').robust_1step.mean()
    check('027C: true escalation robustness',d.loc[['prompt_restart','commitment_projection']],[.7,0])
    d=frame('027D','heldout_prompt_rescue.csv');g=d[d.policy=='generic']
    check('027D: blind repeat success',g.groupby('repeat').correct.mean(),[52/60,10/60,49/60,4/60,58/60])
    pivot=g.pivot(index=['seed','question','exit_depth'],columns='repeat',values='correct')
    check('027D: 10101 patterns',(pivot.apply(lambda r:''.join(map(str,r.astype(int))),axis=1)=='10101').sum(),48,0)
    check('027D: mean correctness flips',np.abs(np.diff(pivot.values,axis=1)).sum(axis=1).mean(),3.6)
    d=frame('027D','heldout_stop_on_first_recovery.csv')
    check('027D: first recovery counts',[(d.prompts_used==1).sum(),((d.prompts_used==2)&(d.recovered==1)).sum(),(d.recovered==0).sum()],[52,6,2],0)
    check('027D: gated cap-two attempts',np.minimum(d.prompts_used,2).mean(),68/60)
    d=frame('027E','027E_router_event_assignments.csv')
    check('027E: route counts',d.router_level.value_counts().reindex(['L1','L2','L3','L4'],fill_value=0),[15,108,2,0],0)
    check('027E: routed recovery',d.router_success.sum(),125,0)
    h=d[d.split_027D=='heldout'];check('027E: held-out success',[len(h),h.router_success.sum()],[60,60],0)
    check('027E: held-out routes',h.router_level.value_counts().reindex(['L1','L2','L3','L4'],fill_value=0),[6,54,0,0],0)
    check('027E: routed L2 mean actions',d[d.router_level=='L2'].greedy_return_steps.mean(),112/108)

    d=frame('028A','028A_real_trajectory_routing_by_task.csv')
    check('028A: candidate totals',d[['strong','k2','k4','k8','external_new']].sum(),[300,131,142,178,300],0)
    check('028A: phase totals',d[['pre_edit','post_edit_unverified','post_edit_validated','test_failed']].sum(),[112,113,75,0],0)
    check('028A: external scope increment',d.external_L3_fallback_needed.sum(),122,0)
    check('028A: premature Submit lower bound',np.maximum(d.progress_class_S-d.post_edit_validated,0).sum(),76,0)
    s=ROOT/'evidence/supporting'
    d=pd.read_csv(s/'ASTIG_013A/astig013a_cooldown_sweep.csv').set_index('cooldown_h')
    check('ASTIG-013A: cooldown counts',d.loc[[1,2,4,8],'intercepted'],[141,250,291,293],0)
    check('ASTIG-013A: gated control interventions',d.gated_submitted_blocks.sum(),0,0)
    d=pd.read_csv(s/'ASTIG_013C/astig013c_successful_phase_calibration.csv')
    check('ASTIG-013C: calibration trajectories',len(d),20,0)
    check('ASTIG-013C: edit/verification/formal-test counts',d[['has_edit_before_submit','post_edit_validation_before_submit','post_edit_test_before_submit']].sum(),[20,20,12],0)

    output={'scope':'Numerical recalculation of included tables; no training, provider-data retrieval or live agent execution.',
            'checks':len(RESULTS),'passed':sum(r['passed'] for r in RESULTS),'results':RESULTS}
    out=ROOT/'checks/recalculation_results.json';out.write_text(json.dumps(output,indent=2))
    print(json.dumps({'checks':output['checks'],'passed':output['passed'],'failed':[r for r in RESULTS if not r['passed']]}))
    return 0 if output['checks']==output['passed'] else 1

if __name__=='__main__':
    raise SystemExit(main())
