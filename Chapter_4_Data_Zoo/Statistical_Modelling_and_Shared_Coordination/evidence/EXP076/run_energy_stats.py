"""EXP076 fixed real temporal statistical comparison; no original data copies."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "STAT-PSYMOE-EXP075-20261002-001"
sys.path.insert(0, str(SOURCE_DIR))
from audit_energy_source import INDOOR, WEATHER, REQUIRED, fetch_csv  # noqa: E402

SEED = 20261002
LAGS = (0, 1, 3, 6, 12, 144)
MODES = ("AR", "INDOOR", "WEATHER", "JOINT")
TIE_PRIORITY = {"WEATHER": 0, "INDOOR": 1, "JOINT": 2}


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_data() -> tuple[list[datetime], dict[str, np.ndarray], dict]:
    raw, download_bytes, csv_member, _ = fetch_csv()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    columns = list(reader.fieldnames or [])
    if any(name not in columns for name in REQUIRED):
        raise ValueError("required official columns unavailable")
    dates = []
    values = {name: [] for name in REQUIRED if name != "date"}
    for row in reader:
        dates.append(datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S"))
        for name in values:
            values[name].append(float(row[name]))
    arrays = {name: np.asarray(rows, dtype=np.float64) for name, rows in values.items()}
    meta = {"download_bytes": download_bytes, "csv_member": csv_member,
            "source_rows": len(dates), "source_first_date": dates[0].isoformat(sep=" "),
            "source_last_date": dates[-1].isoformat(sep=" "),
            "all_required_finite": all(np.all(np.isfinite(a)) for a in arrays.values())}
    return dates, arrays, meta


def daily_errors(dates: list[datetime], target_indices: np.ndarray, y: np.ndarray,
                 predictions: dict[str, np.ndarray]) -> tuple[list[dict], dict]:
    grouped = defaultdict(list)
    for local, j in enumerate(target_indices):
        grouped[dates[int(j)].date().isoformat()].append(local)
    output = []
    for day, locals_ in sorted(grouped.items()):
        if len(locals_) < 100:
            continue
        chosen = np.asarray(locals_, dtype=int)
        row = {"target_date": day, "pairs": len(chosen)}
        for name, pred in predictions.items():
            row[f"{name}_mae_wh"] = float(np.mean(np.abs(pred[chosen] - y[chosen])))
        output.append(row)
    discarded = {day: len(indices) for day, indices in sorted(grouped.items()) if len(indices) < 100}
    return output, {"all_target_dates": len(grouped), "evaluation_dates": len(output),
                    "discarded_partial_target_dates": discarded}


def write_daily(name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("no full target dates")
    with (HERE / name).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def comparison(rows: list[dict], candidate: str) -> dict:
    ar = np.array([row["AR_mae_wh"] for row in rows], dtype=float)
    cp = np.array([row[f"{candidate}_mae_wh"] for row in rows], dtype=float)
    delta = cp - ar
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(rows), size=(2000, len(rows)))
    ci = np.quantile(delta[picks].mean(axis=1), [0.025, 0.975])
    return {"candidate": candidate, "evaluation_days": len(rows),
            "AR_equal_day_mae_wh": float(ar.mean()),
            "candidate_equal_day_mae_wh": float(cp.mean()),
            "candidate_minus_AR_mae_wh": float(delta.mean()),
            "candidate_relative_mae_gain": float((ar.mean() - cp.mean()) / ar.mean()),
            "paired_day_bootstrap_difference_95pct_ci_wh": list(map(float, ci)),
            "days_candidate_better": int(np.sum(delta < 0)),
            "bootstrap_resamples": 2000, "bootstrap_seed": SEED}


def gate(metrics: dict) -> dict[str, bool]:
    return {"relative_mae_gain_at_least_5pct": metrics["candidate_relative_mae_gain"] >= 0.05,
            "paired_day_ci_upper_below_zero": metrics["paired_day_bootstrap_difference_95pct_ci_wh"][1] < 0,
            "at_least_60pct_days_better": metrics["days_candidate_better"] >= math.ceil(0.6 * metrics["evaluation_days"])}


def main() -> None:
    expected = json.loads((SOURCE_DIR / "SOURCE_MATRIX.json").read_text(encoding="utf-8"))
    dates, values, source = read_data()
    n = len(dates)
    btrain, bval = int(n * .70), int(n * .85)
    one_hour = sum(dates[i + 6] - dates[i] == timedelta(hours=1) for i in range(n - 6))
    checks = {"rows_match": n == expected["source_rows"],
              "first_last_dates_match": source["source_first_date"] == expected["source_first_date"]
                                        and source["source_last_date"] == expected["source_last_date"],
              "target_boundaries_match": btrain == expected["target_position_boundaries"]["train_end_exclusive"]
                                         and bval == expected["target_position_boundaries"]["validation_end_exclusive"],
              "hour_pairs_match": one_hour == expected["valid_one_hour_pairs"],
              "all_required_finite": source["all_required_finite"],
              "strict_ten_minute_steps": all(dates[i + 1] - dates[i] == timedelta(minutes=10) for i in range(n - 1))}
    recheck = {**source, "checks": checks,
               "gate": "SOURCE_STRUCTURE_MATCH" if all(checks.values()) else "STOP_SOURCE_VERSION_DRIFT"}
    write_json("SOURCE_RECHECK.json", recheck)
    if not all(checks.values()):
        print(json.dumps(recheck, indent=2))
        return

    origins = np.arange(144, n - 6, dtype=int)
    targets = origins + 6
    y = values["Appliances"][targets]
    appliance = values["Appliances"]
    lag = np.column_stack([appliance[origins - delta] for delta in LAGS])
    target_hour = np.array([dates[int(j)].hour + dates[int(j)].minute / 60 for j in targets])
    target_dow = np.array([dates[int(j)].weekday() for j in targets])
    calendar = np.column_stack((np.sin(2 * np.pi * target_hour / 24),
                                np.cos(2 * np.pi * target_hour / 24),
                                np.sin(2 * np.pi * target_dow / 7),
                                np.cos(2 * np.pi * target_dow / 7)))
    ar_features = np.hstack((lag, calendar))
    indoor = np.column_stack([values[name][origins - 6] for name in INDOOR])
    weather = np.column_stack([values[name][origins - 6] for name in WEATHER])
    feature_sets = {"AR": ar_features,
                    "INDOOR": np.hstack((ar_features, indoor)),
                    "WEATHER": np.hstack((ar_features, weather)),
                    "JOINT": np.hstack((ar_features, indoor, weather))}
    train, validation, test = targets < btrain, (targets >= btrain) & (targets < bval), targets >= bval
    split_counts = {"train": int(train.sum()), "validation": int(validation.sum()), "test": int(test.sum())}
    if not np.all(np.isfinite(y)) or not all(np.all(np.isfinite(x)) for x in feature_sets.values()):
        raise ValueError("nonfinite real model matrix")
    fitted = {}
    fit_times = {}
    val_preds = {}
    for name in MODES:
        model = HistGradientBoostingRegressor(
            loss="absolute_error", max_iter=200, max_leaf_nodes=15,
            min_samples_leaf=50, learning_rate=0.05, l2_regularization=10,
            early_stopping=False, random_state=SEED,
        )
        started = time.perf_counter()
        model.fit(feature_sets[name][train], y[train])
        fit_times[name] = time.perf_counter() - started
        fitted[name] = model
        val_preds[name] = np.maximum(0, model.predict(feature_sets[name][validation]))
    val_preds["PERSIST"] = appliance[origins[validation]]
    val_daily, val_day_meta = daily_errors(dates, targets[validation], y[validation], val_preds)
    write_daily("VALIDATION_DAILY_ERRORS.csv", val_daily)
    mean_mae = {name: float(np.mean([row[f"{name}_mae_wh"] for row in val_daily]))
                for name in (*MODES, "PERSIST")}
    selected = min(("WEATHER", "INDOOR", "JOINT"), key=lambda name: (mean_mae[name], TIE_PRIORITY[name]))
    val_metrics = comparison(val_daily, selected)
    val_metrics.update({"validation_equal_day_mae_wh_by_model": mean_mae,
                        "validation_day_support": val_day_meta,
                        "source_recheck": recheck["gate"],
                        "model_sample_counts": split_counts,
                        "feature_dimensions": {name: x.shape[1] for name, x in feature_sets.items()},
                        "fit_seconds": fit_times,
                        "model_definition": "fixed HistGradientBoostingRegressor absolute_error, 200 iterations, leaves15, min_leaf50, lr0.05, L2=10, no early stopping",
                        "test_performance_scored": False})
    val_metrics["gates"] = gate(val_metrics)
    val_metrics["decision"] = ("PASS_ADDITIONAL_CHANNEL_DEV_GATE" if all(val_metrics["gates"].values())
                               else "STOP_ADDITIONAL_CHANNEL_DEV_GATE")
    write_json("VALIDATION_METRICS.json", val_metrics)
    print(json.dumps({"validation": {k: val_metrics[k] for k in (
        "validation_equal_day_mae_wh_by_model", "candidate", "candidate_relative_mae_gain",
        "paired_day_bootstrap_difference_95pct_ci_wh", "days_candidate_better",
        "evaluation_days", "gates", "decision")}}, indent=2))
    if val_metrics["decision"] != "PASS_ADDITIONAL_CHANNEL_DEV_GATE":
        return

    test_preds = {"AR": np.maximum(0, fitted["AR"].predict(feature_sets["AR"][test])),
                  selected: np.maximum(0, fitted[selected].predict(feature_sets[selected][test])),
                  "PERSIST": appliance[origins[test]]}
    test_daily, test_day_meta = daily_errors(dates, targets[test], y[test], test_preds)
    write_daily("TEST_DAILY_ERRORS.csv", test_daily)
    test_metrics = comparison(test_daily, selected)
    test_metrics.update({"test_day_support": test_day_meta, "development_gate": val_metrics["decision"],
                         "test_equal_day_mae_wh_by_scored_model": {
                             name: float(np.mean([row[f"{name}_mae_wh"] for row in test_daily]))
                             for name in test_preds}, "test_performance_scored": True})
    test_metrics["gates"] = gate(test_metrics)
    test_metrics["decision"] = ("ADDITIONAL_CHANNEL_TEMPORAL_GAIN_SUPPORTED_WITHIN_ONE_HOUSE"
                                if all(test_metrics["gates"].values()) else "NO_TEMPORAL_HOLDOUT_CHANNEL_GAIN")
    write_json("TEST_METRICS.json", test_metrics)
    print(json.dumps({"test": {k: test_metrics[k] for k in (
        "test_equal_day_mae_wh_by_scored_model", "candidate", "candidate_relative_mae_gain",
        "paired_day_bootstrap_difference_95pct_ci_wh", "days_candidate_better",
        "evaluation_days", "gates", "decision")}}, indent=2))


if __name__ == "__main__":
    main()
