#!/usr/bin/env python3
"""EXP065 fixed 2024 local traditional statistics, one 2025 temporal holdout."""

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
P60 = HERE.parent / "STAT-PSYMOE-EXP060-20261002-001"
P62 = HERE.parent / "STAT-PSYMOE-EXP062-20261002-001"
P64 = HERE.parent / "STAT-PSYMOE-EXP064-20261002-001"
sys.path.insert(0, str(HERE.parent / "STAT-PSYMOE-EXP061-20261002-001"))
import audit_external_source as audit  # noqa: E402

RUN_ID = "EXP065-STAT-001"
MAX_BYTES = 50 * 1024 * 1024
SITES = "BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR".split()
GRIDS = {
    2024: [datetime(2024, 1, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(8784)],
    2025: [datetime(2025, 1, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(8760)],
}


def reconstruct_pairs(year, grid, observations, features):
    rows = []
    counts = Counter()
    for site in SITES:
        obs = observations[site]
        for i in range(len(grid) - 24):
            current = obs.get(i)
            if current is None or current[0] != "blank":
                continue
            future = obs.get(i + 24)
            if future is None or future[0] != "valid":
                continue
            neighbors = [observations[s][i][1] for s in SITES if s != site
                         and observations[s].get(i, (None, None))[0] == "valid"]
            if len(neighbors) < 8:
                continue
            p25, median, p75 = np.percentile(np.asarray(neighbors, dtype=float), [25, 50, 75])
            time = grid[i]
            hour = float(time.hour)
            phase = (time.timetuple().tm_yday - 1 + hour / 24) / 365.25
            feature_values = {
                "log_neighbor_p25": math.log1p(p25),
                "log_neighbor_median": math.log1p(median),
                "log_neighbor_p75": math.log1p(p75),
                "neighbor_count": float(len(neighbors)),
                "sin_hour": math.sin(2 * math.pi * hour / 24),
                "cos_hour": math.cos(2 * math.pi * hour / 24),
                "sin_year": math.sin(2 * math.pi * phase),
                "cos_year": math.cos(2 * math.pi * phase),
            }
            row = {"year": year, "site": site, "origin_time_gmt_end": time.isoformat(),
                   "target_time_gmt_end": grid[i + 24].isoformat(),
                   "origin_day_gmt": time.date().isoformat(),
                   "target": float(future[1]), "B0": float(median),
                   "neighbor_count": len(neighbors), "features": [feature_values[f] for f in features]}
            rows.append(row)
            counts[site] += 1
    return rows, counts


def original_beijing_log(rows, state):
    x = np.array([r["features"] for r in rows], dtype=float)
    scaled = (x - np.asarray(state["scaler_mean"])) / np.asarray(state["scaler_scale"])
    return scaled @ np.asarray(state["coef"]) + state["intercept"]


def fit_ridge(rows, columns):
    x = np.array([[r["features"][i] for i in columns] for r in rows], dtype=float)
    target = np.log1p(np.array([r["target"] for r in rows], dtype=float))
    scaler = StandardScaler()
    x_scaled = scaler.fit_transform(x)
    ridge = Ridge(alpha=1.0, fit_intercept=True)
    ridge.fit(x_scaled, target)
    state = {"model": "Ridge(alpha=1.0, fit_intercept=True)",
             "target": "log1p(real_PM_t_plus_24)", "inverse": "max(0,expm1)",
             "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(),
             "coef": ridge.coef_.tolist(), "intercept": float(ridge.intercept_),
             "train_pairs": len(rows)}
    return state, scaler, ridge


def predict_ridge(rows, columns, scaler, model):
    x = np.array([[r["features"][i] for i in columns] for r in rows], dtype=float)
    return np.maximum(0, np.expm1(model.predict(scaler.transform(x))))


def score(rows, name):
    y = np.asarray([r["target"] for r in rows], dtype=float)
    p = np.asarray([r[name] for r in rows], dtype=float)
    return {"n": len(rows), "MAE": float(np.mean(np.abs(y - p))),
            "RMSE": float(np.sqrt(np.mean((y - p) ** 2))),
            "prediction_mean": float(np.mean(p))}


def block_diff(rows, candidate, baseline):
    by_day = defaultdict(list)
    for row in rows:
        by_day[row["origin_day_gmt"]].append(row)
    days = sorted(by_day)
    sums = np.asarray([sum(abs(r["target"] - r[candidate])
        - abs(r["target"] - r[baseline]) for r in by_day[d]) for d in days], dtype=float)
    counts = np.asarray([len(by_day[d]) for d in days], dtype=int)
    rng = np.random.default_rng(20261002)
    indices = rng.integers(0, len(days), size=(1000, len(days)))
    boot = sums[indices].sum(axis=1) / counts[indices].sum(axis=1)
    return {"block": "GMT_origin_day_all_stations_together", "days": len(days),
            "resamples": 1000, "seed": 20261002,
            "candidate_minus_baseline_MAE": float(sums.sum() / counts.sum()),
            "bootstrap_95ci": np.quantile(boot, [0.025, 0.975]).tolist()}


def main():
    for name in ("SOURCE_RECHECK.json", "MODEL_STATES.json", "PREDICTIONS.csv", "METRICS.json"):
        if (HERE / name).exists():
            raise FileExistsError("preserve existing direct output: " + name)
    source_index = {
        2024: json.loads((P62 / "SOURCE_MATRIX.json").read_text()),
        2025: json.loads((P64 / "SOURCE_MATRIX.json").read_text()),
    }
    support = {
        2024: json.loads((P62 / "PAIR_SUPPORT.json").read_text()),
        2025: json.loads((P64 / "PAIR_SUPPORT.json").read_text()),
    }
    original = json.loads((P60 / "MODEL_STATES.json").read_text())["N1"]
    features = original["features"]
    if any(support[y]["qualified_sites"] != SITES for y in GRIDS):
        raise ValueError("preselected same ten qualified sites changed")
    observations = {}
    recheck = {"run_id": RUN_ID, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
               "source_indices": {"2024": str(P62 / "SOURCE_MATRIX.json"),
                                  "2025": str(P64 / "SOURCE_MATRIX.json")},
               "model_ref": str(P60 / "MODEL_STATES.json"),
               "per_year_site": {}, "per_year_pair_match": {}, "total_bytes": 0}
    total = 0
    for year in (2024, 2025):
        grid = GRIDS[year]
        audit.GRID = grid
        audit.TIME_TO_INDEX = {t: i for i, t in enumerate(grid)}
        index = {x["site"]: x for x in source_index[year]["sites"] if x.get("site") in SITES}
        data = {}
        checks = {}
        for site in SITES:
            expected = index[site]
            raw, _ = audit.fetch(expected["csv_url"], MAX_BYTES - total)
            total += len(raw)
            parsed, obs = audit.parse_csv(raw, site)
            checks[site] = (parsed["schema_ok"] and parsed["counts"] == expected["counts"]
                            and parsed["units"] == expected["units"]
                            and parsed["statuses"] == expected["statuses"])
            data[site] = obs
            print("SOURCE", year, site, "match", checks[site], "bytes", len(raw), flush=True)
        recheck["per_year_site"][str(year)] = checks
        if not all(checks.values()):
            recheck["total_bytes"] = total
            (HERE / "SOURCE_RECHECK.json").write_text(json.dumps(recheck, indent=2) + "\n")
            raise RuntimeError("STOP_SOURCE_VERSION_DRIFT: year/site source changed")
        observations[year] = data
    recheck["total_bytes"] = total
    rows_by_year = {}
    for year in (2024, 2025):
        rows, counts = reconstruct_pairs(year, GRIDS[year], observations[year], features)
        expected_counts = {s: c.get("eligible_pair", 0)
                           for s, c in support[year]["counts_by_target"].items()}
        match = len(rows) == support[year]["pair_count"] and all(
            counts[s] == expected_counts[s] for s in SITES)
        recheck["per_year_pair_match"][str(year)] = {"match": match,
            "total": len(rows), "counts_by_site": dict(counts)}
        rows_by_year[year] = rows
        print("PAIR", year, len(rows), "match", match, flush=True)
    (HERE / "SOURCE_RECHECK.json").write_text(json.dumps(recheck, indent=2) + "\n")
    if not all(x["match"] for x in recheck["per_year_pair_match"].values()):
        raise RuntimeError("STOP_SOURCE_VERSION_DRIFT: pair counts changed")

    train, test = rows_by_year[2024], rows_by_year[2025]
    z_train = original_beijing_log(train, original)
    z_test = original_beijing_log(test, original)
    target_train = np.log1p(np.asarray([r["target"] for r in train], dtype=float))
    offset = float(np.mean(target_train - z_train))
    c0_train = np.maximum(0, np.expm1(z_train + offset))
    c0_test = np.maximum(0, np.expm1(z_test + offset))
    median_index = features.index("log_neighbor_median")
    m1_state, m1_scaler, m1_model = fit_ridge(train, [median_index])
    l1_state, l1_scaler, l1_model = fit_ridge(train, list(range(8)))
    m1_train = predict_ridge(train, [median_index], m1_scaler, m1_model)
    l1_train = predict_ridge(train, list(range(8)), l1_scaler, l1_model)
    m1_test = predict_ridge(test, [median_index], m1_scaler, m1_model)
    l1_test = predict_ridge(test, list(range(8)), l1_scaler, l1_model)
    states = {"run_id": RUN_ID, "train_year": 2024, "train_pairs": len(train),
              "beijing_N1_ref": str(P60 / "MODEL_STATES.json"),
              "B0": {"model": "visible_neighbor_median_no_fit"},
              "C0": {"model": "frozen_Beijing_N1_log_prediction_plus_one_2024_mean_residual",
                     "log_offset": offset, "train_pairs": len(train)},
              "M1": {**m1_state, "features": ["log_neighbor_median"]},
              "L1": {**l1_state, "features": features}}
    (HERE / "MODEL_STATES.json").write_text(json.dumps(states, indent=2) + "\n")
    for rows, vectors in ((train, (c0_train, m1_train, l1_train)),
                          (test, (c0_test, m1_test, l1_test))):
        for row, c, m, l in zip(rows, *vectors):
            row["C0"], row["M1"], row["L1"] = map(float, (c, m, l))
            if not all(math.isfinite(row[k]) and row[k] >= 0 for k in ("B0", "C0", "M1", "L1")):
                raise ValueError("invalid prediction")
    with (HERE / "PREDICTIONS.csv").open("w", newline="") as handle:
        names = ["year", "site", "origin_time_gmt_end", "target_time_gmt_end",
                 "origin_day_gmt", "target", "neighbor_count", "B0", "C0", "M1", "L1"]
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows({k: r[k] for k in names} for r in test)

    names = ("B0", "C0", "M1", "L1")
    overall = {n: score(test, n) for n in names}
    train_scores = {n: score(train, n) for n in names}
    by_station = {s: {n: score([r for r in test if r["site"] == s], n) for n in names}
                  for s in SITES}
    eligible_stations = [s for s in SITES if by_station[s]["B0"]["n"] >= 10]
    if len(eligible_stations) != 9:
        raise ValueError("EXP064 eligible station count changed")
    candidate_results = {}
    for name in ("C0", "M1", "L1"):
        block = block_diff(test, name, "B0")
        relative = 1 - overall[name]["MAE"] / overall["B0"]["MAE"]
        station_gain = {s: 1 - by_station[s][name]["MAE"] / by_station[s]["B0"]["MAE"]
                        for s in eligible_stations}
        conditions = {"overall_gain_at_least_5pct": relative >= .05,
                      "day_block_CI_upper_below_zero": block["bootstrap_95ci"][1] < 0,
                      "at_least_6_of_9_stations_better": sum(v > 0 for v in station_gain.values()) >= 6,
                      "no_eligible_station_worse_over_20pct": min(station_gain.values()) >= -.20}
        candidate_results[name] = {"relative_MAE_gain_vs_B0": relative,
                                   "day_block": block, "station_gains": station_gain,
                                   "conditions": conditions, "pass": all(conditions.values())}
    extra_block = block_diff(test, "L1", "M1")
    extra_gain = 1 - overall["L1"]["MAE"] / overall["M1"]["MAE"]
    station_extra = {s: 1 - by_station[s]["L1"]["MAE"] / by_station[s]["M1"]["MAE"]
                     for s in eligible_stations}
    extra_conditions = {"overall_L1_vs_M1_gain_at_least_3pct": extra_gain >= .03,
                        "day_block_CI_upper_below_zero": extra_block["bootstrap_95ci"][1] < 0,
                        "at_least_6_of_9_stations_better": sum(v > 0 for v in station_extra.values()) >= 6}
    metric = {"run_id": RUN_ID, "qualification": "retrospective real 2024 training; previously unscored 2025 time holdout; exploratory",
              "train_year": 2024, "train_pairs": len(train),
              "test_year": 2025, "test_pairs": len(test),
              "test_days": len({r["origin_day_gmt"] for r in test}),
              "train_scores_fit_in_sample": train_scores,
              "overall": overall, "by_station": by_station,
              "eligible_station_gate_set": eligible_stations,
              "candidate_results": candidate_results,
              "L1_additional_vs_M1": {"relative_MAE_gain": extra_gain,
                   "day_block": extra_block, "station_gains": station_extra,
                   "conditions": extra_conditions, "pass": all(extra_conditions.values())},
              "any_local_stat_candidate_supported": any(x["pass"] for x in candidate_results.values())}
    (HERE / "METRICS.json").write_text(json.dumps(metric, indent=2) + "\n")
    print("MODEL C0_LOG_OFFSET", offset, flush=True)
    print("2025_MAE", {n: overall[n]["MAE"] for n in names}, flush=True)
    print("CANDIDATE_PASS", {n: x["pass"] for n, x in candidate_results.items()}, flush=True)
    print("L1_EXTRA_PASS", metric["L1_additional_vs_M1"]["pass"], flush=True)


if __name__ == "__main__":
    main()
