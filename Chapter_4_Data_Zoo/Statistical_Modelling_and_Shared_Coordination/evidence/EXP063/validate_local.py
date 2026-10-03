#!/usr/bin/env python3
"""Recompute EXP063 metrics from its one derived prediction file only."""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

here = Path(__file__).resolve().parent
rows = list(csv.DictReader((here / "PREDICTIONS.csv").open()))
metric = json.loads((here / "METRICS.json").read_text())
source = json.loads((here / "SOURCE_RECHECK.json").read_text())
prior = json.loads((here.parent / "STAT-PSYMOE-EXP062-20261002-001" / "PAIR_SUPPORT.json").read_text())
checks = {}
checks["source_version_and_pair_count_match"] = source["source_version_match"] and source["pair_support_match"]
checks["667_rows"] = len(rows) == metric["n"] == prior["pair_count"] == 667
checks["ten_sites_and_counts"] = Counter(r["site"] for r in rows) == Counter(
    {s: c.get("eligible_pair", 0) for s, c in prior["counts_by_target"].items()})
checks["unique_station_hour"] = len({(r["site"], r["origin_time_gmt_end"]) for r in rows}) == len(rows)
checks["exact_24_hour_utc"] = all(
    datetime.fromisoformat(r["target_time_gmt_end"]) - datetime.fromisoformat(r["origin_time_gmt_end"])
    == timedelta(hours=24) for r in rows)
checks["eight_or_nine_neighbors"] = all(8 <= int(r["neighbor_count"]) <= 9 for r in rows)
checks["nonnegative_finite"] = all(math.isfinite(float(r[k])) and float(r[k]) >= 0
    for r in rows for k in ("target", "B0", "N1"))
checks["saved_inverse_transform"] = all(math.isclose(
    float(r["N1"]), max(0, math.expm1(float(r["N1_log_prediction"]))), rel_tol=1e-12)
    for r in rows)
y = np.array([float(r["target"]) for r in rows])
b = np.array([float(r["B0"]) for r in rows])
n = np.array([float(r["N1"]) for r in rows])
checks["overall_MAE_recomputed"] = (
    math.isclose(float(np.mean(abs(y - b))), metric["overall"]["B0"]["MAE"], abs_tol=1e-12)
    and math.isclose(float(np.mean(abs(y - n))), metric["overall"]["N1"]["MAE"], abs_tol=1e-12))
checks["overall_RMSE_recomputed"] = (
    math.isclose(float(np.sqrt(np.mean((y - b) ** 2))), metric["overall"]["B0"]["RMSE"], abs_tol=1e-12)
    and math.isclose(float(np.sqrt(np.mean((y - n) ** 2))), metric["overall"]["N1"]["RMSE"], abs_tol=1e-12))
days = defaultdict(list)
for r in rows:
    days[r["origin_day_gmt"]].append(r)
keys = sorted(days)
sums = np.array([sum(abs(float(r["target"]) - float(r["N1"]))
    - abs(float(r["target"]) - float(r["B0"])) for r in days[d]) for d in keys])
counts = np.array([len(days[d]) for d in keys])
rng = np.random.default_rng(20261002)
sample = rng.integers(0, len(keys), size=(1000, len(keys)))
ci = np.quantile(sums[sample].sum(axis=1) / counts[sample].sum(axis=1), [0.025, 0.975])
checks["day_block_interval_recomputed"] = np.allclose(
    ci, metric["day_block_paired"]["bootstrap_95ci"], atol=1e-12, rtol=0)
checks["frozen_gate_failure_recomputed"] = (
    metric["gate"]["pass"] is False and
    all(x is False for x in metric["gate"]["conditions"].values()) and
    all(v < 0 for v in metric["station_relative_MAE_improvement"].values()))
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
