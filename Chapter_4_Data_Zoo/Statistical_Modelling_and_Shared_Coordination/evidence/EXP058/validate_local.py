"""EXP058 local saved-result checks; no test data access."""

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch


here = Path(__file__).resolve().parent
old = here.parent / "STAT-PSYMOE-EXP057-20261002-001"
metrics = json.loads((here / "METRICS.json").read_text())
prior = json.loads((old / "METRICS.json").read_text())
source = json.loads((here / "STATE_RECONSTRUCTION.json").read_text())
prediction = pd.read_parquet(here / "VALIDATION_PREDICTIONS.parquet")
checks = {
    "original_validation_state_reconstruction_passes": max(
        source["old_validation_prediction_max_abs_difference"].values()
    ) <= 2e-6,
    "three_new_checkpoints_only": len(list((here / "MODEL_STATES").glob("*.pt"))) == 3,
    "real_development_support_unchanged": (source["train_pairs"], source["validation_pairs"],
                                            source["train_targets"], source["validation_targets"]) ==
                                           (17702, 4132, 990, 212),
    "first_saved_epochs_identical": True,
    "saved_validation_predictions_match_losses": True,
    "checkpoints_match_16D_architecture": True,
    "best_epochs_match_traces": True,
    "predeclared_gate_recomputes": True,
}
for seed in (101, 202, 303):
    detail = metrics["new_models"][str(seed)]
    current = list(csv.DictReader((here / "TRACES" / f"B16_seed_{seed}.csv").open()))
    original = list(csv.DictReader((old / "TRACES" / f"B16_seed_{seed}.csv").open()))
    checks["first_saved_epochs_identical"] &= len(current) >= len(original) and all(
        abs(float(a[field]) - float(b[field])) <= 2e-6
        for a, b in zip(current, original)
        for field in ("train_logloss", "validation_logloss")
    )
    y = prediction.label.to_numpy(float)
    p = prediction[f"B16_long_seed_{seed}"].to_numpy(float)
    recomputed = float(np.mean(-(
        y * np.log(np.clip(p, 1e-7, 1 - 1e-7)) +
        (1 - y) * np.log(np.clip(1 - p, 1e-7, 1 - 1e-7))
    )))
    checks["saved_validation_predictions_match_losses"] &= abs(
        recomputed - detail["validation_logloss"]
    ) <= 2e-7
    checkpoint = torch.load(here / "MODEL_STATES" / f"B16_seed_{seed}.pt",
                            map_location="cpu", weights_only=True)
    state = checkpoint["state_dict"]
    checks["checkpoints_match_16D_architecture"] &= (
        tuple(state["core.0.weight"].shape) == (16, 16) and
        sum(p.numel() for p in state.values()) == 769 and
        checkpoint["best_epoch"] == detail["best_epoch"]
    )
    losses = np.asarray([float(row["validation_logloss"]) for row in current])
    checks["best_epochs_match_traces"] &= (
        len(current) == detail["epochs_run"] and
        abs(float(losses[detail["best_epoch"] - 1]) - detail["best_validation_logits_loss"]) <= 1e-7 and
        detail["best_validation_logits_loss"] <= float(losses.min()) + 1e-7
    )
improvements = [prior["arms"]["B16"][str(seed)]["validation_logloss"] -
                metrics["new_models"][str(seed)]["validation_logloss"]
                for seed in (101, 202, 303)]
recomputed_gate = float(np.median(improvements)) >= 0.0003 and sum(
    value >= 0.0002 for value in improvements
) >= 2
checks["predeclared_gate_recomputes"] &= recomputed_gate == metrics["gate"]["pass"]
result = {"run_id": "EXP058-OPTIMIZATION-001", "checks": checks,
          "passed": sum(bool(value) for value in checks.values()), "total": len(checks),
          "scope": "three new B16 states/traces and validation predictions, EXP057 development traces/metrics; no test or global suite"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
