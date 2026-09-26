"""Scoped post-exit evidence audit and fresh-process checkpoint recovery.

No optimizer, training, checkpoint changes, OOD selection or historical artifacts.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import datetime as dt

import numpy as np
import torch

from .src.data import Episodes, permutation_rank, belongs, final_answer
from .src.campaign import load_model, CONDITIONS
from .src.models import RecurrentAdapter


def run(root, run_id='A-CAMPAIGN-001'):
    cfg = json.loads((root / 'configs/phaseA_v1.json').read_text())
    done = json.loads((root / 'attempts' / run_id / 'completion.json').read_text())
    assert done['status'] == 'COMPLETED'
    torch.set_num_threads(1)
    contract, recovery, expected, tables, pred_arrays, fields = [], [], {}, {}, {}, []
    for seed in cfg['seeds']:
        folder = root / f'data/seed_{seed}'
        for kind in ('base_train', 'post_train'):
            with np.load(folder / f'{kind}.npz') as x:
                n, b, width = x['rules'].shape
                rules = x['rules'].reshape(-1, width).astype(np.int64)
                ids = permutation_rank(rules)
                assert belongs(ids, 'train').all()
                starts = x['starts'].reshape(-1)
                order = x['row_order'].reshape(-1, width)
                assert np.all(np.sort(order, axis=1) == np.arange(width))
                lengths = np.repeat(x['lengths'], b)
                targets = x['targets'].reshape(-1)
                assert set(np.unique(lengths)).issubset(set(cfg['train_lengths']))
                for length in np.unique(lengths):
                    mask = lengths == length
                    assert np.array_equal(final_answer(rules[mask], starts[mask], int(length)), targets[mask])
                contract.append({'seed': seed, 'material': kind, 'episodes': len(rules),
                                 'unique_rules': len(np.unique(ids)), 'split': 'train', 'labels_checked': len(rules)})
        for split in ('validation', 'test'):
            with np.load(folder / f'{split}.npz') as x:
                ids = permutation_rank(x['rules'])
                assert belongs(ids, split).all()
                assert np.array_equal(ids, x['rule_ids'])
                assert (x['starts'][::2] != x['starts'][1::2]).all()
                assert len(np.unique(ids)) == len(ids) // 2
                contract.append({'seed': seed, 'material': split, 'episodes': len(ids),
                                 'unique_rules': len(np.unique(ids)), 'split': split, 'labels_checked': 0})
                if split == 'test':
                    tables[seed] = {k: x[k].copy() for k in x.files}
        with np.load(folder / 'surface_renamed.npz') as renamed:
            assert belongs(permutation_rank(renamed['rules']), 'test').all()
        with np.load(root / f'results/predictions_seed_{seed}.npz') as x:
            pred_arrays[seed] = {k: x[k].copy() for k in x.files}
        for length in cfg['test_lengths']:
            expected[seed, length] = final_answer(tables[seed]['rules'], tables[seed]['starts'], length)
        base_state = torch.load(root / f'checkpoints/seed_{seed}/BASE_ONE_STEP.ckpt', weights_only=False, map_location='cpu')['state_dict']
        for arm, condition, path, cls in [
            ('rtg', 'rtg_full', 'rtg/SELECTED.ckpt', None),
            ('step0', 'rtg_step0', 'rtg/step_0000.ckpt', None),
            ('recurrent', 'recurrent', 'recurrent/SELECTED.ckpt', RecurrentAdapter),
        ]:
            kwargs = {} if cls is None else {'cls': cls}
            model, state = load_model(cfg, root / f'checkpoints/seed_{seed}' / path, **kwargs)
            assert all(torch.equal(value, base_state[name]) for name, value in model.reader.state_dict().items())
            ep = Episodes(tables[seed]['rules'][:16], tables[seed]['starts'][:16], tables[seed]['row_order'][:16])
            with torch.no_grad():
                for length in (4, 12):
                    prediction = model(*ep.inputs(), length).argmax(-1).numpy()
                    assert np.array_equal(prediction, pred_arrays[seed][f'{condition}_L{length}'][:16])
                    recovery.append({'seed': seed, 'arm': arm, 'checkpoint_batch': state['step'],
                                     'length': length, 'episodes': len(ep), 'predictions_exact': True, 'base_weights_exact': True})
            if arm == 'rtg':
                # Direct relation reading on every state in the held-out rules.
                unique = Episodes(tables[seed]['rules'][::2], tables[seed]['starts'][::2], tables[seed]['row_order'][::2])
                with torch.no_grad():
                    geometry, _ = model.reader.all_rows(*unique.inputs()[:2])
                    base_correct = geometry.argmax(-1).numpy() == unique.rules
                fields.append({'seed': seed, 'all_state_relation_accuracy': float(base_correct.mean()),
                               'queries': int(base_correct.size)})
    flags = np.zeros((len(cfg['seeds']), len(CONDITIONS), len(cfg['test_lengths']), cfg['test_rules']*2), dtype=bool)
    count, correct_counts = 0, {}
    with (root / 'results/per_episode_predictions.jsonl').open() as f:
        for line in f:
            r = json.loads(line)
            s, l, c, i = r['seed'], r['length'], r['condition'], r['episode_index']
            index = (cfg['seeds'].index(s), CONDITIONS.index(c), cfg['test_lengths'].index(l), i)
            assert not flags[index]
            flags[index] = True
            assert r['target'] == int(expected[s, l][i])
            assert r['prediction'] == int(pred_arrays[s][f'{c}_L{l}'][i])
            assert r['rule_id'] == int(tables[s]['rule_ids'][i])
            assert r['start'] == int(tables[s]['starts'][i])
            assert r['correct'] == (r['target'] == r['prediction'])
            assert 0 <= r['target_probability'] <= 1
            key = (s, c, l)
            correct_counts[key] = correct_counts.get(key, 0) + int(r['correct'])
            count += 1
    assert flags.all() and count == done['predictions']
    with (root / 'results/accuracy_by_length.csv').open() as f:
        accuracy_rows = list(csv.DictReader(f))
    assert len(accuracy_rows) == len(cfg['seeds']) * len(CONDITIONS) * len(cfg['test_lengths'])
    for r in accuracy_rows:
        key = (int(r['seed']), r['condition'], int(r['length']))
        assert correct_counts[key] == int(r['correct'])
        assert abs(float(r['accuracy']) - int(r['correct']) / int(r['episodes'])) < 1e-12
    bounds, diagnostic_steps = [], 0
    for seed in cfg['seeds']:
        for line in (root / f'traces/internal_diagnostics/seed_{seed}.jsonl').open():
            r = json.loads(line)
            for name in ('L_before', 'L_after', 'M_before', 'M_after', 'g'):
                assert np.isfinite(r[name]).all()
            assert max(r['M_norms']) <= 1.00001
            assert 0 < r['alpha'] <= 1
            if r['condition'] != 'unbounded':
                assert r['actual_write_norm'] <= cfg['write_budget'] + 1e-5
            if r['condition'] == 'no_write':
                assert r['actual_write_norm'] == 0
            diagnostic_steps += 1
    source = root / 'attempts' / run_id / 'source_snapshot'
    same_source = {p.name: p.read_bytes() == (root / 'src' / p.name).read_bytes() for p in source.glob('*.py')}
    assert all(same_source.values())
    report = {'run_id': 'A-AUDIT-001' if run_id == 'A-CAMPAIGN-001' else run_id + '-AUDIT',
              'ended_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
              'status': 'PASS', 'campaign_complete_before_read': True, 'data_contracts': contract,
              'raw_predictions_checked': count, 'diagnostic_steps_checked': diagnostic_steps,
              'checkpoint_recovery': recovery, 'base_all_states': fields, 'source_snapshot_byte_equality': same_source,
              'scope': 'only this experiment; no training, parameter changes, historical artifacts, or hashes'}
    (root / 'results/scoped_audit.json').write_text(json.dumps(report, indent=2) + '\n')
    return {'status': 'PASS', 'raw_predictions_checked': count, 'recovery_checks': len(recovery),
            'diagnostic_steps': diagnostic_steps, 'base_all_states': fields}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--run-id', default='A-CAMPAIGN-001')
    args = parser.parse_args()
    print(json.dumps(run(args.root, args.run_id), indent=2))
