"""EXP053 one scalar per city using original saved EXP051/052 predictions."""

import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
E051 = HERE.parent / "STAT-PSYMOE-EXP051-20261002-001"
E052 = HERE.parent / "STAT-PSYMOE-EXP052-20261002-001"
RUN_ID = "EXP053-INTERCEPT-001"
CITIES = ("Chengdu", "Guangzhou", "Shanghai", "Shenyang")


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def scores(frame):
    y = frame["observed_target_PM2.5"].to_numpy(dtype=float)
    names = {
        "B0_persistence": "B0_persistence",
        "B1_Beijing_common_ridge": "B1_Beijing",
        "B2_local_ridge": "B2_full_local",
        "B3_intercept_calibrated": "B3_30d_intercept",
    }
    output = {"n": int(len(frame))}
    for column, label in names.items():
        prediction = frame[column].to_numpy(dtype=float)
        output[f"{label}_MAE"] = float(np.mean(np.abs(y - prediction)))
        output[f"{label}_RMSE"] = float(np.sqrt(np.mean((y - prediction) ** 2)))
    b0 = output["B0_persistence_MAE"]
    b2 = output["B2_full_local_MAE"]
    b3 = output["B3_30d_intercept_MAE"]
    output["B3_vs_B0_relative_MAE_improvement"] = float(1 - b3 / b0)
    output["B3_recovery_of_full_local_MAE_gain"] = float((b0 - b3) / (b0 - b2)) if b0 > b2 else None
    return output


def main():
    for name in ("PAIR_SUPPORT.json", "CALIBRATION_STATE.json", "METRICS.json", "B3_PREDICTIONS.csv"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP053 existing output {name}; preserve previous attempt")
    old = pd.read_csv(E051 / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    local = pd.read_csv(E052 / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
    assert not old.duplicated(["city", "origin_time"]).any()
    assert not local.duplicated(["city", "origin_time"]).any()
    support = {"run_id": RUN_ID, "input_EXP051_original": str(E051 / "EXTERNAL_PREDICTIONS.csv"), "input_EXP052_original": str(E052 / "B2_LOCAL_PREDICTIONS.csv"), "network_requests": 0, "calibration_window": ["2014-11-01T00:00:00", "2014-12-01T00:00:00"], "evaluation_window": ["2015-01-01T00:00:00", "2015-12-31T00:00:00"], "cities": {}, "thresholds": {"calibration": 400, "evaluation": 3000}, "gate": None}
    calibration = {}
    evaluation = {}
    for city in CITIES:
        source = old.loc[old["city"] == city]
        cal = source.loc[source["origin_time"].ge("2014-11-01") & source["origin_time"].lt("2014-12-01")].copy()
        ev = source.loc[source["origin_time"].ge("2015-01-01") & source["origin_time"].lt("2015-12-31")].copy()
        previous = local.loc[local["city"] == city, ["origin_time", "target_time", "observed_target_PM2.5", "B2_local_ridge"]]
        joined = ev.merge(previous, on=["origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
        matched = bool(len(joined) == len(ev) and joined["B2_local_ridge"].notna().all())
        calibration[city] = cal
        evaluation[city] = joined
        support["cities"][city] = {"calibration_pairs": len(cal), "evaluation_pairs": len(ev), "matched_full_local_model": matched, "calibration_last_target_time": cal["target_time"].max().isoformat() if len(cal) else None}
    source_pass = all(support["cities"][city]["calibration_pairs"] >= 400 and support["cities"][city]["evaluation_pairs"] >= 3000 and support["cities"][city]["matched_full_local_model"] for city in CITIES)
    support["gate"] = "CALIBRATION_SUPPORT_PASS" if source_pass else "STOP_CALIBRATION_SUPPORT"
    save("PAIR_SUPPORT.json", support)
    print("PAIR_SUPPORT", support["cities"], support["gate"], flush=True)
    if not source_pass:
        return
    state = {"run_id": RUN_ID, "method": "mean(log1p(y)-log1p(B1_Beijing)) on 2014-11 origin hours", "retrospective_base_model_trained_through_2015": True, "city_delta_log_scale": {}, "calibration_pair_counts": {}}
    for city in CITIES:
        cal = calibration[city]
        delta = float(np.mean(np.log1p(cal["observed_target_PM2.5"].to_numpy(dtype=float)) - np.log1p(cal["B1_Beijing_common_ridge"].to_numpy(dtype=float))))
        state["city_delta_log_scale"][city] = delta
        state["calibration_pair_counts"][city] = len(cal)
    save("CALIBRATION_STATE.json", state)
    metrics = {"run_id": RUN_ID, "evidence_class": "EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST", "cities": {}, "gate_pass": None, "conclusion_code": None}
    with (HERE / "B3_PREDICTIONS.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=["city", "origin_time", "target_time", "observed_target_PM2.5", "B3_intercept_calibrated"])
        writer.writeheader()
        for city in CITIES:
            frame = evaluation[city].copy()
            frame["B3_intercept_calibrated"] = np.maximum(0, np.expm1(np.log1p(frame["B1_Beijing_common_ridge"].to_numpy(dtype=float)) + state["city_delta_log_scale"][city]))
            metrics["cities"][city] = scores(frame)
            for origin, target, observed, pred in frame[["origin_time", "target_time", "observed_target_PM2.5", "B3_intercept_calibrated"]].itertuples(index=False, name=None):
                writer.writerow({"city": city, "origin_time": origin.isoformat(), "target_time": target.isoformat(), "observed_target_PM2.5": float(observed), "B3_intercept_calibrated": float(pred)})
            print(city, metrics["cities"][city], flush=True)
    passed = all(metrics["cities"][city]["B3_vs_B0_relative_MAE_improvement"] >= 0.05 and metrics["cities"][city]["B3_recovery_of_full_local_MAE_gain"] is not None and metrics["cities"][city]["B3_recovery_of_full_local_MAE_gain"] >= 0.8 for city in CITIES)
    metrics["gate_pass"] = passed
    metrics["conclusion_code"] = "ONE_INTERCEPT_30D_SUFFICIENT_EXPLORATORY" if passed else "ONE_INTERCEPT_30D_INSUFFICIENT_EXPLORATORY"
    save("METRICS.json", metrics)
    print("GATE", metrics["conclusion_code"], flush=True)


if __name__ == "__main__":
    main()
