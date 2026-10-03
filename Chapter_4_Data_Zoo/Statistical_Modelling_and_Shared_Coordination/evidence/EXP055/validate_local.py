"""Read-only validation of EXP055 saved fixed-window models and metrics."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
states = json.loads((HERE / "MODEL_STATES.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
new = pd.read_csv(HERE / "WINDOW_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
old = pd.read_csv(ROOT / "STAT-PSYMOE-EXP051-20261002-001" / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
full = pd.read_csv(ROOT / "STAT-PSYMOE-EXP052-20261002-001" / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
keys = ["city", "origin_time", "target_time", "observed_target_PM2.5"]
frame = new.merge(old, on=keys, how="left", validate="one_to_one").merge(full, on=keys, how="left", validate="one_to_one")
assert support["gate"] == "HISTORY_PAIR_SUPPORT_PASS" and support["network_requests"] == 1
assert len(frame) == len(new) == 32532 and not new.duplicated(["city", "origin_time"]).any()
assert (new["target_time"] - new["origin_time"] == pd.Timedelta(hours=24)).all()
assert new["origin_time"].ge("2015-01-01").all() and new["origin_time"].lt("2015-12-31").all()
assert frame[["B0_persistence", "B1_Beijing_common_ridge", "B2_local_ridge"]].notna().all().all()
assert np.isfinite(new[["Q4_ridge", "H2_ridge", "Y2014_ridge"]]).all().all()
assert (new[["Q4_ridge", "H2_ridge", "Y2014_ridge"]] >= 0).all().all()
assert states["feature_order"] == ["log1p_current_PM", "TEMP", "PRES"]
checks = 0
for city, rows in frame.groupby("city"):
    assert len(rows) == support["cities"][city]["test_2015_pairs"]
    assert set(states["city_window_states"][city]) == {"Q4", "H2", "Y2014"}
    y = rows["observed_target_PM2.5"].to_numpy(dtype=float)
    reference = {
        "B0_persistence": rows["B0_persistence"].to_numpy(dtype=float),
        "B1_Beijing": rows["B1_Beijing_common_ridge"].to_numpy(dtype=float),
        "B2_two_year_local": rows["B2_local_ridge"].to_numpy(dtype=float),
    }
    for window in ("Q4", "H2", "Y2014"):
        state = states["city_window_states"][city][window]
        assert state["train_pairs"] == support["cities"][city]["train_pairs"][window]
        assert len(state["coef"]) == len(state["scaler_mean"]) == len(state["scaler_scale"]) == 3
        saved = metrics["windows"][window][city]
        assert len(rows) == saved["n"]
        predictions = dict(reference, history_model=rows[f"{window}_ridge"].to_numpy(dtype=float))
        maes = {}
        for label, pred in predictions.items():
            maes[label] = float(np.mean(np.abs(y - pred)))
            assert np.isclose(maes[label], saved[f"{label}_MAE"], atol=1e-10, rtol=0)
            assert np.isclose(float(np.sqrt(np.mean((y - pred) ** 2))), saved[f"{label}_RMSE"], atol=1e-10, rtol=0)
            checks += 2
        improvement = 1 - maes["history_model"] / maes["B0_persistence"]
        recovery = (maes["B0_persistence"] - maes["history_model"]) / (maes["B0_persistence"] - maes["B2_two_year_local"])
        assert np.isclose(improvement, saved["history_vs_B0_relative_MAE_improvement"], atol=1e-10, rtol=0)
        assert np.isclose(recovery, saved["history_recovery_of_two_year_MAE_gain"], atol=1e-10, rtol=0)
        checks += 2
def all_pass(window):
    return all(m["history_vs_B0_relative_MAE_improvement"] >= .05 and m["history_recovery_of_two_year_MAE_gain"] >= .8 for m in metrics["windows"][window].values())
assert not all_pass("Q4") and not all_pass("H2") and all_pass("Y2014")
assert metrics["conclusion_code"] == "ONE_YEAR_HISTORY_SUFFICIENT_EXPLORATORY"
result = {"scope": "EXP055 saved predictions plus original EXP051/052 derived rows", "matched_2015_pairs": len(frame), "city_window_metric_checks": checks, "gate_recomputed": metrics["conclusion_code"], "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print("EXP055_LOCAL_VALIDATION_PASS", len(frame), checks)
