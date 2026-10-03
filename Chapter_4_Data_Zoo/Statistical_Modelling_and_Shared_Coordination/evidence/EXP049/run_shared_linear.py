"""EXP049: original Beijing source, fixed contemporaneous network mean, one ridge."""

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
ROOT = HERE.parent
EXP046 = ROOT / "STAT-PSYMOE-EXP046-20261002-001"
EXP047 = ROOT / "STAT-PSYMOE-EXP047-20261002-001"
EXP048 = ROOT / "STAT-PSYMOE-EXP048-20261002-001"
SOURCE = json.loads((EXP046 / "SOURCE_METADATA.json").read_text())
QUAL = json.loads((EXP047 / "NUMERIC_SUMMARY.json").read_text())
HELD_OUT = ("Aotizhongxin", "Wanshouxigong")
TRAIN_SITES = sorted(set(QUAL["qualifying_stations"]) - set(HELD_OUT))
MAX_BYTES = 20 * 1024 * 1024
RUN_ID = "EXP049-SHARED-LINEAR-001"
EVALUATION = ("validation_same10", "future_same10", "station_2016", "future_station_2")


def local_features(frame):
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
        np.log1p(frame["reference_mean_PM2.5"].to_numpy(dtype=float)),
    ))


def scores(frame):
    y = frame["target_PM2.5"].to_numpy(dtype=float)
    b1 = frame["B1_ridge"].to_numpy(dtype=float)
    b2 = frame["B2_ridge"].to_numpy(dtype=float)
    b1_mae = float(np.mean(np.abs(y - b1)))
    b2_mae = float(np.mean(np.abs(y - b2)))
    return {
        "n": int(len(frame)),
        "B1_matched_MAE": b1_mae,
        "B2_shared_linear_MAE": b2_mae,
        "B1_matched_RMSE": float(np.sqrt(np.mean((y - b1) ** 2))),
        "B2_shared_linear_RMSE": float(np.sqrt(np.mean((y - b2) ** 2))),
        "B2_relative_MAE_improvement": float(1 - b2_mae / b1_mae),
    }


def main():
    assert QUAL["gate"] == "REAL_MULTISITE_SOURCE_READY" and len(TRAIN_SITES) == 10
    assert sorted(QUAL["qualifying_stations"])[0] == HELD_OUT[0]
    assert sorted(QUAL["qualifying_stations"])[-1] == HELD_OUT[1]
    for name in ("PAIR_SUPPORT.json", "MODEL_STATE.json", "METRICS.json", "B2_PREDICTIONS.csv"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP049 existing result {name}; preserve prior attempt")

    request = urllib.request.Request(SOURCE["official_download"], headers={"User-Agent": "EXP049-network-linear/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_BYTES:
            raise RuntimeError("original ZIP exceeds frozen 20 MiB budget")
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise RuntimeError("original ZIP response exceeds frozen 20 MiB budget")
    with zipfile.ZipFile(io.BytesIO(body)) as outer:
        nested = outer.read("PRSA2017_Data_20130301-20170228.zip")
    frames = []
    with zipfile.ZipFile(io.BytesIO(nested)) as inner:
        for item in inner.infolist():
            match = re.fullmatch(r"PRSA_Data_(.+)_20130301-20170228\.csv", Path(item.filename).name)
            if not match:
                continue
            station = match.group(1)
            with inner.open(item) as stream:
                frame = pd.read_csv(stream, na_values=["NA"])
            assert len(frame) == 35064 and set(frame["station"].dropna().unique()) == {station}
            frame["time"] = pd.to_datetime(frame[["year", "month", "day", "hour"]])
            frame = frame.sort_values("time").reset_index(drop=True)
            assert frame["time"].is_unique
            assert frame["time"].iloc[0] == pd.Timestamp("2013-03-01 00:00:00")
            assert frame["time"].iloc[-1] == pd.Timestamp("2017-02-28 23:00:00")
            frame["target_time"] = frame["time"].shift(-24)
            frame["target_PM2.5"] = frame["PM2.5"].shift(-24)
            assert (frame["target_time"].iloc[:-24] == frame["time"].iloc[:-24] + pd.Timedelta(hours=24)).all()
            frames.append(frame[["station", "time", "target_time", "PM2.5", "TEMP", "PRES", "WSPM", "target_PM2.5"]])
    assert len(frames) == 12
    all_rows = pd.concat(frames, ignore_index=True)
    assert len(all_rows) == 420768

    # Only the ten EXP048 training stations may contribute network inputs.
    reference = all_rows.loc[all_rows["station"].isin(TRAIN_SITES), ["station", "time", "PM2.5"]]
    reference = reference.pivot(index="time", columns="station", values="PM2.5").reindex(columns=TRAIN_SITES)
    reference = reference.where(np.isfinite(reference) & (reference >= 0))
    prepared = []
    for station, frame in all_rows.groupby("station", sort=True):
        peers = reference.drop(columns=[station]) if station in TRAIN_SITES else reference
        count = peers.notna().sum(axis=1)
        mean = peers.mean(axis=1, skipna=True)
        frame = frame.copy()
        frame["reference_count"] = frame["time"].map(count).to_numpy(dtype=int)
        frame["reference_mean_PM2.5"] = frame["time"].map(mean).to_numpy(dtype=float)
        prepared.append(frame)
    all_rows = pd.concat(prepared, ignore_index=True)
    complete = all_rows[["PM2.5", "TEMP", "PRES", "WSPM", "target_PM2.5", "reference_mean_PM2.5"]].notna().all(axis=1)
    for name in ("PM2.5", "TEMP", "PRES", "WSPM", "target_PM2.5", "reference_mean_PM2.5"):
        complete &= np.isfinite(all_rows[name])
    complete &= (all_rows["PM2.5"] >= 0) & (all_rows["target_PM2.5"] >= 0)
    complete &= (all_rows["reference_count"] >= 8) & (all_rows["reference_mean_PM2.5"] >= 0)
    valid = all_rows.loc[complete].copy()
    t = valid["time"]
    train_time = (t >= "2013-03-01") & (t < "2015-12-31")
    val_time = (t >= "2016-01-01") & (t < "2016-12-31")
    future_time = (t >= "2017-01-01") & (t < "2017-02-28")
    in_train = valid["station"].isin(TRAIN_SITES)
    in_held = valid["station"].isin(HELD_OUT)
    domains = {
        "train": valid.loc[train_time & in_train].copy(),
        "validation_same10": valid.loc[val_time & in_train].copy(),
        "future_same10": valid.loc[future_time & in_train].copy(),
        "station_2016": valid.loc[val_time & in_held].copy(),
        "future_station_2": valid.loc[future_time & in_held].copy(),
    }
    thresholds = {"train": 180000, "validation_same10": 60000, "future_same10": 9000, "station_2016": 13000, "future_station_2": 1800}
    counts = {name: len(frame) for name, frame in domains.items()}
    held_future = domains["future_station_2"].groupby("station").size().to_dict()
    source_pass = all(counts[name] >= minimum for name, minimum in thresholds.items()) and all(held_future.get(station, 0) >= 750 for station in HELD_OUT)
    support = {
        "run_id": RUN_ID,
        "official_original_url": SOURCE["official_download"],
        "EXP048_B1_predictions_original_path": str(EXP048 / "HOLDOUT_PREDICTIONS.csv"),
        "network_requests": 1,
        "response_bytes": len(body),
        "all_original_rows": len(all_rows),
        "network_eligible_observed_24h_pairs": len(valid),
        "excluded_missing_or_insufficient_reference": len(all_rows) - len(valid),
        "reference_sites": TRAIN_SITES,
        "held_out_stations": HELD_OUT,
        "domain_pair_counts": counts,
        "heldout_future_by_station": held_future,
        "reference_count_distribution_by_domain": {name: frame["reference_count"].value_counts().sort_index().to_dict() for name, frame in domains.items()},
        "thresholds": thresholds,
        "gate": "PAIR_SUPPORT_PASS" if source_pass else "STOP_NETWORK_PAIR_SUPPORT",
    }
    (HERE / "PAIR_SUPPORT.json").write_text(json.dumps(support, ensure_ascii=False, indent=2) + "\n")
    print("PAIR_SUPPORT", json.dumps({"counts": counts, "heldout_future": held_future, "gate": support["gate"]}), flush=True)
    if not source_pass:
        return

    old = pd.read_csv(EXP048 / "HOLDOUT_PREDICTIONS.csv")
    old["origin_time"] = pd.to_datetime(old["origin_time"])
    old["target_time"] = pd.to_datetime(old["target_time"])
    assert len(old) == 116919 and not old.duplicated(["domain", "station", "origin_time"]).any()
    for name in EVALUATION:
        frame = domains[name]
        prior = old.loc[old["domain"] == name, ["station", "origin_time", "target_time", "observed_target_PM2.5", "B1_ridge"]]
        joined = frame.merge(prior, left_on=["station", "time"], right_on=["station", "origin_time"], how="left", validate="one_to_one")
        assert joined["B1_ridge"].notna().all() and len(joined) == len(frame)
        assert (joined["target_time_x"] == joined["target_time_y"]).all()
        assert np.array_equal(joined["target_PM2.5"].to_numpy(), joined["observed_target_PM2.5"].to_numpy())
        assert (joined["reference_count"] >= 8).all()
        domains[name] = joined

    train = domains["train"]
    scaler = StandardScaler()
    x_train = scaler.fit_transform(local_features(train))
    model = Ridge(alpha=1.0, fit_intercept=True)
    model.fit(x_train, np.log1p(train["target_PM2.5"].to_numpy(dtype=float)))
    state = {
        "run_id": RUN_ID, "model": "Ridge(alpha=1.0, fit_intercept=True)",
        "target_transform": "log1p", "inverse": "max(0, expm1)",
        "feature_order": ["log1p_current_PM2.5", "TEMP", "PRES", "WSPM", "sin_hour", "cos_hour", "sin_year_phase", "cos_year_phase", "log1p_current_reference_mean_PM2.5"],
        "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(),
        "coef": model.coef_.tolist(), "intercept": float(model.intercept_),
        "train_pairs": len(train), "EXP048_B1_model_original_path": str(EXP048 / "MODEL_STATE.json"),
    }
    (HERE / "MODEL_STATE.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    metrics = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_HOLDOUTS", "EXP048_B1_predictions_original_path": str(EXP048 / "HOLDOUT_PREDICTIONS.csv"), "domains": {}, "by_station": {}}
    with (HERE / "B2_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["domain", "station", "origin_time", "target_time", "observed_target_PM2.5", "reference_count", "reference_mean_PM2.5", "B2_ridge"])
        writer.writeheader()
        for name in EVALUATION:
            frame = domains[name]
            frame["B2_ridge"] = np.maximum(0, np.expm1(model.predict(scaler.transform(local_features(frame)))))
            metrics["domains"][name] = scores(frame)
            metrics["by_station"][name] = {station: scores(group) for station, group in frame.groupby("station")}
            columns = ["station", "time", "target_time_x", "target_PM2.5", "reference_count", "reference_mean_PM2.5", "B2_ridge"]
            for station, origin, target_time, observed, ref_count, ref_mean, prediction in frame[columns].itertuples(index=False, name=None):
                writer.writerow({
                    "domain": name, "station": station, "origin_time": origin.isoformat(),
                    "target_time": target_time.isoformat(), "observed_target_PM2.5": float(observed),
                    "reference_count": int(ref_count), "reference_mean_PM2.5": float(ref_mean),
                    "B2_ridge": float(prediction),
                })
            print(name, metrics["domains"][name], flush=True)
    metrics["gate_pass"] = all(metrics["domains"][name]["B2_relative_MAE_improvement"] >= 0.03 for name in EVALUATION) and all(metrics["by_station"]["future_station_2"][station]["B2_relative_MAE_improvement"] >= 0 for station in HELD_OUT)
    metrics["conclusion_code"] = "EXPLORATORY_SHARED_CURRENT_SIGNAL" if metrics["gate_pass"] else "NO_STABLE_SHARED_CURRENT_GAIN"
    (HERE / "METRICS.json").write_text(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
    print("OVERALL_GATE", metrics["conclusion_code"], flush=True)


if __name__ == "__main__":
    main()
