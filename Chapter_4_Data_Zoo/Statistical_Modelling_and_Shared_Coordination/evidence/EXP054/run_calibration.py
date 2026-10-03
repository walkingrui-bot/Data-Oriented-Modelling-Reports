"""EXP054 fixed 30-day affine output and local three-feature ridge comparisons."""

import csv
import importlib.util
import io
import json
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
E051 = HERE.parent / "STAT-PSYMOE-EXP051-20261002-001"
E052 = HERE.parent / "STAT-PSYMOE-EXP052-20261002-001"
E053 = HERE.parent / "STAT-PSYMOE-EXP053-20261002-001"
spec = importlib.util.spec_from_file_location("exp051_original_reader", E051 / "run_transport.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
CITIES = ("Chengdu", "Guangzhou", "Shanghai", "Shenyang")
RUN_ID = "EXP054-CALIBRATION-001"


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def scores(frame):
    y = frame["target_PM"].to_numpy(dtype=float)
    columns = {
        "B0_persistence": "PM",
        "B1_Beijing": "B1_Beijing_common_ridge",
        "B2_full_local": "B2_local_ridge",
        "B3_one_intercept": "B3_intercept_calibrated",
        "B4_affine_output": "B4_affine_output",
        "B5_3feature_local": "B5_3feature_local",
    }
    result = {"n": int(len(frame))}
    for label, column in columns.items():
        pred = frame[column].to_numpy(dtype=float)
        result[f"{label}_MAE"] = float(np.mean(np.abs(y - pred)))
        result[f"{label}_RMSE"] = float(np.sqrt(np.mean((y - pred) ** 2)))
    b0 = result["B0_persistence_MAE"]
    b2 = result["B2_full_local_MAE"]
    for label in ("B4_affine_output", "B5_3feature_local"):
        value = result[f"{label}_MAE"]
        result[f"{label}_vs_B0_relative_MAE_improvement"] = float(1 - value / b0)
        result[f"{label}_recovery_of_full_local_MAE_gain"] = float((b0 - value) / (b0 - b2)) if b0 > b2 else None
    return result


def main():
    for name in ("PAIR_SUPPORT.json", "MODEL_STATES.json", "METRICS.json", "B4_B5_PREDICTIONS.csv"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP054 existing output {name}; preserve previous attempt")
    old = pd.read_csv(E051 / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    local = pd.read_csv(E052 / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    intercept = pd.read_csv(E053 / "B3_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    raw_zip = reader.original_read(reader.FIVE_URL, 10 * 1024 * 1024, "EXP054-adaptation/1")
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as outer:
        raw_rar = outer.read("FiveCitiePMData.rar")
    city_data = {}
    support = {"run_id": RUN_ID, "official_original_url": reader.FIVE_URL, "network_requests": 1, "response_bytes": len(raw_zip), "EXP051_original_predictions": str(E051 / "EXTERNAL_PREDICTIONS.csv"), "EXP052_original_predictions": str(E052 / "B2_LOCAL_PREDICTIONS.csv"), "EXP053_original_predictions": str(E053 / "B3_PREDICTIONS.csv"), "cities": {}, "thresholds": {"calibration": 400, "evaluation": 3000}, "gate": None}
    for city in CITIES:
        full, member = reader.city_original(raw_rar, city)
        cal = reader.valid_pairs(full.loc[full["time"].ge("2014-11-01") & full["time"].lt("2014-12-01")].copy())
        test = reader.valid_pairs(full.loc[full["time"].ge("2015-01-01") & full["time"].lt("2015-12-31")].copy())
        b1_cal = old.loc[(old["city"] == city) & old["origin_time"].ge("2014-11-01") & old["origin_time"].lt("2014-12-01"), ["origin_time", "target_time", "observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"]]
        b1_test = old.loc[(old["city"] == city) & old["origin_time"].ge("2015-01-01") & old["origin_time"].lt("2015-12-31"), ["origin_time", "target_time", "observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"]]
        cal = cal.merge(b1_cal, left_on="time", right_on="origin_time", how="left", validate="one_to_one")
        test = test.merge(b1_test, left_on="time", right_on="origin_time", how="left", validate="one_to_one")
        def match(frame):
            return bool(frame["B1_Beijing_common_ridge"].notna().all() and (frame["target_time_x"] == frame["target_time_y"]).all() and np.array_equal(frame["target_PM"].to_numpy(), frame["observed_target_PM2.5"].to_numpy()) and np.array_equal(frame["PM"].to_numpy(), frame["B0_persistence"].to_numpy()))
        matched = match(cal) and match(test)
        city_data[city] = (cal, test)
        support["cities"][city] = {"original_archive_member": member, "calibration_pairs": len(cal), "evaluation_2015_pairs": len(test), "matched_EXP051_original": matched, "last_calibration_target_time": cal["target_time_x"].max().isoformat() if len(cal) else None}
    support_pass = all(support["cities"][c]["calibration_pairs"] >= 400 and support["cities"][c]["evaluation_2015_pairs"] >= 3000 and support["cities"][c]["matched_EXP051_original"] for c in CITIES)
    support["gate"] = "CALIBRATION_SUPPORT_PASS" if support_pass else "STOP_CALIBRATION_SUPPORT"
    save("PAIR_SUPPORT.json", support)
    print("PAIR_SUPPORT", support["cities"], support["gate"], flush=True)
    if not support_pass:
        return

    fitted = {}
    states = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "calibration_origin_window": ["2014-11-01T00:00:00", "2014-12-01T00:00:00"], "retrospective_base_model_trained_through_2015": True, "B4_B5_city_states": {}}
    for city in CITIES:
        cal = city_data[city][0]
        y = np.log1p(cal["target_PM"].to_numpy(dtype=float))
        b4_x = np.log1p(cal["B1_Beijing_common_ridge"].to_numpy(dtype=float)).reshape(-1, 1)
        b4_scaler = StandardScaler()
        b4_model = Ridge(alpha=1.0, fit_intercept=True).fit(b4_scaler.fit_transform(b4_x), y)
        b5_scaler = StandardScaler()
        b5_model = Ridge(alpha=1.0, fit_intercept=True).fit(b5_scaler.fit_transform(reader.features(cal)), y)
        fitted[city] = (b4_scaler, b4_model, b5_scaler, b5_model)
        states["B4_B5_city_states"][city] = {
            "calibration_pairs": len(cal),
            "B4": {"input": "log1p_B1", "scaler_mean": b4_scaler.mean_.tolist(), "scaler_scale": b4_scaler.scale_.tolist(), "coef": b4_model.coef_.tolist(), "intercept": float(b4_model.intercept_)},
            "B5": {"input_order": ["log1p_PM", "TEMP", "PRES"], "scaler_mean": b5_scaler.mean_.tolist(), "scaler_scale": b5_scaler.scale_.tolist(), "coef": b5_model.coef_.tolist(), "intercept": float(b5_model.intercept_)},
        }
    save("MODEL_STATES.json", states)
    metrics = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "cities": {}, "conclusion_code": None}
    with (HERE / "B4_B5_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["city", "origin_time", "target_time", "observed_target_PM2.5", "B4_affine_output", "B5_3feature_local"])
        writer.writeheader()
        for city in CITIES:
            frame = city_data[city][1]
            assert (frame["target_time_x"] == frame["target_time_y"]).all()
            frame = frame.drop(columns=["target_time_y"]).rename(columns={"target_time_x": "target_time"})
            earlier = local.loc[local["city"] == city, ["origin_time", "target_time", "observed_target_PM2.5", "B2_local_ridge"]]
            b3 = intercept.loc[intercept["city"] == city, ["origin_time", "target_time", "observed_target_PM2.5", "B3_intercept_calibrated"]]
            frame = frame.merge(earlier, on=["origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
            frame = frame.merge(b3, on=["origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
            assert frame[["B2_local_ridge", "B3_intercept_calibrated"]].notna().all().all()
            b4_scaler, b4_model, b5_scaler, b5_model = fitted[city]
            b4_x = np.log1p(frame["B1_Beijing_common_ridge"].to_numpy(dtype=float)).reshape(-1, 1)
            frame["B4_affine_output"] = np.maximum(0, np.expm1(b4_model.predict(b4_scaler.transform(b4_x))))
            frame["B5_3feature_local"] = np.maximum(0, np.expm1(b5_model.predict(b5_scaler.transform(reader.features(frame)))))
            metrics["cities"][city] = scores(frame)
            for origin, target, observed, b4, b5 in frame[["time", "target_time", "target_PM", "B4_affine_output", "B5_3feature_local"]].itertuples(index=False, name=None):
                writer.writerow({"city": city, "origin_time": origin.isoformat(), "target_time": target.isoformat(), "observed_target_PM2.5": float(observed), "B4_affine_output": float(b4), "B5_3feature_local": float(b5)})
            print(city, metrics["cities"][city], flush=True)
    def enough(label):
        return all(metrics["cities"][city][f"{label}_vs_B0_relative_MAE_improvement"] >= 0.05 and metrics["cities"][city][f"{label}_recovery_of_full_local_MAE_gain"] is not None and metrics["cities"][city][f"{label}_recovery_of_full_local_MAE_gain"] >= 0.8 for city in CITIES)
    if enough("B4_affine_output"):
        conclusion = "AFFINE_OUTPUT_30D_SUFFICIENT_EXPLORATORY"
    elif enough("B5_3feature_local"):
        conclusion = "THREE_FEATURE_LOCAL_30D_SUFFICIENT_EXPLORATORY"
    else:
        conclusion = "THIRTY_DAY_ADAPTATION_INSUFFICIENT_EXPLORATORY"
    metrics["conclusion_code"] = conclusion
    save("METRICS.json", metrics)
    print("GATE", conclusion, flush=True)


if __name__ == "__main__":
    main()
