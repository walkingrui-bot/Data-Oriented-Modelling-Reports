"""EXP052 four local historical ridges on exposed 2015 external rows."""

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

HERE = Path(__file__).resolve().parent
E051 = HERE.parent / "STAT-PSYMOE-EXP051-20261002-001"
spec = importlib.util.spec_from_file_location("exp051_original_reader", E051 / "run_transport.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
RUN_ID = "EXP052-LOCAL-RIDGE-001"
CITIES = ("Chengdu", "Guangzhou", "Shanghai", "Shenyang")


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def scores(frame):
    y = frame["target_PM"].to_numpy(dtype=float)
    models = {
        "B0_persistence": frame["PM"].to_numpy(dtype=float),
        "B1_Beijing": frame["B1_Beijing_common_ridge"].to_numpy(dtype=float),
        "B2_local": frame["B2_local_ridge"].to_numpy(dtype=float),
    }
    output = {"n": int(len(frame))}
    for label, prediction in models.items():
        output[f"{label}_MAE"] = float(np.mean(np.abs(y - prediction)))
        output[f"{label}_RMSE"] = float(np.sqrt(np.mean((y - prediction) ** 2)))
    output["B2_vs_B0_relative_MAE_improvement"] = float(1 - output["B2_local_MAE"] / output["B0_persistence_MAE"])
    output["B2_vs_B1_relative_MAE_improvement"] = float(1 - output["B2_local_MAE"] / output["B1_Beijing_MAE"])
    return output


def main():
    for name in ("PAIR_SUPPORT.json", "MODEL_STATES.json", "METRICS.json", "B2_LOCAL_PREDICTIONS.csv"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP052 existing output {name}; preserve prior attempt")
    raw_zip = reader.original_read(reader.FIVE_URL, 10 * 1024 * 1024, "EXP052-local-diagnostic/1")
    import io
    import zipfile
    with zipfile.ZipFile(io.BytesIO(raw_zip)) as outer:
        raw_rar = outer.read("FiveCitiePMData.rar")
    city_sets = {}
    support = {"run_id": RUN_ID, "official_original_url": reader.FIVE_URL, "network_requests": 1, "response_bytes": len(raw_zip), "EXP051_original_prediction_path": str(E051 / "EXTERNAL_PREDICTIONS.csv"), "cities": {}, "thresholds": {"train": 5000, "test_2015": 3000}, "gate": None}
    for city in CITIES:
        full, member = reader.city_original(raw_rar, city)
        train_raw = full.loc[full["time"].ge("2013-01-01") & full["time"].lt("2014-12-31")].copy()
        test_raw = full.loc[full["time"].ge("2015-01-01") & full["time"].lt("2015-12-31")].copy()
        train = reader.valid_pairs(train_raw)
        test = reader.valid_pairs(test_raw)
        assert (train["target_time"] == train["time"] + pd.Timedelta(hours=24)).all()
        assert (test["target_time"] == test["time"] + pd.Timedelta(hours=24)).all()
        city_sets[city] = {"train": train, "test": test}
        support["cities"][city] = {
            "original_archive_member": member,
            "train_pairs": len(train), "test_2015_pairs": len(test),
            "train_excluded": len(train_raw) - len(train),
            "test_2015_excluded": len(test_raw) - len(test),
        }
    support_pass = all(support["cities"][city]["train_pairs"] >= 5000 and support["cities"][city]["test_2015_pairs"] >= 3000 for city in CITIES)
    support["gate"] = "LOCAL_PAIR_SUPPORT_PASS" if support_pass else "STOP_LOCAL_PAIR_SUPPORT"
    save("PAIR_SUPPORT.json", support)
    print("PAIR_SUPPORT", {k: {"train": v["train_pairs"], "test": v["test_2015_pairs"]} for k, v in support["cities"].items()}, support["gate"], flush=True)
    if not support_pass:
        return

    fitted = {}
    model_states = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "feature_order": ["log1p_current_PM", "TEMP", "PRES"], "model": "per-city Ridge(alpha=1.0, fit_intercept=True)", "train_origin_window": ["2013-01-01T00:00:00", "2014-12-31T00:00:00"], "city_states": {}}
    for city in CITIES:
        train = city_sets[city]["train"]
        scaler = StandardScaler()
        x = scaler.fit_transform(reader.features(train))
        model = Ridge(alpha=1.0, fit_intercept=True)
        model.fit(x, np.log1p(train["target_PM"].to_numpy(dtype=float)))
        fitted[city] = (scaler, model)
        model_states["city_states"][city] = {
            "original_archive_member": support["cities"][city]["original_archive_member"],
            "train_pairs": len(train),
            "scaler_mean": scaler.mean_.tolist(), "scaler_scale": scaler.scale_.tolist(),
            "coef": model.coef_.tolist(), "intercept": float(model.intercept_),
        }
    save("MODEL_STATES.json", model_states)

    old = pd.read_csv(E051 / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    old = old.loc[old["origin_time"].ge("2015-01-01") & old["origin_time"].lt("2015-12-31")]
    assert not old.duplicated(["city", "origin_time"]).any()
    metrics = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "cities": {}, "conclusion_code": None}
    with (HERE / "B2_LOCAL_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["city", "origin_time", "target_time", "observed_target_PM2.5", "B2_local_ridge"])
        writer.writeheader()
        for city in CITIES:
            frame = city_sets[city]["test"]
            prior = old.loc[old["city"] == city, ["origin_time", "target_time", "observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"]]
            joined = frame.merge(prior, left_on="time", right_on="origin_time", how="left", validate="one_to_one")
            assert len(joined) == len(frame) and joined["B1_Beijing_common_ridge"].notna().all()
            assert (joined["target_time_x"] == joined["target_time_y"]).all()
            assert np.array_equal(joined["target_PM"].to_numpy(), joined["observed_target_PM2.5"].to_numpy())
            assert np.array_equal(joined["PM"].to_numpy(), joined["B0_persistence"].to_numpy())
            scaler, model = fitted[city]
            joined["B2_local_ridge"] = np.maximum(0, np.expm1(model.predict(scaler.transform(reader.features(joined)))))
            metrics["cities"][city] = scores(joined)
            for origin, target, observed, prediction in joined[["time", "target_time_x", "target_PM", "B2_local_ridge"]].itertuples(index=False, name=None):
                writer.writerow({"city": city, "origin_time": origin.isoformat(), "target_time": target.isoformat(), "observed_target_PM2.5": float(observed), "B2_local_ridge": float(prediction)})
            print(city, metrics["cities"][city], flush=True)
    failed = ("Chengdu", "Shanghai")
    if all(metrics["cities"][city]["B2_vs_B0_relative_MAE_improvement"] >= 0.05 and metrics["cities"][city]["B2_vs_B1_relative_MAE_improvement"] >= 0.03 for city in failed):
        conclusion = "LOCAL_FORM_USEFUL_TRANSPORT_COEFFICIENTS_FAIL"
    elif any(metrics["cities"][city]["B2_vs_B0_relative_MAE_improvement"] < 0.05 for city in failed):
        conclusion = "LOCAL_FORM_NOT_STABLY_USEFUL_IN_FAILED_CITIES"
    else:
        conclusion = "MIXED_DIAGNOSTIC"
    metrics["conclusion_code"] = conclusion
    save("METRICS.json", metrics)
    print("DIAGNOSTIC", conclusion, flush=True)


if __name__ == "__main__":
    main()
