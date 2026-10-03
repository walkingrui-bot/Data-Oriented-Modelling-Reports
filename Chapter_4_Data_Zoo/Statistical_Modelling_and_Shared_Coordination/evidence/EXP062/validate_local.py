#!/usr/bin/env python3
"""Scoped validation for EXP062 directory/source/support derivations."""

import json
from pathlib import Path

here = Path(__file__).resolve().parent
directory = json.loads((here / "DIRECTORY.json").read_text())
source = json.loads((here / "SOURCE_MATRIX.json").read_text())
support = json.loads((here / "PAIR_SUPPORT.json").read_text())
old = json.loads((here.parent / "STAT-PSYMOE-EXP061-20261002-001" / "SOURCE_MATRIX.json").read_text())
checks = {}
checks["full_directory_result_count"] = directory["query_result_count"] == 199
checks["all_bbox_candidates_processed"] = (
    directory["selected_count"] == source["directory_selected_count"] == len(source["sites"]) == 20)
box = directory["bbox"]
checks["candidate_coordinates_inside_frozen_box"] = all(
    box["latitude_min"] <= x["latitude"] <= box["latitude_max"] and
    box["longitude_min"] <= x["longitude"] <= box["longitude_max"]
    for x in directory["selected_sites"])
checks["candidate_long_ids_match"] = [x["uka_id"] for x in source["sites"]] == [
    x["uka_id"] for x in directory["selected_sites"]]
checks["source_codes_unique_and_no_errors"] = source["candidate_codes_unique"] and all(
    "site" in x and "error" not in x for x in source["sites"])
checks["bounded_read_and_hour_grid"] = (
    source["downloaded_bytes_total"] <= 60 * 1024 * 1024 and source["grid_hours"] == 8784)
categories = ("valid_ratified_pm", "explicit_blank_pm", "non_numeric_pm",
              "nonfinite_or_negative_pm", "not_ratified_pm", "wrong_unit_pm")
checks["pm_rows_accounted"] = all(
    sum(x["counts"].get(k, 0) for k in categories) == x["counts"]["explicit_grid_rows"]
    for x in source["sites"] if x.get("pm_column_present"))
checks["hour_uniqueness"] = all(
    x["counts"].get("duplicate_hour_rows", 0) == 0 and
    x["counts"].get("unparsed_time_rows", 0) == 0 and
    x["counts"].get("off_grid_rows", 0) == 0
    for x in source["sites"] if x.get("pm_column_present"))
checks["qualified_sites_rederived"] = support["qualified_sites"] == [
    x["site"] for x in source["sites"] if x.get("schema_ok")
    and x.get("counts", {}).get("valid_ratified_pm", 0) >= 6000]
checks["ten_qualified_sites"] = len(support["qualified_sites"]) == 10
checks["old_eight_site_source_counts_reproduced"] = all(
    next(x for x in source["sites"] if x["site"] == y["site"])["counts"] == y["counts"]
    for y in old["sites"] if y["site"] in support["qualified_sites"])
checks["eligible_pair_support"] = (
    support["pair_count"] == 667 and support["unique_target_dates"] == 133 and
    len(support["target_sites_at_least_10"]) == 10 and
    sum(x.get("eligible_pair", 0) for x in support["counts_by_target"].values()) == 667)
checks["neighbor_counts_sum_to_future_targets"] = (
    sum(support["neighbor_count_distribution"].values()) ==
    sum(x.get("true_future_target", 0) for x in support["counts_by_target"].values()))
result = {"checks": checks, "passed": sum(checks.values()), "total": len(checks),
          "result": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
