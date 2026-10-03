"""EXP059 local aggregate consistency checks, without re-downloading originals."""

import json
from pathlib import Path

import pandas as pd


here = Path(__file__).resolve().parent
s = json.loads((here / "SOURCE_SUPPORT.json").read_text())
counts = pd.read_csv(here / "STATION_YEAR_COUNTS.csv")
checks = {
    "twelve_stations_and_35064_hour_grid": s["original_station_count"] == 12 and
        s["common_original_hours"] == 35064 and s["original_row_count"] == 420768,
    "station_year_aggregation_is_12_times_5": len(counts) == 60 and
        counts.groupby("station").size().eq(5).all(),
    "attrition_nonincreasing": all(
        a["origin_original_na"] >= a["plus_real_24h_target"] >=
        a["plus_station_meteorology"] >= a["plus_eight_neighbor_PM"] == a["eligible"]
        for a in s["attrition"].values()
    ),
    "all_domain_totals_match_station_counts": all(
        s["domain_counts"][name] == sum(per_station.values())
        for name, per_station in s["domain_by_station"].items()
    ),
    "frozen_gate_recomputes": True,
    "no_model_output": s["models_run"] is False,
}
gate = all(s["domain_counts"][name] >= threshold
           for name, threshold in s["thresholds"].items())
gate &= len(s["train_stations_at_least_20"]) >= 5
gate &= len(s["validation_stations_at_least_10"]) >= 5
gate &= len(s["future_stations_at_least_5"]) >= 4
gate &= all(s["domain_by_station"]["station_2016"][station] >= 10 and
            s["domain_by_station"]["future_station_2"][station] >= 3
            for station in s["held_out_stations"])
checks["frozen_gate_recomputes"] = gate == (s["gate"] == "NATURAL_OUTAGE_SOURCE_READY_FOR_DESIGN")
result = {"run_id": "EXP059-SOURCE-001", "checks": {k: bool(v) for k, v in checks.items()},
          "passed": sum(bool(v) for v in checks.values()), "total": len(checks),
          "scope": "this experiment's aggregate JSON/CSV and frozen source gate; no model, original reload, test or global suite"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
