"""Read-only local check of EXP049 keys, time lock and paired saved scores."""

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
EXP048 = HERE.parent / "STAT-PSYMOE-EXP048-20261002-001"
support = json.loads((HERE / "PAIR_SUPPORT.json").read_text())
state = json.loads((HERE / "MODEL_STATE.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
new = pd.read_csv(HERE / "B2_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
old = pd.read_csv(EXP048 / "HOLDOUT_PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
assert len(new) == sum(support["domain_pair_counts"][d] for d in metrics["domains"])
assert len(new) == 115298
assert not new.duplicated(["domain", "station", "origin_time"]).any()
assert ((new["target_time"] - new["origin_time"]) == pd.Timedelta(hours=24)).all()
assert (new["reference_count"] >= 8).all()
assert np.isfinite(new[["observed_target_PM2.5", "reference_mean_PM2.5", "B2_ridge"]]).all().all()
assert (new[["observed_target_PM2.5", "reference_mean_PM2.5", "B2_ridge"]] >= 0).all().all()
assert len(state["feature_order"]) == len(state["coef"]) == len(state["scaler_mean"]) == len(state["scaler_scale"]) == 9
assert np.isfinite(state["coef"] + state["scaler_mean"] + state["scaler_scale"] + [state["intercept"]]).all()
assert state["train_pairs"] == support["domain_pair_counts"]["train"]
assert state["feature_order"][-1] == "log1p_current_reference_mean_PM2.5"

joined = new.merge(old, on=["domain", "station", "origin_time", "target_time", "observed_target_PM2.5"], how="left", validate="one_to_one")
assert len(joined) == len(new) and joined["B1_ridge"].notna().all()
train_stations = set(support["reference_sites"])
held = set(support["held_out_stations"])
assert train_stations.isdisjoint(held) and len(train_stations) == 10 and len(held) == 2
dates = {
    "validation_same10": ("2016-01-01", "2016-12-31", train_stations),
    "future_same10": ("2017-01-01", "2017-02-28", train_stations),
    "station_2016": ("2016-01-01", "2016-12-31", held),
    "future_station_2": ("2017-01-01", "2017-02-28", held),
}
checks = 0
for domain, (start, end, sites) in dates.items():
    frame = joined.loc[joined["domain"] == domain]
    assert len(frame) == metrics["domains"][domain]["n"]
    assert set(frame["station"]) == sites
    assert frame["origin_time"].ge(pd.Timestamp(start)).all() and frame["origin_time"].lt(pd.Timestamp(end)).all()
    for subset, saved in [(frame, metrics["domains"][domain])] + [(group, metrics["by_station"][domain][site]) for site, group in frame.groupby("station")]:
        y = subset["observed_target_PM2.5"].to_numpy(dtype=float)
        b1 = subset["B1_ridge"].to_numpy(dtype=float)
        b2 = subset["B2_ridge"].to_numpy(dtype=float)
        mae1 = float(np.mean(np.abs(y - b1)))
        mae2 = float(np.mean(np.abs(y - b2)))
        rmse1 = float(np.sqrt(np.mean((y - b1) ** 2)))
        rmse2 = float(np.sqrt(np.mean((y - b2) ** 2)))
        assert len(subset) == saved["n"]
        for key, actual in [("B1_matched_MAE", mae1), ("B2_shared_linear_MAE", mae2), ("B1_matched_RMSE", rmse1), ("B2_shared_linear_RMSE", rmse2), ("B2_relative_MAE_improvement", 1 - mae2 / mae1)]:
            assert np.isclose(actual, saved[key], rtol=0, atol=1e-10), (domain, key)
            checks += 1
expected_gate = all(metrics["domains"][d]["B2_relative_MAE_improvement"] >= 0.03 for d in dates) and all(metrics["by_station"]["future_station_2"][s]["B2_relative_MAE_improvement"] >= 0 for s in held)
assert metrics["gate_pass"] == expected_gate and not expected_gate
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps({"scope": "EXP049 only; reads original EXP048 B1 predictions", "validated_evaluation_pairs": len(joined), "domain_and_station_metric_checks": checks, "target_horizon_hours": 24, "matched_B1_rows": len(joined), "gate_recomputed": metrics["conclusion_code"], "status": "PASS"}, indent=2) + "\n")
print("EXP049_LOCAL_VALIDATION_PASS", len(joined), checks)
