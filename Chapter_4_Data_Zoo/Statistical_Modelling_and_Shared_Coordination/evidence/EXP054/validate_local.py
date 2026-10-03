"""Validate saved EXP054 evaluation keys, model states, metrics and gate."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
states = json.loads((HERE / "MODEL_STATES.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
new = pd.read_csv(HERE / "B4_B5_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
old = pd.read_csv(ROOT / "STAT-PSYMOE-EXP051-20261002-001" / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
b2 = pd.read_csv(ROOT / "STAT-PSYMOE-EXP052-20261002-001" / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
b3 = pd.read_csv(ROOT / "STAT-PSYMOE-EXP053-20261002-001" / "B3_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
keys = ["city", "origin_time", "target_time", "observed_target_PM2.5"]
joined = new.merge(old, on=keys, how="left", validate="one_to_one").merge(b2, on=keys, how="left", validate="one_to_one").merge(b3, on=keys, how="left", validate="one_to_one")
assert support["gate"] == "CALIBRATION_SUPPORT_PASS" and support["network_requests"] == 1
assert len(new) == len(joined) == 32532 and not new.duplicated(["city", "origin_time"]).any()
assert (new["target_time"] - new["origin_time"] == pd.Timedelta(hours=24)).all()
assert new["origin_time"].ge("2015-01-01").all() and new["origin_time"].lt("2015-12-31").all()
assert np.isfinite(new[["B4_affine_output", "B5_3feature_local"]]).all().all()
assert (new[["B4_affine_output", "B5_3feature_local"]] >= 0).all().all()
assert joined[["B0_persistence", "B1_Beijing_common_ridge", "B2_local_ridge", "B3_intercept_calibrated"]].notna().all().all()
assert set(states["B4_B5_city_states"]) == set(support["cities"]) == set(metrics["cities"])
checks = 0
for city, frame in joined.groupby("city"):
    saved = metrics["cities"][city]
    assert len(frame) == saved["n"] == support["cities"][city]["evaluation_2015_pairs"]
    assert support["cities"][city]["calibration_pairs"] == states["B4_B5_city_states"][city]["calibration_pairs"]
    assert support["cities"][city]["last_calibration_target_time"] < "2015-01-01"
    assert len(states["B4_B5_city_states"][city]["B4"]["coef"]) == 1
    assert len(states["B4_B5_city_states"][city]["B5"]["coef"]) == 3
    y = frame["observed_target_PM2.5"].to_numpy(dtype=float)
    lookup = {"B0_persistence": "B0_persistence", "B1_Beijing": "B1_Beijing_common_ridge", "B2_full_local": "B2_local_ridge", "B3_one_intercept": "B3_intercept_calibrated", "B4_affine_output": "B4_affine_output", "B5_3feature_local": "B5_3feature_local"}
    maes = {}
    for label, column in lookup.items():
        pred = frame[column].to_numpy(dtype=float)
        maes[label] = float(np.mean(np.abs(y - pred)))
        assert np.isclose(maes[label], saved[f"{label}_MAE"], atol=1e-10, rtol=0)
        assert np.isclose(float(np.sqrt(np.mean((y - pred) ** 2))), saved[f"{label}_RMSE"], atol=1e-10, rtol=0)
        checks += 2
    for label in ("B4_affine_output", "B5_3feature_local"):
        improvement = 1 - maes[label] / maes["B0_persistence"]
        recovery = (maes["B0_persistence"] - maes[label]) / (maes["B0_persistence"] - maes["B2_full_local"])
        assert np.isclose(improvement, saved[f"{label}_vs_B0_relative_MAE_improvement"], atol=1e-10, rtol=0)
        assert np.isclose(recovery, saved[f"{label}_recovery_of_full_local_MAE_gain"], atol=1e-10, rtol=0)
        checks += 2
for label in ("B4_affine_output", "B5_3feature_local"):
    assert not all(m[f"{label}_vs_B0_relative_MAE_improvement"] >= .05 and m[f"{label}_recovery_of_full_local_MAE_gain"] >= .8 for m in metrics["cities"].values())
assert metrics["conclusion_code"] == "THIRTY_DAY_ADAPTATION_INSUFFICIENT_EXPLORATORY"
result = {"scope": "EXP054 saved outputs plus original EXP051/052/053 derived rows", "matched_2015_pairs": len(joined), "city_metric_checks": checks, "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print("EXP054_LOCAL_VALIDATION_PASS", len(joined), checks)
