#!/usr/bin/env python3
"""Local derived-output checks for EXP064 source audit."""

import json
from pathlib import Path

here = Path(__file__).resolve().parent
source = json.loads((here / "SOURCE_MATRIX.json").read_text())
support = json.loads((here / "PAIR_SUPPORT.json").read_text())
fixed = "BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR".split()
checks = {}
checks["fixed_ten_sites"] = [x["site"] for x in source["sites"]] == fixed
checks["all_official_2025_files"] = source["all_ten_retrieved"] and all(
    f"/site_data/{x['site']}_2025.csv" in x["csv_url"] and "error" not in x
    for x in source["sites"])
checks["read_budget"] = source["downloaded_bytes_total"] <= 30 * 1024 * 1024
checks["2025_hour_grid"] = (source["grid_hours"] == 8760
    and source["grid_start"] == "2025-01-01T01:00:00+00:00"
    and source["grid_end"] == "2026-01-01T00:00:00+00:00")
categories = ("valid_ratified_pm", "explicit_blank_pm", "non_numeric_pm",
              "nonfinite_or_negative_pm", "not_ratified_pm", "wrong_unit_pm")
checks["explicit_rows_accounted"] = all(
    sum(x["counts"].get(k, 0) for k in categories) == x["counts"]["explicit_grid_rows"]
    for x in source["sites"])
checks["no_clock_errors"] = all(
    x["counts"].get("duplicate_hour_rows", 0) == 0 and
    x["counts"].get("unparsed_time_rows", 0) == 0 and
    x["counts"].get("off_grid_rows", 0) == 0 for x in source["sites"])
checks["ten_qualified_sites"] = support["qualified_sites"] == fixed and all(
    x["counts"]["valid_ratified_pm"] >= 6000 for x in source["sites"])
checks["pair_total_rederived"] = support["pair_count"] == sum(
    x.get("eligible_pair", 0) for x in support["counts_by_target"].values()) == 589
checks["neighbor_distribution"] = sum(support["neighbor_count_distribution"].values()) == sum(
    x.get("true_future_target", 0) for x in support["counts_by_target"].values())
checks["five_station_and_thirty_day_gate"] = (
    len(support["target_sites_at_least_10"]) == 9 and support["unique_origin_dates"] == 151)
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
