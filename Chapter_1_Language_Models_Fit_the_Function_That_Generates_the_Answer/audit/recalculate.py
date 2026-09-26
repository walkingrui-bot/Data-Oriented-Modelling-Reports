"""Recompute report aggregates using only the Python standard library.
Run from any directory: python audit/recalculate.py
No training or neural-network intervention is rerun by this script.
"""
from pathlib import Path
import csv, json, statistics

ROOT=Path(__file__).resolve().parents[1]
def rows(path):
    with (ROOT/'evidence'/path).open(encoding='utf-8-sig',newline='') as f:
        return list(csv.DictReader(f))

out=[]
r=rows('L_language/tables/37_author_loo_corrected.csv')
out.append(dict(check='author_genre_rows',n=len(r),unique_authors=len({x['author'] for x in r}),majority_correct=sum(x['true_genre']==x['majority_prediction'] for x in r),mean_window_accuracy=statistics.mean(float(x['window_level_accuracy']) for x in r)))
r=rows('L_language/tables/30_expected_ppmi_three_batches.csv')
ns=[int(x['n_sources']) for x in r]
out.append(dict(check='expected_field_summary',language_batch_rows=len(r),reported_sources=sum(ns),unweighted_fraction=statistics.mean(float(x['expected_effN_greater_fraction']) for x in r),weighted_fraction=sum(n*float(x['expected_effN_greater_fraction']) for n,x in zip(ns,r))/sum(ns),median_ratio=statistics.median(float(x['median_effN_ratio']) for x in r)))
for file in ['X2_selective_history/03_attention_vs_causal_voice.csv','X3_state_transplant/01_forged_history_injection.csv','X3_state_transplant/02_one_shot_rule_formation.csv']:
    r=rows(file);means={}
    for key in r[0]:
        if key=='seed':continue
        try: means[key]=statistics.mean(float(x[key]) for x in r)
        except (ValueError,TypeError):pass
    out.append(dict(check=file,means=means))
r=rows('R5_posttraining/results/seeds_summary.csv')
config=json.loads((ROOT/'evidence/R5_posttraining/configs/phaseA_v1.json').read_text())
# Each of five base readers receives the configured 800 optimizer updates.
out.append(dict(check='actual_optimizer_updates',total_base_updates=len(r)*config['base_updates'],total_adapter_updates=sum(int(x['rtg_optimizer_updates'])+int(x['recurrent_optimizer_updates']) for x in r)))
(ROOT/'audit/summary_recalculation.json').write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n')
print(json.dumps(out,indent=2,ensure_ascii=False))
