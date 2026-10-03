"""Independent local check of EXP085 split, derived predictions, and frozen gates."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.metrics import balanced_accuracy_score


here = Path(__file__).resolve().parent
with (here / "TRIAL_FEATURES.csv").open(newline="") as handle:
    features = list(csv.DictReader(handle))
by_config = defaultdict(list)
for row in features:
    by_config[row["configuration"]].append(row)
split_ok = all(len(group) == 6 and Counter(row["split"] for row in group) == {"train": 4, "validation": 1, "test": 1}
               for group in by_config.values())
selection = json.loads((here / "TRAIN_CV_SELECTION.json").read_text())
chosen = min(range(1, 9), key=lambda sensor: (selection["candidate_sensor_cv_logloss"][str(sensor)], sensor))
checks = {"24_config_trial_split": len(by_config) == 24 and split_ok,
          "144_unique_trials": len(features) == len({row["trial_id"] for row in features}) == 144,
          "train_cv_single_sensor_minimum": chosen == selection["selected_sensor"],
          "source_and_support_gates_passed": all(json.loads((here / name).read_text())["gate_result"] == result for name, result in
                                                 (("SOURCE_RECHECK.json", "SOURCE_VERSION_MATCH"),
                                                  ("MODEL_SUPPORT.json", "MODEL_SUPPORT_PASS"))),
          "test_files_present_only_after_validation_pass": json.loads((here / "VALIDATION_METRICS.json").read_text())["three_gate_pass"] and
                                                   (here / "TEST_METRICS.json").exists() and (here / "TEST_PREDICTIONS.csv").exists()}
for prefix in ("VALIDATION", "TEST"):
    with (here / f"{prefix}_PREDICTIONS.csv").open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    metrics = json.loads((here / f"{prefix}_METRICS.json").read_text())
    y = np.asarray([int(row["true_gas"] == "ME") for row in rows])
    single = np.asarray([float(row["p_me_single"]) for row in rows])
    multi = np.asarray([float(row["p_me_multi"]) for row in rows])
    loss_single = -(y * np.log(single) + (1-y) * np.log(1-single))
    loss_multi = -(y * np.log(multi) + (1-y) * np.log(1-multi))
    diff = loss_multi - loss_single
    draws = np.random.default_rng(20261002).integers(0, len(diff), size=(2000, len(diff)))
    ci = np.quantile(np.mean(diff[draws], axis=1), [0.025, 0.975])
    bacc_gain = balanced_accuracy_score(y, multi >= .5) - balanced_accuracy_score(y, single >= .5)
    checks[f"{prefix.lower()}_24_balanced_trials"] = (len(rows) == 24 and sum(y) == 12 and
        len({row["trial_id"] for row in rows}) == 24)
    checks[f"{prefix.lower()}_point_metrics"] = (np.isclose(np.mean(loss_single), metrics["single_logloss"]) and
        np.isclose(np.mean(loss_multi), metrics["multi_logloss"]) and np.isclose(bacc_gain, metrics["balanced_accuracy_gain"]))
    checks[f"{prefix.lower()}_bootstrap"] = np.allclose(ci, metrics["paired_trial_bootstrap_2000_ci95_for_multi_minus_single"])
    expected = {"logloss_improvement_at_least_0_05": -np.mean(diff) >= .05,
                "bootstrap_upper_below_zero": ci[1] < 0,
                "balanced_accuracy_gain_at_least_0_05": bacc_gain >= .05}
    checks[f"{prefix.lower()}_frozen_gates"] = metrics["checks"] == expected and metrics["three_gate_pass"] == all(expected.values())
checks["validation_pass_test_fail"] = json.loads((here / "VALIDATION_METRICS.json").read_text())["three_gate_pass"] and not json.loads((here / "TEST_METRICS.json").read_text())["three_gate_pass"]
result = {"checks": {key: bool(value) for key, value in checks.items()},
          "passed": sum(bool(value) for value in checks.values()), "total": len(checks),
          "local_validation": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
