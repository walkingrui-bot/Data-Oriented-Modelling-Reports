#!/usr/bin/env python3
"""EXP066 bounded derived source checks."""

import json
from pathlib import Path

here = Path(__file__).resolve().parent
source = json.loads((here / "SOURCE_MATRIX.json").read_text())
support = json.loads((here / "PAIR_SUPPORT.json").read_text())
fixed = "BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR".split()
checks = {}
checks["fixed_ten_sites"] = [x["site"] for x in source["sites"]] == fixed
checks["all_ten_official_2026_files"] = source["all_ten_retrieved"] and all(
    f"/site_data/{x['site']}_2026.csv" in x["csv_url"] and "error" not in x
    for x in source["sites"])
checks["download_budget"] = source["downloaded_bytes_total"] <= 30 * 1024 * 1024
checks["origin_window_frozen"] = (
    source["origin_window_hours"] == 5831 and
    source["origin_window_end_exclusive"] == "2026-09-01T00:00:00+00:00")
categories = ("valid_ratified_pm", "explicit_blank_pm", "non_numeric_pm",
              "nonfinite_or_negative_pm", "not_ratified_pm", "wrong_unit_pm")
checks["explicit_rows_accounted"] = all(
    sum(x["counts"].get(k, 0) for k in categories) == x["counts"]["explicit_grid_rows"]
    for x in source["sites"])
checks["no_clock_parse_or_duplicate_errors"] = all(
    x["counts"].get("duplicate_hour_rows", 0) == 0 and
    x["counts"].get("unparsed_time_rows", 0) == 0 and
    x["counts"].get("off_grid_rows", 0) == 0 for x in source["sites"])
checks["qualified_set_rederived"] = support["qualified_sites"] == [
    x["site"] for x in source["sites"] if x.get("schema_ok")
    and x["ratified_valid_in_origin_window"] >= 4000]
checks["only_eight_qualified"] = len(support["qualified_sites"]) == 8
checks["BEX_MY1_below_frozen_threshold"] = all(
    next(x for x in source["sites"] if x["site"] == s)["ratified_valid_in_origin_window"] < 4000
    for s in ("BEX", "MY1"))
checks["no_eight_neighbor_pairs"] = support["pair_count"] == 0 and all(
    int(k) <= 7 for k in support["neighbor_count_distribution"])
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
