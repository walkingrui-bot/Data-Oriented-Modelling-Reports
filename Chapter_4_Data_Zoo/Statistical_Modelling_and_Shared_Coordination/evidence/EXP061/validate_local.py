#!/usr/bin/env python3
"""Check only EXP061 derived source and support outputs."""

import json
from pathlib import Path

root = Path(__file__).resolve().parent
source = json.loads((root / "SOURCE_MATRIX.json").read_text())
support = json.loads((root / "PAIR_SUPPORT.json").read_text())
expected = "BEX CA1 CLL2 HG4 HIL HORS HP1 HRL KC1 LON6 MY1 TED2".split()
checks = {}
checks["twelve_preselected_sites"] = [x["site"] for x in source["sites"]] == expected
checks["all_twelve_official_files_retrieved"] = source["all_12_retrieved"] and all(
    "csv_url" in x and "error" not in x for x in source["sites"])
checks["official_hourly_paths"] = all(
    f"/site_data/{x['site']}_2024.csv" in x["csv_url"]
    for x in source["sites"])
checks["bounded_read"] = source["downloaded_bytes_total"] <= 30 * 1024 * 1024
checks["leap_year_hour_ending_grid"] = (source["grid_hours"] == 8784
    and source["grid_start"] == "2024-01-01T01:00:00+00:00"
    and source["grid_end"] == "2025-01-01T00:00:00+00:00")
category_names = ("valid_ratified_pm", "explicit_blank_pm", "non_numeric_pm",
                  "nonfinite_or_negative_pm", "not_ratified_pm", "wrong_unit_pm")
checks["present_hour_categories_sum"] = all(
    sum(x["counts"].get(k, 0) for k in category_names)
    == x["counts"]["explicit_grid_rows"]
    for x in source["sites"] if x.get("pm_column_present"))
checks["no_duplicate_or_unparsed_hour"] = all(
    x["counts"].get("duplicate_hour_rows", 0) == 0
    and x["counts"].get("unparsed_time_rows", 0) == 0
    and x["counts"].get("off_grid_rows", 0) == 0
    for x in source["sites"] if x.get("pm_column_present"))
checks["qualified_sites_rederived"] = support["qualified_sites"] == [
    x["site"] for x in source["sites"] if x.get("schema_ok")
    and x["counts"].get("valid_ratified_pm", 0) >= 6000]
checks["qualified_site_count_eight"] = len(support["qualified_sites"]) == 8
checks["target_count_and_neighbors"] = (
    sum(c.get("true_future_target", 0) for c in support["counts_by_target"].values())
    == sum(support["neighbor_count_distribution"].values()) == 581)
checks["no_eight_neighbor_pairs"] = (
    support["pair_count"] == 0
    and max(map(int, support["neighbor_count_distribution"])) == 7)
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(root / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
