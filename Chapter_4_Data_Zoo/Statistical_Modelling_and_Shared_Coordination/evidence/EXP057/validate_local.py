"""EXP057 local verification of saved development results; no test data access."""

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch


here = Path(__file__).resolve().parent
old = here.parent / "STAT-PSYMOE-EXP017-20261002-001/results/native_six/EXP017-NATIVE-TRAIN-001"
metrics = json.loads((here / "METRICS.json").read_text())
source = json.loads((here / "STATE_RECONSTRUCTION.json").read_text())
pred = pd.read_parquet(here / "VALIDATION_PREDICTIONS.parquet")
checks = {
    "reconstructed_original_validation_within_2e_6": max(
        source["old_validation_prediction_max_abs_difference"].values()
    ) <= 2e-6,
    "real_development_unit_counts": (
        source["train_pairs"], source["validation_pairs"],
        source["train_targets"], source["validation_targets"],
        source["train_events"], source["validation_events"],
    ) == (17702, 4132, 990, 212, 916, 220),
    "nine_expected_new_models_only": set(metrics["arms"]) == {"B16", "C32", "F32"} and
        len(list((here / "MODEL_STATES").glob("*.pt"))) == 9,
    "all_saved_predictions_recompute_reported_loss": True,
    "all_checkpoint_shapes_and_parameter_counts_match": True,
    "all_best_epochs_match_traces": True,
    "B16_epoch_1000_matches_original_traces": True,
    "frozen_gate_recomputes": True,
}
for arm, seeded in metrics["arms"].items():
    for seed, item in seeded.items():
        probability = pred[f"{arm}_seed_{seed}"].to_numpy(float)
        y = pred.label.to_numpy(float)
        calculated = float(np.mean(-(
            y * np.log(np.clip(probability, 1e-7, 1 - 1e-7)) +
            (1 - y) * np.log(np.clip(1 - probability, 1e-7, 1 - 1e-7))
        )))
        checks["all_saved_predictions_recompute_reported_loss"] &= abs(
            calculated - item["validation_logloss"]
        ) < 2e-7
        rows = list(csv.DictReader((here / "TRACES" / f"{arm}_seed_{seed}.csv").open()))
        losses = np.asarray([float(row["validation_logloss"]) for row in rows])
        checks["all_best_epochs_match_traces"] &= (
            len(rows) == item["epochs_run"] and
            abs(float(losses[item["best_epoch"] - 1]) - item["best_validation_logits_loss"]) < 1e-7 and
            item["best_validation_logits_loss"] <= float(losses.min()) + 1e-7
        )
        checkpoint = torch.load(here / "MODEL_STATES" / f"{arm}_seed_{seed}.pt",
                                map_location="cpu", weights_only=True)
        parameters = checkpoint["state_dict"]
        checks["all_checkpoint_shapes_and_parameter_counts_match"] &= (
            tuple(parameters["core.0.weight"].shape) == tuple(item["core_weight_shape"]) and
            sum(p.numel() for p in parameters.values()) == item["total_parameters"] and
            checkpoint["best_epoch"] == item["best_epoch"]
        )
        if arm == "B16":
            original = list(csv.DictReader((old / f"training_trace_seed_{seed}.csv").open()))
            checks["B16_epoch_1000_matches_original_traces"] &= abs(
                float(rows[999]["validation_logloss"]) -
                float(original[999]["validation_logloss"])
            ) < 2e-6
for arm in ("C32", "F32"):
    differences = [metrics["arms"][arm][str(seed)]["validation_logloss"] -
                   metrics["arms"]["B16"][str(seed)]["validation_logloss"]
                   for seed in (101, 202, 303)]
    expected = float(np.median(differences)) <= -0.0010 and sum(
        value <= -0.0005 for value in differences
    ) >= 2
    checks["frozen_gate_recomputes"] &= expected == metrics["gates"][arm]["gate_pass"]
result = {"run_id": "EXP057-CAPACITY-001", "checks": checks,
          "passed": sum(bool(x) for x in checks.values()), "total": len(checks),
          "scope": "EXP057 validation predictions, nine saved new states/traces, original B16 training traces and original validation reconstruction summary; no test data or global suite"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
