from pathlib import Path
import json, re, math, csv
import pandas as pd

ROOT=Path(__file__).resolve().parent.parent
E=ROOT/'evidence/experiments'
import os
OUT=Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'verification_results')))
OUT.mkdir(parents=True,exist_ok=True)
TABLES={x['number']:x for x in json.loads((ROOT/'evidence/report_tables/TABLES.json').read_text())}
CHECKS=[]
SOURCES={}

def data(exp,file):
    return pd.read_csv(E/exp/file)

def row(df,**keys):
    for k,v in keys.items(): df=df[df[k]==v]
    assert len(df)==1, (keys,len(df))
    return df.iloc[0]

def val(s):
    s=str(s).replace('−','-').replace(',','').strip()
    m=re.fullmatch(r'[≈~]?\s*([+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?)\s*(%|ms|h|d|°)?',s)
    if not m:return None
    n=m[1]; exp=int(n.lower().split('e')[1]) if 'e' in n.lower() else 0
    mant=n.lower().split('e')[0]; dec=len(mant.split('.')[1]) if '.' in mant else 0
    return float(n),0.500001*10**(exp-dec)

def check(t,r,c,value,source,detail=''):
    text=TABLES[t]['rows'][r][c]
    parsed=val(text)
    assert parsed is not None,(t,r,c,text)
    n,tol=parsed
    passed=abs(n-value)<=tol+1e-12
    CHECKS.append(dict(table=t,row=r+1,column=c+1,row_label=TABLES[t]['rows'][r][0],column_label=TABLES[t]['rows'][0][c],reported=text,evidence_value=float(value),absolute_difference=abs(n-value),rounding_tolerance=tol,status='matched' if passed else 'review',source=source,calculation=detail))
    SOURCES.setdefault(t,set()).add(source)

def sequential(t, exp, file, columns, keys=None, aliases=None, scales=None, frame=None):
    df=data(exp,file) if frame is None else frame
    src=f'{exp}/{file}'
    scales=scales or {};aliases=aliases or {}
    for i,r in enumerate(TABLES[t]['rows'][1:],1):
        if keys:
            filt={k:aliases.get((c,r[c]),r[c]) for c,k in keys.items()}
            s=row(df,**filt)
        else:s=df.iloc[i-1]
        for c,k in columns.items():
            mul=scales.get(c,1)
            check(t,i,c,s[k]*mul,src,f'{k}'+(f' × {mul}' if mul!=1 else ''))

# Chemical signal study, including its theoretical uniform-ranking baseline.
df=data('001','zero_shot_postprefix_summary.csv')
mods=['Transformer-structure','GRU-structure-contrastive','Markov-last-signal','GRU-shuffled-chemistry']
actual=df['model'].tolist()
for i,needle in enumerate(['Transformer','contrastive','Markov','shuffled'],1):
    model=next(x for x in actual if needle.lower() in x.lower())
    s=row(df,model=model)
    for c,k,m in [(1,'top1',100),(2,'top5',100),(3,'mean_rank',1)]:check(8,i,c,s[k]*m,'001/zero_shot_postprefix_summary.csv',f'{model}; {k} × {m}')
check(8,5,1,100/60,'001/experiment_spec.json','uniform ranking; 1 / 60 × 100')
check(8,5,2,500/60,'001/experiment_spec.json','uniform ranking; 5 / 60 × 100')
df=data('001','latent_communication_state_probe.csv')
df=df[df.model.str.contains('GRU',case=False)]
for i in range(1,7):
    s=row(df,prefix_signals=i-1); check(9,i,1,s.mean_R2,'001/latent_communication_state_probe.csv','GRU mean_R2')
sequential(9,'001','GRU_state_control_geometry.csv',{0:'prefix_signals',2:'state_d95',3:'next_signal_control_stable_rank_mean'})

# Homogeneous and heterogeneous dynamics.
j=json.loads((E/'002/summary.json').read_text())['homogeneous']
for i,key in enumerate(['direct','generated_rule','moe'],1):
    check(15,i,1,j[key+'_one_step'],'002/summary.json',key+'_one_step')
    check(15,i,2,j[key+'_rollout8'],'002/summary.json',key+'_rollout8')
df=data('002','matched_budget_models.csv').groupby('model',as_index=False).mean(numeric_only=True)
sequential(16,'002','matched_budget_models.csv',{1:'params',2:'one_step',3:'rollout4',4:'rollout8'},keys={0:'model'},frame=df)
for i,k in enumerate(['uniform_penalty_pct','shuffle_penalty_pct'],1):check(17,i,1,data('002','router_ablation.csv')[k].mean(),'002/router_ablation.csv',f'mean over seeds: {k}')

# Data geometry, routing, sharing and drift.
sequential(20,'003','condition_summary.csv',{3:'state_d95',4:'memory_gain',5:'moe_gain_rollout_pct'},scales={4:100})
df=data('003','router_summary.csv');df=df[df.law_count==4]
sequential(21,'003','router_summary.csv',{1:'router_law_NMI',2:'router_entropy',3:'uniform_penalty_pct',4:'shuffle_penalty_pct'},frame=df)
sequential(22,'003','capacity_followup_summary.csv',{0:'latent_dim',2:'params',3:'one_step_mse',4:'rollout_mse'},keys={0:'latent_dim',1:'model'},aliases={(0,'3'):3,(0,'14'):14})
sequential(27,'004','condition_comparison.csv',{1:'observed_d95',2:'median_curvature_index',3:'median_local_condition',4:'rollout_last_MSE_MonoBlock',5:'rollout_last_MSE_StateMoE',6:'MoE_gain_pct_rollout_last_MSE'},keys={0:'condition'})
sequential(28,'004','capacity_oracle_comparison_with_baseline.csv',{2:'rollout_last_MSE',3:'gain_vs_mono_pct'},keys={0:'condition',1:'model'})
sequential(29,'005','condition_comparison.csv',{1:'obs_rank_single_frame',2:'obs_rank_4frame_gramian',3:'one_step_MSE_SingleFrame',4:'one_step_MSE_RecurrentMono',5:'history_gain_one_step_pct',6:'rollout_last_MSE_RecurrentMono',7:'rollout_last_MSE_RecurrentMoE',8:'moe_gain_rollout_pct'},keys={0:'condition'})
df=data('006','fair_capacity_summary.csv')
for i,r in enumerate(TABLES[30]['rows'][1:],1):
    cond='X_'+r[0].replace('+','_')
    for c,m in enumerate(['MonoFull','HardSplitFull','SoftMoEFull','SharedResidualFull'],1):check(30,i,c,row(df,condition=cond,model=m).test_MSE,'006/fair_capacity_summary.csv',f'{cond}; {m}; test_MSE')
    for c,m,k in [(1,'HardSplitFull','boundary_MSE'),(2,'SoftMoEFull','boundary_MSE'),(3,'HardSplitFull','jump'),(4,'SoftMoEFull','jump')]:check(31,i,c,row(df,condition=cond,model=m)[k],'006/fair_capacity_summary.csv',f'{cond}; {m}; {k}')
aliases={(0,s):'X_'+s.replace('+','_') for s in ['broad+dense','broad+sparse','sharp+dense','sharp+sparse']}
sequential(32,'006','training_compatibility_summary.csv',{1:'self_update_gain',2:'adjacent_transfer_gain',3:'far_transfer_gain',4:'negative_transfer_fraction',5:'weakest_adjacent_mutual_transfer'},keys={0:'condition'},aliases=aliases,scales={4:100})
sequential(33,'006','contrast_compatibility_scan.csv',{0:'contrast',1:'adjacent_transfer',2:'far_transfer',3:'negative_fraction',4:'mono_MSE',5:'softMoE_MSE',6:'soft_gain_pct'},scales={3:100})
sequential(35,'007','partition_recovery.csv',{1:'ARI_oracle',2:'NMI_oracle'},keys={0:'partition'})
for t in [36,37]:sequential(t,'007','all_partition_performance_combined.csv',{1:'test_MSE',2:'boundary_MSE',3:'nonboundary_MSE'},keys={0:'partition'})
sequential(38,'008','drift_summary.csv',{0:'era',1:'functional_rule_drift',2:'expert_map_migration',3:'Mono',4:'RefreshedMap',5:'StaleMap',6:'stale_penalty_vs_refreshed_pct'})
sequential(39,'008','strict_routing_intervention_summary.csv',{0:'era',1:'fresh_route_MSE',2:'stale_route_same_experts_MSE',3:'strict_stale_route_penalty_pct',4:'functional_rule_drift',5:'expert_map_migration'})
j=json.loads((E/'009/geometry_audit.json').read_text())
for i,k in enumerate(['current_frame_family_accuracy','two_frame_transition_family_accuracy','normalized_covariance_difference','current_mean_difference'],1):check(40,i,1,j[k],'009/geometry_audit.json',k)
sequential(41,'009','model_summary_with_unsupervised_routing.csv',{1:'params',2:'one_step_MSE',3:'rollout3_MSE',4:'rollout_last_MSE'},keys={0:'model'})

# Carriers, events and measurement policy.
df=data('010','model_summary.csv')
for i,r in enumerate(TABLES[42]['rows'][1:],1):
    cond=r[0]
    for c,m in enumerate(['Snapshot','GlobalGRU','CompartmentGRU','SourceTracker'],1):check(42,i,c,row(df,condition=cond,model=m).rollout_last_MSE,'010/model_summary.csv',f'{cond}; {m}; rollout_last_MSE')
    check(42,i,5,df[df.condition==cond].latent_probe_R2.max(),'010/model_summary.csv',f'{cond}; max latent_probe_R2 over architectures')
    v=data('010','slot_specialization.csv'); check(42,i,6,v[v.condition==cond].matched_slot_source_R2.mean(),'010/slot_specialization.csv',f'{cond}; mean matched_slot_source_R2 over seeds')
sequential(43,'010','sparse_anchor_supervision_summary.csv',{1:'main_h1_MSE',2:'matched_slot_source_R2',3:'future_anchor_MSE'})
df=data('011','replicated_summary.csv'); conds=df.condition.tolist()
alias={(0,'Regular'):next(x for x in conds if 'irregular' not in x.lower()),(0,'Irregular'):next(x for x in conds if 'irregular' in x.lower())}
sequential(44,'011','replicated_summary.csv',{2:'full_MSE',3:'event_MSE',4:'latent_probe_R2'},keys={0:'condition',1:'model'},aliases=alias)
sequential(45,'011','replicated_summary.csv',{2:'birth_MSE',3:'branch_MSE',4:'death_MSE',5:'merge_MSE'},keys={0:'condition',1:'model'},aliases=alias)
df=data('012','model_summary_with_clocked_graph.csv')
sequential(46,'012','model_summary_with_clocked_graph.csv',{2:'full_MSE',3:'event_MSE',4:'latent_probe_R2'},keys={1:'model'},frame=df[df.sampling=='Regular'])
sequential(47,'012','model_summary_with_clocked_graph.csv',{1:'full_MSE',2:'event_MSE',3:'latent_probe_R2'},keys={0:'model'},frame=df[df.sampling=='Irregular'])
df=data('013','model_summary.csv')
alias={(0,'Moderate'):next(x for x in df.condition if 'moderate' in x.lower()),(0,'Severe'):next(x for x in df.condition if 'severe' in x.lower()),(1,'NoTime EventGRU'):'EventGRU_NoTime',(1,'Timed EventGRU'):'EventGRU_Time',(1,'CTGraph'):'CTGraphResidual'}
sequential(48,'013','model_summary.csv',{2:'MSE_all',3:'MSE_cross_lifecycle',4:'MSE_no_lifecycle',5:'latent_probe_R2'},keys={0:'condition',1:'model'},aliases=alias)
sequential(49,'013','sampling_density_scan_summary.csv',{1:'observed_fraction',2:'MSE_all_BucketGRU',3:'MSE_all_EventGRU_NoTime',4:'MSE_all_EventGRU_Time',5:'TimedEvent_gain_vs_Bucket_pct',6:'TimedEvent_lifecycle_gain_vs_Bucket_pct'},keys={0:'sampling'})
sequential(50,'013','timing_identifiability_summary.csv',{0:'NoTime_MSE',1:'Timed_MSE',2:'Timed_gain_pct'})
sequential(51,'014','policy_audit.csv',{1:'observed_fraction',2:'obsrate_severity_corr'},keys={0:'policy'})
alias={(0,'MultiPolicy'):'MultiPolicy_MaskDelta',(0,'PermutedMaskAug'):'PermutedMaskAug_MaskDelta',(0,'RepeatedA'):'RepeatedA_MaskDelta'}
df=data('014','robustness_comparison.csv')
if 'MultiPolicy' in df.model.tolist():alias={}
sequential(52,'014','robustness_comparison.csv',{1:'A_MSE',2:'B_MSE',3:'C_MSE'},keys={0:'model'},aliases=alias)
sequential(53,'014','robustness_comparison.csv',{1:'A_MSE',2:'B_MSE',3:'C_MSE',4:'mean_shifted_MSE'},keys={0:'model'},aliases=alias)
sequential(54,'014','counterfactual_policy_summary.csv',{2:'counterfactual_prediction_disagreement'},keys={0:'model',1:'policy_pair'})

# Module coordination, resource state and architecture comparisons.
sequential(55,'015','lesion_summary_with_training_ablation.csv',{1:'params',2:'normal_MSE',3:'single_lesion_mean_MSE',4:'single_lesion_penalty_pct',5:'dual_lesion_mean_MSE',6:'dual_lesion_penalty_pct'},keys={0:'model'})
sequential(56,'015','perturbation_training_effects.csv',{2:'normal_MSE_change_pct',3:'single_lesion_penalty_reduction_pctpoints',4:'dual_lesion_penalty_reduction_pctpoints'},keys={0:'base_model'})
sequential(57,'015','coordination_geometry.csv',{1:'expert_output_cosine_mean',2:'mean_max_router_weight',3:'mean_router_entropy'},keys={0:'model'})
sequential(58,'015','router_recovery_summary_corrected.csv',{1:'before_MSE',2:'after_router_adaptation_MSE',3:'router_adaptation_change_pct'},keys={0:'model'})
df=data('016','scenario_summary.csv')
for i,r in enumerate(TABLES[59]['rows'][1:],1):
    for c,sc in enumerate(['healthy','chronic_fatigue','weak_effector','outages'],1):check(59,i,c,row(df,model=r[0],scenario=sc).MSE_mean,'016/scenario_summary.csv',f'{r[0]}; {sc}; MSE_mean')
sequential(60,'016','current_availability_sufficiency.csv',{1:'FatigueAware_NoCurriculum_MSE',2:'CoordinatedBody_MSE',3:'curriculum_gain_pct'},keys={0:'scenario'})
alias={(1,'1'):1,(1,'2'):2}
sequential(61,'016','substitution_audit_summary.csv',{1:'failed_effector',2:'paired_substitute',3:'desired_weight_change_substitute',4:'realized_load_change_substitute'},keys={0:'model',1:'failed_effector'},aliases=alias)
sequential(62,'017','summary.csv',{1:'params',2:'MSE_mean',3:'MSE_early',4:'MSE_late',5:'MSE_worst',6:'final_availability',7:'final_hidden_wear'},keys={0:'model'})
sequential(63,'017','wear_distribution_summary.csv',{1:'mean_max_hidden_wear',2:'late_max_hidden_wear',3:'mean_cross_effector_wear_std',4:'fraction_effector_time_q_gt_0_34',5:'fraction_effector_time_q_gt_0_38',6:'mean_router_entropy'},keys={0:'model'})
sequential(64,'017','hidden_wear_probe_summary.csv',{1:'hidden_wear_R2_from_history_state',2:'hidden_wear_R2_from_current_availability'},keys={0:'model'})
sequential(65,'017','matched_history_probe_summary.csv',{1:'final_weight_eff0_after_heavy_history',2:'final_weight_eff0_after_balanced_history',3:'history_avoidance_eff0',4:'final_distribution_L1_change'},keys={0:'model'})
sequential(66,'018B','scenario_summary.csv',{2:'MSE_mean',3:'MSE_late'},keys={0:'model',1:'scenario'})
df=data('018B','scenario_summary.csv')
for i,r in enumerate(TABLES[66]['rows'][1:],1):
    if r[4]!='-':check(66,i,4,row(df,model=r[0],scenario=r[1]).final_availability,'018B/scenario_summary.csv','final_availability')
sequential(67,'018B','effector_necessity.csv',{1:'shared_only_MSE'},keys={0:'model'})
sequential(68,'018B','redistribution.csv',{1:'failed_weight_change',2:'nonfailed_weight_gain',3:'failed_realized_load_change'},keys={0:'model'})
sequential(69,'019','gain_normalization_comparison.csv',{1:'DenseWorld_MSE',2:'NormHealthy',3:'NormLesion',4:'NormFatigue',5:'Norm_vs_Dense_gain_pct',6:'NormLesion_degradation_pct',7:'NormFatigue_degradation_pct'},keys={0:'world'})
sequential(70,'019','normalized_redistribution.csv',{1:'failed_weight_change',2:'nonfailed_weight_gain',3:'failed_realized_load_change'},keys={0:'world'})
df=data('020','replicated_summary.csv');sc=data('020','replicated_scorecard.csv')
for i,r in enumerate(TABLES[71]['rows'][1:],1):
    w=r[0]
    for c,m in [(1,'Dense'),(2,'Baseline'),(3,'Dual')]:check(71,i,c,row(df,world=w,model=m,scenario='healthy').MSE,'020/replicated_summary.csv',f'{w}; {m}; healthy MSE')
    for c,k in [(4,'vs_dense_pct'),(5,'lesion_deg_pct')]:check(71,i,c,row(sc,world=w,model='Dual')[k],'020/replicated_scorecard.csv',f'{w}; Dual; {k}')
sequential(73,'021','cross_source_scorecard.csv',{1:'Dense_metric',2:'Body_healthy_metric',3:'Body_lesion_metric',4:'Body_vs_Dense_gain_pct',5:'Lesion_degradation_pct'},keys={0:'source'})
sequential(74,'021','graph_adapter_repair_summary.csv',{2:'rollout_metric',3:'late_metric'},keys={0:'model',1:'scenario'})
sequential(75,'021','graph_long_training_summary.csv',{2:'rollout_metric',3:'late_metric'},keys={0:'model',1:'scenario'})
for i,r in enumerate(TABLES[76]['rows'][1:],1):
    file='graph_long_training_audit.csv' if r[0]=='graph' else 'final_cross_source_scorecard.csv'
    d=data('021',file); ss=d.iloc[0] if r[0]=='graph' else row(d,source=r[0])
    for c,k in [(1,'Body_vs_Dense_gain_pct'),(2,'Lesion_degradation_pct')]:check(76,i,c,ss[k],'021/'+file,k)


# Empirical graph summaries and frozen-corpus coordination.
sequential(77,'022','real_graph_geometry_metrics.csv',{1:'lcc_nodes',2:'avg_distance_lcc',3:'B2_fraction_lcc',4:'B4_fraction_lcc',5:'norm_laplacian_lambda2_lcc'},keys={0:'dataset'},scales={3:100,4:100})
sequential(78,'022','real_graph_geometry_metrics.csv',{1:'degree_mean',2:'degree_cv',3:'degree_gini',4:'degree_assortativity',5:'clustering_sample'},keys={0:'dataset'})
df=data('023','facebook_attribute_summary.csv').iloc[0]
for i,prefix in [(1,'edge'),(2,'random_nonedge')]:
    for c,k,mul in [(1,prefix+'_feature_cosine',1),(2,prefix+'_feature_jaccard',1),(3,prefix+'_shared_circle_fraction',100)]:check(79,i,c,df[k]*mul,'023/facebook_attribute_summary.csv',f'{k} × {mul}')
ks=['repeated_event_fraction','events_per_unique_dyad','dyad_event_count_gini','top10pct_dyads_event_share','top1pct_dyads_event_share','sender_burstiness_median','dyad_burstiness_median','repeat_dyad_gap_median_hours','consecutive_30d_edge_jaccard_mean','prior_window_edge_retention_mean','current_window_new_edge_fraction_mean']
df=data('023','email_temporal_summary.csv').iloc[0]
for i,k in enumerate(ks,1):check(80,i,1,df[k]*(100 if '%' in TABLES[80]['rows'][i][1] else 1),'023/email_temporal_summary.csv',k)
df=data('023','bitcoin_edge_attribute_summary.csv').iloc[0]
for i,suffix in enumerate(['absolute_rating_mean','edge_common_neighbors_mean','edge_common_neighbors_median','endpoint_degree_geomean'],1):
    for c,prefix in [(1,'positive'),(2,'negative')]:
        k=prefix+'_'+suffix;check(81,i,c,df[k],'023/bitcoin_edge_attribute_summary.csv',k)
sequential(82,'024','active_neighbour_scale.csv',{0:'window_days',1:'n_windows',2:'median_coverage',3:'median_active_partners',4:'median_effective_partners',5:'median_effective_static_coverage'},scales={2:100,5:100})
sequential(83,'024','temporal_state_geometry.csv',{0:'window_days',1:'node_consecutive_cosine',2:'dyad_consecutive_cosine',3:'node_r95',4:'dyad_r95',5:'node_entropy_effective_rank',6:'dyad_entropy_effective_rank'})
sequential(84,'024','degree_strata_30d.csv',{1:'nodes',2:'median_coverage',3:'active_next_window_fraction',4:'median_partner_retention'},scales={2:100,3:100})
sequential(85,'024','community_activity_30d.csv',{1:'active_dyads',2:'mean_events_per_active_dyad',3:'median_lifetime_days',4:'mean_jaccard',5:'mean_retention'})
sequential(86,'025','rg025_multiscale_renormalization.csv',{0:'window_days',1:'median_coverage',2:'median_effective_static_coverage',3:'median_active_partners',4:'median_effective_partners',5:'node_consecutive_cosine',6:'dyad_consecutive_cosine',7:'retention',8:'new_edge_fraction'},scales={1:100,2:100,7:100,8:100})
j=json.loads((E/'026/do026_summary_final.json').read_text())
for i,s in enumerate(j['partition_16'],1):
    for c,k,m in [(1,'byte_load_cv',1),(2,'max_byte_share',100),(3,'semantic_knn_edge_cut',100)]:check(87,i,c,s[k]*m,'026/do026_summary_final.json',f'partition_16; {s["policy"]}; {k} × {m}')
df=data('026','do026_compact_router.csv');df=df[(df.shards==16)&(df.prototypes_per_shard==4)]
sequential(88,'026','do026_compact_router.csv',{1:'mean_scored_fraction',2:'mean_recall_at5',3:'exact_top5_set_rate'},frame=df,scales={1:100,2:100,3:100})
df=data('026','do026_process_benchmark.csv')
for i,m in [(1,'centralized'),(2,'distributed_broadcast')]:
    s=row(df,mode=m,batch_size=256)
    for c,k in [(1,'workers'),(2,'batch_size'),(3,'qps')]:check(89,i,c,s[k],'026/do026_process_benchmark.csv',f'{m}; batch_size=256; {k}')
df=data('026','do026_routed_process_benchmark.csv')
for i,k in enumerate(['routed_top2','routed_top4','routed_top8'],3):
    s=row(df,mode=k)
    for c,jj in [(1,'workers'),(3,'qps')]:check(89,i,c,s[jj],'026/do026_routed_process_benchmark.csv',f'{k}; {jj}')
aliases={(0,'No replica'):'none',(0,'Hot 25%'):'hot25',(0,'Boundary 25%'):'boundary25',(0,'One backup/object'):'full1'}
sequential(90,'027','do027_failure_policy_summary.csv',{1:'storage_overhead_ratio',2:'mean_recall',3:'worst_recall',4:'mean_routed4_recall'},keys={0:'replication'},aliases=aliases,scales={1:100,2:100,3:100,4:100})
aliases.update({(1,'Wait all 8'):'barrier',(1,'Continue at 7/8'):'quorum7'})
sequential(91,'027','do027_straggler_timeout.csv',{2:'median_wall_s',3:'mean_recall_at5',4:'mean_exact_top5'},keys={0:'replication',1:'mode'},aliases=aliases,scales={2:1000,3:100,4:100})
aliases={(0,'Naive shared RMW'):'naive_rmw',(0,'One global lock'):'global_lock',(0,'Ownership-scoped shard locks'):'shard_locks'}
sequential(92,'027','do027_update_summary.csv',{1:'median_updates_per_s',2:'mean_lost_fraction',3:'mean_error_objects'},keys={0:'mode'},aliases=aliases,scales={2:100})
sequential(94,'028','do028_policy_summary.csv',{1:'accepted_rate',2:'mean_recall_at5',3:'internal_state_error_fraction',4:'reference_oracle_error_fraction',5:'final_exact_object_fraction_vs_reference'},scales={1:100,3:100,4:100,5:100})

(OUT/'numeric_reconciliation.json').write_text(json.dumps(CHECKS,indent=2))
(OUT/'table_evidence_sources.json').write_text(json.dumps({str(k):sorted(v) for k,v in SOURCES.items()},indent=2))
print(json.dumps({'checks':len(CHECKS),'tables':len(SOURCES),'matched':sum(x['status']=='matched' for x in CHECKS),'review':[x for x in CHECKS if x['status']!='matched']},indent=2))
