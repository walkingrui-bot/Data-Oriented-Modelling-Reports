#!/usr/bin/env python3
"""Post-result, descriptive paired comparisons for EXP017-SOURCE-TRAIN-001."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


RUN = Path(__file__).resolve().parent / "results/source_level_six/EXP017-SOURCE-TRAIN-001"
OUT = RUN / "paired_analysis.json"


def row_loss(label: np.ndarray, pred: np.ndarray) -> np.ndarray:
    pred = np.clip(pred.astype(float), 1e-7, 1 - 1e-7)
    return -(label * np.log(pred) + (1 - label) * np.log1p(-pred))


def paired_difference(df: pd.DataFrame, left: str, right: str, seed: int = 1702) -> dict:
    label = df.label.to_numpy(int)
    difference = row_loss(label, df[left].to_numpy()) - row_loss(label, df[right].to_numpy())
    groups, reverse = np.unique(df.targetId.to_numpy(), return_inverse=True)
    group_sum = np.bincount(reverse, weights=difference, minlength=len(groups))
    group_count = np.bincount(reverse, minlength=len(groups))
    rng = np.random.default_rng(seed)
    boot = np.empty(1000)
    for i in range(len(boot)):
        chosen = rng.integers(0, len(groups), len(groups))
        boot[i] = group_sum[chosen].sum() / group_count[chosen].sum()
    return {
        "left_minus_right_logloss": float(difference.mean()),
        "target_grouped_bootstrap_95ci": np.quantile(boot, [0.025, 0.975]).tolist(),
        "target_groups": len(groups),
        "resamples": len(boot),
        "post_result_descriptive": True,
    }


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"Existing result is preserved: {OUT}")
    df = pd.read_parquet(RUN / "test_predictions.parquet")
    comparisons = [
        ("stat_moe", "additive_logistic"),
        ("stat_moe", "empirical_bayes"),
        ("ganglion_seed_101", "stat_moe"),
        ("ganglion_seed_202", "stat_moe"),
        ("ganglion_seed_303", "stat_moe"),
    ]
    paired = {f"{left}_minus_{right}": paired_difference(df, left, right) for left, right in comparisons}
    traces = {}
    for seed in (101, 202, 303):
        trace = pd.read_csv(RUN / f"training_trace_seed_{seed}.csv")
        tail = trace.tail(50)
        traces[str(seed)] = {
            "epochs_run": len(trace),
            "validation_logloss_first": float(trace.validation_logloss.iloc[0]),
            "validation_logloss_last": float(trace.validation_logloss.iloc[-1]),
            "last_50_epoch_validation_slope_per_epoch": float(np.polyfit(tail.epoch, tail.validation_logloss, 1)[0]),
            "last_50_epoch_train_slope_per_epoch": float(np.polyfit(tail.epoch, tail.train_logloss, 1)[0]),
        }
    result = {
        "run_id": "EXP017-ANALYSIS-001",
        "parent_run": "EXP017-SOURCE-TRAIN-001",
        "paired_comparisons": paired,
        "convergence_trace": traces,
        "interpretation_boundary": "Post-result descriptive analysis on the original fixed test predictions; no model selection or retraining here.",
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
