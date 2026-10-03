"""EXP044 local evidence and OOF score integrity only."""

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
source = json.loads((HERE / "SOURCE_GATE.json").read_text())
splits = json.loads((HERE / "SPLITS.json").read_text())
opt = json.loads((HERE / "OPTIMIZATION.json").read_text())
metrics = json.loads((HERE / "METRICS.json").read_text())
table = list(csv.DictReader((HERE / "ANALYSIS_TABLE.csv").open(newline="")))
pred = list(csv.DictReader((HERE / "PREDICTIONS.csv").open(newline="")))
assert source["gate"] == "ANALYSIS_SOURCE_READY" and source["source_requests"] == 42
assert len(table) == 40 and len({r["participant_id"] for r in table}) == 40
assert Counter(int(r["y_fell_last_month"]) for r in table) == {0: 30, 1: 10}
assert len(splits["seeds"]) == 5 and len(opt["fits"]) == 50 and len(pred) == 200
assert all(info["converged"] and info["n_iter"] < 1000 for info in opt["fits"].values())
checks = 0
for seed, values in metrics["repetitions"].items():
    rows = [r for r in pred if r["seed"] == seed]
    assert len(rows) == 40 and len({r["participant_id"] for r in rows}) == 40
    for fold in range(5):
        sample = [r for r in rows if int(r["fold"]) == fold]
        assert Counter(int(r["y_fell_last_month"]) for r in sample) == {0: 6, 1: 2}
    y = np.array([int(r["y_fell_last_month"]) for r in rows])
    for name in ("M0", "M1", "M2"):
        p = np.clip(np.array([float(r[f"p_{name}"]) for r in rows]), 1e-9, 1-1e-9)
        macro = -0.5 * (np.log(p[y == 1]).mean() + np.log(1-p[y == 0]).mean())
        bacc = 0.5 * ((p[y == 1] >= .5).mean() + (p[y == 0] < .5).mean())
        assert abs(macro - values["scores"][name]["macro_log_loss"]) < 1e-12
        assert abs(bacc - values["scores"][name]["balanced_accuracy"]) < 1e-12
        checks += 2
assert metrics["qualifying_repetitions"] == 0 and metrics["gate_pass"] is False
result = {"scope": "EXP044 only", "source_people": 40, "OOF_predictions": 200, "converged_fits": 50, "recomputed_metric_checks": checks, "status": "PASS"}
(HERE / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result))
