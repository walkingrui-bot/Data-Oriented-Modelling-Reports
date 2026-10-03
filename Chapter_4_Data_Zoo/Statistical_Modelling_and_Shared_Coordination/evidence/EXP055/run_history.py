"""EXP055 fixed-capacity local ridge across three historical windows."""

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
spec = importlib.util.spec_from_file_location("exp051_original_reader", E051 / "run_transport.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
RUN_ID = "EXP055-HISTORY-001"
CITIES = ("Chengdu", "Guangzhou", "Shanghai", "Shenyang")
WINDOWS = {"Q4": "2014-10-01", "H2": "2014-07-01", "Y2014": "2014-01-01"}
MIN_TRAIN = {"Q4": 1500, "H2": 3000, "Y2014": 5000}


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def scores(frame, prediction):
    y = frame["target_PM"].to_numpy(dtype=float)
    b0 = frame["PM"].to_numpy(dtype=float)
    b1 = frame["B1_Beijing_common_ridge"].to_numpy(dtype=float)
    b2 = frame["B2_local_ridge"].to_numpy(dtype=float)
    result = {"n": int(len(frame))}
    for label, pred in (("B0_persistence", b0), ("B1_Beijing", b1), ("B2_two_year_local", b2), ("history_model", prediction)):
        result[f"{label}_MAE"] = float(np.mean(np.abs(y - pred)))
        result[f"{label}_RMSE"] = float(np.sqrt(np.mean((y - pred) ** 2)))
    result["history_vs_B0_relative_MAE_improvement"] = float(1 - result["history_model_MAE"] / result["B0_persistence_MAE"])
    denominator = result["B0_persistence_MAE"] - result["B2_two_year_local_MAE"]
    result["history_recovery_of_two_year_MAE_gain"] = float((result["B0_persistence_MAE"] - result["history_model_MAE"]) / denominator) if denominator > 0 else None
    return result


def main():
    for name in ("PAIR_SUPPORT.json", "MODEL_STATES.json", "METRICS.json", "WINDOW_PREDICTIONS.csv"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP055 existing output {name}; preserve previous attempt")
    raw_zip = reader.original_read(reader.FIVE_URL, 10 * 1024 * 1024, "EXP055-history-length/1")
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as outer:
        raw_rar = outer.read("FiveCitiePMData.rar")
    old = pd.read_csv(E051 / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    two_year = pd.read_csv(E052 / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    city_data = {}
    support = {"run_id": RUN_ID, "official_original_url": reader.FIVE_URL, "network_requests": 1, "response_bytes": len(raw_zip), "EXP051_original_predictions": str(E051 / "EXTERNAL_PREDICTIONS.csv"), "EXP052_original_predictions": str(E052 / "B2_LOCAL_PREDICTIONS.csv"), "training_window_end_exclusive": "2014-12-31T00:00:00", "evaluation_window": ["2015-01-01T00:00:00", "2015-12-31T00:00:00"], "cities": {}, "minimum_train_pairs": MIN_TRAIN, "minimum_evaluation_pairs": 3000, "gate": None}
    for city in CITIES:
        full, member = reader.city_original(raw_rar, city)
        valid = reader.valid_pairs(full)
        train = {name: valid.loc[valid["time"].ge(start) & valid["time"].lt("2014-12-31")].copy() for name, start in WINDOWS.items()}
        test = valid.loc[valid["time"].ge("2015-01-01") & valid["time"].lt("2015-12-31")].copy()
        original = old.loc[(old["city"] == city) & old["origin_time"].ge("2015-01-01") & old["origin_time"].lt("2015-12-31"), ["origin_time", "target_time", "observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"]]
        full_local = two_year.loc[two_year["city"] == city, ["origin_time", "target_time", "observed_target_PM2.5", "B2_local_ridge"]]
        test = test.merge(original, left_on="time", right_on="origin_time", how="left", validate="one_to_one")
        matched = bool(test["B1_Beijing_common_ridge"].notna().all() and (test["target_time_x"] == test["target_time_y"]).all() and np.array_equal(test["target_PM"].to_numpy(), test["observed_target_PM2.5"].to_numpy()) and np.array_equal(test["PM"].to_numpy(), test["B0_persistence"].to_numpy()))
        test = test.drop(columns=["target_time_y"]).rename(columns={"target_time_x": "target_time"})
        test = test.merge(full_local, on=["origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
        matched = matched and test["B2_local_ridge"].notna().all()
        city_data[city] = (train, test)
        support["cities"][city] = {"original_archive_member": member, "train_pairs": {name: len(frame) for name, frame in train.items()}, "test_2015_pairs": len(test), "matched_original_predictions": bool(matched)}
    source_pass = all(support["cities"][city]["matched_original_predictions"] and support["cities"][city]["test_2015_pairs"] >= 3000 and all(support["cities"][city]["train_pairs"][name] >= MIN_TRAIN[name] for name in WINDOWS) for city in CITIES)
    support["gate"] = "HISTORY_PAIR_SUPPORT_PASS" if source_pass else "STOP_HISTORY_PAIR_SUPPORT"
    save("PAIR_SUPPORT.json", support)
    print("PAIR_SUPPORT", support["cities"], support["gate"], flush=True)
    if not source_pass:
        return

    fitted = {}
    states = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "feature_order": ["log1p_current_PM", "TEMP", "PRES"], "target_transform": "log1p", "inverse": "max(0, expm1)", "model": "Ridge(alpha=1.0, fit_intercept=True)", "city_window_states": {}}
    for city in CITIES:
        fitted[city] = {}
        states["city_window_states"][city] = {}
        for name, frame in city_data[city][0].items():
            scaler = StandardScaler()
            x = scaler.fit_transform(reader.features(frame))
            model = Ridge(alpha=1.0, fit_intercept=True).fit(x, np.log1p(frame["target_PM"].to_numpy(dtype=float)))
            fitted[city][name] = (scaler, model)
            states["city_window_states"][city][name] = {"origin_start": WINDOWS[name], "origin_end_exclusive": "2014-12-31", "train_pairs": len(frame), "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(), "coef": model.coef_.tolist(), "intercept": float(model.intercept_)}
    save("MODEL_STATES.json", states)
    metrics = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "windows": {name: {} for name in WINDOWS}, "conclusion_code": None}
    with (HERE / "WINDOW_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["city", "origin_time", "target_time", "observed_target_PM2.5", "Q4_ridge", "H2_ridge", "Y2014_ridge"])
        writer.writeheader()
        for city in CITIES:
            frame = city_data[city][1]
            predictions = {}
            for name in WINDOWS:
                scaler, model = fitted[city][name]
                predictions[name] = np.maximum(0, np.expm1(model.predict(scaler.transform(reader.features(frame)))))
                metrics["windows"][name][city] = scores(frame, predictions[name])
            for row, q4, h2, year in zip(frame[["time", "target_time", "target_PM"]].itertuples(index=False, name=None), predictions["Q4"], predictions["H2"], predictions["Y2014"]):
                origin, target, observed = row
                writer.writerow({"city": city, "origin_time": origin.isoformat(), "target_time": target.isoformat(), "observed_target_PM2.5": float(observed), "Q4_ridge": float(q4), "H2_ridge": float(h2), "Y2014_ridge": float(year)})
            print(city, {name: metrics["windows"][name][city]["history_vs_B0_relative_MAE_improvement"] for name in WINDOWS}, flush=True)
    conclusion = "NO_SHORTER_WINDOW_MEETS_GATE"
    codes = {"Q4": "Q4_HISTORY_SUFFICIENT_EXPLORATORY", "H2": "H2_HISTORY_SUFFICIENT_EXPLORATORY", "Y2014": "ONE_YEAR_HISTORY_SUFFICIENT_EXPLORATORY"}
    for name in WINDOWS:
        if all(metrics["windows"][name][city]["history_vs_B0_relative_MAE_improvement"] >= 0.05 and metrics["windows"][name][city]["history_recovery_of_two_year_MAE_gain"] is not None and metrics["windows"][name][city]["history_recovery_of_two_year_MAE_gain"] >= 0.8 for city in CITIES):
            conclusion = codes[name]
            break
    metrics["conclusion_code"] = conclusion
    save("METRICS.json", metrics)
    print("GATE", conclusion, flush=True)


if __name__ == "__main__":
    main()
