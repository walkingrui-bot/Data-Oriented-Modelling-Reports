"""EXP036-INTERSECTION-002: person support and side observability from archive paths only."""

import csv
import json
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ZIP_MEMBER_INDEX.csv"
TASK = ROOT / "TASK_INTERSECTION.csv"
DIAG = ROOT / "INTERSECTION_DIAGNOSTICS.json"
PATTERN = re.compile(r"^Parkinson Dataset/(Healthy patients|Parkinson patients)/1_10mSlow/([0-9]+)-?RTSOCS - .*\.csv$")


def main():
    if TASK.exists() or DIAG.exists():
        raise FileExistsError("Preserve EXP036-INTERSECTION-002 outputs")
    with SOURCE.open(newline="") as handle:
        members = list(csv.DictReader(handle))
    rows = []
    for member in members:
        if member["directory"] == "True":
            continue
        match = PATTERN.fullmatch(member["member_path"])
        if not match:
            continue
        group = "HC" if match.group(1) == "Healthy patients" else "PD"
        rows.append({"group": group, "participant_id": match.group(2),
                     "member_path": member["member_path"],
                     "uncompressed_bytes": member["uncompressed_bytes"],
                     "left_foot_path_evidence": "UNKNOWN", "right_foot_path_evidence": "UNKNOWN"})
    rows.sort(key=lambda r: (r["group"], int(r["participant_id"])))
    with TASK.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else
                                ["group", "participant_id", "member_path", "uncompressed_bytes",
                                 "left_foot_path_evidence", "right_foot_path_evidence"])
        writer.writeheader()
        writer.writerows(rows)
    counts = Counter(r["group"] for r in rows)
    unique = {group: len({r["participant_id"] for r in rows if r["group"] == group}) for group in ("PD", "HC")}
    explicit_side = sum("left" in Path(r["member_path"]).stem.lower() and
                        "right" in Path(r["member_path"]).stem.lower() for r in rows)
    output = {"run_id": "EXP036-INTERSECTION-002", "source": "ZIP central directory names only",
              "task": "1_10mSlow", "file_counts": dict(counts), "unique_people": unique,
              "duplicate_person_files": len(rows) - sum(unique.values()),
              "explicit_both_foot_names": explicit_side,
              "official_schema_note": "Zenodo description lists a foot column; directory names do not establish both side values per person.",
              "gate": "STOP_FILE_INTERSECTION_UNKNOWN"}
    DIAG.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
