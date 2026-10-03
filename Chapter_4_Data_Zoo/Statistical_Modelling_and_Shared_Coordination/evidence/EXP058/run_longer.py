#!/usr/bin/env python3
"""EXP058 longer-budget B16 development test using EXP057's original training code."""

import csv
import json
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
import torch


HERE = Path(__file__).resolve().parent
P57 = HERE.parent / "STAT-PSYMOE-EXP057-20261002-001"
sys.path.insert(0, str(P57))
import run_capacity as capacity  # noqa: E402

RUN_ID = "EXP058-OPTIMIZATION-001"
SEEDS = (101, 202, 303)


def main():
    for name in ("STATE_RECONSTRUCTION.json", "METRICS.json", "FAILURE.json"):
        if (HERE / name).exists():
            raise FileExistsError(f"Preserve existing attempt output: {name}")
    for name in ("MODEL_STATES", "TRACES", "DIAGNOSTICS"):
        (HERE / name).mkdir(exist_ok=False)
    capacity.HERE = HERE
    capacity.RUN_ID = RUN_ID
    capacity.MAX_EPOCHS = 4000
    capacity.PATIENCE = 500
    capacity.MAX_SECONDS = 45 * 60
    torch.set_num_threads(4)
    started = time.monotonic()
    dev, y, index, states = capacity.make_development_states()
    tr, va = index["train"], index["validation"]
    device = "mps" if torch.backends.mps.is_available() else (
        "cuda" if torch.cuda.is_available() else "cpu"
    )
    print("STATES_RECONSTRUCTED", len(tr), len(va), device, flush=True)
    old = json.loads((P57 / "METRICS.json").read_text())
    details = {}
    preds = dev.iloc[va][["targetId", "diseaseId", "label"]].copy().reset_index(drop=True)
    prefixes = {}
    for seed in SEEDS:
        result, pred = capacity.fit_one("B16", seed, states["train"], y[tr],
                                        states["validation"], y[va], device, started)
        details[str(seed)] = result
        preds[f"B16_long_seed_{seed}"] = pred
        current = list(csv.DictReader((HERE / "TRACES" / f"B16_seed_{seed}.csv").open()))
        prior = list(csv.DictReader((P57 / "TRACES" / f"B16_seed_{seed}.csv").open()))
        if len(current) < len(prior):
            raise RuntimeError(f"Longer run stopped before earlier trace for seed {seed}")
        max_difference = max(abs(float(a[field]) - float(b[field]))
                             for a, b in zip(current, prior)
                             for field in ("train_logloss", "validation_logloss"))
        prefixes[str(seed)] = {"compared_epochs": len(prior), "max_abs_difference": max_difference}
        if max_difference > 2e-6:
            raise RuntimeError(f"Earlier training prefix mismatch for seed {seed}: {max_difference}")
    improvements = {str(seed): old["arms"]["B16"][str(seed)]["validation_logloss"] -
                    details[str(seed)]["validation_logloss"] for seed in SEEDS}
    median = float(np.median(list(improvements.values())))
    enough = sum(value >= 0.0002 for value in improvements.values())
    gate = {"comparison": "B16_4000_minus_B16_2000_as_improvement",
            "same_seed_improvements": improvements,
            "median_improvement": median,
            "seeds_improving_by_at_least_0_0002": enough,
            "pass": median >= 0.0003 and enough >= 2}
    preds.to_parquet(HERE / "VALIDATION_PREDICTIONS.parquet", index=False)
    metrics = {"run_id": RUN_ID,
               "qualification": "retrospective development; no old test evaluation",
               "device": device, "model": "B16 fixed 769 parameters",
               "optimizer": "Adam", "learning_rate": 0.002,
               "max_epochs": 4000, "patience": 500,
               "seeds": list(SEEDS), "real_train_pairs": len(tr),
               "real_validation_pairs": len(va),
               "new_models": details, "prefix_checks": prefixes,
               "gate": gate,
               "F32_2000_prior_validation_median": float(np.median([
                   old["arms"]["F32"][str(seed)]["validation_logloss"] for seed in SEEDS
               ])),
               "B16_2000_prior_validation_median": float(np.median([
                   old["arms"]["B16"][str(seed)]["validation_logloss"] for seed in SEEDS
               ])),
               "B16_4000_validation_median": float(np.median([
                   details[str(seed)]["validation_logloss"] for seed in SEEDS
               ])),
               "any_best_epoch_at_cap": any(detail["best_epoch"] == 4000
                                            for detail in details.values()),
               "total_seconds": time.monotonic() - started}
    (HERE / "METRICS.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print("GATE", json.dumps(gate), flush=True)
    print("TOTAL_SECONDS", metrics["total_seconds"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not (HERE / "FAILURE.json").exists():
            (HERE / "FAILURE.json").write_text(json.dumps({
                "run_id": RUN_ID, "error_type": type(exc).__name__,
                "error": str(exc), "traceback": traceback.format_exc(),
                "existing_direct_outputs": sorted(p.name for p in HERE.iterdir()),
            }, indent=2) + "\n")
        raise
