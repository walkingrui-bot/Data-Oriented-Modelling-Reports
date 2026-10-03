"""EXP088: fixed conventional calibration comparison on real exposure episodes."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import urllib.request
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.model_selection import GroupKFold


HERE = Path(__file__).resolve().parent
SOURCE_PARENT = HERE.parent / "STAT-PSYMOE-EXP086-20261002-001"
EVENT_PARENT = HERE.parent / "STAT-PSYMOE-EXP087-20261002-001"
sys.path.insert(0, str(SOURCE_PARENT))
from audit_co_source import SPLIT, URL, date_info  # noqa: E402


COMMON = ["humidity_median", "temperature_median", "flow_median", "heater_median"]
SENSOR = [f"sensor_{i}_{kind}" for i in range(1, 15) for kind in ("median", "iqr")]
FEATURES = COMMON + SENSOR


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")


def extract_day(archive: zipfile.ZipFile, path: str, day: str) -> tuple[list[dict], dict]:
    first = None
    counts = [0] * 100
    center = [[] for _ in range(100)]
    valid = 0
    with archive.open(path) as handle:
        for raw in handle:
            line = raw.decode("utf-8-sig", errors="replace").strip()
            if not line:
                continue
            tokens = [token for token in SPLIT.split(line) if token]
            if len(tokens) != 20:
                continue
            try:
                values = [float(token) for token in tokens]
            except ValueError:
                continue
            if not all(math.isfinite(value) for value in values):
                continue
            valid += 1
            stamp = values[0]
            if first is None:
                first = stamp
            idx = int((stamp - first - 900) // 900)
            if not 0 <= idx < 100:
                continue
            counts[idx] += 1
            relative = stamp - first - 900 - 900 * idx
            if 300 <= relative < 840:
                center[idx].append(values)
    rows = []
    middle_counts = []
    for idx, values in enumerate(center):
        middle_counts.append(len(values))
        if not values:
            continue
        array = np.asarray(values, dtype=float)
        medians = np.median(array[:, 1:20], axis=0)
        q25 = np.quantile(array[:, 6:20], .25, axis=0)
        q75 = np.quantile(array[:, 6:20], .75, axis=0)
        item = {"date": day, "window_index": idx,
                "co_ppm": float(medians[0]), "concentration_level_0_1ppm": float(round(medians[0], 1)),
                "center_rows": len(values), "full_window_rows": counts[idx]}
        item.update({name: float(medians[position]) for position, name in
                     ((1, COMMON[0]), (2, COMMON[1]), (3, COMMON[2]), (4, COMMON[3]))})
        for sensor in range(14):
            item[f"sensor_{sensor+1}_median"] = float(medians[5+sensor])
            item[f"sensor_{sensor+1}_iqr"] = float(q75[sensor] - q25[sensor])
        rows.append(item)
    summary = {"date": day, "valid_full_numeric_rows": valid,
               "windows_with_at_least_1400_center_rows": sum(count >= 1400 for count in middle_counts),
               "windows_with_at_least_2500_full_rows": sum(count >= 2500 for count in counts),
               "center_row_counts": middle_counts, "full_window_row_counts": counts,
               "levels_0_1ppm": len({row["concentration_level_0_1ppm"] for row in rows})}
    return rows, summary


def source_and_events() -> list[dict] | None:
    previous = json.loads((EVENT_PARENT / "EPISODE_MATRIX.json").read_text())
    previous_days = {day["date"]: day for day in previous["days"]}
    with urllib.request.urlopen(URL, timeout=120) as response:
        blob = response.read(210_000_001)
    if len(blob) > 210_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(blob)) as outer:
        nested = [name for name in outer.namelist() if name.lower().endswith(".zip")]
        if len(nested) != 1:
            write_json("SOURCE_RECHECK.json", {"gate_result": "STOP_SOURCE_VERSION_DRIFT", "model_fits": 0,
                                               "outer_members": outer.namelist()})
            return None
        with zipfile.ZipFile(io.BytesIO(outer.read(nested[0]))) as archive:
            dated = [(name, date_info(name)) for name in archive.namelist() if not name.endswith("/")]
            dated = [(name, info) for name, info in dated if info is not None]
            episodes = []
            summaries = []
            for name, info in dated:
                rows, summary = extract_day(archive, name, info[0])
                episodes.extend(rows)
                summaries.append(summary)
    summaries.sort(key=lambda row: row["date"])
    episodes.sort(key=lambda row: (row["date"], row["window_index"]))
    checks = {
        "same_13_dates": len(summaries) == 13 and {row["date"] for row in summaries} == set(previous_days),
        "same_source_numeric_rows": len(summaries) == 13 and all(row["valid_full_numeric_rows"] == previous_days[row["date"]]["full_numeric_rows"] for row in summaries),
        "same_100_episode_counts_each_day": len(summaries) == 13 and all(
            row["full_window_row_counts"] == [v["full_numeric_rows"] for v in previous_days[row["date"]]["windows"]]
            and row["center_row_counts"] == [v["central_rows"] for v in previous_days[row["date"]]["windows"]]
            for row in summaries),
        "1300_finite_complete_episodes": len(episodes) == 1300 and all(
            row["center_rows"] >= 1400 and row["full_window_rows"] >= 2500 and
            all(math.isfinite(row[name]) for name in FEATURES) and math.isfinite(row["co_ppm"])
            for row in episodes),
        "same_co_medians_as_source_audit": len(episodes) == 1300 and all(
            abs(row["co_ppm"] - previous_days[row["date"]]["windows"][row["window_index"]]["central_co_median_ppm"]) < 1e-9
            for row in episodes),
        "ten_levels_each_day": len(summaries) == 13 and all(row["levels_0_1ppm"] == 10 for row in summaries),
    }
    write_json("SOURCE_RECHECK.json", {"official_zip_url": URL, "download_bytes": len(blob),
                                      "exp086_old_gate_still_failed": "STOP_CO_SENSOR_SOURCE_SCHEMA_OR_SUPPORT",
                                      "per_day": [{key: value for key, value in row.items() if not key.endswith("counts")}
                                                  for row in summaries],
                                      "checks": checks, "gate_result": "SOURCE_EPISODES_MATCH" if all(checks.values()) else "STOP_SOURCE_VERSION_DRIFT",
                                      "model_fits": 0})
    return episodes if all(checks.values()) else None


def add_split(episodes: list[dict]) -> bool:
    dates = sorted({row["date"] for row in episodes})
    split_by_date = {date: "train" if i < 7 else "validation" if i < 10 else "later_day"
                     for i, date in enumerate(dates)}
    for row in episodes:
        row["split"] = split_by_date[row["date"]]
    counts = {split: sum(row["split"] == split for row in episodes) for split in ("train", "validation", "later_day")}
    checks = {"thirteen_dates": len(dates) == 13,
              "train_700": counts["train"] == 700,
              "validation_300": counts["validation"] == 300,
              "later_day_300": counts["later_day"] == 300,
              "nonoverlapping_episode_keys": len({(row["date"], row["window_index"]) for row in episodes}) == 1300}
    write_json("MODEL_SUPPORT.json", {"dates": dates, "split_by_date": split_by_date,
                                      "episode_counts": counts, "checks": checks,
                                      "gate_result": "MODEL_SUPPORT_PASS" if all(checks.values()) else "STOP_CO_MODEL_EVENT_SUPPORT",
                                      "model_fits": 0})
    return all(checks.values())


def matrix(rows: list[dict], columns: list[str]) -> np.ndarray:
    return np.asarray([[row[column] for column in columns] for row in rows], dtype=float)


def model():
    return HistGradientBoostingRegressor(loss="absolute_error", max_iter=200, max_leaf_nodes=15,
                                         min_samples_leaf=25, learning_rate=.05, l2_regularization=10,
                                         early_stopping=False, random_state=20261002)


def day_equal_mae(rows: list[dict], prediction: np.ndarray) -> float:
    by_day = defaultdict(list)
    for row, value in zip(rows, prediction):
        by_day[row["date"]].append(abs(float(value) - row["co_ppm"]))
    return float(np.mean([np.mean(errors) for errors in by_day.values()]))


def score(rows: list[dict], base_pred: np.ndarray, multi_pred: np.ndarray, prefix: str) -> dict:
    dates = sorted({row["date"] for row in rows})
    day_errors = defaultdict(lambda: [[], []])
    level_errors = defaultdict(lambda: [[], []])
    with (HERE / f"{prefix}_PREDICTIONS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["date", "window_index", "co_ppm", "concentration_level_0_1ppm",
                         "base_pred_ppm", "multi_pred_ppm", "base_abs_error", "multi_abs_error"])
        for row, bp, mp in zip(rows, base_pred, multi_pred):
            be, me = abs(float(bp) - row["co_ppm"]), abs(float(mp) - row["co_ppm"])
            day_errors[row["date"]][0].append(be)
            day_errors[row["date"]][1].append(me)
            level_errors[row["concentration_level_0_1ppm"]][0].append(be)
            level_errors[row["concentration_level_0_1ppm"]][1].append(me)
            writer.writerow([row["date"], row["window_index"], row["co_ppm"],
                             row["concentration_level_0_1ppm"], float(bp), float(mp), be, me])
    daily = {date: {"base_mae": float(np.mean(day_errors[date][0])),
                    "multi_mae": float(np.mean(day_errors[date][1]))} for date in dates}
    levels = {str(level): {"base_mae": float(np.mean(errors[0])), "multi_mae": float(np.mean(errors[1]))}
              for level, errors in sorted(level_errors.items())}
    base_mae = float(np.mean([day["base_mae"] for day in daily.values()]))
    multi_mae = float(np.mean([day["multi_mae"] for day in daily.values()]))
    improved_days = sum(day["multi_mae"] < day["base_mae"] for day in daily.values())
    improved_levels = sum(item["multi_mae"] < item["base_mae"] for item in levels.values())
    result = {"episodes": len(rows), "days": len(dates), "base_day_equal_mae_ppm": base_mae,
              "multi_day_equal_mae_ppm": multi_mae,
              "relative_multi_gain_pct": float((base_mae - multi_mae) / base_mae * 100),
              "improved_days": improved_days, "improved_levels": improved_levels,
              "daily_mae": daily, "by_concentration_level_mae": levels}
    checks = {"gain_at_least_5pct": result["relative_multi_gain_pct"] >= 5,
              "all_three_days_improve": len(dates) == 3 and improved_days == 3,
              "at_least_seven_of_ten_levels_improve": len(levels) == 10 and improved_levels >= 7}
    result["checks"] = checks
    result["three_gate_pass"] = all(checks.values())
    write_json(f"{prefix}_METRICS.json", result)
    return result


def main() -> None:
    episodes = source_and_events()
    if episodes is None:
        print("STOP_SOURCE_VERSION_DRIFT")
        return
    if not add_split(episodes):
        print("STOP_CO_MODEL_EVENT_SUPPORT")
        return
    with (HERE / "EVENT_FEATURES.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["date", "window_index", "split", "co_ppm",
                                                        "concentration_level_0_1ppm", "center_rows", "full_window_rows", *FEATURES])
        writer.writeheader()
        writer.writerows(episodes)
    train = [row for row in episodes if row["split"] == "train"]
    validation = [row for row in episodes if row["split"] == "validation"]
    later = [row for row in episodes if row["split"] == "later_day"]
    y_train = np.asarray([row["co_ppm"] for row in train], dtype=float)
    groups = np.asarray([row["date"] for row in train])
    folds = list(GroupKFold(n_splits=4).split(np.zeros(len(train)), y_train, groups))
    candidates = [("ENV", COMMON)] + [(f"SENSOR_{sensor}", COMMON +
                   [f"sensor_{sensor}_median", f"sensor_{sensor}_iqr"]) for sensor in range(1, 15)]
    cv = {}
    for name, columns in candidates:
        x_train = matrix(train, columns)
        oof = np.empty(len(train), dtype=float)
        for fit_idx, valid_idx in folds:
            fitted = model()
            fitted.fit(x_train[fit_idx], y_train[fit_idx])
            oof[valid_idx] = np.clip(fitted.predict(x_train[valid_idx]), 0, 20)
        cv[name] = day_equal_mae(train, oof)
    chosen, base_columns = min(candidates, key=lambda pair: (cv[pair[0]], candidates.index(pair)))
    write_json("TRAIN_CV_SELECTION.json", {"train_days": 7, "train_episodes": 700,
                                           "group_cv_folds": 4, "candidate_day_equal_mae": cv,
                                           "selected_comparator": chosen,
                                           "base_features": base_columns, "multi_features": FEATURES,
                                           "cv_model_fits": 60, "final_model_fits": 2})
    base = model()
    multi = model()
    base.fit(matrix(train, base_columns), y_train)
    multi.fit(matrix(train, FEATURES), y_train)
    validation_metrics = score(validation,
                               np.clip(base.predict(matrix(validation, base_columns)), 0, 20),
                               np.clip(multi.predict(matrix(validation, FEATURES)), 0, 20), "VALIDATION")
    if not validation_metrics["three_gate_pass"]:
        print(json.dumps({"gate_result": "STOP_CO_MULTISENSOR_DEV_GATE", "selected_comparator": chosen,
                          "validation_metrics": validation_metrics, "test_performance_scores": 0}, indent=2))
        return
    later_metrics = score(later, np.clip(base.predict(matrix(later, base_columns)), 0, 20),
                          np.clip(multi.predict(matrix(later, FEATURES)), 0, 20), "LATER_DAY")
    print(json.dumps({"gate_result": "EXPLORATORY_CO_MULTISENSOR_LATER_DAY_GAIN_WITHIN_ONE_RIG" if later_metrics["three_gate_pass"] else "NO_CO_LATER_DAY_MULTISENSOR_GAIN",
                      "selected_comparator": chosen, "validation_metrics": validation_metrics,
                      "later_day_metrics": later_metrics, "test_performance_scores": 1}, indent=2))


if __name__ == "__main__":
    main()
