"""Recompute EXP053 scalar calibration and metrics from original derived inputs."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
E051 = HERE.parent / "STAT-PSYMOE-EXP051-20261002-001"
E052 = HERE.parent / "STAT-PSYMOE-EXP052-20261002-001"
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
state = json.loads((HERE / "CALIBRATION_STATE.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
old = pd.read_csv(E051 / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
local = pd.read_csv(E052 / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
new = pd.read_csv(HERE / "B3_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
assert support["gate"] == "CALIBRATION_SUPPORT_PASS" and support["network_requests"] == 0
assert len(new) == 32532 and not new.duplicated(["city", "origin_time"]).any()
assert (new["target_time"] - new["origin_time"] == pd.Timedelta(hours=24)).all()
assert new["origin_time"].ge("2015-01-01").all() and new["origin_time"].lt("2015-12-31").all()
joined = new.merge(old, on=["city", "origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
joined = joined.merge(local, on=["city", "origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
assert len(joined) == len(new) and joined[["B0_persistence", "B1_Beijing_common_ridge", "B2_local_ridge"]].notna().all().all()
checks = 0
for city, frame in joined.groupby("city"):
    cal = old.loc[(old["city"] == city) & old["origin_time"].ge("2014-11-01") & old["origin_time"].lt("2014-12-01")]
    assert len(cal) == support["cities"][city]["calibration_pairs"] == state["calibration_pair_counts"][city]
    assert cal["target_time"].max() < pd.Timestamp("2015-01-01")
    delta = float(np.mean(np.log1p(cal["observed_target_PM2.5"]) - np.log1p(cal["B1_Beijing_common_ridge"])))
    assert np.isclose(delta, state["city_delta_log_scale"][city], atol=1e-12, rtol=0)
    expected_b3 = np.maximum(0, np.expm1(np.log1p(frame["B1_Beijing_common_ridge"].to_numpy(dtype=float)) + delta))
    assert np.allclose(expected_b3, frame["B3_intercept_calibrated"], atol=1e-9, rtol=0)
    saved = metrics["cities"][city]
    assert len(frame) == saved["n"] == support["cities"][city]["evaluation_pairs"]
    y = frame["observed_target_PM2.5"].to_numpy(dtype=float)
    maes = {}
    for label, field in [("B0_persistence", "B0_persistence"), ("B1_Beijing", "B1_Beijing_common_ridge"), ("B2_full_local", "B2_local_ridge"), ("B3_30d_intercept", "B3_intercept_calibrated")]:
        pred = frame[field].to_numpy(dtype=float)
        maes[label] = float(np.mean(np.abs(y - pred)))
        assert np.isclose(maes[label], saved[f"{label}_MAE"], atol=1e-10, rtol=0)
        assert np.isclose(float(np.sqrt(np.mean((y - pred) ** 2))), saved[f"{label}_RMSE"], atol=1e-10, rtol=0)
        checks += 2
    assert np.isclose(1 - maes["B3_30d_intercept"] / maes["B0_persistence"], saved["B3_vs_B0_relative_MAE_improvement"], atol=1e-10, rtol=0)
    assert np.isclose((maes["B0_persistence"] - maes["B3_30d_intercept"]) / (maes["B0_persistence"] - maes["B2_full_local"]), saved["B3_recovery_of_full_local_MAE_gain"], atol=1e-10, rtol=0)
    checks += 2
assert not metrics["gate_pass"] and metrics["conclusion_code"] == "ONE_INTERCEPT_30D_INSUFFICIENT_EXPLORATORY"
result = {"scope": "EXP053 plus direct EXP051/052 derived inputs", "matched_2015_pairs": len(joined), "calibration_city_states": len(state["city_delta_log_scale"]), "metric_checks": checks, "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print("EXP053_LOCAL_VALIDATION_PASS", len(joined), checks)
