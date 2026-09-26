"""Post-hoc read-only diagnosis, using saved traces rather than rerunning models."""
import collections
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import numpy as np


def main(run_id='A-DIAG-001'):
    root = Path(__file__).resolve().parent
    config = json.loads((root / 'configs/phaseA_v1.json').read_text())
    rows, tables, global_ids = [], {}, set()
    for seed in config['seeds']:
        with np.load(root / f'data/seed_{seed}/test.npz') as x:
            rules = x['rules'].copy()
            tables[seed] = {k: x[k].copy() for k in x.files}
            global_ids.update(int(i) for i in x['rule_ids'])
        coefficients = json.loads((root / f'results/seed_{seed}_training.json').read_text())['arms']['rtg']['coefficients']
        base, groups = {}, collections.defaultdict(list)
        for line in (root / f'traces/internal_diagnostics/seed_{seed}.jsonl').open():
            r = json.loads(line)
            if r['condition'] not in ('full', 'step0', 'no_write', 'reset_m', 'unbounded'):
                continue
            key = (r['condition'], r['length'], r['episode_index'])
            if r['step'] == 0:
                base[key] = np.asarray(r['L_before'])
            retention = .9 if r['condition'] == 'step0' else coefficients['retention']
            before, after = np.asarray(r['L_before']), np.asarray(r['L_after'])
            write = after - (base[key] + retention * (before - base[key]))
            child, correct_next = r['b'], int(rules[r['episode_index'], r['b']])
            local = write[child]
            groups[r['condition'], r['length']].append({
                'max_write_is_correct_descendant': int(local.argmax() == correct_next),
                'correct_descendant_logit_write': float(local[correct_next]),
                'correct_minus_other_mean': float(local[correct_next] - np.delete(local, correct_next).mean()),
                'actual_write_norm': r['actual_write_norm'],
                'local_transition_correct': int(r['b'] == int(rules[r['episode_index'], r['a']])),
                'budget_active': int(r['alpha'] < .999999),
            })
        for (condition, length), values in groups.items():
            # Zero-write argmax has no meaningful direction, so explicitly NA.
            rows.append({'seed': seed, 'condition': condition, 'length': length, 'transitions': len(values),
                         **{key: ('' if condition == 'no_write' and key == 'max_write_is_correct_descendant'
                                  else float(np.mean([v[key] for v in values]))) for key in values[0]}})
    with (root / 'results/rewrite_alignment_diagnostic.csv').open('w', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    limits = collections.Counter()
    failures_by_condition = collections.Counter()
    with (root / 'traces/control_failure_examples.jsonl').open('w') as out:
        for line in (root / 'results/per_episode_predictions.jsonl').open():
            r = json.loads(line)
            if r['correct']:
                continue
            failures_by_condition[r['condition']] += 1
            key = (r['seed'], r['condition'])
            if limits[key] >= 8:
                continue
            data = tables[r['seed']]
            r.update(rule=data['rules'][r['episode_index']].tolist(),
                     row_order=data['row_order'][r['episode_index']].tolist(),
                     evidence_type='saved_final_prediction_no_new_model_run')
            out.write(json.dumps(r, separators=(',', ':'))+'\n');limits[key] += 1
    receipt = {'run_id': run_id, 'status': 'COMPLETED', 'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
               'new_model_calls': 0, 'global_distinct_test_rules': len(global_ids),
               'saved_control_examples': sum(limits.values()), 'formal_errors_by_condition': dict(failures_by_condition),
               'trace_scope': 'prespecified four episodes per seed, two rules per seed; descriptive only',
               'step0_retention': 'registered value 0.9; float32 reconstruction has rounding error'}
    (root / 'results/diagnostic_receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt, indent=2))
    for condition in ('full', 'step0', 'reset_m', 'unbounded'):
        subset = [r for r in rows if r['condition'] == condition and r['length'] == 20]
        print(condition, {k: np.mean([r[k] for r in subset]) for k in
                          ('max_write_is_correct_descendant','correct_minus_other_mean','actual_write_norm','local_transition_correct')})


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--run-id', default='A-DIAG-001')
    args = parser.parse_args()
    main(args.run_id)
