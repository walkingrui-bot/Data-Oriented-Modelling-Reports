"""EXP038 cohort audit, reusing EXP037 original-member reader in place."""

import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PREV36 = RESEARCH / "STAT-PSYMOE-EXP036-20261002-001"
PREV37 = RESEARCH / "STAT-PSYMOE-EXP037-20261002-001"
sys.path.insert(0, str(PREV37))
import audit_two_members as reader  # noqa: E402 -- source reused at original path


def qualify(member):
    reasons = []
    foot = {k.lower(): v for k, v in member["foot_counts"].items()}
    if set(foot) == {"l", "r"}:
        foot = {"left": foot["l"], "right": foot["r"]}
    if set(foot) != {"left", "right"}:
        reasons.append("SIDE_SET_UNCLEAR")
    elif foot["left"] < 500 or foot["right"] < 500:
        reasons.append("SIDE_LENGTH_BELOW_500")
    if member["time_column"] is None:
        reasons.append("TIMESTAMP_COLUMN_ABSENT")
    else:
        times = {k.lower(): v for k, v in member["time_by_foot"].items()}
        if set(times) == {"l", "r"}:
            times = {"left": times["l"], "right": times["r"]}
        if set(times) != {"left", "right"}:
            reasons.append("TIME_SIDE_SET_UNCLEAR")
        else:
            for side in ("left", "right"):
                if times[side]["finite"] != foot.get(side, -1) or not times[side]["strictly_increasing"]:
                    reasons.append("TIME_INVALID_" + side.upper())
    fields = member["numeric_nonpressure_columns"]
    for axis in ("acx", "acy", "acz", "gyrx", "gyry", "gyrz"):
        if fields.get(axis, {}).get("finite") != member["row_count"]:
            reasons.append("AXIS_INVALID_" + axis.upper())
    return reasons


def main():
    target = list(csv.DictReader((PREV36 / "TASK_INTERSECTION.csv").open(newline="")))
    if len(target) != 89 or len({(r["group"], r["participant_id"]) for r in target}) != 89:
        raise RuntimeError("fixed person path table is not 89 unique group-ID pairs")
    if Counter(r["group"] for r in target) != {"PD": 44, "HC": 45}:
        raise RuntimeError("fixed group denominators differ")
    old = json.loads((PREV37 / "SOURCE_AUDIT.json").read_text())["members"]
    old_names = {v["original_member_path"]: (label, v) for label, v in old.items()}
    if len(old_names) != 2:
        raise RuntimeError("EXP037 two original member references missing")
    tail_start = reader.ZIP_SIZE - 4 * 1024 * 1024
    tail = reader.get_range(tail_start, reader.ZIP_SIZE - 1, 4 * 1024 * 1024)
    with zipfile.ZipFile(io.BytesIO(tail)) as archive:
        infos = {info.filename: info for info in archive.infolist()}
    rows_path = HERE / "SOURCE_ROWS_001.jsonl"
    results = []
    requested_range_bytes = len(tail)
    source_requests = 1
    new_targets = [r for r in target if r["member_path"] not in old_names]
    if len(new_targets) != 87:
        raise RuntimeError("exactly 87 new member paths required")
    with rows_path.open("x") as out:
        for i, cohort in enumerate(new_targets, 1):
            path = cohort["member_path"]
            result = {"run_id": "EXP038-COHORT-001", "group": cohort["group"], "participant_id": cohort["participant_id"], "original_member_path": path}
            info = infos.get(path)
            if info is None:
                result.update({"qualification": "ACCESS_ERROR", "reasons": ["ZIP_MEMBER_ABSENT"]})
            elif info.compress_size > 1024 * 1024 - 1024 or info.file_size > 2 * 1024 * 1024:
                result.update({"qualification": "ACCESS_ERROR", "reasons": ["MEMBER_EXCEEDS_BUDGET"]})
            else:
                source_requests += 1
                requested_range_bytes += info.compress_size + 1024
                try:
                    parsed = reader.parse_member(reader.get_csv_member(info, tail_start))
                    reasons = qualify(parsed)
                    result.update({"qualification": "PASS" if not reasons else "NUMERIC_FAIL", "reasons": reasons, "diagnostics": parsed})
                except Exception as exc:  # preserve this person's failure and continue within fixed budget
                    result.update({"qualification": "ACCESS_ERROR", "reasons": [type(exc).__name__ + ": " + str(exc)[:200]]})
            out.write(json.dumps(result, ensure_ascii=False) + "\n")
            out.flush()
            results.append(result)
            if i % 10 == 0 or i == len(new_targets):
                print(f"source audit {i}/{len(new_targets)}", flush=True)
    for cohort in target:
        if cohort["member_path"] in old_names:
            _, previous = old_names[cohort["member_path"]]
            reasons = qualify(previous)
            results.append({"group": cohort["group"], "participant_id": cohort["participant_id"], "original_member_path": cohort["member_path"], "qualification": "PASS" if not reasons else "NUMERIC_FAIL", "reasons": reasons, "source_reference": str(PREV37 / "SOURCE_AUDIT.json")})
    counts = {group: dict(Counter(r["qualification"] for r in results if r["group"] == group)) for group in ("PD", "HC")}
    access_error_count = sum(r["qualification"] == "ACCESS_ERROR" for r in results)
    if access_error_count:
        gate = "SOURCE_ACCESS_INDETERMINATE"
    elif counts["PD"].get("PASS", 0) >= 36 and counts["HC"].get("PASS", 0) >= 36:
        gate = "COHORT_SOURCE_PASS"
    else:
        gate = "STOP_NUMERIC_SOURCE"
    summary = {"run_id": "EXP038-COHORT-001", "input_paths": str(PREV36 / "TASK_INTERSECTION.csv"), "prior_two_source_reference": str(PREV37 / "SOURCE_AUDIT.json"), "new_rows_path": str(rows_path), "source_requests": source_requests, "requested_range_bytes": requested_range_bytes, "group_denominators": {"PD": 44, "HC": 45}, "group_qualifications": counts, "gate": gate, "all_reasons": dict(Counter(reason for r in results for reason in r["reasons"])), "all_person_keys_unique": len({(r["group"], r["participant_id"]) for r in results}) == 89}
    (HERE / "GROUP_SUMMARY.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
