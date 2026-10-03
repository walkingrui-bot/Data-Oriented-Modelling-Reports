#!/usr/bin/env python3
"""Recheck EXP067 derived rows, prior B0 metrics, and day-block intervals."""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

here = Path(__file__).resolve().parent
rows = list(csv.DictReader((here / "RISK_ROWS.csv").open()))
metrics = json.loads((here / "METRICS.json").read_text())
source = json.loads((here / "SOURCE_RECHECK.json").read_text())
prior = {
    "2024": json.loads((here.parent / "STAT-PSYMOE-EXP063-20261002-001" / "METRICS.json").read_text()),
    "2025": json.loads((here.parent / "STAT-PSYMOE-EXP065-20261002-001" / "METRICS.json").read_text()),
}
checks = {}
checks["all_twenty_source_counts_match"] = all(all(x.values()) for x in source["per_year_site"].values())
checks["both_prior_prediction_sets_match"] = all(source["per_year_prediction_match"].values())
checks["exact_pair_counts"] = Counter(x["year"] for x in rows) == {"2024": 667, "2025": 589}
checks["unique_station_hour"] = len({(x["year"], x["site"], x["origin_time_gmt_end"]) for x in rows}) == len(rows)
checks["age_group_definition"] = all(
    (x["group"] == "LEFT_CENSORED_OR_UNKNOWN_START") or
    (x["group"] == "SHORT_1_2" and 1 <= int(x["outage_age_hours"]) <= 2) or
    (x["group"] == "MIDDLE_3_5" and 3 <= int(x["outage_age_hours"]) <= 5) or
    (x["group"] == "LONG_6_PLUS" and int(x["outage_age_hours"]) >= 6)
    for x in rows)
checks["finite_nonnegative_error"] = all(math.isfinite(float(x["B0_abs_error"]))
    and float(x["B0_abs_error"]) >= 0 for x in rows)
checks["prior_B0_MAE_reproduced"] = all(math.isclose(
    sum(float(x["B0_abs_error"]) for x in rows if x["year"] == y)
    / sum(x["year"] == y for x in rows),
    prior[y]["overall"]["B0"]["MAE"] if y == "2024" else prior[y]["overall"]["B0"]["MAE"],
    abs_tol=1e-12) for y in ("2024", "2025"))
checks["group_counts_reproduced"] = all(
    sum(x["year"] == y and x["group"] == g for x in rows) == metrics["per_year"][y]["groups"][g]["n"]
    for y in ("2024", "2025") for g in metrics["per_year"][y]["groups"])
checks["support_both_years"] = metrics["support_both_years"] and all(
    metrics["per_year"][y]["support_pass"] for y in ("2024", "2025"))
def ci(year):
    subset = [x for x in rows if x["year"] == year and x["group"] in ("SHORT_1_2", "LONG_6_PLUS")]
    days = sorted({x["day"] for x in subset})
    by = defaultdict(list)
    for x in subset:
        by[x["day"]].append(x)
    ss = np.array([sum(float(x["B0_abs_error"]) for x in by[d] if x["group"] == "SHORT_1_2") for d in days])
    sn = np.array([sum(x["group"] == "SHORT_1_2" for x in by[d]) for d in days])
    ls = np.array([sum(float(x["B0_abs_error"]) for x in by[d] if x["group"] == "LONG_6_PLUS") for d in days])
    ln = np.array([sum(x["group"] == "LONG_6_PLUS" for x in by[d]) for d in days])
    rng = np.random.default_rng(20261002)
    idx = rng.integers(0, len(days), size=(1000, len(days)))
    v = ls[idx].sum(axis=1) / ln[idx].sum(axis=1) - ss[idx].sum(axis=1) / sn[idx].sum(axis=1)
    return np.quantile(v, [.025, .975])
checks["both_day_intervals_reproduced"] = all(np.allclose(
    ci(y), metrics["per_year"][y]["long_minus_short_day_block"]["bootstrap_95ci"],
    rtol=0, atol=1e-12) for y in ("2024", "2025"))
checks["frozen_risk_gate_failure"] = metrics["gate_code"] == "NO_REPEATED_LONG_OUTAGE_RISK" and not metrics["risk_both_years"]
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
