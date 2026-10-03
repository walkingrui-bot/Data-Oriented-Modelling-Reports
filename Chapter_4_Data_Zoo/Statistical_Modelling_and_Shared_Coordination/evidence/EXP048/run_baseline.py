"""EXP048 fixed 24h PM2.5 persistence vs ridge on original UCI observations."""

import csv
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
P46 = HERE.parent / "STAT-PSYMOE-EXP046-20261002-001"
P47 = HERE.parent / "STAT-PSYMOE-EXP047-20261002-001"
META = json.loads((P46 / "SOURCE_METADATA.json").read_text())
QUAL = json.loads((P47 / "NUMERIC_SUMMARY.json").read_text())
HELD_OUT = ("Aotizhongxin", "Wanshouxigong")
MAX_BYTES = 20 * 1024 * 1024


def features(frame):
    time = frame["time"]
    hour = time.dt.hour.to_numpy(dtype=float)
    year_phase = (time.dt.dayofyear.to_numpy(dtype=float) - 1 + hour / 24) / 365.25
    return np.column_stack((
        np.log1p(frame["PM2.5"].to_numpy(dtype=float)),
        frame["TEMP"].to_numpy(dtype=float),
        frame["PRES"].to_numpy(dtype=float),
        frame["WSPM"].to_numpy(dtype=float),
        np.sin(2 * np.pi * hour / 24), np.cos(2 * np.pi * hour / 24),
        np.sin(2 * np.pi * year_phase), np.cos(2 * np.pi * year_phase),
    ))


def scores(y, baseline, ridge):
    return {
        "n": int(len(y)),
        "B0_persistence_MAE": float(np.mean(np.abs(y - baseline))),
        "B1_ridge_MAE": float(np.mean(np.abs(y - ridge))),
        "B0_persistence_RMSE": float(np.sqrt(np.mean((y - baseline) ** 2))),
        "B1_ridge_RMSE": float(np.sqrt(np.mean((y - ridge) ** 2))),
        "B1_relative_MAE_improvement": float(1 - np.mean(np.abs(y - ridge)) / np.mean(np.abs(y - baseline))),
    }


def main():
    assert QUAL["gate"] == "REAL_MULTISITE_SOURCE_READY" and QUAL["qualified_station_count"] == 12
    assert sorted(QUAL["qualifying_stations"])[0] == HELD_OUT[0]
    assert sorted(QUAL["qualifying_stations"])[-1] == HELD_OUT[1]
    if any((HERE / name).exists() for name in ("PAIR_SUPPORT.json", "MODEL_STATE.json", "METRICS.json", "HOLDOUT_PREDICTIONS.csv")):
        raise FileExistsError("EXP048 attempt outputs already exist; preserve them")
    request = urllib.request.Request(META["official_download"], headers={"User-Agent": "EXP048-baseline/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_BYTES:
            raise RuntimeError("original ZIP exceeds budget")
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise RuntimeError("original ZIP response exceeds budget")
    with zipfile.ZipFile(io.BytesIO(body)) as outer:
        inner_name = "PRSA2017_Data_20130301-20170228.zip"
        nested = outer.read(inner_name)
    frames = []
    with zipfile.ZipFile(io.BytesIO(nested)) as inner:
        for item in inner.infolist():
            basename = Path(item.filename).name
            match = re.fullmatch(r"PRSA_Data_(.+)_20130301-20170228\.csv", basename)
            if not match:
                continue
            station = match.group(1)
            with inner.open(item) as stream:
                frame = pd.read_csv(stream, na_values=["NA"])
            assert set(frame["station"].dropna().unique()) == {station} and len(frame) == 35064
            frame["time"] = pd.to_datetime(frame[["year", "month", "day", "hour"]])
            frame = frame.sort_values("time").reset_index(drop=True)
            assert frame["time"].is_unique and frame["time"].iloc[0] == pd.Timestamp("2013-03-01 00:00:00") and frame["time"].iloc[-1] == pd.Timestamp("2017-02-28 23:00:00")
            frame["future_time"] = frame["time"].shift(-24)
            frame["target_PM2.5"] = frame["PM2.5"].shift(-24)
            assert (frame["future_time"].iloc[:-24] == frame["time"].iloc[:-24] + pd.Timedelta(hours=24)).all()
            frames.append(frame[["station", "time", "future_time", "PM2.5", "TEMP", "PRES", "WSPM", "target_PM2.5"]])
    all_rows = pd.concat(frames, ignore_index=True)
    complete = all_rows[["PM2.5", "TEMP", "PRES", "WSPM", "target_PM2.5"]].notna().all(axis=1)
    for col in ("PM2.5", "TEMP", "PRES", "WSPM", "target_PM2.5"):
        complete &= np.isfinite(all_rows[col])
    complete &= (all_rows["PM2.5"] >= 0) & (all_rows["target_PM2.5"] >= 0)
    valid = all_rows.loc[complete].copy()
    train_sites = set(QUAL["qualifying_stations"]) - set(HELD_OUT)
    t = valid["time"]
    train_time = (t >= "2013-03-01") & (t < "2015-12-31")
    val_time = (t >= "2016-01-01") & (t < "2016-12-31")
    future_time = (t >= "2017-01-01") & (t < "2017-02-28")
    in_train_sites = valid["station"].isin(train_sites)
    in_holdout_sites = valid["station"].isin(HELD_OUT)
    masks = {
        "train": train_time & in_train_sites,
        "validation_same10": val_time & in_train_sites,
        "future_same10": future_time & in_train_sites,
        "station_2016": val_time & in_holdout_sites,
        "future_station_2": future_time & in_holdout_sites,
    }
    domains = {name: valid.loc[mask].copy() for name, mask in masks.items()}
    thresholds = {"train": 100000, "validation_same10": 70000, "future_same10": 10000, "station_2016": 14000, "future_station_2": 2000}
    counts = {name: len(frame) for name, frame in domains.items()}
    heldout_future_by_station = domains["future_station_2"].groupby("station").size().to_dict()
    source_pass = all(counts[name] >= threshold for name, threshold in thresholds.items()) and all(heldout_future_by_station.get(station, 0) >= 900 for station in HELD_OUT)
    support = {"run_id": "EXP048-BASELINE-001", "official_original_url": META["official_download"], "network_requests": 1, "response_bytes": len(body), "all_original_rows": len(all_rows), "complete_observed_24h_pairs_all_stations": len(valid), "excluded_missing_or_invalid_pairs": len(all_rows) - len(valid), "held_out_stations": HELD_OUT, "train_station_count": len(train_sites), "domain_pair_counts": counts, "heldout_future_by_station": heldout_future_by_station, "thresholds": thresholds, "gate": "PAIR_SUPPORT_PASS" if source_pass else "STOP_PAIR_SUPPORT"}
    (HERE / "PAIR_SUPPORT.json").write_text(json.dumps(support, ensure_ascii=False, indent=2) + "\n")
    print("PAIR_SUPPORT", json.dumps(support, ensure_ascii=False), flush=True)
    if not source_pass:
        return
    train = domains["train"]
    scaler = StandardScaler()
    x_train = scaler.fit_transform(features(train))
    y_train = np.log1p(train["target_PM2.5"].to_numpy(dtype=float))
    model = Ridge(alpha=1.0, fit_intercept=True)
    model.fit(x_train, y_train)
    state = {"run_id": "EXP048-BASELINE-001", "model": "Ridge(alpha=1.0, fit_intercept=True)", "target_transform": "log1p", "inverse": "max(0, expm1)", "feature_order": ["log1p_current_PM2.5", "TEMP", "PRES", "WSPM", "sin_hour", "cos_hour", "sin_year_phase", "cos_year_phase"], "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(), "coef": model.coef_.tolist(), "intercept": float(model.intercept_), "train_pairs": len(train)}
    (HERE / "MODEL_STATE.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    metrics = {"run_id": "EXP048-BASELINE-001", "development_only_validation": "validation_same10", "test_evaluated_once": ["future_same10", "station_2016", "future_station_2"], "domains": {}, "by_station": {}}
    with (HERE / "HOLDOUT_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["domain", "station", "origin_time", "target_time", "observed_target_PM2.5", "B0_persistence", "B1_ridge"])
        writer.writeheader()
        for name in ("validation_same10", "future_same10", "station_2016", "future_station_2"):
            frame = domains[name]
            y = frame["target_PM2.5"].to_numpy(dtype=float)
            baseline = frame["PM2.5"].to_numpy(dtype=float)
            pred = np.maximum(0, np.expm1(model.predict(scaler.transform(features(frame)))))
            metrics["domains"][name] = scores(y, baseline, pred)
            metrics["by_station"][name] = {}
            for station in sorted(frame["station"].unique()):
                sel = frame["station"].to_numpy() == station
                metrics["by_station"][name][station] = scores(y[sel], baseline[sel], pred[sel])
            for station, origin, target_time, yi, b0, b1 in zip(frame["station"], frame["time"], frame["future_time"], y, baseline, pred):
                writer.writerow({"domain": name, "station": station, "origin_time": origin.isoformat(), "target_time": target_time.isoformat(), "observed_target_PM2.5": float(yi), "B0_persistence": float(b0), "B1_ridge": float(b1)})
            print(name, metrics["domains"][name], flush=True)
    metrics["gate_pass"] = all(metrics["domains"][name]["B1_relative_MAE_improvement"] >= 0.05 for name in ("validation_same10", "future_same10", "station_2016", "future_station_2"))
    metrics["conclusion_code"] = "TRADITIONAL_BASELINE_GENERALISES_IN_FROZEN_DOMAINS" if metrics["gate_pass"] else "NO_STABLE_TRADITIONAL_GAIN"
    (HERE / "METRICS.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    print("OVERALL_GATE", metrics["conclusion_code"], flush=True)


if __name__ == "__main__":
    main()
