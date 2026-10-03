"""EXP025-COHORT-001: participant-level PADS source alignment, no raw copies."""

import csv
import io
import json
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://physionet.org/files/parkinsons-disease-smartwatch/1.0.0/"
AUDIT = ROOT / "SUBJECT_AUDIT.csv"
PREFLIGHT = ROOT / "PREFLIGHT_25.json"
INDEX = ROOT / "SOURCE_INDEX.json"
DIAG = ROOT / "CHANNEL_DIAGNOSTICS.json"
FILE_CAP = 500_000
TOTAL_CAP = 50 * 1024 * 1024
FIELDS = ["subject_id", "patient_http", "movement_http", "questionnaire_http", "patient_id_match", "movement_id_match", "questionnaire_id_match", "condition", "filelist_condition", "filelist_label", "condition_match", "questionnaire_items", "questionnaire_missing_answers", "movement_sessions", "bilateral_task_count", "left_references", "right_references", "sampling_rate", "has_disease_comment", "has_age_at_diagnosis", "source_error", "bytes_read"]


def fetch(path):
    request = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 EXP025 source audit"})
    with urllib.request.urlopen(request, timeout=35) as response:
        body = response.read(FILE_CAP + 1)
        status = response.status
        metadata = {"content_type": response.headers.get("Content-Type"), "last_modified": response.headers.get("Last-Modified")}
    if len(body) > FILE_CAP:
        raise ValueError(f"file exceeds {FILE_CAP} bytes: {path}")
    return body, status, metadata


def one_subject(subject_id, filelist):
    row = {x: "" for x in FIELDS}
    row["subject_id"] = subject_id
    total = 0
    paths = {
        "patient": f"patients/patient_{subject_id}.json",
        "movement": f"movement/observation_{subject_id}.json",
        "questionnaire": f"questionnaire/questionnaire_response_{subject_id}.json",
    }
    parsed = {}
    meta = {}
    try:
        for kind, path in paths.items():
            blob, status, metadata = fetch(path)
            total += len(blob)
            row[f"{kind}_http"] = status
            parsed[kind] = json.loads(blob)
            meta[kind] = metadata
        patient, movement, questionnaire = parsed["patient"], parsed["movement"], parsed["questionnaire"]
        source_row = filelist[subject_id]
        row["patient_id_match"] = str(patient.get("id", "")) == subject_id
        row["movement_id_match"] = str(movement.get("subject_id", "")) == subject_id
        row["questionnaire_id_match"] = str(questionnaire.get("subject_id", "")) == subject_id
        row["condition"] = patient.get("condition", "")
        row["filelist_condition"] = source_row.get("condition", "")
        row["filelist_label"] = source_row.get("label", "")
        row["condition_match"] = row["condition"] == row["filelist_condition"]
        items = questionnaire.get("item", [])
        row["questionnaire_items"] = len(items)
        row["questionnaire_missing_answers"] = sum(x.get("answer") is None for x in items)
        sessions = movement.get("session", [])
        row["movement_sessions"] = len(sessions)
        left = right = bilateral = 0
        for session in sessions:
            records = session.get("records", [])
            left_files = [r.get("file_name", "") for r in records if r.get("device_location") == "LeftWrist"]
            right_files = [r.get("file_name", "") for r in records if r.get("device_location") == "RightWrist"]
            left += sum(x.startswith("timeseries/") for x in left_files)
            right += sum(x.startswith("timeseries/") for x in right_files)
            bilateral += bool(left_files and right_files and all(x.startswith("timeseries/") for x in left_files + right_files))
        row["bilateral_task_count"] = bilateral
        row["left_references"] = left
        row["right_references"] = right
        row["sampling_rate"] = movement.get("sampling_rate", "")
        row["has_disease_comment"] = bool(patient.get("disease_comment"))
        row["has_age_at_diagnosis"] = patient.get("age_at_diagnosis") is not None
    except Exception as exc:
        row["source_error"] = f"{type(exc).__name__}:{str(exc)[:180]}"
    row["bytes_read"] = total
    return row, meta


def main():
    if any(p.exists() for p in (AUDIT, PREFLIGHT, INDEX, DIAG)):
        raise RuntimeError("Preserve existing EXP025-COHORT-001 output")
    blob, http, filelist_meta = fetch("preprocessed/file_list.csv")
    filelist_rows = list(csv.DictReader(io.StringIO(blob.decode("utf-8-sig"))))
    filelist = {r["id"]: r for r in filelist_rows}
    if http != 200 or len(filelist_rows) != 469 or len(filelist) != 469:
        raise RuntimeError("PADS file list does not have 469 unique participants")
    label_map = defaultdict(set)
    for row in filelist_rows:
        label_map[row["condition"]].add(row["label"])
    total_bytes = len(blob)
    output = []
    sampled_meta = {}
    with AUDIT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for batch_start, batch_end in ((1, 25), (26, 469)):
            with ThreadPoolExecutor(max_workers=8) as executor:
                futures = {executor.submit(one_subject, f"{i:03d}", filelist): i for i in range(batch_start, batch_end + 1)}
                for future in as_completed(futures):
                    row, meta = future.result()
                    output.append(row)
                    writer.writerow(row)
                    f.flush()
                    total_bytes += int(row["bytes_read"])
                    if not sampled_meta and meta:
                        sampled_meta = meta
                    if len(output) % 50 == 0:
                        print("read_subjects", len(output), "bytes", total_bytes, flush=True)
            if batch_end == 25:
                first = [r for r in output if int(r["subject_id"]) <= 25]
                checked = sum(not r["source_error"] and r["patient_id_match"] is True and r["movement_id_match"] is True and r["questionnaire_id_match"] is True and r["condition_match"] is True for r in first)
                PREFLIGHT.write_text(json.dumps({"run_id": "EXP025-COHORT-001", "fixed_ids": "001-025", "checked": checked, "denominator": 25, "failed_ids": [r["subject_id"] for r in first if r["source_error"] or r["condition_match"] is not True], "label_map_from_file_list": {k: sorted(v) for k, v in label_map.items()}}, ensure_ascii=False, indent=2) + "\n")
                if checked != 25:
                    break
            if total_bytes > TOTAL_CAP:
                break
    conditions = Counter(r["condition"] for r in output if not r["source_error"])
    paired = sum(not r["source_error"] and r["questionnaire_items"] and int(r["bilateral_task_count"]) >= 8 for r in output)
    errors = [r["subject_id"] for r in output if r["source_error"]]
    diag = {
        "run_id": "EXP025-COHORT-001", "subjects_read": len(output), "source_errors": len(errors), "source_error_ids": errors,
        "condition_counts": dict(conditions), "paired_questionnaire_and_ge8_bilateral_tasks": paired,
        "questionnaire_item_counts": dict(Counter(str(r["questionnaire_items"]) for r in output)),
        "bilateral_task_counts": dict(Counter(str(r["bilateral_task_count"]) for r in output)),
        "label_map_from_file_list": {k: sorted(v) for k, v in label_map.items()},
        "total_bytes_read": total_bytes, "requests_expected": 1 + 3 * len(output),
        "note": "Original patient/observation/questionnaire JSON and filelist CSV were read in memory; only derived per-person counts and labels were stored. Timeseries files were referenced, not read.",
    }
    DIAG.write_text(json.dumps(diag, ensure_ascii=False, indent=2) + "\n")
    INDEX.write_text(json.dumps({
        "run_id": "EXP025-COHORT-001", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "official_dataset_page": "https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/",
        "base_url": BASE, "version": "1.0.0", "license_as_stated_by_official_page": "CC BY-NC-SA 4.0",
        "file_list_url": BASE + "preprocessed/file_list.csv", "file_list_http": http,
        "file_list_last_modified": filelist_meta["last_modified"], "file_list_rows": len(filelist_rows),
        "patient_url_pattern": BASE + "patients/patient_{subject_id}.json",
        "observation_url_pattern": BASE + "movement/observation_{subject_id}.json",
        "questionnaire_url_pattern": BASE + "questionnaire/questionnaire_response_{subject_id}.json",
        "example_source_metadata": sampled_meta, "original_files_saved": False,
        "budget_bytes": TOTAL_CAP, "actual_bytes_read": total_bytes,
    }, ensure_ascii=False, indent=2) + "\n")
    print("DONE", {"subjects": len(output), "errors": len(errors), "conditions": dict(conditions), "paired": paired, "bytes": total_bytes})


if __name__ == "__main__":
    main()
