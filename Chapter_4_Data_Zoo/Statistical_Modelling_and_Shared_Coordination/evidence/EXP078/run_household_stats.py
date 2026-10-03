"""EXP078: frozen four-arm year-held-out real household power comparison."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import time
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "STAT-PSYMOE-EXP077-20261002-001"
sys.path.insert(0, str(SOURCE_DIR))
from audit_household_source import URL, MEMBER, COLUMNS, NUMERIC, parse_date  # noqa: E402

SEED = 20261002
LAG_HOURS = (0, 1, 2, 24, 168)
MODES = ("AR", "SUB", "ELECTRICAL", "JOINT")
TIE_PRIORITY = {"ELECTRICAL": 0, "SUB": 1, "JOINT": 2}


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_hourly() -> tuple[dict[datetime, tuple[float, ...] | None], dict]:
    with urllib.request.urlopen(URL, timeout=120) as response:
        archive_bytes = response.read(30_000_001)
    if len(archive_bytes) > 30_000_000:
        raise ValueError("network budget exceeded")
    hourly = {}
    row_count = 0
    first_pair = None
    last_pair = None
    bad_width = 0
    year_counts = defaultdict(int)
    hourly_missing = defaultdict(int)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = archive.namelist()
        if MEMBER not in members:
            raise ValueError("source member absent")
        with archive.open(MEMBER) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig") as handle:
            header = handle.readline().strip().split(";")
            for line in handle:
                row_count += 1
                parts = line.rstrip("\r\n").split(";")
                if len(parts) != len(COLUMNS):
                    bad_width += 1
                    continue
                date_pair = (parts[0], parts[1])
                if first_pair is None:
                    first_pair = date_pair
                last_pair = date_pair
                # Year extraction does not use measurements or model outcomes.
                year_counts[int(parts[0].split("/")[-1])] += 1
                if parts[1] != "00:00:00" and not parts[1].endswith(":00:00"):
                    continue
                stamp = parse_date(*date_pair)
                values = []
                for raw in parts[2:]:
                    if raw in ("", "?"):
                        values = None
                        break
                    try:
                        number = float(raw)
                    except ValueError:
                        values = None
                        break
                    if not math.isfinite(number) or number < 0:
                        values = None
                        break
                    values.append(number)
                if values is None:
                    hourly_missing[stamp.year] += 1
                hourly[stamp] = tuple(values) if values is not None else None
    meta = {
        "download_bytes": len(archive_bytes), "archive_members": members,
        "source_rows": row_count, "source_bad_width_rows": bad_width,
        "source_first_date": parse_date(*first_pair).isoformat(sep=" "),
        "source_last_date": parse_date(*last_pair).isoformat(sep=" "),
        "source_columns": header,
        "source_rows_by_year": dict(sorted(year_counts.items())),
        "hourly_calendar_keys": len(hourly),
        "hourly_missing_or_invalid_by_year": dict(sorted(hourly_missing.items())),
    }
    return hourly, meta


def build_samples(hourly: dict) -> dict:
    output = {key: [] for key in ("AR", "SUB_EXTRA", "ELECTRICAL_EXTRA", "y", "origin_power", "target_date", "target_year")}
    candidate_hours = defaultdict(int)
    excluded_incomplete = defaultdict(int)
    for origin in sorted(hourly):
        target = origin + timedelta(hours=1)
        if target.year not in (2007, 2008, 2009, 2010):
            continue
        candidate_hours[target.year] += 1
        target_row = hourly.get(target)
        lag_rows = [hourly.get(origin - timedelta(hours=lag)) for lag in LAG_HOURS]
        if target_row is None or any(row is None for row in lag_rows):
            excluded_incomplete[target.year] += 1
            continue
        hour = target.hour
        weekday = target.weekday()
        annual = (target.timetuple().tm_yday - 1 + hour / 24) / (366 if target.year % 4 == 0 else 365)
        calendar = (math.sin(2 * math.pi * hour / 24), math.cos(2 * math.pi * hour / 24),
                    math.sin(2 * math.pi * weekday / 7), math.cos(2 * math.pi * weekday / 7),
                    math.sin(2 * math.pi * annual), math.cos(2 * math.pi * annual))
        output["AR"].append([row[0] for row in lag_rows] + list(calendar))
        output["SUB_EXTRA"].append([row[column] for column in (4, 5, 6) for row in lag_rows])
        output["ELECTRICAL_EXTRA"].append([row[column] for column in (1, 2, 3) for row in lag_rows])
        output["y"].append(target_row[0])
        output["origin_power"].append(lag_rows[0][0])
        output["target_date"].append(target.date().isoformat())
        output["target_year"].append(target.year)
    for name in ("AR", "SUB_EXTRA", "ELECTRICAL_EXTRA", "y", "origin_power"):
        output[name] = np.asarray(output[name], dtype=float)
    output["target_year"] = np.asarray(output["target_year"], dtype=int)
    output["candidate_hour_origins_by_target_year"] = dict(sorted(candidate_hours.items()))
    output["excluded_incomplete_by_target_year"] = dict(sorted(excluded_incomplete.items()))
    return output


def date_counts(dates: list[str], mask: np.ndarray) -> dict[str, int]:
    counts = defaultdict(int)
    for date, selected in zip(dates, mask):
        if selected:
            counts[date] += 1
    return dict(counts)


def support_gate(samples: dict) -> dict:
    years = samples["target_year"]
    train = (years == 2007) | (years == 2008)
    validation = years == 2009
    test = years == 2010
    by_year = {str(y): {"pairs": int(np.sum(years == y)),
                        "target_dates": len(date_counts(samples["target_date"], years == y)),
                        "evaluation_dates_at_least_18_hours": sum(
                            count >= 18 for count in date_counts(samples["target_date"], years == y).values())}
               for y in (2007, 2008, 2009, 2010)}
    checks = {
        "train_at_least_10000_pairs_500_days": int(train.sum()) >= 10000 and
            by_year["2007"]["target_dates"] + by_year["2008"]["target_dates"] >= 500,
        "validation_at_least_6000_pairs_250_eval_days": int(validation.sum()) >= 6000 and
            by_year["2009"]["evaluation_dates_at_least_18_hours"] >= 250,
        "test_at_least_5000_pairs_250_eval_days": int(test.sum()) >= 5000 and
            by_year["2010"]["evaluation_dates_at_least_18_hours"] >= 250,
    }
    return {"by_target_year": by_year,
            "candidate_hour_origins_by_target_year": samples["candidate_hour_origins_by_target_year"],
            "excluded_incomplete_by_target_year": samples["excluded_incomplete_by_target_year"],
            "checks": checks,
            "decision": "HOURLY_MODEL_SUPPORT_READY" if all(checks.values()) else "STOP_HOURLY_MODEL_SUPPORT"}


def daily_errors(dates: list[str], y: np.ndarray, predictions: dict[str, np.ndarray]) -> tuple[list[dict], dict]:
    grouped = defaultdict(list)
    for index, day in enumerate(dates):
        grouped[day].append(index)
    rows = []
    for day, indices in sorted(grouped.items()):
        if len(indices) < 18:
            continue
        idx = np.asarray(indices, dtype=int)
        row = {"target_date": day, "pairs": len(idx)}
        for name, pred in predictions.items():
            row[f"{name}_mae_kw"] = float(np.mean(np.abs(pred[idx] - y[idx])))
        rows.append(row)
    return rows, {"all_target_dates": len(grouped), "evaluation_dates": len(rows),
                  "discarded_partial_target_dates": {day: len(indices) for day, indices in sorted(grouped.items()) if len(indices) < 18}}


def write_daily(name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("no evaluation dates")
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def comparison(rows: list[dict], candidate: str) -> dict:
    ar = np.asarray([row["AR_mae_kw"] for row in rows])
    cp = np.asarray([row[f"{candidate}_mae_kw"] for row in rows])
    delta = cp - ar
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(rows), size=(2000, len(rows)))
    ci = np.quantile(delta[picks].mean(axis=1), [0.025, 0.975])
    return {"candidate": candidate, "evaluation_days": len(rows),
            "AR_equal_day_mae_kw": float(ar.mean()),
            "candidate_equal_day_mae_kw": float(cp.mean()),
            "candidate_minus_AR_mae_kw": float(delta.mean()),
            "candidate_relative_mae_gain": float((ar.mean() - cp.mean()) / ar.mean()),
            "paired_day_bootstrap_difference_95pct_ci_kw": list(map(float, ci)),
            "days_candidate_better": int(np.sum(delta < 0)),
            "bootstrap_resamples": 2000, "bootstrap_seed": SEED}


def gate(metrics: dict) -> dict[str, bool]:
    return {"relative_mae_gain_at_least_5pct": metrics["candidate_relative_mae_gain"] >= .05,
            "paired_day_ci_upper_below_zero": metrics["paired_day_bootstrap_difference_95pct_ci_kw"][1] < 0,
            "at_least_60pct_days_better": metrics["days_candidate_better"] >= math.ceil(.6 * metrics["evaluation_days"])}


def main() -> None:
    expected = json.loads((SOURCE_DIR / "SOURCE_MATRIX.json").read_text(encoding="utf-8"))
    hourly, source = read_hourly()
    checks = {
        "official_member_only": source["archive_members"] == [expected["archive_member"]],
        "columns_match": source["source_columns"] == expected["actual_columns"],
        "rows_match": source["source_rows"] == expected["source_rows"],
        "first_last_match": source["source_first_date"] == expected["first_calendar_value"] and
                            source["source_last_date"] == expected["last_calendar_value"],
        "no_bad_row_width": source["source_bad_width_rows"] == 0,
        "year_rows_match": all(source["source_rows_by_year"].get(y) == expected["by_target_year"][str(y)]["rows"]
                               for y in (2007, 2008, 2009, 2010)),
    }
    source.update({"checks": checks,
                   "decision": "SOURCE_STRUCTURE_MATCH" if all(checks.values()) else "STOP_SOURCE_VERSION_DRIFT"})
    write_json("SOURCE_RECHECK.json", source)
    if not all(checks.values()):
        print(json.dumps({"source_recheck": source["decision"], "checks": checks}, indent=2))
        return
    samples = build_samples(hourly)
    support = support_gate(samples)
    write_json("MODEL_SUPPORT.json", support)
    if support["decision"] != "HOURLY_MODEL_SUPPORT_READY":
        print(json.dumps({"model_support": support}, indent=2))
        return
    years = samples["target_year"]
    train, validation, test = (years == 2007) | (years == 2008), years == 2009, years == 2010
    ar = samples["AR"]
    sub = samples["SUB_EXTRA"]
    electrical = samples["ELECTRICAL_EXTRA"]
    feature_sets = {"AR": ar,
                    "SUB": np.hstack((ar, sub)),
                    "ELECTRICAL": np.hstack((ar, electrical)),
                    "JOINT": np.hstack((ar, sub, electrical))}
    if not np.all(np.isfinite(samples["y"])) or not all(np.all(np.isfinite(x)) for x in feature_sets.values()):
        raise ValueError("nonfinite complete-case model matrix")
    fitted = {}
    fit_seconds = {}
    val_preds = {}
    for name in MODES:
        model = HistGradientBoostingRegressor(
            loss="absolute_error", max_iter=200, max_leaf_nodes=15,
            min_samples_leaf=50, learning_rate=0.05, l2_regularization=10,
            early_stopping=False, random_state=SEED)
        started = time.perf_counter()
        model.fit(feature_sets[name][train], samples["y"][train])
        fit_seconds[name] = time.perf_counter() - started
        fitted[name] = model
        val_preds[name] = np.maximum(0, model.predict(feature_sets[name][validation]))
    val_preds["PERSIST"] = samples["origin_power"][validation]
    val_dates = [day for day, selected in zip(samples["target_date"], validation) if selected]
    val_daily, day_support = daily_errors(val_dates, samples["y"][validation], val_preds)
    write_daily("VALIDATION_DAILY_ERRORS.csv", val_daily)
    means = {name: float(np.mean([row[f"{name}_mae_kw"] for row in val_daily])) for name in (*MODES, "PERSIST")}
    selected = min(("ELECTRICAL", "SUB", "JOINT"), key=lambda name: (means[name], TIE_PRIORITY[name]))
    metrics = comparison(val_daily, selected)
    metrics.update({"validation_equal_day_mae_kw_by_model": means,
                    "validation_day_support": day_support,
                    "source_recheck": source["decision"], "model_support": support["decision"],
                    "model_sample_counts": {"train": int(train.sum()), "validation": int(validation.sum()),
                                            "test": int(test.sum())},
                    "feature_dimensions": {name: x.shape[1] for name, x in feature_sets.items()},
                    "fit_seconds": fit_seconds,
                    "model_definition": "fixed HistGradientBoostingRegressor absolute_error, 200 iterations, leaves15, min_leaf50, lr0.05, L2=10, no early stopping",
                    "test_performance_scored": False})
    metrics["gates"] = gate(metrics)
    metrics["decision"] = ("PASS_ADDITIONAL_CHANNEL_DEV_GATE" if all(metrics["gates"].values())
                           else "STOP_ADDITIONAL_CHANNEL_DEV_GATE")
    write_json("VALIDATION_METRICS.json", metrics)
    print(json.dumps({"validation": {k: metrics[k] for k in (
        "validation_equal_day_mae_kw_by_model", "candidate", "candidate_relative_mae_gain",
        "paired_day_bootstrap_difference_95pct_ci_kw", "days_candidate_better", "evaluation_days",
        "gates", "decision")}}, indent=2))
    if metrics["decision"] != "PASS_ADDITIONAL_CHANNEL_DEV_GATE":
        return
    test_preds = {"AR": np.maximum(0, fitted["AR"].predict(feature_sets["AR"][test])),
                  selected: np.maximum(0, fitted[selected].predict(feature_sets[selected][test])),
                  "PERSIST": samples["origin_power"][test]}
    test_dates = [day for day, selected_row in zip(samples["target_date"], test) if selected_row]
    test_daily, test_day_support = daily_errors(test_dates, samples["y"][test], test_preds)
    write_daily("TEST_DAILY_ERRORS.csv", test_daily)
    test_metrics = comparison(test_daily, selected)
    test_metrics.update({"test_day_support": test_day_support, "development_gate": metrics["decision"],
                         "test_equal_day_mae_kw_by_scored_model": {
                             name: float(np.mean([row[f"{name}_mae_kw"] for row in test_daily]))
                             for name in test_preds}, "test_performance_scored": True})
    test_metrics["gates"] = gate(test_metrics)
    test_metrics["decision"] = ("ADDITIONAL_CHANNEL_YEAR_HOLDOUT_GAIN_SUPPORTED_WITHIN_ONE_HOUSE"
                                if all(test_metrics["gates"].values()) else "NO_2010_CHANNEL_GAIN")
    write_json("TEST_METRICS.json", test_metrics)
    print(json.dumps({"test": {k: test_metrics[k] for k in (
        "test_equal_day_mae_kw_by_scored_model", "candidate", "candidate_relative_mae_gain",
        "paired_day_bootstrap_difference_95pct_ci_kw", "days_candidate_better", "evaluation_days",
        "gates", "decision")}}, indent=2))


if __name__ == "__main__":
    main()
