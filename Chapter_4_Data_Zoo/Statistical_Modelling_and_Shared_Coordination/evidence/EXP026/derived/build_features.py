"""EXP026-SOURCE-001: stream official PADS responses; save only one derived feature table."""

import csv
import io
import json
import math
import threading
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://physionet.org/files/parkinsons-disease-smartwatch/1.0.0/"
SPLIT = ROOT / "SPLIT_MANIFEST.csv"
FEATURES = ROOT / "FEATURES.csv"
AUDIT = ROOT / "SOURCE_AUDIT.csv"
SUMMARY = ROOT / "SOURCE_SUMMARY.json"
FILE_CAP = 500_000
BYTE_CAP = 250 * 1024 * 1024
REQUEST_CAP = 2000
Q_NAMES = [f"q{i:02d}" for i in range(1, 31)]
ONE_WRIST = [f"{sensor}_{stat}" for sensor in ("acc", "gyro") for stat in ("mean", "std", "p95p05", "jerk_rms", "band3to7_ratio")]
MOTION_NAMES = [f"{wrist}_{name}" for wrist in ("left", "right") for name in ONE_WRIST] + [f"absdiff_{name}" for name in ONE_WRIST]
CHANNELS = ["Time", "Accelerometer_X", "Accelerometer_Y", "Accelerometer_Z", "Gyroscope_X", "Gyroscope_Y", "Gyroscope_Z"]
lock = threading.Lock()
requests = 0
bytes_read = 0


def fetch(path):
    global requests, bytes_read
    errors = []
    for attempt in (1, 2):
        with lock:
            if requests >= REQUEST_CAP:
                raise RuntimeError("REQUEST_BUDGET_EXCEEDED")
            requests += 1
        try:
            req = urllib.request.Request(BASE + path, headers={"User-Agent": "Mozilla/5.0 EXP026 person-level research"})
            with urllib.request.urlopen(req, timeout=35) as response:
                blob = response.read(FILE_CAP + 1)
                status = response.status
            if len(blob) > FILE_CAP:
                raise ValueError("SOURCE_FILE_OVER_500KB")
            with lock:
                bytes_read += len(blob)
                if bytes_read > BYTE_CAP:
                    raise RuntimeError("BYTE_BUDGET_EXCEEDED")
            if status != 200:
                raise RuntimeError(f"HTTP_{status}")
            return blob, attempt, errors
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:100]}")
            if "BUDGET_EXCEEDED" in str(exc) or attempt == 2:
                raise RuntimeError(";".join(errors)) from exc
    raise AssertionError("unreachable")


def wrist_features(body, expected_rows, sampling_rate):
    arr = np.loadtxt(io.BytesIO(body), delimiter=",", dtype=np.float64)
    if arr.ndim != 2 or arr.shape != (expected_rows, 7) or not np.isfinite(arr).all():
        raise ValueError(f"SCHEMA_ERROR:array_shape_or_numeric:{arr.shape}")
    if not np.all(np.diff(arr[:, 0]) > 0):
        raise ValueError("SCHEMA_ERROR:time_not_increasing")
    out = {}
    hz = np.fft.rfftfreq(len(arr), 1.0 / sampling_rate)
    denom_mask = (hz >= 0.5) & (hz <= 15.0)
    tremor_mask = (hz >= 3.0) & (hz <= 7.0)
    for sensor, cols in (("acc", (1, 2, 3)), ("gyro", (4, 5, 6))):
        xyz = arr[:, cols]
        magnitude = np.linalg.norm(xyz, axis=1)
        centered = xyz - xyz.mean(axis=0)
        power = np.abs(np.fft.rfft(centered, axis=0)) ** 2
        denom = power[denom_mask].sum(axis=0)
        ratio = np.divide(power[tremor_mask].sum(axis=0), denom, out=np.zeros_like(denom), where=denom > 0)
        vals = [magnitude.mean(), magnitude.std(), np.quantile(magnitude, .95)-np.quantile(magnitude, .05), np.sqrt(np.mean(np.diff(magnitude)**2)), ratio.mean()]
        for stat, value in zip(("mean", "std", "p95p05", "jerk_rms", "band3to7_ratio"), vals):
            out[f"{sensor}_{stat}"] = float(value)
    if set(out) != set(ONE_WRIST) or not all(math.isfinite(v) for v in out.values()):
        raise ValueError("SCHEMA_ERROR:feature_nonfinite")
    return out


def one_person(row):
    subject_id = row["subject_id"]
    feature = {"subject_id": subject_id, "label": row["label"], "split": row["split"]}
    feature.update({name: "" for name in Q_NAMES + MOTION_NAMES})
    audit = {"subject_id": subject_id, "questionnaire_status": "", "observation_status": "", "left_status": "", "right_status": "", "questionnaire_missing": "", "left_rows": "", "right_rows": "", "retried_requests": 0, "retry_errors": "", "source_error": ""}
    try:
        body, attempts, errors = fetch(f"questionnaire/questionnaire_response_{subject_id}.json")
        audit["retried_requests"] += attempts - 1
        audit["retry_errors"] += "|".join(errors)
        q = json.loads(body)
        if str(q.get("subject_id")) != subject_id:
            raise ValueError("SCHEMA_ERROR:questionnaire_id")
        items = q.get("item", [])
        answers = {str(item.get("link_id")): item.get("answer") for item in items}
        if len(items) != 30 or set(answers) != {f"{i:02d}" for i in range(1, 31)}:
            raise ValueError("SCHEMA_ERROR:questionnaire_keys")
        for name in Q_NAMES:
            ans = answers[name[1:]]
            if ans is not None and not isinstance(ans, bool):
                raise ValueError("SCHEMA_ERROR:questionnaire_answer_type")
            feature[name] = "" if ans is None else int(ans)
        audit["questionnaire_missing"] = sum(feature[name] == "" for name in Q_NAMES)
        audit["questionnaire_status"] = "OK"
    except Exception as exc:
        audit["questionnaire_status"] = "FAIL"
        audit["source_error"] += f"QUESTIONNAIRE:{type(exc).__name__}:{str(exc)[:130]}|"
    try:
        body, attempts, errors = fetch(f"movement/observation_{subject_id}.json")
        audit["retried_requests"] += attempts - 1
        audit["retry_errors"] += "|".join(errors)
        observation = json.loads(body)
        if str(observation.get("subject_id")) != subject_id or observation.get("sampling_rate") != 100:
            raise ValueError("SCHEMA_ERROR:observation_identity_or_rate")
        sessions = [s for s in observation.get("session", []) if s.get("record_name") == "Relaxed"]
        if len(sessions) != 1:
            raise ValueError("SCHEMA_ERROR:relaxed_session_count")
        session = sessions[0]
        n = session.get("rows")
        if not isinstance(n, int) or n < 1000 or n > 4096:
            raise ValueError("SCHEMA_ERROR:row_count")
        records = {r.get("device_location"): r for r in session.get("records", [])}
        if set(records) != {"LeftWrist", "RightWrist"}:
            raise ValueError("SCHEMA_ERROR:bilateral_records")
        for wrist in ("Left", "Right"):
            rec = records[wrist + "Wrist"]
            path = f"timeseries/{subject_id}_Relaxed_{wrist}Wrist.txt"
            if rec.get("file_name") != path or rec.get("channels") != CHANNELS:
                raise ValueError("SCHEMA_ERROR:time_series_reference_or_channels")
        audit["observation_status"] = "OK"
    except Exception as exc:
        audit["observation_status"] = "FAIL"
        audit["source_error"] += f"OBSERVATION:{type(exc).__name__}:{str(exc)[:130]}|"
        return feature, audit
    wrists = {}
    for wrist in ("Left", "Right"):
        field = wrist.lower() + "_status"
        try:
            path = f"movement/timeseries/{subject_id}_Relaxed_{wrist}Wrist.txt"
            body, attempts, errors = fetch(path)
            audit["retried_requests"] += attempts - 1
            audit["retry_errors"] += "|".join(errors)
            wrists[wrist.lower()] = wrist_features(body, n, 100)
            audit[field] = "OK"
            audit[wrist.lower() + "_rows"] = n
        except Exception as exc:
            audit[field] = "FAIL"
            audit["source_error"] += f"{wrist.upper()}:{type(exc).__name__}:{str(exc)[:130]}|"
    for wrist in ("left", "right"):
        if wrist in wrists:
            feature.update({f"{wrist}_{name}": value for name, value in wrists[wrist].items()})
    if len(wrists) == 2:
        feature.update({f"absdiff_{name}": abs(wrists["left"][name]-wrists["right"][name]) for name in ONE_WRIST})
    return feature, audit


def main():
    if any(p.exists() for p in (FEATURES, AUDIT, SUMMARY)):
        raise FileExistsError("EXP026-SOURCE-001 outputs already exist; preserve run")
    with SPLIT.open(newline="") as f:
        people = list(csv.DictReader(f))
    if len(people) != 469 or len({r["subject_id"] for r in people}) != 469:
        raise ValueError("Split manifest is not 469 unique persons")
    feature_fields = ["subject_id", "label", "split"] + Q_NAMES + MOTION_NAMES
    audit_fields = ["subject_id", "questionnaire_status", "observation_status", "left_status", "right_status", "questionnaire_missing", "left_rows", "right_rows", "retried_requests", "retry_errors", "source_error"]
    audits = []
    with FEATURES.open("w", newline="") as f_feat, AUDIT.open("w", newline="") as f_audit:
        fw = csv.DictWriter(f_feat, fieldnames=feature_fields)
        aw = csv.DictWriter(f_audit, fieldnames=audit_fields)
        fw.writeheader(); aw.writeheader()
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures = [pool.submit(one_person, row) for row in people]
            for future in as_completed(futures):
                feature, audit = future.result()
                fw.writerow(feature); aw.writerow(audit)
                f_feat.flush(); f_audit.flush()
                audits.append(audit)
                if len(audits) % 50 == 0:
                    print("persons", len(audits), "requests", requests, "bytes", bytes_read, flush=True)
    ok = Counter()
    for a in audits:
        for key in ("questionnaire_status", "observation_status", "left_status", "right_status"):
            if a[key] == "OK": ok[key] += 1
    missing_people = [a["subject_id"] for a in audits if a["left_status"] != "OK" or a["right_status"] != "OK"]
    schema_errors = [a["subject_id"] for a in audits if "SCHEMA_ERROR" in a["source_error"]]
    by_label = Counter()
    labels = {r["subject_id"]: r["label"] for r in people}
    for sid in missing_people: by_label[labels[sid]] += 1
    source_gate = len(missing_people) <= int(.05 * 469) and all(by_label[str(label)] <= int(.10 * n) for label, n in ((0,79),(1,276),(2,114))) and not schema_errors and requests <= REQUEST_CAP and bytes_read <= BYTE_CAP
    summary = {"run_id": "EXP026-SOURCE-001", "subjects": len(audits), "requests": requests, "bytes_read": bytes_read, "expected_requests_without_retry": 4*469, "ok": dict(ok), "missing_bilateral_persons": len(missing_people), "missing_bilateral_ids": missing_people, "missing_bilateral_by_label": dict(by_label), "schema_error_ids": schema_errors, "retried_requests": sum(int(a["retried_requests"]) for a in audits), "source_gate": "PASS" if source_gate else "STOP_SOURCE", "original_responses_saved": False, "feature_columns": feature_fields}
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("feature_columns", "missing_bilateral_ids", "schema_error_ids")}, indent=2), flush=True)
    if not source_gate:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
