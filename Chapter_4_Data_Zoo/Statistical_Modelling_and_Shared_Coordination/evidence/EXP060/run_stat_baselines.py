#!/usr/bin/env python3
"""EXP060 traditional baselines on real naturally missing origin PM2.5."""

from __future__ import annotations

import json
import math
import sys
import time
import traceback
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler


HERE = Path(__file__).resolve().parent
P59 = HERE.parent / "STAT-PSYMOE-EXP059-20261002-001"
sys.path.insert(0, str(P59))
from audit_natural_outage import HELD_OUT, load_original  # noqa: E402

RUN_ID = "EXP060-STAT-001"
EXPECTED_COUNTS = {
    "train_same10": 3185, "validation_same10": 1286, "future_same10": 85,
    "station_2016": 277, "future_station_2": 16,
}
NEIGHBOR_FEATURES = ["log_neighbor_p25", "log_neighbor_median", "log_neighbor_p75",
                     "neighbor_count", "sin_hour", "cos_hour", "sin_year", "cos_year"]
WEATHER_FEATURES = ["TEMP", "PRES", "WSPM", "sin_hour", "cos_hour", "sin_year", "cos_year"]
JOINT_FEATURES = ["log_neighbor_p25", "log_neighbor_median", "log_neighbor_p75",
                  "neighbor_count", "TEMP", "PRES", "WSPM",
                  "sin_hour", "cos_hour", "sin_year", "cos_year"]


def make_pairs(frames):
    stations = sorted(frames)
    hours = frames[stations[0]].index
    pm = pd.DataFrame({station: frames[station]["PM2.5"] for station in stations}, index=hours)
    valid_pm = np.isfinite(pm.to_numpy(float)) & (pm.to_numpy(float) >= 0)
    neighbor_total = valid_pm.sum(axis=1)
    records = []
    domain_counts = {name: 0 for name in EXPECTED_COUNTS}
    for j, station in enumerate(stations):
        original = frames[station]
        current = original["PM2.5"].to_numpy(float)
        future = original["PM2.5"].shift(-24).to_numpy(float)
        weather = original[["TEMP", "PRES", "WSPM"]].to_numpy(float)
        neighbor_count = neighbor_total - valid_pm[:, j].astype(int)
        eligible = np.isnan(current) & np.isfinite(future) & (future >= 0) & (
            np.isfinite(weather).all(axis=1)
        ) & (neighbor_count >= 8)
        indices = np.flatnonzero(eligible)
        if not len(indices):
            continue
        other = pm.drop(columns=station).to_numpy(float)[indices]
        other = np.where(np.isfinite(other) & (other >= 0), other, np.nan)
        percentiles = np.nanpercentile(other, (25, 50, 75), axis=1)
        if not np.isfinite(percentiles).all():
            raise RuntimeError(f"Neighbor percentile invalid: {station}")
        selected_time = hours[indices]
        selected_weather = weather[indices]
        selected_future = future[indices]
        count = neighbor_count[indices]
        train_site = station not in HELD_OUT
        hour = selected_time.hour.to_numpy(dtype=float)
        year_phase = (selected_time.dayofyear.to_numpy(dtype=float) - 1 + hour / 24) / 365.25
        candidate = pd.DataFrame({
            "station": station, "origin_time": selected_time,
            "target_time": selected_time + pd.Timedelta(hours=24),
            "target": selected_future,
            "neighbor_count": count,
            "neighbor_median": percentiles[1],
            "log_neighbor_p25": np.log1p(percentiles[0]),
            "log_neighbor_median": np.log1p(percentiles[1]),
            "log_neighbor_p75": np.log1p(percentiles[2]),
            "TEMP": selected_weather[:, 0], "PRES": selected_weather[:, 1],
            "WSPM": selected_weather[:, 2],
            "sin_hour": np.sin(2 * np.pi * hour / 24),
            "cos_hour": np.cos(2 * np.pi * hour / 24),
            "sin_year": np.sin(2 * np.pi * year_phase),
            "cos_year": np.cos(2 * np.pi * year_phase),
        })
        time = candidate.origin_time
        masks = {
            "train_same10": train_site & (time >= "2013-03-01") & (time < "2015-12-31"),
            "validation_same10": train_site & (time >= "2016-01-01") & (time < "2016-12-31"),
            "future_same10": train_site & (time >= "2017-01-01") & (time < "2017-02-28"),
            "station_2016": (not train_site) & (time >= "2016-01-01") & (time < "2016-12-31"),
            "future_station_2": (not train_site) & (time >= "2017-01-01") & (time < "2017-02-28"),
        }
        for name, mask in masks.items():
            subset = candidate.loc[mask].copy()
            subset["domain"] = name
            domain_counts[name] += len(subset)
            records.append(subset)
    pairs = pd.concat(records, ignore_index=True)
    if domain_counts != EXPECTED_COUNTS:
        raise RuntimeError(f"EXP059 source pair counts changed: {domain_counts} != {EXPECTED_COUNTS}")
    if pairs.duplicated(["station", "origin_time"]).any():
        raise RuntimeError("Duplicate natural-outage station-hour pairs")
    if not np.isfinite(pairs[["target", "neighbor_median", *JOINT_FEATURES]].to_numpy(float)).all():
        raise RuntimeError("Nonfinite model value")
    return pairs, domain_counts


def fit_ridge(train, pairs, features):
    scaler = StandardScaler()
    x = scaler.fit_transform(train[features].to_numpy(float))
    y = np.log1p(train.target.to_numpy(float))
    model = Ridge(alpha=1.0, fit_intercept=True)
    model.fit(x, y)
    predicted = np.maximum(0, np.expm1(model.predict(scaler.transform(pairs[features].to_numpy(float)))))
    if not np.isfinite(predicted).all():
        raise RuntimeError("Nonfinite ridge prediction")
    state = {"model": "Ridge(alpha=1.0, fit_intercept=True)",
             "fit_unit": "log1p(real_t_plus_24_PM2.5)", "inverse": "max(0, expm1)",
             "features": features, "scaler_mean": scaler.mean_.tolist(),
             "scaler_scale": scaler.scale_.tolist(),
             "coef": model.coef_.tolist(), "intercept": float(model.intercept_),
             "train_pairs": len(train)}
    return state, predicted


def score(frame, model):
    y = frame.target.to_numpy(float)
    p = frame[model].to_numpy(float)
    return {"n": len(frame), "MAE": float(np.mean(np.abs(y - p))),
            "RMSE": float(np.sqrt(np.mean((y - p) ** 2)))}


def day_block_ci(frame, seed):
    error_difference = np.abs(frame.target.to_numpy(float) - frame.J1.to_numpy(float)) - (
        np.abs(frame.target.to_numpy(float) - frame.N1.to_numpy(float))
    )
    grouped = pd.DataFrame({"day": frame.origin_time.dt.floor("D"),
                            "difference": error_difference}).groupby("day").difference.agg(["sum", "count"])
    sums = grouped["sum"].to_numpy(float)
    counts = grouped["count"].to_numpy(int)
    if not len(sums):
        raise RuntimeError("No calendar-day bootstrap units")
    rng = np.random.default_rng(seed)
    sampled = rng.integers(0, len(sums), size=(1000, len(sums)))
    values = sums[sampled].sum(axis=1) / counts[sampled].sum(axis=1)
    return {"block": "calendar_day_all_stations_together", "days": len(sums),
            "resamples": 1000, "seed": seed,
            "J1_minus_N1_MAE": float(np.mean(error_difference)),
            "bootstrap_95ci": np.quantile(values, [0.025, 0.975]).tolist()}


def main():
    for name in ("PAIR_SUPPORT.json", "MODEL_STATES.json", "METRICS.json", "FAILURE.json"):
        if (HERE / name).exists():
            raise FileExistsError("Preserve previous attempt output: " + name)
    start = time.monotonic()
    frames, response_bytes, nested = load_original()
    pairs, counts = make_pairs(frames)
    support = {"run_id": RUN_ID, "official_original_url":
               json.loads((P59 / "SOURCE_SUPPORT.json").read_text())["official_original_url"],
               "network_requests": 1, "response_bytes": response_bytes,
               "nested_original_member": nested,
               "domain_pair_counts": counts, "matches_EXP059_frozen_source": True,
               "natural_origin_NA_only": True, "future_target_exactly_24_hours": True,
               "no_raw_data_copy": True}
    (HERE / "PAIR_SUPPORT.json").write_text(json.dumps(support, indent=2) + "\n")
    print("PAIR_SUPPORT", json.dumps(counts), flush=True)
    train = pairs.loc[pairs.domain == "train_same10"]
    states = {"run_id": RUN_ID, "train_pairs": len(train), "B0":
              {"model": "neighbor_median_at_origin_no_fit"}}
    pairs["B0"] = pairs.neighbor_median.to_numpy(float)
    for name, features in (("N1", NEIGHBOR_FEATURES), ("W1", WEATHER_FEATURES),
                           ("J1", JOINT_FEATURES)):
        states[name], pairs[name] = fit_ridge(train, pairs, features)
    (HERE / "MODEL_STATES.json").write_text(json.dumps(states, indent=2) + "\n")
    metrics = {"run_id": RUN_ID, "qualification": "exploratory natural-missingness prediction within original Beijing source",
               "domains": {}, "by_station": {}, "day_block_paired": {},
               "models": ("B0", "N1", "W1", "J1"), "train_pairs": len(train)}
    for name in EXPECTED_COUNTS:
        subset = pairs.loc[pairs.domain == name]
        metrics["domains"][name] = {model: score(subset, model) for model in metrics["models"]}
        metrics["by_station"][name] = {
            station: {model: score(rows, model) for model in metrics["models"]}
            for station, rows in subset.groupby("station")
        }
        print(name, {model: round(metrics["domains"][name][model]["MAE"], 4)
                     for model in metrics["models"]}, flush=True)
    for name in ("validation_same10", "station_2016"):
        metrics["day_block_paired"][name] = day_block_ci(
            pairs.loc[pairs.domain == name], 20261002
        )
    def rel(name, baseline):
        scores = metrics["domains"][name]
        return 1 - scores["J1"]["MAE"] / scores[baseline]["MAE"]
    validation = rel("validation_same10", "N1")
    heldout = rel("station_2016", "N1")
    future = rel("future_same10", "N1")
    versus_b0 = {name: rel(name, "B0") for name in ("validation_same10", "station_2016")}
    ci = metrics["day_block_paired"]
    conditions = {"validation_N1_improvement_at_least_3pct": validation >= .03,
                  "station2016_N1_improvement_at_least_2pct": heldout >= .02,
                  "validation_day_block_CI_upper_below_zero": ci["validation_same10"]["bootstrap_95ci"][1] < 0,
                  "station2016_day_block_CI_upper_below_zero": ci["station_2016"]["bootstrap_95ci"][1] < 0,
                  "validation_B0_improvement_at_least_5pct": versus_b0["validation_same10"] >= .05,
                  "station2016_B0_improvement_at_least_5pct": versus_b0["station_2016"] >= .05,
                  "future_same10_N1_no_more_than_5pct_worse": future >= -.05}
    metrics["gate"] = {"J1_vs_N1_relative_MAE_improvement": {
        "validation_same10": validation, "station_2016": heldout, "future_same10": future},
        "J1_vs_B0_relative_MAE_improvement": versus_b0,
        "conditions": conditions,
        "pass": all(conditions.values()),
        "code": "JOINT_WEATHER_ADDED_VALUE" if all(conditions.values()) else "NO_STABLE_JOINT_WEATHER_GAIN"}
    metrics["run_seconds"] = time.monotonic() - start
    (HERE / "METRICS.json").write_text(json.dumps(metrics, indent=2) + "\n")
    output = pairs.loc[pairs.domain != "train_same10", [
        "domain", "station", "origin_time", "target_time", "target",
        "neighbor_count", "B0", "N1", "W1", "J1"
    ]].rename(columns={"target": "observed_target_PM2.5"})
    output.to_csv(HERE / "PREDICTIONS.csv", index=False)
    print("GATE", metrics["gate"]["code"], json.dumps(conditions), flush=True)
    print("RUN_SECONDS", metrics["run_seconds"], flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not (HERE / "FAILURE.json").exists():
            (HERE / "FAILURE.json").write_text(json.dumps({
                "run_id": RUN_ID, "error_type": type(exc).__name__,
                "error": str(exc), "traceback": traceback.format_exc(),
                "existing_direct_outputs": sorted(p.name for p in HERE.iterdir()),
            }, indent=2) + "\n")
        raise
