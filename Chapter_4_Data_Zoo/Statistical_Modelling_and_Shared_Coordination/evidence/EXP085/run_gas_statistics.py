"""EXP085: frozen independent-trial gas identity statistical comparison."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, log_loss
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP084-20261002-001"
sys.path.insert(0, str(PARENT))
from audit_gas_trials import SPLIT, URL, audit_member, parse_path  # noqa: E402


FEATURES = ["temp_base", "temp_delta", "humidity_base", "humidity_delta"] + [
    f"sensor_{sensor}_{part}" for sensor in range(1, 9) for part in ("base", "delta")]
COMMON = FEATURES[:4]


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def source_and_features() -> list[dict] | None:
    with urllib.request.urlopen(URL, timeout=90) as response:
        blob = response.read(30_000_001)
    if len(blob) > 30_000_000:
        raise ValueError("network budget exceeded")
    old = json.loads((PARENT / "SOURCE_MATRIX.json").read_text())
    trials = []
    config_counts = Counter()
    raw_ids = set()
    down_ids = set()
    qa = []
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        raw = [name for name in names if "raw" in name.split("/")[0].lower()]
        down = [name for name in names if "raw" not in name.split("/")[0].lower()]
        raw_ids = {parse_path(name)[0] for name in raw if parse_path(name) is not None}
        down_ids = {parse_path(name)[0] for name in down if parse_path(name) is not None}
        for name in down:
            parts = parse_path(name)
            if parts is None:
                continue
            trial_id, et, gas, level = parts
            configuration = f"Et_{et}_{gas}_{level}"
            config_counts[configuration] += 1
            source_row = audit_member(archive, name)
            qa.append(source_row)
            if level == "N":
                continue
            arrays = []
            for line in archive.read(name).decode("utf-8-sig", errors="replace").splitlines():
                tokens = [token for token in SPLIT.split(line.strip()) if token]
                if len(tokens) != 11:
                    continue
                try:
                    values = [float(token) for token in tokens]
                except ValueError:
                    continue
                if all(math.isfinite(value) for value in values):
                    arrays.append(values)
            array = np.asarray(arrays, dtype=float)
            baseline = np.median(array[(array[:, 0] >= 0) & (array[:, 0] < 60), 1:], axis=0)
            exposure = np.median(array[(array[:, 0] >= 60) & (array[:, 0] < 240), 1:], axis=0)
            feat = np.empty(20, dtype=float)
            feat[0:4] = [baseline[0], exposure[0] - baseline[0], baseline[1], exposure[1] - baseline[1]]
            for sensor in range(8):
                feat[4 + 2 * sensor:6 + 2 * sensor] = [baseline[sensor + 2], exposure[sensor + 2] - baseline[sensor + 2]]
            row = {"trial_id": trial_id, "configuration": configuration,
                   "label": 0 if gas == "CO" else 1, "second_gas": gas}
            row.update({key: float(value) for key, value in zip(FEATURES, feat)})
            trials.append(row)
    nonzero_counts = Counter(row["configuration"] for row in trials)
    gases = Counter(row["second_gas"] for row in trials)
    summary = {
        "total_nonempty_rows": sum(row["nonempty_rows"] for row in qa),
        "total_invalid_rows": sum(row["invalid_rows"] for row in qa),
        "min_time_span_s": min(row["time_span_s"] for row in qa),
        "min_baseline_valid_rows": min(row["baseline_valid_rows_0_60s"] for row in qa),
        "min_exposure_valid_rows": min(row["exposure_valid_rows_60_240s"] for row in qa),
        "min_eight_sensor_finite_fraction": min(row["eight_sensor_finite_fraction"] for row in qa),
        "equal_time_steps": sum(row["equal_time_steps"] for row in qa),
        "backwards_time_steps": sum(row["backwards_time_steps"] for row in qa),
        "nonmonotonic_trial_ids": [parse_path(row["path"])[0] for row in qa if not row["nondecreasing_time"]],
    }
    checks = {
        "exact_raw_down_id_support": len(raw) == len(down) == 180 and len(raw_ids) == len(down_ids) == 180 and raw_ids == down_ids,
        "all_configurations_match_exp084": dict(sorted(config_counts.items())) == old["all_configurations_counts"],
        "nonzero_configurations_match_exp084": dict(sorted(nonzero_counts.items())) == old["nonzero_second_gas_configuration_counts"],
        "nonzero_gas_balance_match_exp084": dict(gases) == old["nonzero_second_gas_trial_counts"],
        "trial_numeric_summary_match_exp084": summary == old["trial_numeric_summary"],
        "feature_values_finite": len(trials) == 144 and all(all(math.isfinite(row[name]) for name in FEATURES) for row in trials),
    }
    write_json("SOURCE_RECHECK.json", {"official_zip_url": URL, "download_bytes": len(blob),
                                      "raw_trial_count": len(raw), "downsampled_trial_count": len(down),
                                      "nonzero_trial_count": len(trials), "checks": checks,
                                      "gate_result": "SOURCE_VERSION_MATCH" if all(checks.values()) else "STOP_SOURCE_DRIFT",
                                      "model_fits": 0})
    return trials if all(checks.values()) else None


def assign_splits(trials: list[dict]) -> bool:
    by_config = defaultdict(list)
    for trial in trials:
        by_config[trial["configuration"]].append(trial)
    for entries in by_config.values():
        entries.sort(key=lambda row: row["trial_id"])
        for rank, row in enumerate(entries):
            row["split"] = "train" if rank < 4 else "validation" if rank == 4 else "test"
    counts = {split: Counter(row["second_gas"] for row in trials if row["split"] == split)
              for split in ("train", "validation", "test")}
    checks = {
        "exact_24_configs_six_trials": len(by_config) == 24 and all(len(entries) == 6 for entries in by_config.values()),
        "train_48_48": dict(counts["train"]) == {"CO": 48, "ME": 48},
        "validation_12_12": dict(counts["validation"]) == {"CO": 12, "ME": 12},
        "test_12_12": dict(counts["test"]) == {"CO": 12, "ME": 12},
        "unique_trial_ids": len({row["trial_id"] for row in trials}) == 144,
    }
    write_json("MODEL_SUPPORT.json", {"configuration_count": len(by_config),
                                      "trial_counts_by_split_and_gas": {split: dict(counter) for split, counter in counts.items()},
                                      "checks": checks, "gate_result": "MODEL_SUPPORT_PASS" if all(checks.values()) else "STOP_TRIAL_MODEL_SUPPORT",
                                      "model_fits": 0})
    return all(checks.values())


def matrix(rows: list[dict], columns: list[str]) -> np.ndarray:
    return np.asarray([[row[name] for name in columns] for row in rows], dtype=float)


def new_model():
    return make_pipeline(StandardScaler(), LogisticRegression(C=0.1, solver="lbfgs", max_iter=2000,
                                                             random_state=20261002))


def score(rows: list[dict], single_prob: np.ndarray, multi_prob: np.ndarray, prefix: str) -> dict:
    y = np.asarray([row["label"] for row in rows], dtype=int)
    eps = 1e-15
    s = np.clip(single_prob, eps, 1 - eps)
    m = np.clip(multi_prob, eps, 1 - eps)
    single_losses = -(y * np.log(s) + (1 - y) * np.log(1 - s))
    multi_losses = -(y * np.log(m) + (1 - y) * np.log(1 - m))
    diff = multi_losses - single_losses
    with (HERE / f"{prefix}_PREDICTIONS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["trial_id", "configuration", "true_gas", "p_me_single", "p_me_multi", "loss_single", "loss_multi"])
        for row, p_s, p_m, loss_s, loss_m in zip(rows, s, m, single_losses, multi_losses):
            writer.writerow([row["trial_id"], row["configuration"], row["second_gas"],
                             float(p_s), float(p_m), float(loss_s), float(loss_m)])
    draws = np.random.default_rng(20261002).integers(0, len(diff), size=(2000, len(diff)))
    ci = np.quantile(np.mean(diff[draws], axis=1), [0.025, 0.975]).tolist()
    bacc_single = balanced_accuracy_score(y, s >= .5)
    bacc_multi = balanced_accuracy_score(y, m >= .5)
    result = {"independent_trials": len(rows), "co_trials": int(np.sum(y == 0)), "me_trials": int(np.sum(y == 1)),
              "single_logloss": float(np.mean(single_losses)), "multi_logloss": float(np.mean(multi_losses)),
              "multi_minus_single_logloss": float(np.mean(diff)),
              "absolute_logloss_improvement": float(np.mean(single_losses) - np.mean(multi_losses)),
              "paired_trial_bootstrap_2000_ci95_for_multi_minus_single": ci,
              "single_balanced_accuracy": float(bacc_single), "multi_balanced_accuracy": float(bacc_multi),
              "balanced_accuracy_gain": float(bacc_multi - bacc_single),
              "trials_multi_lower_loss": int(np.sum(diff < 0))}
    checks = {"logloss_improvement_at_least_0_05": result["absolute_logloss_improvement"] >= .05,
              "bootstrap_upper_below_zero": ci[1] < 0,
              "balanced_accuracy_gain_at_least_0_05": result["balanced_accuracy_gain"] >= .05}
    result["checks"] = checks
    result["three_gate_pass"] = all(checks.values())
    write_json(f"{prefix}_METRICS.json", result)
    return result


def main() -> None:
    trials = source_and_features()
    if trials is None:
        print("STOP_SOURCE_DRIFT")
        return
    if not assign_splits(trials):
        print("STOP_TRIAL_MODEL_SUPPORT")
        return
    trials.sort(key=lambda row: row["trial_id"])
    with (HERE / "TRIAL_FEATURES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["trial_id", "configuration", "label", "second_gas", "split", *FEATURES])
        writer.writeheader()
        writer.writerows(trials)
    train = [row for row in trials if row["split"] == "train"]
    validation = [row for row in trials if row["split"] == "validation"]
    test = [row for row in trials if row["split"] == "test"]
    y_train = np.asarray([row["label"] for row in train], dtype=int)
    folds = list(StratifiedKFold(n_splits=4, shuffle=True, random_state=20261002).split(np.zeros(len(train)), y_train))
    cv_losses = {}
    for sensor in range(1, 9):
        columns = COMMON + [f"sensor_{sensor}_base", f"sensor_{sensor}_delta"]
        x = matrix(train, columns)
        pooled = np.empty(len(train), dtype=float)
        for fit_idx, valid_idx in folds:
            model = new_model()
            model.fit(x[fit_idx], y_train[fit_idx])
            pooled[valid_idx] = model.predict_proba(x[valid_idx])[:, 1]
        cv_losses[str(sensor)] = float(log_loss(y_train, pooled, labels=[0, 1]))
    chosen = min(range(1, 9), key=lambda sensor: (cv_losses[str(sensor)], sensor))
    single_columns = COMMON + [f"sensor_{chosen}_base", f"sensor_{chosen}_delta"]
    multi_columns = FEATURES
    write_json("TRAIN_CV_SELECTION.json", {"train_trials": len(train), "cv_folds": 4,
                                           "candidate_sensor_cv_logloss": cv_losses,
                                           "selected_sensor": chosen, "single_features": single_columns,
                                           "multi_features": multi_columns,
                                           "fixed_c": .1, "cv_model_fits": 32, "final_model_fits": 2})
    single = new_model()
    single.fit(matrix(train, single_columns), y_train)
    multi = new_model()
    multi.fit(matrix(train, multi_columns), y_train)
    validation_metrics = score(validation,
                               single.predict_proba(matrix(validation, single_columns))[:, 1],
                               multi.predict_proba(matrix(validation, multi_columns))[:, 1], "VALIDATION")
    if not validation_metrics["three_gate_pass"]:
        print(json.dumps({"gate_result": "STOP_MULTISENSOR_DEV_GATE", "selected_single_sensor": chosen,
                          "validation_metrics": validation_metrics, "test_performance_scores": 0}, indent=2))
        return
    test_metrics = score(test, single.predict_proba(matrix(test, single_columns))[:, 1],
                         multi.predict_proba(matrix(test, multi_columns))[:, 1], "TEST")
    print(json.dumps({"gate_result": "MULTISENSOR_TRIAL_REPLICATION_GAIN_WITHIN_ONE_RIG" if test_metrics["three_gate_pass"] else "NO_TEST_MULTISENSOR_GAIN",
                      "selected_single_sensor": chosen, "validation_metrics": validation_metrics,
                      "test_metrics": test_metrics, "test_performance_scores": 1}, indent=2))


if __name__ == "__main__":
    main()
