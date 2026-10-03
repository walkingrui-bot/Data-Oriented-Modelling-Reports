"""EXP074 necessary source gate for label-independent cross-device episodes."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "STAT-PSYMOE-EXP073-20261002-001" / "SOURCE_MATRIX.json"
SELECTED = tuple("FGHIJKLOPQRS")
SENSORS = ("phone_accel", "phone_gyro", "watch_accel", "watch_gyro")
MIN_GAP = 5_000_000_000
MIN_DURATION = 150_000_000_000
MAX_DURATION = 220_000_000_000


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not source["activity_key_matches_18"] or len(source["subjects"]) != 51:
        raise ValueError("EXP073 source matrix is not the valid 51-person/18-code audit")
    people = {}
    class_pass_counts = Counter()
    for subject, record in source["subjects"].items():
        axis = {}
        for sensor in SENSORS:
            periods = []
            for code, activity in record["activities"].items():
                group = activity["sensors"][sensor]
                lo, hi = group["min_timestamp"], group["max_timestamp"]
                if lo is not None and hi is not None and hi > lo:
                    periods.append((lo, hi, code))
            periods.sort(key=lambda row: (row[0], row[2]))
            positions = {code: i for i, (_, _, code) in enumerate(periods)}
            checks = {}
            for code in SELECTED:
                group = record["activities"][code]["sensors"][sensor]
                lo, hi = group["min_timestamp"], group["max_timestamp"]
                valid_source = (group["valid_rows"] >= 500 and group["invalid_rows"] == 0
                                and group["wrong_subject_rows"] == 0 and lo is not None
                                and hi is not None and MIN_DURATION <= hi - lo <= MAX_DURATION)
                if code not in positions:
                    left_gap = right_gap = None
                    boundary = False
                else:
                    i = positions[code]
                    left_gap = None if i == 0 else lo - periods[i - 1][1]
                    right_gap = None if i == len(periods) - 1 else periods[i + 1][0] - hi
                    boundary = ((left_gap is None or left_gap >= MIN_GAP)
                                and (right_gap is None or right_gap >= MIN_GAP))
                checks[code] = {"valid_source": valid_source, "boundary_visible": boundary,
                                "left_gap_ge_5s": left_gap is None or left_gap >= MIN_GAP,
                                "right_gap_ge_5s": right_gap is None or right_gap >= MIN_GAP}
            axis[sensor] = {"selected_order": [row[2] for row in periods if row[2] in SELECTED],
                            "checks": checks}
        orders = [axis[sensor]["selected_order"] for sensor in SENSORS]
        same_order = all(order == orders[0] for order in orders[1:]) and len(orders[0]) == len(SELECTED)
        class_checks = {}
        for code in SELECTED:
            source_ok = all(axis[sensor]["checks"][code]["valid_source"] for sensor in SENSORS)
            boundary_ok = all(axis[sensor]["checks"][code]["boundary_visible"] for sensor in SENSORS)
            class_checks[code] = {"four_source_valid": source_ok,
                                  "four_boundaries_visible": boundary_ok}
            if source_ok:
                class_pass_counts[(code, "source")] += 1
            if boundary_ok:
                class_pass_counts[(code, "boundary")] += 1
        all_source = all(v["four_source_valid"] for v in class_checks.values())
        all_boundary = all(v["four_boundaries_visible"] for v in class_checks.values())
        qualified = all_source and same_order and all_boundary
        people[subject] = {"all_12_four_source_valid": all_source,
                           "same_12_order_four_sensors": same_order,
                           "all_12_four_boundaries_visible": all_boundary,
                           "qualified": qualified, "class_checks": class_checks}
    counts = {"people": len(people),
              "all_12_source": sum(p["all_12_four_source_valid"] for p in people.values()),
              "same_order": sum(p["same_12_order_four_sensors"] for p in people.values()),
              "all_12_boundaries": sum(p["all_12_four_boundaries_visible"] for p in people.values()),
              "qualified": sum(p["qualified"] for p in people.values())}
    decision = ("LABEL_INDEPENDENT_12_EPISODE_SOURCE_READY_FOR_MODEL_DESIGN"
                if counts["qualified"] >= 40 else "STOP_LABEL_INDEPENDENT_EPISODE_SUPPORT")
    result = {"research_id": "STAT-PSYMOE-EXP074-20261002-001",
              "attempt_id": "EXP074-EPISODE-SOURCE-001",
              "source_matrix_path": str(SOURCE), "selected_codes": list(SELECTED),
              "time_tick_interpretation": "relative only; 1e9 ticks approximately 1 s based on 3-minute collection",
              "min_visible_gap_ticks": MIN_GAP, "duration_ticks": [MIN_DURATION, MAX_DURATION],
              "counts": counts, "per_class_people": {code: {
                  "four_source_valid": class_pass_counts[(code, "source")],
                  "four_boundaries_visible": class_pass_counts[(code, "boundary")],
              } for code in SELECTED},
              "subjects": people, "decision": decision,
              "model_fits": 0, "test_performance_scores": 0}
    (HERE / "SOURCE_GATE.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"selected_codes": result["selected_codes"],
                      "counts": counts, "per_class_people": result["per_class_people"],
                      "decision": decision}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
