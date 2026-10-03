"""EXP039 bounded read of exactly five previously skipped original ZIP members."""

import csv
import io
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
P36 = ROOT / "STAT-PSYMOE-EXP036-20261002-001"
P38 = ROOT / "STAT-PSYMOE-EXP038-20261002-001"
sys.path.insert(0, str(P38))
import audit_cohort as prior  # noqa: E402


def main():
    old = [json.loads(line) for line in (P38 / "SOURCE_ROWS_001.jsonl").read_text().splitlines()]
    skipped = [r for r in old if r["reasons"] == ["MEMBER_EXCEEDS_BUDGET"]]
    assert len(skipped) == 5 and {r["participant_id"] for r in skipped} == {"02", "13", "16", "23", "30"}
    assert {r["group"] for r in skipped} == {"PD"}
    catalog = {(r["group"], r["participant_id"]): r["member_path"] for r in csv.DictReader((P36 / "TASK_INTERSECTION.csv").open(newline=""))}
    assert all(catalog[(r["group"], r["participant_id"])] == r["original_member_path"] for r in skipped)
    reader = prior.reader
    tail_start = reader.ZIP_SIZE - 4 * 1024 * 1024
    tail = reader.get_range(tail_start, reader.ZIP_SIZE - 1, 4 * 1024 * 1024)
    with zipfile.ZipFile(io.BytesIO(tail)) as archive:
        infos = {info.filename: info for info in archive.infolist()}
    results = []
    bytes_requested = len(tail)
    requests = 1
    with (HERE / "FIVE_SOURCE_ROWS_001.jsonl").open("x") as out:
        for r in skipped:
            path = r["original_member_path"]
            info = infos.get(path)
            item = {"run_id": "EXP039-FIVE-001", "group": "PD", "participant_id": r["participant_id"], "original_member_path": path}
            if info is None or info.compress_size > 1024 * 1024 - 1024 or info.file_size > 3 * 1024 * 1024:
                item.update({"qualification": "ACCESS_ERROR", "reasons": ["MISSING_OR_OUTSIDE_REGISTERED_BUDGET"]})
            else:
                requests += 1
                bytes_requested += info.compress_size + 1024
                try:
                    parsed = reader.parse_member(reader.get_csv_member(info, tail_start))
                    reasons = prior.qualify(parsed)
                    item.update({"qualification": "PASS" if not reasons else "NUMERIC_FAIL", "reasons": reasons, "diagnostics": parsed})
                except Exception as exc:
                    item.update({"qualification": "ACCESS_ERROR", "reasons": [type(exc).__name__ + ": " + str(exc)[:200]]})
            out.write(json.dumps(item, ensure_ascii=False) + "\n")
            out.flush()
            results.append(item)
            print(item["participant_id"], item["qualification"], item["reasons"], flush=True)
    counts = dict(Counter(r["qualification"] for r in results))
    summary = {"run_id": "EXP039-FIVE-001", "old_source_reference": str(P38 / "SOURCE_ROWS_001.jsonl"), "new_rows_path": str(HERE / "FIVE_SOURCE_ROWS_001.jsonl"), "source_requests": requests, "requested_range_bytes": bytes_requested, "fixed_person_ids": [r["participant_id"] for r in skipped], "qualifications": counts, "gate": "SOURCE_COMPLETION_INDETERMINATE" if counts.get("ACCESS_ERROR", 0) else "SOURCE_COMPLETION_CLASSIFIED", "prior_pass_counts": {"PD": 39, "HC": 45}, "combined_pass_counts": {"PD": 39 + counts.get("PASS", 0), "HC": 45}}
    (HERE / "GROUP_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == "__main__":
    main()
