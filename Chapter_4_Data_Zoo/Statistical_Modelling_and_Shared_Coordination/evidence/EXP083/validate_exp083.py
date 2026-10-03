"""Local independent audit of EXP083 derived daily metrics and stop boundary."""

import csv
import json
from pathlib import Path

import numpy as np


here = Path(__file__).resolve().parent
source = json.loads((here / "SOURCE_RECHECK.json").read_text())
support = json.loads((here / "MODEL_SUPPORT.json").read_text())
metrics = json.loads((here / "VALIDATION_METRICS.json").read_text())
with (here / "VALIDATION_DAILY_ERRORS.csv").open(newline="") as handle:
    rows = list(csv.DictReader(handle))
base = np.array([float(row["BASE_mae"]) for row in rows])
weather = np.array([float(row["WEATHER_mae"]) for row in rows])
diff = weather - base
draws = np.random.default_rng(20261002).integers(0, len(diff), size=(2000, len(diff)))
interval = np.quantile(np.mean(diff[draws], axis=1), [0.025, 0.975])
checks = {
    "source_recheck_all_match": source["gate_result"] == "SOURCE_VERSION_MATCH" and all(source["checks_against_exp082"].values()),
    "source_support_pass": support["gate_result"] == "MODEL_SUPPORT_PASS" and all(support["checks"].values()),
    "daily_rows_match": len(rows) == metrics["evaluation_days"] == support["periods"]["validation_2017"]["evaluation_dates_at_least_18_hours"],
    "all_daily_hours_at_least_18": all(int(row["hours"]) >= 18 for row in rows),
    "base_mae_recomputed": np.isclose(np.mean(base), metrics["base_day_equal_mae"], rtol=0, atol=1e-10),
    "weather_mae_recomputed": np.isclose(np.mean(weather), metrics["weather_day_equal_mae"], rtol=0, atol=1e-10),
    "gain_recomputed": np.isclose((np.mean(base) - np.mean(weather)) / np.mean(base) * 100, metrics["relative_weather_gain_pct"], rtol=0, atol=1e-10),
    "bootstrap_recomputed": np.allclose(interval, metrics["paired_day_bootstrap_2000_ci95_for_weather_minus_base"], rtol=0, atol=1e-10),
    "improved_days_recomputed": int(np.sum(diff < 0)) == metrics["days_weather_better"],
    "frozen_three_gates_failed": metrics["checks"] == {"relative_gain_at_least_5pct": False, "bootstrap_upper_below_zero": False, "at_least_60pct_days_improve": False},
    "test_remained_unscored": not any(here.glob("TEST_*")),
}
result = {"checks": {key: bool(value) for key, value in checks.items()},
          "checks_passed": sum(bool(value) for value in checks.values()),
          "checks_total": len(checks), "local_validation": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
