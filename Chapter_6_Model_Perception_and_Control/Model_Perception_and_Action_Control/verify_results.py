"""Check published derived measurements without downloading raw data or running models."""
from pathlib import Path
from collections import Counter
import csv, json, math, statistics, hashlib
P=Path(__file__).resolve().parent
E=P/'evidence'
def rows(path):return list(csv.DictReader((E/path).open()))
def close(a,b,tol=1e-10):assert math.isclose(float(a),float(b),abs_tol=tol,rel_tol=tol),(a,b)
checks=[]
baseline=rows('MODE_CONTROL/RUN1_baseline_metrics.csv')
assert len(baseline)==140
assert Counter((r['variant'],r['generated_mode']) for r in baseline)=={('ACT','ACT'):70,('TEXT','ACT'):59,('TEXT','TEXT'):11}
pairs={}
for r in baseline:pairs.setdefault(r['pair_id'],{})[r['variant']]=r
assert len(pairs)==70 and all(set(v)=={'TEXT','ACT'} for v in pairs.values())
shifts=[float(v['ACT']['M_ref_mean'])-float(v['TEXT']['M_ref_mean']) for v in pairs.values()]
assert sum(x>0 for x in shifts)==60
close(statistics.mean(shifts),.574,tol=.0005)
checks.append('140 baseline prompts, 70 paired records, first-action counts and paired reference-margin shift')
sweep=rows('ASTIG_012B/astig012b_qwen_parameter_sweep.csv')
assert len(sweep)==12 and all(float(r['local_corrected'])>float(r['raw']) and float(r['strong_local_corrected'])>float(r['strong_raw']) for r in sweep)
checks.append('12 independent-decoder configurations retain the reported direction')
a=rows('ASTIG_013A/astig013a_qwen_loop_task_results.csv')
assert sum(int(r['strong_loop_states']) for r in a)==300
assert sum(int(r['h4_intercepted']) for r in a)==291
assert sum(float(r['h4_interception_pct'])==100 for r in a)==5
checks.append('Cooldown intercepts 291/300 edges; five tasks have 100 percent coverage')
b=rows('ASTIG_013B/astig013b_task_results.csv')
for k,v in [('k2',131),('k4',142),('k8',178),('external_new',300),('progress_class_E',139),('progress_class_T',64),('progress_class_S',97)]:assert sum(int(r[k]) for r in b)==v
c=rows('ASTIG_013C/astig013c_qwen_phase_counts.csv')
for k,v in [('pre_edit',112),('post_edit_unverified',113),('post_edit_validated',75)]:assert sum(int(r[k]) for r in c)==v
bounds=rows('ASTIG_013C/astig013c_premature_submit_bounds.csv')
assert sum(int(r['premature_submit_lower_bound']) for r in bounds)==76
checks.append('Candidate availability, progression roles, phase counts and premature-submit lower bound')
h=rows('ASTIG_013D/astig013d_takeover_horizon.csv')
assert [int(r['cumulative_success']) for r in h]==[80,102,150,189,300]
assert [int(r['minimal_horizon_states']) for r in h]==[80,22,48,39,111]
for r in h:assert int(r['terminal_submit'])+int(r['gate_clear_nonterminal'])==int(r['cumulative_success'])
checks.append('Controlled-replay horizon totals and release decomposition')
for rep in ['decision','mean']:
    rr=rows(f'MODE_COLLISION_001/MODE_COLLISION_001_three_seed_{rep}_geometry.csv')
    ss=rows(f'MODE_COLLISION_001/MODE_COLLISION_001_three_seed_{rep}_summary.csv')
    for s in ss:
        a=[r for r in rr if r['layer']==s['layer']];assert len(a)==3
        for key,prefix in [('probe_acc','probe'),('fisher_ratio','fisher'),('knn_cross_mix','mix')]:
            vals=[float(r[key]) for r in a];close(statistics.mean(vals),s[prefix+'_mean']);close(statistics.stdev(vals),s[prefix+'_sd'])
checks.append('All three-seed means and sample standard deviations underlying the layerwise figures')
f=json.loads((E/'MODE_CONTROL/MODE_CONTROL_FINAL_summary.json').read_text())
for block in ['23','22','21']:
    g=f['block_gates'][block]
    close(g['C_raw'],(g['text_plus1_mean_ci95'][0]-g['act_minus1_mean_ci95'][0])/2)
    assert g['C_raw']>max(g['control_C_95th'])
assert [f['reversal']['by_reverse_block'][str(b)]['restored_act_from_initial_rescue'] for b in [24,25,26,27]]==[9,9,9,5]
checks.append('Final-summary bidirectional control arithmetic, matched-control comparisons and reversal counts')
if (P/'SHA256SUMS').exists():
    for line in (P/'SHA256SUMS').read_text().splitlines():
        expected,name=line.split('  ',1);assert hashlib.sha256((P/name).read_bytes()).hexdigest()==expected,name
    checks.append('Published file checksums')
print(json.dumps({'status':'passed','scope':'Derived-output consistency and release integrity; no retraining or new intervention run','checks':checks},indent=2))
