"""EXP083: frozen, year-separated I-94 traffic versus lagged weather test."""

from __future__ import annotations

import csv
import gzip
import io
import json
import math
import statistics
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP082-20261002-001" / "SOURCE_MATRIX.json"
URL = "https://archive.ics.uci.edu/static/public/492/metro%2Binterstate%2Btraffic%2Bvolume.zip"
MEMBER = "Metro_Interstate_Traffic_Volume.csv.gz"
WEATHER = ("temp", "rain_1h", "snow_1h", "clouds_all")
NEEDED = ("date_time", "traffic_volume", *WEATHER)
PERIODS = ("train_2013_2016", "validation_2017", "test_2018")
ONE_HOUR = timedelta(hours=1)


def write_json(name: str, obj: dict) -> None:
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def number(raw: str) -> float | None:
    if raw.strip() in ("", "?"):
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def load_and_recheck() -> dict[datetime, dict] | None:
    with urllib.request.urlopen(URL, timeout=90) as response:
        blob = response.read(2_000_001)
    if len(blob) > 2_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        members = archive.namelist()
        if members != [MEMBER]:
            write_json("SOURCE_RECHECK.json", {"archive_members": members, "gate_result": "STOP_SOURCE_VERSION_DRIFT", "model_fits": 0})
            return None
        with archive.open(MEMBER) as handle:
            raw = gzip.decompress(handle.read())
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    columns = tuple(reader.fieldnames or ())
    if not all(key in columns for key in NEEDED):
        write_json("SOURCE_RECHECK.json", {"actual_columns": columns, "gate_result": "STOP_SOURCE_VERSION_DRIFT", "model_fits": 0})
        return None
    by_hour = defaultdict(list)
    rows = bad_date = 0
    for row in reader:
        rows += 1
        try:
            stamp = datetime.strptime(row["date_time"].strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            bad_date += 1
            continue
        by_hour[stamp].append({k: number(row[k]) for k in NEEDED if k != "date_time"})
    collapsed = {}
    conflicts = {k: 0 for k in WEATHER}
    outcome_conflicts = 0
    for stamp, entries in by_hour.items():
        outcomes = [entry["traffic_volume"] for entry in entries]
        good = all(v is not None and v >= 0 for v in outcomes) and len(set(outcomes)) == 1
        outcome_conflicts += int(len(entries) > 1 and not good)
        weather = {}
        for key in WEATHER:
            values = [entry[key] for entry in entries]
            weather[key] = float(statistics.median(values)) if all(v is not None for v in values) else None
            conflicts[key] += int(len(entries) > 1 and all(v is not None for v in values) and max(values) > min(values))
        collapsed[stamp] = {"traffic_volume": outcomes[0] if good else None, "weather": weather}
    periods = {key: {"pairs": 0, "target_dates": set()} for key in PERIODS}
    for stamp, entry in collapsed.items():
        target = stamp + ONE_HOUR
        future = collapsed.get(target)
        if future is None or entry["traffic_volume"] is None or future["traffic_volume"] is None:
            continue
        if any(value is None for value in entry["weather"].values()):
            continue
        key = period_name(target.year)
        if key is not None:
            periods[key]["pairs"] += 1
            periods[key]["target_dates"].add(target.date().isoformat())
    for item in periods.values():
        item["target_dates"] = len(item["target_dates"])
    prior = json.loads(PARENT.read_text(encoding="utf-8"))
    checks = {
        "source_rows": rows == prior["source_rows"],
        "calendar_parse_failures": bad_date == prior["calendar_parse_failures"],
        "unique_calendar_hours": len(collapsed) == prior["unique_calendar_hours"],
        "first_unique_hour": min(collapsed).isoformat(sep=" ") == prior["first_unique_hour"],
        "last_unique_hour": max(collapsed).isoformat(sep=" ") == prior["last_unique_hour"],
        "duplicate_calendar_hours": sum(len(v) > 1 for v in by_hour.values()) == prior["duplicate_calendar_hours"],
        "extra_duplicate_rows": sum(len(v) - 1 for v in by_hour.values()) == prior["extra_duplicate_rows"],
        "conflicting_duplicate_outcome_hours": outcome_conflicts == prior["conflicting_duplicate_outcome_hours"],
        "numeric_weather_conflicting_duplicate_hours_by_column": conflicts == prior["numeric_weather_conflicting_duplicate_hours_by_column"],
        "one_hour_pair_support_by_target_year": periods == prior["one_hour_pair_support_by_target_year"],
    }
    result = {
        "research_id": "STAT-PSYMOE-EXP083-20261002-001", "official_zip_url": URL,
        "archive_member": MEMBER, "source_rows": rows, "unique_calendar_hours": len(collapsed),
        "duplicate_calendar_hours": sum(len(v) > 1 for v in by_hour.values()),
        "extra_duplicate_rows": sum(len(v) - 1 for v in by_hour.values()),
        "weather_conflicting_duplicate_hours": conflicts,
        "one_hour_pair_support_by_target_year": periods, "checks_against_exp082": checks,
        "gate_result": "SOURCE_VERSION_MATCH" if all(checks.values()) else "STOP_SOURCE_VERSION_DRIFT",
        "model_fits": 0,
    }
    write_json("SOURCE_RECHECK.json", result)
    return collapsed if all(checks.values()) else None


def period_name(year: int) -> str | None:
    if 2013 <= year <= 2016:
        return PERIODS[0]
    if year == 2017:
        return PERIODS[1]
    if year == 2018:
        return PERIODS[2]
    return None


def samples(collapsed: dict) -> dict:
    out = {key: {"x_base": [], "x_weather": [], "y": [], "date": [], "persist": [], "week": []} for key in PERIODS}
    for stamp in sorted(collapsed):
        target = stamp + ONE_HOUR
        key = period_name(target.year)
        if key is None or target not in collapsed:
            continue
        lags = [stamp - timedelta(hours=h) for h in (0, 1, 24, 168)]
        if any(t not in collapsed or collapsed[t]["traffic_volume"] is None for t in lags):
            continue
        weather = collapsed[lags[1]]["weather"]
        if any(weather[w] is None for w in WEATHER):
            continue
        y = collapsed[target]["traffic_volume"]
        if y is None:
            continue
        traffic = [collapsed[t]["traffic_volume"] for t in lags]
        hour = target.hour
        weekday = target.weekday()
        doy = target.timetuple().tm_yday
        calendar = [math.sin(2 * math.pi * hour / 24), math.cos(2 * math.pi * hour / 24),
                    math.sin(2 * math.pi * weekday / 7), math.cos(2 * math.pi * weekday / 7),
                    math.sin(2 * math.pi * doy / 365.25), math.cos(2 * math.pi * doy / 365.25)]
        base = traffic + calendar
        item = out[key]
        item["x_base"].append(base)
        item["x_weather"].append(base + [weather[w] for w in WEATHER])
        item["y"].append(y)
        item["date"].append(target.date().isoformat())
        item["persist"].append(traffic[0])
        item["week"].append(traffic[3])
    return out


def support(data: dict) -> bool:
    entries = {}
    for key, item in data.items():
        counts = defaultdict(int)
        for date in item["date"]:
            counts[date] += 1
        entries[key] = {"pairs": len(item["y"]), "target_dates": len(counts),
                        "evaluation_dates_at_least_18_hours": sum(v >= 18 for v in counts.values()),
                        "excluded_sparse_dates": sum(v < 18 for v in counts.values()),
                        "min_hour_count": min(counts.values()) if counts else 0}
    checks = {
        "train_pairs_at_least_12000": entries[PERIODS[0]]["pairs"] >= 12_000,
        "train_dates_at_least_700": entries[PERIODS[0]]["target_dates"] >= 700,
        "validation_pairs_at_least_6000": entries[PERIODS[1]]["pairs"] >= 6_000,
        "validation_evaluation_dates_at_least_250": entries[PERIODS[1]]["evaluation_dates_at_least_18_hours"] >= 250,
        "test_pairs_at_least_4500": entries[PERIODS[2]]["pairs"] >= 4_500,
        "test_evaluation_dates_at_least_220": entries[PERIODS[2]]["evaluation_dates_at_least_18_hours"] >= 220,
    }
    write_json("MODEL_SUPPORT.json", {"periods": entries, "checks": checks,
                                      "gate_result": "MODEL_SUPPORT_PASS" if all(checks.values()) else "STOP_TRAFFIC_MODEL_SUPPORT",
                                      "model_fits": 0})
    return all(checks.values())


def evaluation(item: dict, preds: dict, prefix: str) -> dict:
    daily = defaultdict(lambda: defaultdict(list))
    for i, date in enumerate(item["date"]):
        for name, prediction in preds.items():
            daily[date][name].append(abs(float(prediction[i]) - float(item["y"][i])))
    names = list(preds)
    rows = []
    for date, arm_errors in sorted(daily.items()):
        n = len(arm_errors[names[0]])
        if n < 18:
            continue
        row = {"target_date": date, "hours": n}
        row.update({name + "_mae": float(np.mean(arm_errors[name])) for name in names})
        rows.append(row)
    with (HERE / f"{prefix}_DAILY_ERRORS.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["target_date", "hours"] + [name + "_mae" for name in names])
        writer.writeheader()
        writer.writerows(rows)
    base = np.array([r["BASE_mae"] for r in rows], dtype=float)
    weather = np.array([r["WEATHER_mae"] for r in rows], dtype=float)
    diff = weather - base
    rng = np.random.default_rng(20261002)
    indices = rng.integers(0, len(diff), size=(2000, len(diff)))
    interval = np.quantile(np.mean(diff[indices], axis=1), [0.025, 0.975]).tolist()
    result = {
        "evaluation_days": len(rows), "base_day_equal_mae": float(np.mean(base)),
        "weather_day_equal_mae": float(np.mean(weather)),
        "weather_minus_base_day_equal_mae": float(np.mean(diff)),
        "relative_weather_gain_pct": float((np.mean(base) - np.mean(weather)) / np.mean(base) * 100),
        "paired_day_bootstrap_2000_ci95_for_weather_minus_base": interval,
        "days_weather_better": int(np.sum(diff < 0)),
        "fraction_days_weather_better": float(np.mean(diff < 0)),
        "descriptive_day_equal_mae": {name: float(np.mean([r[name + "_mae"] for r in rows])) for name in names if name not in ("BASE", "WEATHER")},
    }
    checks = {"relative_gain_at_least_5pct": result["relative_weather_gain_pct"] >= 5,
              "bootstrap_upper_below_zero": interval[1] < 0,
              "at_least_60pct_days_improve": result["fraction_days_weather_better"] >= .6}
    result["checks"] = checks
    result["three_gate_pass"] = all(checks.values())
    write_json(f"{prefix}_METRICS.json", result)
    return result


def main() -> None:
    collapsed = load_and_recheck()
    if collapsed is None:
        print("STOP_SOURCE_VERSION_DRIFT")
        return
    data = samples(collapsed)
    if not support(data):
        print("STOP_TRAFFIC_MODEL_SUPPORT")
        return
    params = dict(loss="absolute_error", max_iter=200, max_leaf_nodes=15,
                  min_samples_leaf=50, learning_rate=0.05, l2_regularization=10,
                  early_stopping=False, random_state=20261002)
    train = data[PERIODS[0]]
    models = {}
    for name, column in (("BASE", "x_base"), ("WEATHER", "x_weather")):
        model = HistGradientBoostingRegressor(**params)
        model.fit(np.asarray(train[column], dtype=float), np.asarray(train["y"], dtype=float))
        models[name] = (model, column)
    val = data[PERIODS[1]]
    preds = {name: np.maximum(model.predict(np.asarray(val[column], dtype=float)), 0)
             for name, (model, column) in models.items()}
    preds.update({"PERSIST": val["persist"], "WEEK": val["week"]})
    metrics = evaluation(val, preds, "VALIDATION")
    if not metrics["three_gate_pass"]:
        print(json.dumps({"gate_result": "STOP_WEATHER_TRAFFIC_DEV_GATE", "validation_metrics": metrics,
                          "model_fits": 2, "test_performance_scores": 0}, indent=2))
        return
    test = data[PERIODS[2]]
    preds = {name: np.maximum(model.predict(np.asarray(test[column], dtype=float)), 0)
             for name, (model, column) in models.items()}
    preds.update({"PERSIST": test["persist"], "WEEK": test["week"]})
    test_metrics = evaluation(test, preds, "TEST")
    print(json.dumps({"gate_result": "WEATHER_TRAFFIC_YEAR_HOLDOUT_GAIN_WITHIN_ONE_SITE" if test_metrics["three_gate_pass"] else "NO_2018_WEATHER_TRAFFIC_GAIN",
                      "validation_metrics": metrics, "test_metrics": test_metrics, "model_fits": 2,
                      "test_performance_scores": 1}, indent=2))


if __name__ == "__main__":
    main()
