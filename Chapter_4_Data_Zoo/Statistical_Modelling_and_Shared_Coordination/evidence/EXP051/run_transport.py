"""EXP051 frozen Beijing common-schema ridge and one external four-city score."""

import csv
import io
import json
import re
import subprocess
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
E046 = ROOT / "STAT-PSYMOE-EXP046-20261002-001"
E047 = ROOT / "STAT-PSYMOE-EXP047-20261002-001"
E050 = ROOT / "STAT-PSYMOE-EXP050-20261002-001"
BEIJING_URL = json.loads((E046 / "SOURCE_METADATA.json").read_text())["official_download"]
FIVE_URL = json.loads((E050 / "SOURCE_METADATA.json").read_text())["official_original_download"]
QUAL = json.loads((E047 / "NUMERIC_SUMMARY.json").read_text())
HELD = ("Aotizhongxin", "Wanshouxigong")
TRAIN_SITES = sorted(set(QUAL["qualifying_stations"]) - set(HELD))
CITIES = ("Chengdu", "Guangzhou", "Shanghai", "Shenyang")
RUN_ID = "EXP051-TRANSPORT-001"


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def original_read(url, max_bytes, user_agent):
    request = urllib.request.Request(url, headers={"User-Agent": user_agent})
    with urllib.request.urlopen(request, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > max_bytes:
            raise RuntimeError("official response exceeds preregistered network budget")
        body = response.read(max_bytes + 1)
    if len(body) > max_bytes:
        raise RuntimeError("official response exceeds preregistered network budget")
    return body


def features(frame):
    return np.column_stack((
        np.log1p(frame["PM"].to_numpy(dtype=float)),
        frame["TEMP"].to_numpy(dtype=float),
        frame["PRES"].to_numpy(dtype=float),
    ))


def scores(frame, prediction):
    y = frame["target_PM"].to_numpy(dtype=float)
    b0 = frame["PM"].to_numpy(dtype=float)
    b1 = prediction
    mae0 = float(np.mean(np.abs(y - b0)))
    mae1 = float(np.mean(np.abs(y - b1)))
    return {
        "n": int(len(frame)),
        "B0_persistence_MAE": mae0,
        "B1_Beijing_common_ridge_MAE": mae1,
        "B0_persistence_RMSE": float(np.sqrt(np.mean((y - b0) ** 2))),
        "B1_Beijing_common_ridge_RMSE": float(np.sqrt(np.mean((y - b1) ** 2))),
        "B1_relative_MAE_improvement": float(1 - mae1 / mae0),
    }


def valid_pairs(frame):
    good = frame[["PM", "TEMP", "PRES", "target_PM"]].notna().all(axis=1)
    for name in ("PM", "TEMP", "PRES", "target_PM"):
        good &= np.isfinite(frame[name])
    good &= (frame["PM"] >= 0) & (frame["target_PM"] >= 0) & (frame["PRES"] > 0)
    return frame.loc[good].copy()


def beijing_original(body):
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
            frame["target_PM"] = frame["PM2.5"].shift(-24)
            assert (frame["target_time"].iloc[:-24] == frame["time"].iloc[:-24] + pd.Timedelta(hours=24)).all()
            frame["PM"] = frame["PM2.5"]
            frames.append(frame[["station", "time", "target_time", "PM", "TEMP", "PRES", "target_PM"]])
    assert len(frames) == 12
    return pd.concat(frames, ignore_index=True)


def city_original(raw_rar, city):
    member = f"{city}PM20100101_20151231.csv"
    result = subprocess.run(["/usr/bin/bsdtar", "-xOf", "-", member], input=raw_rar, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90, check=False)
    if result.returncode:
        raise RuntimeError(f"{member} original member parse: {result.stderr.decode('utf-8', errors='replace')[:500]}")
    raw = pd.read_csv(io.BytesIO(result.stdout), na_values=["NA"])
    assert len(raw) == 52584 and "PM_US Post" in raw.columns
    raw["time"] = pd.to_datetime(raw[["year", "month", "day", "hour"]])
    raw = raw.sort_values("time").reset_index(drop=True)
    assert raw["time"].is_unique and raw["time"].notna().all()
    assert raw["time"].iloc[0] == pd.Timestamp("2010-01-01 00:00:00")
    assert raw["time"].iloc[-1] == pd.Timestamp("2015-12-31 23:00:00")
    frame = pd.DataFrame({
        "city": city,
        "time": raw["time"],
        "target_time": raw["time"] + pd.Timedelta(hours=24),
        "PM": pd.to_numeric(raw["PM_US Post"], errors="coerce"),
        "TEMP": pd.to_numeric(raw["TEMP"], errors="coerce"),
        "PRES": pd.to_numeric(raw["PRES"], errors="coerce"),
    })
    pm_indexed = pd.Series(frame["PM"].to_numpy(dtype=float), index=frame["time"])
    frame["target_PM"] = pm_indexed.reindex(frame["target_time"]).to_numpy(dtype=float)
    return frame, member


def main():
    assert QUAL["gate"] == "REAL_MULTISITE_SOURCE_READY" and len(TRAIN_SITES) == 10
    assert json.loads((E050 / "NUMERIC_SUPPORT.json").read_text())["gate"] == "EXTERNAL_COMMON_SCHEMA_SOURCE_READY"
    for name in ("MODEL_STATE.json", "BEIJING_DEVELOPMENT.json", "PAIR_SUPPORT.json", "METRICS.json", "EXTERNAL_PREDICTIONS.csv"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP051 existing output {name}; preserve prior attempt")

    beijing_body = original_read(BEIJING_URL, 20 * 1024 * 1024, "EXP051-Beijing-fit/1")
    beijing = beijing_original(beijing_body)
    valid = valid_pairs(beijing)
    train = valid.loc[valid["station"].isin(TRAIN_SITES) & valid["time"].ge("2013-03-01") & valid["time"].lt("2015-12-31")].copy()
    development = valid.loc[valid["station"].isin(TRAIN_SITES) & valid["time"].ge("2016-01-01") & valid["time"].lt("2016-12-31")].copy()
    print("BEIJING_SUPPORT", len(train), len(development), flush=True)
    if len(train) < 200000 or len(development) < 70000:
        save("PAIR_SUPPORT.json", {"run_id": RUN_ID, "beijing_response_bytes": len(beijing_body), "beijing_train_pairs": len(train), "beijing_development_pairs": len(development), "external_network_requests": 0, "gate": "STOP_BEIJING_PAIR_SUPPORT"})
        return

    scaler = StandardScaler()
    x_train = scaler.fit_transform(features(train))
    model = Ridge(alpha=1.0, fit_intercept=True)
    model.fit(x_train, np.log1p(train["target_PM"].to_numpy(dtype=float)))
    state = {
        "run_id": RUN_ID, "source": "UCI501 Beijing only", "training_stations": TRAIN_SITES,
        "training_origin_start": "2013-03-01T00:00:00", "training_origin_end_exclusive": "2015-12-31T00:00:00",
        "model": "Ridge(alpha=1.0, fit_intercept=True)", "feature_order": ["log1p_current_PM", "TEMP", "PRES"],
        "target_transform": "log1p", "inverse": "max(0, expm1)",
        "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(),
        "coef": model.coef_.tolist(), "intercept": float(model.intercept_), "train_pairs": len(train),
        "frozen_before_external_original_read": True,
    }
    save("MODEL_STATE.json", state)
    dev_pred = np.maximum(0, np.expm1(model.predict(scaler.transform(features(development)))))
    dev = {"run_id": RUN_ID, "evidence_class": "EXPOSED_BEIJING_DEVELOPMENT", "origin_year": 2016, "metrics": scores(development, dev_pred)}
    dev["admissibility_pass"] = dev["metrics"]["B1_relative_MAE_improvement"] >= 0.05
    save("BEIJING_DEVELOPMENT.json", dev)
    print("BEIJING_DEVELOPMENT", dev["metrics"], "pass", dev["admissibility_pass"], flush=True)
    if not dev["admissibility_pass"]:
        save("PAIR_SUPPORT.json", {"run_id": RUN_ID, "beijing_response_bytes": len(beijing_body), "beijing_train_pairs": len(train), "beijing_development_pairs": len(development), "external_network_requests": 0, "gate": "STOP_INTERNAL_MODEL_ADMISSIBILITY"})
        return

    # The four-city original and every external outcome are touched only after model freezing.
    five_body = original_read(FIVE_URL, 10 * 1024 * 1024, "EXP051-four-city-test/1")
    with zipfile.ZipFile(io.BytesIO(five_body)) as outer:
        raw_rar = outer.read("FiveCitiePMData.rar")
    city_frames = {}
    support = {
        "run_id": RUN_ID, "beijing_original_url": BEIJING_URL, "external_original_url": FIVE_URL,
        "beijing_network_requests": 1, "beijing_response_bytes": len(beijing_body),
        "external_network_requests": 1, "external_response_bytes": len(five_body),
        "beijing_train_pairs": len(train), "beijing_development_pairs": len(development),
        "external_origin_window": ["2013-01-01T00:00:00", "2015-12-31T00:00:00"],
        "external_city_pair_counts": {}, "external_city_excluded_in_window": {}, "external_original_members": {},
        "external_min_pairs_each": 5000, "gate": None,
    }
    for city in CITIES:
        frame, member = city_original(raw_rar, city)
        in_window = frame.loc[frame["time"].ge("2013-01-01") & frame["time"].lt("2015-12-31")].copy()
        paired = valid_pairs(in_window)
        assert (paired["target_time"] == paired["time"] + pd.Timedelta(hours=24)).all()
        city_frames[city] = paired
        support["external_city_pair_counts"][city] = len(paired)
        support["external_city_excluded_in_window"][city] = len(in_window) - len(paired)
        support["external_original_members"][city] = member
    source_pass = all(support["external_city_pair_counts"][city] >= 5000 for city in CITIES)
    support["gate"] = "EXTERNAL_PAIR_SUPPORT_PASS" if source_pass else "STOP_EXTERNAL_PAIR_SUPPORT"
    save("PAIR_SUPPORT.json", support)
    print("EXTERNAL_SUPPORT", support["external_city_pair_counts"], support["gate"], flush=True)
    if not source_pass:
        return

    metrics = {"run_id": RUN_ID, "evidence_class": "NEW_EXTERNAL_GEOGRAPHY_TEST", "cities": {}, "gate_pass": None, "conclusion_code": None}
    with (HERE / "EXTERNAL_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["city", "origin_time", "target_time", "observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"])
        writer.writeheader()
        for city in CITIES:
            frame = city_frames[city]
            prediction = np.maximum(0, np.expm1(model.predict(scaler.transform(features(frame)))))
            metrics["cities"][city] = scores(frame, prediction)
            cols = ["time", "target_time", "target_PM", "PM"]
            for (origin, target, observed, current), value in zip(frame[cols].itertuples(index=False, name=None), prediction):
                writer.writerow({"city": city, "origin_time": origin.isoformat(), "target_time": target.isoformat(), "observed_target_PM2.5": float(observed), "B0_persistence": float(current), "B1_Beijing_common_ridge": float(value)})
            print(city, metrics["cities"][city], flush=True)
    metrics["gate_pass"] = all(metrics["cities"][city]["B1_relative_MAE_improvement"] >= 0.05 for city in CITIES)
    metrics["conclusion_code"] = "ZERO_SHOT_EXTERNAL_TRANSPORT_PASS_FOUR_CITIES" if metrics["gate_pass"] else "ZERO_SHOT_EXTERNAL_TRANSPORT_NOT_STABLE"
    save("METRICS.json", metrics)
    print("EXTERNAL_GATE", metrics["conclusion_code"], flush=True)


if __name__ == "__main__":
    main()
