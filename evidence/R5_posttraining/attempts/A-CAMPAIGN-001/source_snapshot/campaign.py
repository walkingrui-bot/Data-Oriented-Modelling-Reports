"""Fixed five-seed Phase A campaign. No console progress or OOD selection.

All validation/checkpoint operations are the preset execution schedule. The agent
does not inspect outputs until the complete command exits. Every supervised loss
uses only final_answer; diagnostic trajectories never enter the optimizer.
"""
from __future__ import annotations

import argparse
import contextlib
import copy
import csv
import datetime as dt
import json
import os
from pathlib import Path
import platform
import random
import shutil
import sys
import time
import traceback

import numpy as np
import torch
from torch.nn import functional as F

from .data import Episodes, random_episodes, evaluation_episodes, renamed_episodes, belongs
from .models import RuleReader, RTG, RecurrentAdapter, iterated_base, trainable_count

PROJECT = Path(__file__).resolve().parents[1]
CONDITIONS = ('base_only', 'iterated_base', 'rtg_step0', 'rtg_full', 'rtg_no_write',
              'rtg_no_inheritance', 'rtg_reset_m', 'rtg_gamma_zero', 'rtg_unbounded', 'recurrent')


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n')


def json_line(handle, obj):
    handle.write(json.dumps(obj, ensure_ascii=False, separators=(',', ':')) + '\n')
    handle.flush()


def append_event(attempt, obj):
    with (attempt / 'events.jsonl').open('a') as f:
        json_line(f, {'recorded_at': now(), **obj})


def seed_all(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def checkpoint(path, model, optimizer, step, config, metadata):
    torch.save({'state_dict': model.state_dict(), 'optimizer': optimizer.state_dict() if optimizer else None,
                'step': step, 'config': config, 'metadata': metadata,
                'torch_rng': torch.get_rng_state(), 'numpy_rng': np.random.get_state(),
                'python_rng': random.getstate()}, path)


def load_model(config, path, cls=RTG):
    state = torch.load(path, map_location='cpu', weights_only=False)
    reader = RuleReader(config['n'], config['base_dim'])
    model = cls(reader, config['relation_dim'], config['geometry_scale'], config['write_budget'])
    model.load_state_dict(state['state_dict'])
    model.eval()
    return model, state


def make_training(seed, steps, config, base=False):
    rng = np.random.default_rng(seed)
    rules, starts, orders, lengths, targets = [], [], [], [], []
    for _ in range(steps):
        length = 1 if base else int(rng.choice(config['train_lengths']))
        ep = random_episodes(rng, config['batch_size'], config['n'], 'train')
        rules.append(ep.rules.astype(np.uint8))
        starts.append(ep.starts.astype(np.uint8))
        orders.append(ep.row_order.astype(np.uint8))
        lengths.append(length)
        targets.append(ep.target(length).numpy().astype(np.uint8))
    return {'rules': np.asarray(rules), 'starts': np.asarray(starts), 'row_order': np.asarray(orders),
            'lengths': np.asarray(lengths, dtype=np.uint8), 'targets': np.asarray(targets)}


def train_episode(data, i):
    return Episodes(data['rules'][i], data['starts'][i], data['row_order'][i])


@torch.no_grad()
def validation(model, episodes, lengths, base=False):
    correct, count, loss = 0, 0, 0.
    model.eval()
    for length in lengths:
        for offset in range(0, len(episodes), 128):
            ep = episodes.take(slice(offset, offset + 128))
            logits = model(*ep.inputs()) if base else model(*ep.inputs(), length)
            target = ep.target(length)
            loss += float(F.cross_entropy(logits, target, reduction='sum'))
            correct += int((logits.argmax(-1) == target).sum())
            count += len(ep)
    return {'accuracy': correct / count, 'loss': loss / count, 'count': count}


def run_training(config, root, attempt, seed, curve):
    seed_all(seed)
    ckpt = root / 'checkpoints' / f'seed_{seed}'
    ckpt.mkdir(parents=True, exist_ok=False)
    data_dir = root / 'data' / f'seed_{seed}'
    data_dir.mkdir(parents=True, exist_ok=False)
    val = evaluation_episodes(np.random.default_rng(seed + 11000), config['validation_rules'], config['n'], 'validation')
    val.save(data_dir / 'validation.npz')
    reader = RuleReader(config['n'], config['base_dim'])
    base_initial = copy.deepcopy(reader.state_dict())
    base_data = make_training(seed + 21000, config['base_updates'], config, base=True)
    np.savez_compressed(data_dir / 'base_train.npz', **base_data)
    optimizer = torch.optim.Adam(reader.parameters(), lr=config['base_lr'])
    stage_id = f'{attempt.name}-S{seed}-BASE'
    append_event(attempt, {'run_id': stage_id, 'purpose': 'one-step reader pretraining', 'status': 'RUNNING',
                           'seed': seed, 'input': str(data_dir / 'base_train.npz'), 'updates': config['base_updates']})
    started = time.monotonic()
    for i in range(config['base_updates']):
        reader.train()
        ep = train_episode(base_data, i)
        logits = reader(*ep.inputs())
        loss = F.cross_entropy(logits, torch.from_numpy(base_data['targets'][i].astype(np.int64)))
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        grad = torch.nn.utils.clip_grad_norm_(reader.parameters(), 1.)
        if not torch.isfinite(loss) or not torch.isfinite(grad):
            raise FloatingPointError(f'Nonfinite base loss/gradient seed={seed} update={i+1}')
        optimizer.step()
        curve.writerow([seed, 'base', i + 1, 'train', 1, float(loss.detach()),
                        float((logits.argmax(-1) == ep.target(1)).float().mean()), float(grad), 1])
    base_validation = validation(reader, val, [1], base=True)
    curve.writerow([seed, 'base', config['base_updates'], 'validation', 1,
                    base_validation['loss'], base_validation['accuracy'], '', 0])
    checkpoint(ckpt / 'BASE_ONE_STEP.ckpt', reader, optimizer, config['base_updates'], config, base_validation)
    base_seconds = time.monotonic() - started
    append_event(attempt, {'run_id': stage_id, 'status': 'COMPLETED', 'base_validation': base_validation,
                           'seconds': base_seconds, 'checkpoint': str(ckpt / 'BASE_ONE_STEP.ckpt')})
    del base_data, optimizer
    reader.eval().requires_grad_(False)
    train_data = make_training(seed + 31000, config['post_updates'], config)
    np.savez_compressed(data_dir / 'post_train.npz', **train_data)
    rtg = RTG(copy.deepcopy(reader), config['relation_dim'], config['geometry_scale'], config['write_budget'])
    recurrent = RecurrentAdapter(copy.deepcopy(reader), config['relation_dim'], config['geometry_scale'], config['write_budget'])
    recurrent.load_state_dict(rtg.state_dict())
    assert trainable_count(rtg) == trainable_count(recurrent)
    trained = {}
    for arm, model in [('rtg', rtg), ('recurrent', recurrent)]:
        arm_dir = ckpt / arm
        arm_dir.mkdir()
        arm_id = f'{attempt.name}-S{seed}-{arm.upper()}'
        append_event(attempt, {'run_id': arm_id, 'purpose': 'final-answer-only post-training', 'status': 'RUNNING',
                               'seed': seed, 'input': str(data_dir / 'post_train.npz'), 'updates': config['post_updates']})
        start_weights = copy.deepcopy(model.state_dict())
        opt = torch.optim.Adam([p for p in model.parameters() if p.requires_grad], lr=config['post_lr'])
        scores = validation(model, val, config['train_lengths'])
        best_key, best_step = (scores['accuracy'], -scores['loss']), 0
        checkpoint(arm_dir / 'step_0000.ckpt', model, opt, 0, config, scores)
        curve.writerow([seed, arm, 0, 'validation', '1..4', scores['loss'], scores['accuracy'], '', 0])
        started = time.monotonic()
        optimizer_updates = 0
        for i in range(config['post_updates']):
            model.train()
            ep = train_episode(train_data, i)
            length = int(train_data['lengths'][i])
            target = torch.from_numpy(train_data['targets'][i].astype(np.int64))
            opt.zero_grad(set_to_none=True)
            logits = model(*ep.inputs(), length)
            loss = F.cross_entropy(logits, target)
            grad = torch.tensor(0.)
            # A frozen reader's first answer precedes all dynamic writes. Neither
            # arm receives an artificial gradient or an Adam momentum step here.
            if length > 1:
                loss.backward()
                grad = torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.)
            if not torch.isfinite(loss) or not torch.isfinite(grad):
                raise FloatingPointError(f'Nonfinite {arm} loss/gradient seed={seed} update={i+1}')
            if length > 1:
                opt.step()
                optimizer_updates += 1
            curve.writerow([seed, arm, i + 1, 'train', length, float(loss.detach()),
                            float((logits.argmax(-1) == target).float().mean()), float(grad), int(length > 1)])
            if (i + 1) % config['validation_every'] == 0 or i + 1 == config['post_updates']:
                scores = validation(model, val, config['train_lengths'])
                scores['optimizer_updates'] = optimizer_updates
                checkpoint(arm_dir / f'step_{i+1:04d}.ckpt', model, opt, i + 1, config, scores)
                curve.writerow([seed, arm, i + 1, 'validation', '1..4', scores['loss'], scores['accuracy'], '', 0])
                key = (scores['accuracy'], -scores['loss'])
                if key > best_key:
                    best_key, best_step = key, i + 1
        seconds = time.monotonic() - started
        selected = arm_dir / f'step_{best_step:04d}.ckpt'
        shutil.copy2(selected, arm_dir / 'SELECTED.ckpt')
        chosen = torch.load(selected, map_location='cpu', weights_only=False)
        model.load_state_dict(chosen['state_dict'])
        model.eval()
        differences = {name: {'changed_elements': int((value != start_weights[name]).sum()),
                              'elements': value.numel(), 'l2_change': float((value - start_weights[name]).norm())}
                       for name, value in model.state_dict().items()}
        base_changed = sum(v['changed_elements'] for k, v in differences.items() if k.startswith('reader.'))
        assert base_changed == 0
        trained[arm] = {'selected_step': best_step, 'validation': chosen['metadata'],
                        'actual_optimizer_updates': optimizer_updates,
                        'seconds': seconds, 'trainable_parameters': trainable_count(model),
                        'base_changed_elements': base_changed, 'base_update_fraction': 0.,
                        'coefficients': model.coefficient_dict(), 'parameter_changes': differences}
        write_json(arm_dir / 'selection.json', trained[arm])
        append_event(attempt, {'run_id': arm_id, 'status': 'COMPLETED', 'selected_step': best_step,
                               'seconds': seconds, 'base_changed_elements': base_changed})
    step0, _ = load_model(config, ckpt / 'rtg/step_0000.ckpt')
    info = {'seed': seed, 'base_validation': base_validation, 'base_seconds': base_seconds,
            'base_parameters': sum(p.numel() for p in reader.parameters()),
            'base_pretrain_changed_elements': sum(int((v != base_initial[k]).sum()) for k, v in reader.state_dict().items()),
            'arms': trained}
    return reader, rtg, recurrent, step0, info, data_dir


@torch.no_grad()
def predict(condition, reader, rtg, recurrent, step0, ep, length):
    args = ep.inputs()
    if condition == 'base_only':
        return reader(*args)
    if condition == 'iterated_base':
        return iterated_base(reader, *args, length)
    if condition == 'recurrent':
        return recurrent(*args, length)
    if condition == 'rtg_step0':
        return step0(*args, length)
    mode = condition.removeprefix('rtg_')
    return rtg(*args, length, mode=mode)


@torch.no_grad()
def evaluate(config, root, attempt, seed, reader, rtg, recurrent, step0, data_dir, summary_csv, predictions, failures):
    test = evaluation_episodes(np.random.default_rng(seed + 41000), config['test_rules'], config['n'], 'test')
    test.save(data_dir / 'test.npz')
    test_rule_ids = test.rule_ids
    assert belongs(test_rule_ids, 'test').all()
    full_arrays, rows, failed = {}, [], []
    for condition in CONDITIONS:
        for length in config['test_lengths']:
            all_pred, all_prob = [], []
            for offset in range(0, len(test), 128):
                ep = test.take(slice(offset, offset + 128))
                logits = predict(condition, reader, rtg, recurrent, step0, ep, length)
                assert torch.isfinite(logits).all()
                all_pred.extend(logits.argmax(-1).tolist())
                all_prob.extend(torch.softmax(logits, -1).gather(1, ep.target(length)[:, None])[:, 0].tolist())
            target = test.target(length).numpy()
            pred = np.asarray(all_pred)
            correct = pred == target
            row = {'seed': seed, 'condition': condition, 'length': length, 'correct': int(correct.sum()),
                   'episodes': len(test), 'rules': config['test_rules'], 'accuracy': float(correct.mean())}
            rows.append(row)
            summary_csv.writerow(row)
            full_arrays[f'{condition}_L{length}'] = pred.astype(np.uint8)
            for i in range(len(test)):
                record = {'seed': seed, 'condition': condition, 'length': length, 'episode_index': i,
                          'rule_id': int(test_rule_ids[i]), 'start': int(test.starts[i]),
                          'target': int(target[i]), 'prediction': int(pred[i]), 'correct': bool(correct[i]),
                          'target_probability': all_prob[i]}
                # Buffered write: no per-row fsync or console diagnostics.
                predictions.write(json.dumps(record, separators=(',', ':')) + '\n')
                if condition == 'rtg_full' and not correct[i]:
                    failures.write(json.dumps({**record, 'rule': test.rules[i].tolist(),
                                               'row_order': test.row_order[i].tolist()}, separators=(',', ':')) + '\n')
                    if len(failed) < config['failure_traces_per_seed']:
                        failed.append((i, length))
    np.savez_compressed(root / 'results' / f'predictions_seed_{seed}.npz', **full_arrays)
    diagnostic_modes = [('full', rtg), ('no_write', rtg), ('reset_m', rtg), ('unbounded', rtg), ('step0', step0)]
    with (root / 'traces/internal_diagnostics' / f'seed_{seed}.jsonl').open('w') as diagnostics:
        for mode, model in diagnostic_modes:
            for length in config['diagnostic_lengths']:
                subset = test.take(slice(0, config['diagnostic_episodes']))
                _, trace = model(*subset.inputs(), length, mode='full' if mode == 'step0' else mode, trace=True)
                for record in trace:
                    json_line(diagnostics, {'seed': seed, 'condition': mode, 'length': length, **record})
        for episode_index, length in failed:
            subset = test.take(slice(episode_index, episode_index + 1))
            _, trace = rtg(*subset.inputs(), length, trace=True)
            for record in trace:
                json_line(diagnostics, {'seed': seed, 'condition': 'failure_full', 'length': length,
                                       **record, 'episode_index': episode_index})
    surface(config, root, seed, reader, rtg, recurrent, step0, test, data_dir)
    append_event(attempt, {'run_id': f'{attempt.name}-S{seed}-EVAL', 'status': 'COMPLETED',
                           'conditions': len(CONDITIONS), 'rule_instances': config['test_rules'],
                           'predictions': len(CONDITIONS) * len(test) * len(config['test_lengths'])})
    return rows


@torch.no_grad()
def surface(config, root, seed, reader, rtg, recurrent, step0, test, data_dir):
    original = test.take(slice(0, 2 * config['surface_rules']))
    rng = np.random.default_rng(seed + 51000)
    reordered = Episodes(original.rules.copy(), original.starts.copy(), rng.random(original.rules.shape).argsort(1))
    renamed, names = renamed_episodes(rng, original)
    reordered.save(data_dir / 'surface_reordered.npz')
    renamed.save(data_dir / 'surface_renamed.npz')
    np.save(data_dir / 'surface_rename_map.npy', names.astype(np.uint8))
    with (root / 'results' / f'surface_seed_{seed}.jsonl').open('w') as out:
        for condition in ('iterated_base', 'rtg_full', 'recurrent'):
            for length in config['surface_lengths']:
                original_pred = predict(condition, reader, rtg, recurrent, step0, original, length).argmax(-1).numpy()
                for transform, transformed in [('row_shuffle', reordered), ('symbol_rename', renamed)]:
                    pred = predict(condition, reader, rtg, recurrent, step0, transformed, length).argmax(-1).numpy()
                    expected = original_pred if transform == 'row_shuffle' else names[np.arange(len(names)), original_pred]
                    target = transformed.target(length).numpy()
                    for i in range(len(original)):
                        json_line(out, {'seed': seed, 'condition': condition, 'length': length,
                                        'transform': transform, 'episode_index': i,
                                        'original_prediction': int(original_pred[i]), 'transformed_prediction': int(pred[i]),
                                        'expected_transformed_prediction': int(expected[i]), 'target': int(target[i]),
                                        'equivariant': bool(pred[i] == expected[i]), 'correct': bool(pred[i] == target[i])})


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--output-root', type=Path, default=PROJECT)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    root = args.output_root.resolve()
    if (root / 'results/accuracy_by_length.csv').exists() or any((root / 'checkpoints').glob('seed_*')):
        raise FileExistsError('Existing campaign evidence: choose a new empty --output-root; never overwrite a prior run.')
    for name in ('attempts', 'checkpoints', 'data', 'results', 'traces/internal_diagnostics'):
        (root / name).mkdir(parents=True, exist_ok=True)
    attempt = root / 'attempts' / args.run_id
    attempt.mkdir(exist_ok=False)
    shutil.copytree(PROJECT / 'src', attempt / 'source_snapshot', ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copy2(args.config, attempt / 'config.json')
    shutil.copy2(PROJECT / 'PLAN.md', attempt / 'PLAN_at_launch.md')
    torch.set_num_threads(config['threads'])
    torch.use_deterministic_algorithms(True)
    env = {'python': sys.version, 'torch': torch.__version__, 'numpy': np.__version__, 'platform': platform.platform(),
           'executable': sys.executable, 'threads': torch.get_num_threads(), 'device': 'cpu',
           'free_bytes_at_launch': shutil.disk_usage(root).free, 'started_utc': now()}
    write_json(attempt / 'environment.json', env)
    (root / 'environment.txt').write_text(json.dumps(env, ensure_ascii=False, indent=2) + '\n')
    append_event(attempt, {'run_id': args.run_id, 'research_id': config['research_id'], 'status': 'RUNNING',
                           'config': str(args.config), 'seeds': config['seeds'], 'output_root': str(root),
                           'command': sys.argv, 'supervision': 'final_answer_only'})
    started = time.monotonic()
    seed_summaries, all_rows, errors = [], [], []
    with (attempt / 'stdout.log').open('w') as stdout, (attempt / 'stderr.log').open('w') as stderr:
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            with (root / 'results/train_curve.csv').open('w', newline='') as train_file, \
                 (root / 'results/accuracy_by_length.csv').open('w', newline='') as accuracy_file, \
                 (root / 'results/per_episode_predictions.jsonl').open('w') as predictions, \
                 (root / 'traces/failures.jsonl').open('w') as failures:
                curve = csv.writer(train_file)
                curve.writerow(['seed', 'arm', 'update', 'split', 'length', 'loss', 'accuracy', 'gradient_norm_before_clip', 'optimizer_step'])
                summary_csv = csv.DictWriter(accuracy_file, fieldnames=['seed', 'condition', 'length', 'correct', 'episodes', 'rules', 'accuracy'])
                summary_csv.writeheader()
                for seed in config['seeds']:
                    try:
                        reader, rtg, recurrent, step0, info, data_dir = run_training(config, root, attempt, seed, curve)
                        append_event(attempt, {'run_id': f'{args.run_id}-S{seed}-EVAL', 'status': 'RUNNING',
                                               'purpose': 'frozen paired test and diagnostics', 'seed': seed})
                        rows = evaluate(config, root, attempt, seed, reader, rtg, recurrent, step0,
                                        data_dir, summary_csv, predictions, failures)
                        seed_summaries.append(info)
                        all_rows.extend(rows)
                        write_json(root / 'results' / f'seed_{seed}_training.json', info)
                    except Exception:
                        error = traceback.format_exc()
                        stderr.write(error + '\n')
                        stderr.flush()
                        errors.append({'seed': seed, 'error': error})
                        append_event(attempt, {'run_id': f'{args.run_id}-S{seed}', 'status': 'FAILED', 'error': error})
                    train_file.flush()
                    accuracy_file.flush()
                    predictions.flush()
                    failures.flush()
                    if time.monotonic() - started > config['max_seconds']:
                        errors.append({'status': 'TIME_BUDGET', 'after_seed': seed})
                        break
                    if sum(p.stat().st_size for p in root.rglob('*') if p.is_file()) > config['max_bytes']:
                        errors.append({'status': 'STORAGE_BUDGET', 'after_seed': seed})
                        break
    complete = len(seed_summaries) == len(config['seeds']) and not errors
    with (root / 'results/train_curve.csv').open() as completed_curve:
        actual_updates = sum(int(row['optimizer_step']) for row in csv.DictReader(completed_curve))
    status = {'run_id': args.run_id, 'status': 'COMPLETED' if complete else 'PARTIAL_FAILED',
              'completed_seeds': [x['seed'] for x in seed_summaries], 'ended_utc': now(),
              'seconds': time.monotonic() - started, 'errors': errors,
              'training_updates': actual_updates,
              'predictions': sum(r['episodes'] for r in all_rows)}
    write_json(attempt / 'completion.json', status)
    append_event(attempt, status)
    print(json.dumps(status, ensure_ascii=False))
    if not complete:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
