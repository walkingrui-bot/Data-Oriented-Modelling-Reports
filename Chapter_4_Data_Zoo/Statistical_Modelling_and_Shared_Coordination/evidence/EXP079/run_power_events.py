"""EXP079: fixed real high-load event classification by year."""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP078-20261002-001"
SOURCE = HERE.parent / "STAT-PSYMOE-EXP077-20261002-001"
sys.path.insert(0, str(PARENT))
from run_household_stats import read_hourly, build_samples, support_gate  # noqa: E402

SEED = 20261002
MODES = ("AR", "SUB", "ELECTRICAL", "JOINT")
TIE_PRIORITY = {"ELECTRICAL": 0, "SUB": 1, "JOINT": 2}


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def clip(prob: np.ndarray) -> np.ndarray:
    return np.clip(prob, 1e-6, 1 - 1e-6)


def day_loss(dates: list[str], y: np.ndarray, predictions: dict[str, np.ndarray]) -> tuple[list[dict], dict, np.ndarray]:
    grouped = defaultdict(list)
    for index, date in enumerate(dates):
        grouped[date].append(index)
    output = []
    keep = np.zeros(len(y), dtype=bool)
    for date, indices in sorted(grouped.items()):
        if len(indices) < 18:
            continue
        idx = np.asarray(indices, dtype=int)
        keep[idx] = True
        row = {"target_date": date, "pairs": len(idx), "events": int(y[idx].sum())}
        for name, pred in predictions.items():
            p = clip(pred[idx])
            row[f"{name}_logloss"] = float(np.mean(-(y[idx] * np.log(p) + (1 - y[idx]) * np.log1p(-p))))
        output.append(row)
    meta = {"all_target_dates": len(grouped), "evaluation_dates": len(output),
            "evaluation_pairs": int(keep.sum()), "evaluation_events": int(y[keep].sum()),
            "discarded_partial_target_dates": {date: len(indices) for date, indices in sorted(grouped.items()) if len(indices) < 18}}
    return output, meta, keep


def write_daily(name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("no full evaluation dates")
    with (HERE / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def comparison(rows: list[dict], candidate: str, y: np.ndarray,
               predictions: dict[str, np.ndarray], keep: np.ndarray) -> dict:
    ar = np.asarray([row["AR_logloss"] for row in rows])
    cp = np.asarray([row[f"{candidate}_logloss"] for row in rows])
    delta = cp - ar
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0, len(rows), size=(2000, len(rows)))
    ci = np.quantile(delta[picks].mean(axis=1), [.025, .975])
    ap_ar = float(average_precision_score(y[keep], predictions["AR"][keep]))
    ap_cp = float(average_precision_score(y[keep], predictions[candidate][keep]))
    return {"candidate": candidate, "evaluation_days": len(rows),
            "AR_equal_day_logloss": float(ar.mean()),
            "candidate_equal_day_logloss": float(cp.mean()),
            "candidate_minus_AR_equal_day_logloss": float(delta.mean()),
            "candidate_relative_logloss_gain": float((ar.mean() - cp.mean()) / ar.mean()),
            "paired_day_bootstrap_difference_95pct_ci": list(map(float, ci)),
            "days_candidate_better": int(np.sum(delta < 0)),
            "AR_average_precision": ap_ar, "candidate_average_precision": ap_cp,
            "candidate_minus_AR_average_precision": ap_cp - ap_ar,
            "bootstrap_resamples": 2000, "bootstrap_seed": SEED}


def gate(metrics: dict) -> dict[str, bool]:
    return {"relative_logloss_gain_at_least_5pct": metrics["candidate_relative_logloss_gain"] >= .05,
            "paired_day_ci_upper_below_zero": metrics["paired_day_bootstrap_difference_95pct_ci"][1] < 0,
            "at_least_60pct_days_better": metrics["days_candidate_better"] >= math.ceil(.6 * metrics["evaluation_days"]),
            "average_precision_gain_at_least_0p02": metrics["candidate_minus_AR_average_precision"] >= .02}


def main() -> None:
    expected = json.loads((SOURCE / "SOURCE_MATRIX.json").read_text(encoding="utf-8"))
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
    train = (years == 2007) | (years == 2008)
    validation = years == 2009
    test = years == 2010
    threshold = float(np.quantile(samples["y"][train], .90, method="linear"))
    events = samples["y"] >= threshold
    event_support = {"training_threshold_q90_kw": threshold,
                     "definition": "future target Global_active_power >= training-only q90; not a hazard threshold",
                     "train_pairs": int(train.sum()), "train_events": int(events[train].sum()),
                     "validation_pairs": int(validation.sum()), "validation_events": int(events[validation].sum()),
                     "test_event_count_checked_before_dev_gate": False}
    event_support["checks"] = {"train_at_least_1000_events": event_support["train_events"] >= 1000,
                               "validation_at_least_400_events": event_support["validation_events"] >= 400}
    event_support["decision"] = ("EVENT_SUPPORT_READY" if all(event_support["checks"].values())
                                 else "STOP_EVENT_SUPPORT")
    write_json("EVENT_SUPPORT.json", event_support)
    if event_support["decision"] != "EVENT_SUPPORT_READY":
        print(json.dumps({"event_support": event_support}, indent=2))
        return
    ar = samples["AR"]
    sub = samples["SUB_EXTRA"]
    electrical = samples["ELECTRICAL_EXTRA"]
    feature_sets = {"AR": ar,
                    "SUB": np.hstack((ar, sub)),
                    "ELECTRICAL": np.hstack((ar, electrical)),
                    "JOINT": np.hstack((ar, sub, electrical))}
    fitted = {}
    fit_seconds = {}
    val_probs = {}
    for name in MODES:
        model = HistGradientBoostingClassifier(
            max_iter=200, max_leaf_nodes=15, min_samples_leaf=50,
            learning_rate=0.05, l2_regularization=10, early_stopping=False, random_state=SEED)
        started = time.perf_counter()
        model.fit(feature_sets[name][train], events[train].astype(int))
        fit_seconds[name] = time.perf_counter() - started
        fitted[name] = model
        val_probs[name] = clip(model.predict_proba(feature_sets[name][validation])[:, 1])
    train_prevalence = float(events[train].mean())
    val_probs["PREVALENCE"] = np.full(int(validation.sum()), train_prevalence)
    val_dates = [day for day, selected in zip(samples["target_date"], validation) if selected]
    val_y = events[validation].astype(int)
    val_daily, day_support, keep = day_loss(val_dates, val_y, val_probs)
    write_daily("VALIDATION_DAILY_ERRORS.csv", val_daily)
    means = {name: float(np.mean([row[f"{name}_logloss"] for row in val_daily]))
             for name in (*MODES, "PREVALENCE")}
    selected = min(("ELECTRICAL", "SUB", "JOINT"), key=lambda name: (means[name], TIE_PRIORITY[name]))
    metrics = comparison(val_daily, selected, val_y, val_probs, keep)
    metrics.update({"validation_equal_day_logloss_by_model": means,
                    "validation_average_precision_by_model": {
                        name: float(average_precision_score(val_y[keep], prob[keep])) for name, prob in val_probs.items()},
                    "validation_day_support": day_support,
                    "source_recheck": source["decision"], "model_support": support["decision"],
                    "event_support": event_support["decision"], "training_threshold_q90_kw": threshold,
                    "model_sample_counts": {"train": int(train.sum()), "validation": int(validation.sum()),
                                            "test": int(test.sum())},
                    "feature_dimensions": {name: x.shape[1] for name, x in feature_sets.items()},
                    "fit_seconds": fit_seconds,
                    "model_definition": "fixed HistGradientBoostingClassifier, 200 iterations, leaves15, min_leaf50, lr0.05, L2=10, no early stopping",
                    "test_performance_scored": False})
    metrics["gates"] = gate(metrics)
    metrics["decision"] = ("PASS_EVENT_CHANNEL_DEV_GATE" if all(metrics["gates"].values())
                           else "STOP_EVENT_CHANNEL_DEV_GATE")
    write_json("VALIDATION_METRICS.json", metrics)
    print(json.dumps({"validation": {k: metrics[k] for k in (
        "training_threshold_q90_kw", "validation_equal_day_logloss_by_model",
        "validation_average_precision_by_model", "candidate", "candidate_relative_logloss_gain",
        "paired_day_bootstrap_difference_95pct_ci", "days_candidate_better", "evaluation_days",
        "gates", "decision")}}, indent=2))
    if metrics["decision"] != "PASS_EVENT_CHANNEL_DEV_GATE":
        return
    test_probs = {"AR": clip(fitted["AR"].predict_proba(feature_sets["AR"][test])[:, 1]),
                  selected: clip(fitted[selected].predict_proba(feature_sets[selected][test])[:, 1]),
                  "PREVALENCE": np.full(int(test.sum()), train_prevalence)}
    test_dates = [day for day, selected_row in zip(samples["target_date"], test) if selected_row]
    test_y = events[test].astype(int)
    test_daily, test_day_support, test_keep = day_loss(test_dates, test_y, test_probs)
    write_daily("TEST_DAILY_ERRORS.csv", test_daily)
    test_metrics = comparison(test_daily, selected, test_y, test_probs, test_keep)
    test_metrics.update({"test_day_support": test_day_support,
                         "test_equal_day_logloss_by_scored_model": {
                             name: float(np.mean([row[f"{name}_logloss"] for row in test_daily]))
                             for name in test_probs},
                         "test_average_precision_by_scored_model": {
                             name: float(average_precision_score(test_y[test_keep], prob[test_keep]))
                             for name, prob in test_probs.items()},
                         "development_gate": metrics["decision"], "test_performance_scored": True})
    test_metrics["gates"] = gate(test_metrics)
    test_metrics["decision"] = ("EVENT_CHANNEL_YEAR_HOLDOUT_GAIN_SUPPORTED_WITHIN_ONE_HOUSE"
                                if all(test_metrics["gates"].values()) else "NO_2010_EVENT_CHANNEL_GAIN")
    write_json("TEST_METRICS.json", test_metrics)
    print(json.dumps({"test": {k: test_metrics[k] for k in (
        "test_equal_day_logloss_by_scored_model", "test_average_precision_by_scored_model",
        "candidate", "candidate_relative_logloss_gain",
        "paired_day_bootstrap_difference_95pct_ci", "days_candidate_better", "evaluation_days",
        "gates", "decision")}}, indent=2))


if __name__ == "__main__":
    main()
