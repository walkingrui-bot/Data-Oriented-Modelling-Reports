"""EXP060 local validation of saved predictions, state and paired day gate."""

import json
from pathlib import Path

import numpy as np
import pandas as pd


here = Path(__file__).resolve().parent
m = json.loads((here / "METRICS.json").read_text())
support = json.loads((here / "PAIR_SUPPORT.json").read_text())
states = json.loads((here / "MODEL_STATES.json").read_text())
pred = pd.read_csv(here / "PREDICTIONS.csv", parse_dates=["origin_time", "target_time"])
checks = {
    "source_counts_equal_EXP059": support["domain_pair_counts"] == {
        "train_same10": 3185, "validation_same10": 1286,
        "future_same10": 85, "station_2016": 277, "future_station_2": 16,
    },
    "heldout_row_counts": pred.domain.value_counts().to_dict() == {
        "validation_same10": 1286, "future_same10": 85,
        "station_2016": 277, "future_station_2": 16,
    },
    "exact_future_24h_and_no_duplicate_origin": (
        (pred.target_time - pred.origin_time == pd.Timedelta(hours=24)).all() and
        not pred.duplicated(["station", "origin_time"]).any()
    ),
    "all_neighbors_at_least_eight_and_predictions_finite": (
        pred.neighbor_count.ge(8).all() and
        np.isfinite(pred[["observed_target_PM2.5", "B0", "N1", "W1", "J1"]]).all().all() and
        pred[["observed_target_PM2.5", "B0", "N1", "W1", "J1"]].ge(0).all().all()
    ),
    "three_trained_states_only_and_train_count": (
        set(states) == {"run_id", "train_pairs", "B0", "N1", "W1", "J1"} and
        states["train_pairs"] == 3185 and
        all(states[name]["model"] == "Ridge(alpha=1.0, fit_intercept=True)"
            for name in ("N1", "W1", "J1"))
    ),
    "heldout_metrics_recomputed": True,
    "day_block_ci_recomputed": True,
    "frozen_gate_recomputed": True,
}
for domain, frame in pred.groupby("domain"):
    y = frame["observed_target_PM2.5"].to_numpy(float)
    for model in ("B0", "N1", "W1", "J1"):
        p = frame[model].to_numpy(float)
        mae = float(np.mean(np.abs(y - p)))
        rmse = float(np.sqrt(np.mean((y - p) ** 2)))
        saved = m["domains"][domain][model]
        checks["heldout_metrics_recomputed"] &= (
            len(frame) == saved["n"] and abs(mae - saved["MAE"]) < 1e-8 and
            abs(rmse - saved["RMSE"]) < 1e-8
        )
for domain in ("validation_same10", "station_2016"):
    frame = pred.loc[pred.domain == domain]
    error_difference = (
        np.abs(frame["observed_target_PM2.5"].to_numpy(float) - frame.J1.to_numpy(float)) -
        np.abs(frame["observed_target_PM2.5"].to_numpy(float) - frame.N1.to_numpy(float))
    )
    grouped = pd.DataFrame({"day": frame.origin_time.dt.floor("D"),
                            "difference": error_difference}).groupby("day").difference.agg(["sum", "count"])
    sums, counts = grouped["sum"].to_numpy(float), grouped["count"].to_numpy(int)
    sampled = np.random.default_rng(20261002).integers(0, len(sums), size=(1000, len(sums)))
    interval = np.quantile(sums[sampled].sum(axis=1) / counts[sampled].sum(axis=1), [0.025, 0.975])
    saved = m["day_block_paired"][domain]
    checks["day_block_ci_recomputed"] &= (
        len(sums) == saved["days"] and
        np.max(np.abs(interval - np.asarray(saved["bootstrap_95ci"]))) < 1e-8
    )
gate = m["gate"]["conditions"]
checks["frozen_gate_recomputed"] &= all(gate.values()) == m["gate"]["pass"] and not m["gate"]["pass"]
result = {"run_id": "EXP060-STAT-001", "checks": {k: bool(v) for k, v in checks.items()},
          "passed": sum(bool(v) for v in checks.values()), "total": len(checks),
          "scope": "EXP060 saved source support, model state and derived heldout predictions; day-block interval and gate; no original reload or global suite"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
