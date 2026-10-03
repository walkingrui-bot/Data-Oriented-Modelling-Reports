#!/usr/bin/env python3
"""EXP065 scoped recomputation from derived 2025 predictions and states."""

import csv
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np

here = Path(__file__).resolve().parent
pred = list(csv.DictReader((here / "PREDICTIONS.csv").open()))
metrics = json.loads((here / "METRICS.json").read_text())
states = json.loads((here / "MODEL_STATES.json").read_text())
source = json.loads((here / "SOURCE_RECHECK.json").read_text())
prior = json.loads((here.parent / "STAT-PSYMOE-EXP064-20261002-001" / "PAIR_SUPPORT.json").read_text())
checks = {}
checks["both_source_years_match"] = all(all(x.values()) for x in source["per_year_site"].values())
checks["both_pair_years_match"] = all(x["match"] for x in source["per_year_pair_match"].values())
checks["training_only_2024_667"] = (states["train_year"] == 2024
    and states["train_pairs"] == 667 and
    all(states[x]["train_pairs"] == 667 for x in ("C0", "M1", "L1")))
checks["test_only_2025_589"] = len(pred) == metrics["test_pairs"] == prior["pair_count"] == 589
checks["site_pair_counts"] = Counter(x["site"] for x in pred) == Counter({
    s: c.get("eligible_pair", 0) for s, c in prior["counts_by_target"].items()})
checks["unique_and_exact_time"] = (len({(x["site"], x["origin_time_gmt_end"]) for x in pred}) == len(pred)
    and all(datetime.fromisoformat(x["target_time_gmt_end"])
            - datetime.fromisoformat(x["origin_time_gmt_end"])
            == timedelta(hours=24) for x in pred))
checks["eight_or_nine_neighbors"] = all(8 <= int(x["neighbor_count"]) <= 9 for x in pred)
checks["all_saved_values_finite_nonnegative"] = all(math.isfinite(float(x[name]))
    and float(x[name]) >= 0 for x in pred for name in ("target", "B0", "C0", "M1", "L1"))
y = np.asarray([float(x["target"]) for x in pred])
checks["all_four_MAE_RMSE_recomputed"] = all(
    math.isclose(float(np.mean(abs(y - np.asarray([float(x[name]) for x in pred])))),
                 metrics["overall"][name]["MAE"], abs_tol=1e-12) and
    math.isclose(float(np.sqrt(np.mean((y - np.asarray([float(x[name]) for x in pred])) ** 2))),
                 metrics["overall"][name]["RMSE"], abs_tol=1e-12)
    for name in ("B0", "C0", "M1", "L1"))
checks["all_station_MAE_recomputed"] = all(math.isclose(
    sum(abs(float(x["target"]) - float(x[name])) for x in pred if x["site"] == site)
    / sum(x["site"] == site for x in pred), metrics["by_station"][site][name]["MAE"],
    abs_tol=1e-12) for site in metrics["by_station"] for name in ("B0", "C0", "M1", "L1"))
days = defaultdict(list)
for x in pred:
    days[x["origin_day_gmt"]].append(x)
keys = sorted(days)
def calc_ci(candidate, baseline):
    sums = np.asarray([sum(abs(float(x["target"]) - float(x[candidate]))
        - abs(float(x["target"]) - float(x[baseline])) for x in days[d]) for d in keys])
    counts = np.asarray([len(days[d]) for d in keys])
    rng = np.random.default_rng(20261002)
    idx = rng.integers(0, len(keys), size=(1000, len(keys)))
    return np.quantile(sums[idx].sum(axis=1) / counts[idx].sum(axis=1), [.025, .975])
checks["all_four_day_intervals_recomputed"] = all(np.allclose(
    calc_ci(name, "B0"), metrics["candidate_results"][name]["day_block"]["bootstrap_95ci"],
    atol=1e-12, rtol=0) for name in ("C0", "M1", "L1")) and np.allclose(
    calc_ci("L1", "M1"), metrics["L1_additional_vs_M1"]["day_block"]["bootstrap_95ci"],
    atol=1e-12, rtol=0)
checks["frozen_gates_not_passed"] = (not metrics["any_local_stat_candidate_supported"]
    and all(not x["pass"] for x in metrics["candidate_results"].values())
    and not metrics["L1_additional_vs_M1"]["pass"])
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
