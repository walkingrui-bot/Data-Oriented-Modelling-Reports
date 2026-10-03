"""Read-only local validation of EXP051 saved external predictions and gate."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
state = json.loads((HERE / "MODEL_STATE.json").read_text())
dev = json.loads((HERE / "BEIJING_DEVELOPMENT.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
rows = pd.read_csv(HERE / "EXTERNAL_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
assert support["gate"] == "EXTERNAL_PAIR_SUPPORT_PASS"
assert len(rows) == sum(support["external_city_pair_counts"].values()) == 93767
assert not rows.duplicated(["city", "origin_time"]).any()
assert set(rows["city"]) == {"Chengdu", "Guangzhou", "Shanghai", "Shenyang"}
assert (rows["target_time"] - rows["origin_time"] == pd.Timedelta(hours=24)).all()
assert rows["origin_time"].ge("2013-01-01").all() and rows["origin_time"].lt("2015-12-31").all()
assert np.isfinite(rows[["observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"]]).all().all()
assert (rows[["observed_target_PM2.5", "B0_persistence", "B1_Beijing_common_ridge"]] >= 0).all().all()
assert state["feature_order"] == ["log1p_current_PM", "TEMP", "PRES"]
assert state["frozen_before_external_original_read"]
assert len(state["coef"]) == len(state["scaler_mean"]) == len(state["scaler_scale"]) == 3
assert set(state["training_stations"]).isdisjoint({"Chengdu", "Guangzhou", "Shanghai", "Shenyang"})
assert dev["admissibility_pass"] and dev["metrics"]["B1_relative_MAE_improvement"] >= 0.05
checks = 0
for city, frame in rows.groupby("city"):
    saved = metrics["cities"][city]
    assert len(frame) == support["external_city_pair_counts"][city] == saved["n"]
    y = frame["observed_target_PM2.5"].to_numpy(dtype=float)
    b0 = frame["B0_persistence"].to_numpy(dtype=float)
    b1 = frame["B1_Beijing_common_ridge"].to_numpy(dtype=float)
    mae0 = float(np.mean(np.abs(y - b0)))
    mae1 = float(np.mean(np.abs(y - b1)))
    for key, actual in [
        ("B0_persistence_MAE", mae0),
        ("B1_Beijing_common_ridge_MAE", mae1),
        ("B0_persistence_RMSE", float(np.sqrt(np.mean((y - b0) ** 2)))),
        ("B1_Beijing_common_ridge_RMSE", float(np.sqrt(np.mean((y - b1) ** 2)))),
        ("B1_relative_MAE_improvement", 1 - mae1 / mae0),
    ]:
        assert np.isclose(actual, saved[key], atol=1e-10, rtol=0), (city, key)
        checks += 1
expected = all(item["B1_relative_MAE_improvement"] >= 0.05 for item in metrics["cities"].values())
assert metrics["gate_pass"] == expected and not expected
result = {"scope": "EXP051 saved external predictions only", "external_pairs": len(rows), "city_metric_checks": checks, "target_horizon_hours": 24, "gate_recomputed": metrics["conclusion_code"], "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print("EXP051_LOCAL_VALIDATION_PASS", len(rows), checks)
