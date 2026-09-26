"""Read the completed fixed campaign; no training or checkpoint selection here.

Run with a NumPy/matplotlib runtime. Checkpoint recovery has a separate Torch entry.
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
from pathlib import Path
import shutil

import numpy as np


def csv_out(path, rows):
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def oracle(rules, starts, length):
    state = starts.astype(np.int64)
    for _ in range(length):
        state = rules[np.arange(len(rules)), state]
    return state


def analyze(root, run_id='A-CAMPAIGN-001'):
    cfg = json.loads((root / 'configs/phaseA_v1.json').read_text())
    done = json.loads((root / 'attempts' / run_id / 'completion.json').read_text())
    if done['status'] != 'COMPLETED':
        raise RuntimeError('Incomplete campaign must be diagnosed separately; do not report a full gate.')
    with (root / 'results/accuracy_by_length.csv').open() as f:
        rows = list(csv.DictReader(f))
    indexed = {(int(r['seed']), r['condition'], int(r['length'])): float(r['accuracy']) for r in rows}
    conditions = list(dict.fromkeys(r['condition'] for r in rows))
    summaries, seed_rows, pairs, counts = [], [], [], []
    for condition in conditions:
        for length in cfg['test_lengths']:
            a = np.array([indexed[s, condition, length] for s in cfg['seeds']])
            summaries.append({'condition': condition, 'length': length, 'seed_mean': a.mean(),
                              'seed_std': a.std(ddof=1), 'seed_min': a.min(), 'seed_max': a.max(), 'seeds': len(a)})
    for seed in cfg['seeds']:
        info = json.loads((root / f'results/seed_{seed}_training.json').read_text())
        mean = lambda c: float(np.mean([indexed[seed, c, l] for l in (8, 10, 12)]))
        seed_rows.append({'seed': seed, 'base_validation_accuracy': info['base_validation']['accuracy'],
                          'rtg_selected_batch': info['arms']['rtg']['selected_step'],
                          'recurrent_selected_batch': info['arms']['recurrent']['selected_step'],
                          'rtg_optimizer_updates': info['arms']['rtg']['actual_optimizer_updates'],
                          'recurrent_optimizer_updates': info['arms']['recurrent']['actual_optimizer_updates'],
                          'adapter_trainable_parameters': info['arms']['rtg']['trainable_parameters'],
                          'base_parameters': info['base_parameters'],
                          'base_update_fraction': info['arms']['rtg']['base_update_fraction'],
                          **{f'{c}_long': mean(c) for c in conditions},
                          'full_minus_recurrent_pp': 100 * (mean('rtg_full') - mean('recurrent')),
                          'full_minus_base_pp': 100 * (mean('rtg_full') - mean('base_only'))})
        with np.load(root / f'data/seed_{seed}/test.npz') as data, np.load(root / f'results/predictions_seed_{seed}.npz') as preds:
            target = np.stack([oracle(data['rules'], data['starts'], l) for l in (8, 10, 12)])
            full = np.stack([preds[f'rtg_full_L{l}'] for l in (8, 10, 12)])
            rng = np.random.default_rng(seed + 71000)
            resample = rng.integers(cfg['test_rules'], size=(2000, cfg['test_rules']))
            for control in conditions:
                if control == 'rtg_full':
                    continue
                alternative = np.stack([preds[f'{control}_L{l}'] for l in (8, 10, 12)])
                difference = ((full == target).astype(float) - (alternative == target).astype(float))
                by_rule = difference.reshape(3, cfg['test_rules'], 2).mean(axis=(0, 2))
                boots = by_rule[resample].mean(1)
                pairs.append({'seed': seed, 'control': control, 'full_minus_control_pp': 100 * by_rule.mean(),
                              'rule_bootstrap_lower_pp': 100 * np.quantile(boots, .025),
                              'rule_bootstrap_upper_pp': 100 * np.quantile(boots, .975),
                              'prediction_disagreement': float((full != alternative).mean()),
                              'independent_rules': cfg['test_rules'], 'starts_per_rule': 2, 'lengths': '8,10,12'})
            for length in cfg['test_lengths']:
                first = oracle(data['rules'], data['starts'], 1)
                truth = oracle(data['rules'], data['starts'], length)
                counts.append({'seed': seed, 'length': length,
                               'exact_one_call_cycle_agreement': float((first == truth).mean()),
                               'observed_base_only_accuracy': indexed[seed, 'base_only', length]})
    absolute = all(np.mean([indexed[s, 'rtg_full', l] for s in cfg['seeds']]) >= cfg['gate']['long_accuracy'] for l in (8, 10, 12))
    reader_ok = all(r['base_validation_accuracy'] >= cfg['gate']['base_accuracy'] for r in seed_rows)
    advantage = all(np.mean([r[f'{control}_pp'] for r in seed_rows]) >= 100 * cfg['gate']['advantage']
                    and all(r[f'{control}_pp'] > 0 for r in seed_rows)
                    for control in ('full_minus_base', 'full_minus_recurrent'))
    gate = {'phase': 'A', 'base_gate': reader_ok, 'absolute_extrapolation_gate': absolute,
            'relative_advantage_gate': advantage, 'gate_pass': reader_ok and absolute and advantage,
            'thresholds': cfg['gate'], 'independent_seeds': len(seed_rows), 'test_rules_per_seed': cfg['test_rules'],
            'long_lengths': [8, 10, 12], 'main_predictions': done['predictions'],
            'optimizer_updates': done['training_updates'],
            'next_phase': 'B_REQUIRES_EXECUTABLE_PROTOCOL' if reader_ok and absolute and advantage else 'STOP_AFTER_A_DIAGNOSIS'}
    csv_out(root / 'results/condition_summary.csv', summaries)
    csv_out(root / 'results/seeds_summary.csv', seed_rows)
    csv_out(root / 'results/paired_long_comparisons.csv', pairs)
    csv_out(root / 'results/base_cycle_reference.csv', counts)
    shutil.copy2(root / 'results/accuracy_by_length.csv', root / 'results/phaseA_accuracy_by_length.csv')
    (root / 'results/gate_A.json').write_text(json.dumps(gate, indent=2) + '\n')
    surface_rows = []
    for seed in cfg['seeds']:
        grouped = collections.defaultdict(list)
        for line in (root / f'results/surface_seed_{seed}.jsonl').read_text().splitlines():
            r = json.loads(line)
            grouped[r['condition'], r['length'], r['transform']].append(r)
        for (condition, length, transform), group in grouped.items():
            surface_rows.append({'seed': seed, 'condition': condition, 'length': length, 'transform': transform,
                                 'episodes': len(group), 'accuracy': np.mean([r['correct'] for r in group]),
                                 'equivariance': np.mean([r['equivariant'] for r in group])})
    csv_out(root / 'results/surface_summary.csv', surface_rows)
    diagnostic_rows, failures = diagnostics(root, cfg)
    csv_out(root / 'results/internal_diagnostics_summary.csv', diagnostic_rows)
    if failures:
        csv_out(root / 'results/failure_first_deviation.csv', failures)
    (root / 'results/failure_diagnosis.json').write_text(json.dumps({'traced_failures': failures,
        'scope': 'first four failed final episodes per seed, if any; diagnostic only'}, indent=2) + '\n')
    plot(root, cfg, summaries, diagnostic_rows)
    return gate, seed_rows


def diagnostics(root, cfg):
    groups = collections.defaultdict(list)
    failures = []
    for seed in cfg['seeds']:
        with np.load(root / f'data/seed_{seed}/test.npz') as data:
            rules = data['rules'].copy()
        first_l, identified = {}, set()
        for line in (root / f'traces/internal_diagnostics/seed_{seed}.jsonl').open():
            r = json.loads(line)
            key = (r['condition'], r['length'], r['episode_index'])
            if r['step'] == 0:
                first_l[key] = np.asarray(r['L_before'])
            if r['condition'] == 'failure_full':
                correct_child = int(rules[r['episode_index'], r['a']])
                if r['b'] != correct_child and key not in identified:
                    original_child = int(first_l[key][r['a']].argmax())
                    failures.append({'seed': seed, 'length': r['length'], 'episode_index': r['episode_index'],
                                     'first_local_deviation_step': r['step'] + 1, 'state': r['a'],
                                     'realized_child': r['b'], 'correct_child': correct_child,
                                     'frozen_reader_child': original_child,
                                     'classification': 'write_flipped_correct_base' if original_child == correct_child else 'base_relation_error'})
                    identified.add(key)
            else:
                for field in ('alpha', 'actual_write_norm', 'continuation_entropy', 'effective_candidates', 'top_share'):
                    groups[seed, r['condition'], r['length'], r['step'], field].append(r[field])
    rows = [{'seed': s, 'condition': c, 'length': l, 'step': t, 'metric': metric,
             'mean': np.mean(v), 'min': np.min(v), 'max': np.max(v), 'traced_episodes': len(v)}
            for (s, c, l, t, metric), v in groups.items()]
    return rows, failures


def plot(root, cfg, summaries, diagnostic_rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False,
                         'axes.spines.right': False, 'savefig.dpi': 180})
    colors = {'rtg_full': '#19647e', 'recurrent': '#e07a5f', 'iterated_base': '#57a773',
              'base_only': '#727d8c', 'rtg_step0': '#9871b4', 'rtg_no_write': '#dfb040'}
    labels = {'rtg_full': 'RTG after training', 'recurrent': 'Equal-parameter recurrent',
              'iterated_base': 'Iterated frozen reader', 'base_only': 'One-call reader',
              'rtg_step0': 'RTG before post-training', 'rtg_no_write': 'RTG no write'}
    fig, ax = plt.subplots(figsize=(9, 5.3))
    for index, condition in enumerate(colors):
        r = [x for x in summaries if x['condition'] == condition]
        x = [a['length'] for a in r]
        y = np.array([a['seed_mean'] for a in r]) * 100
        ax.plot(x, y, label=labels[condition], color=colors[condition], lw=2,
                linestyle=['-', '--', ':', '-', '-.', '--'][index], marker=['o', 's', '^', 'x', 'D', '+'][index],
                markersize=4, alpha=.9)
        ax.fill_between(x, np.array([a['seed_min'] for a in r])*100,
                        np.array([a['seed_max'] for a in r])*100, color=colors[condition], alpha=.07)
    ax.axvspan(1, 4, color='#dbe4ee', alpha=.45, label='Training lengths')
    ax.axhline(90, color='#808080', lw=.8, ls=':')
    ax.set(xlabel='Requested transitions', ylabel='Final-answer accuracy (%)', ylim=(0, 103),
           xticks=cfg['test_lengths'], title='Phase A: static rule composition on unseen permutations')
    ax.legend(fontsize=8, ncol=2, loc='lower center')
    ax.grid(axis='y', alpha=.15)
    fig.text(.12, .015, 'Five seeds; 512 new rules × 2 starts per seed. Bands show seed range; overlapping lines are intentional.', fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));fig.savefig(root/'figures/phaseA_accuracy.png');fig.savefig(root/'figures/phaseA_accuracy.pdf');plt.close(fig)
    with (root / 'results/train_curve.csv').open() as f:
        curves = list(csv.DictReader(f))
    fig, ax = plt.subplots(figsize=(8, 4.6))
    for arm, color in [('rtg', colors['rtg_full']), ('recurrent', colors['recurrent'])]:
        selected = [r for r in curves if r['arm'] == arm and r['split'] == 'validation']
        for j, seed in enumerate(cfg['seeds']):
            r = [a for a in selected if int(a['seed']) == seed]
            ax.plot([int(a['update']) for a in r], [float(a['loss']) for a in r], color=color,
                    alpha=.55, label=arm if j == 0 else None)
    ax.set(xlabel='Scheduled post-training batches', ylabel='Validation final-answer cross-entropy',
           title='Model selection uses only lengths 1–4', yscale='log')
    ax.legend();ax.grid(alpha=.15);fig.tight_layout();fig.savefig(root/'figures/phaseA_learning.png');plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, metric, ylabel in zip(axes, ['actual_write_norm', 'continuation_entropy'], ['Actual write norm', 'Continuation entropy (nats)']):
        for condition, color in [('full', colors['rtg_full']), ('unbounded', colors['recurrent']), ('step0', colors['rtg_step0'])]:
            series = []
            for step in range(20):
                values = [r['mean'] for r in diagnostic_rows if r['condition']==condition and r['length']==20 and r['step']==step and r['metric']==metric]
                series.append(np.mean(values))
            ax.plot(range(1,21), series, label=condition, color=color)
        ax.set(xlabel='Transition', ylabel=ylabel);ax.grid(alpha=.15)
    axes[0].axhline(cfg['write_budget'], color='#777',ls=':',lw=1)
    axes[1].legend(fontsize=8)
    fig.suptitle('Prespecified traces: four episodes per seed, not a global stability proof')
    fig.tight_layout();fig.savefig(root/'figures/phaseA_budget_diagnostics.png');plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--run-id', default='A-CAMPAIGN-001')
    args = parser.parse_args()
    gate, seeds = analyze(args.root, args.run_id)
    print(json.dumps({'gate': gate, 'seeds': seeds}, indent=2))
