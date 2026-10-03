"""EXP048 local split, time-lock, and metric recomputation only."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
state = json.loads((HERE / "MODEL_STATE.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
pred = pd.read_csv(HERE / "HOLDOUT_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
assert support["gate"] == "PAIR_SUPPORT_PASS" and state["train_pairs"] == support["domain_pair_counts"]["train"]
assert support["train_station_count"] == 10 and set(support["held_out_stations"]) == {"Aotizhongxin", "Wanshouxigong"}
assert len(pred) == sum(count for domain, count in support["domain_pair_counts"].items() if domain != "train")
assert (pred["target_time"] - pred["origin_time"] == pd.Timedelta(hours=24)).all()
assert pred[["observed_target_PM2.5", "B0_persistence", "B1_ridge"]].notna().all().all()
assert (pred[["observed_target_PM2.5", "B0_persistence", "B1_ridge"]] >= 0).all().all()
checks = 0
for domain, reported in metrics["domains"].items():
    subset = pred[pred["domain"] == domain]
    assert len(subset) == reported["n"] == support["domain_pair_counts"][domain]
    time = subset["origin_time"]
    if domain in ("validation_same10", "station_2016"):
        assert ((time >= "2016-01-01") & (time < "2016-12-31")).all()
    else:
        assert ((time >= "2017-01-01") & (time < "2017-02-28")).all()
    if domain in ("station_2016", "future_station_2"):
        assert set(subset["station"]) == set(support["held_out_stations"])
    else:
        assert not set(subset["station"]) & set(support["held_out_stations"])
    y = subset["observed_target_PM2.5"].to_numpy()
    b0 = subset["B0_persistence"].to_numpy()
    b1 = subset["B1_ridge"].to_numpy()
    computed = {
        "B0_persistence_MAE": np.mean(np.abs(y-b0)),
        "B1_ridge_MAE": np.mean(np.abs(y-b1)),
        "B0_persistence_RMSE": np.sqrt(np.mean((y-b0)**2)),
        "B1_ridge_RMSE": np.sqrt(np.mean((y-b1)**2)),
        "B1_relative_MAE_improvement": 1-np.mean(np.abs(y-b1))/np.mean(np.abs(y-b0)),
    }
    for key, value in computed.items():
        assert abs(float(value)-reported[key]) < 1e-9
        checks += 1
assert len(state["coef"]) == len(state["feature_order"]) == 8
assert metrics["gate_pass"] is True and all(row["B1_relative_MAE_improvement"] >= .05 for row in metrics["domains"].values())
result = {"scope": "EXP048 only", "validated_evaluation_pairs": len(pred), "domain_metric_checks": checks, "time_lock_hours": 24, "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
