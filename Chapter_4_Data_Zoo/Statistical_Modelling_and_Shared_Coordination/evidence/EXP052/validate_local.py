"""Read-only paired validation of saved EXP052 local model diagnostics."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
E051 = HERE.parent / "STAT-PSYMOE-EXP051-20261002-001"
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
state = json.loads((HERE / "MODEL_STATES.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
new = pd.read_csv(HERE / "B2_LOCAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
old = pd.read_csv(E051 / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
assert support["gate"] == "LOCAL_PAIR_SUPPORT_PASS"
assert len(new) == sum(support["cities"][city]["test_2015_pairs"] for city in support["cities"]) == 32532
assert not new.duplicated(["city", "origin_time"]).any()
assert (new["target_time"] - new["origin_time"] == pd.Timedelta(hours=24)).all()
assert new["origin_time"].ge("2015-01-01").all() and new["origin_time"].lt("2015-12-31").all()
assert np.isfinite(new[["observed_target_PM2.5", "B2_local_ridge"]]).all().all()
assert (new[["observed_target_PM2.5", "B2_local_ridge"]] >= 0).all().all()
assert state["feature_order"] == ["log1p_current_PM", "TEMP", "PRES"]
assert set(state["city_states"]) == set(support["cities"]) == set(metrics["cities"])
joined = new.merge(old, on=["city", "origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
assert len(joined) == len(new) and joined["B1_Beijing_common_ridge"].notna().all()
checks = 0
for city, frame in joined.groupby("city"):
    saved = metrics["cities"][city]
    assert len(frame) == saved["n"] == support["cities"][city]["test_2015_pairs"]
    city_state = state["city_states"][city]
    assert city_state["train_pairs"] == support["cities"][city]["train_pairs"]
    assert len(city_state["coef"]) == len(city_state["scaler_mean"]) == len(city_state["scaler_scale"]) == 3
    y = frame["observed_target_PM2.5"].to_numpy(dtype=float)
    pred = {
        "B0_persistence": frame["B0_persistence"].to_numpy(dtype=float),
        "B1_Beijing": frame["B1_Beijing_common_ridge"].to_numpy(dtype=float),
        "B2_local": frame["B2_local_ridge"].to_numpy(dtype=float),
    }
    maes = {}
    for label, values in pred.items():
        maes[label] = float(np.mean(np.abs(y - values)))
        assert np.isclose(maes[label], saved[f"{label}_MAE"], atol=1e-10, rtol=0)
        assert np.isclose(float(np.sqrt(np.mean((y - values) ** 2))), saved[f"{label}_RMSE"], atol=1e-10, rtol=0)
        checks += 2
    assert np.isclose(1 - maes["B2_local"] / maes["B0_persistence"], saved["B2_vs_B0_relative_MAE_improvement"], atol=1e-10, rtol=0)
    assert np.isclose(1 - maes["B2_local"] / maes["B1_Beijing"], saved["B2_vs_B1_relative_MAE_improvement"], atol=1e-10, rtol=0)
    checks += 2
assert all(metrics["cities"][c]["B2_vs_B0_relative_MAE_improvement"] >= .05 and metrics["cities"][c]["B2_vs_B1_relative_MAE_improvement"] >= .03 for c in ("Chengdu", "Shanghai"))
assert metrics["conclusion_code"] == "LOCAL_FORM_USEFUL_TRANSPORT_COEFFICIENTS_FAIL"
result = {"scope": "EXP052 saved derived rows plus EXP051 original predictions", "matched_2015_pairs": len(joined), "metric_checks": checks, "target_horizon_hours": 24, "gate_recomputed": metrics["conclusion_code"], "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print("EXP052_LOCAL_VALIDATION_PASS", len(joined), checks)
