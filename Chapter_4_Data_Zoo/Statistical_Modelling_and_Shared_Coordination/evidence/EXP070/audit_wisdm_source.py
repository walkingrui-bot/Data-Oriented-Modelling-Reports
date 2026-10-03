"""EXP070 official WISDM raw phone acc/gyro source audit; no raw copy saved."""

from __future__ import annotations

import io
import json
import math
import re
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdataset.zip"
MAX_BYTES = 330 * 1024 * 1024
CODES = {"A": "Walking", "D": "Sitting", "E": "Standing"}


def get_archive() -> tuple[zipfile.ZipFile, int, int]:
    request = urllib.request.Request(URL, headers={"User-Agent": "StatPsyMoE-EXP070-source-audit/1.0"})
    with urllib.request.urlopen(request, timeout=180) as response:
        length = response.headers.get("Content-Length")
        if length is not None and int(length) > MAX_BYTES:
            raise ValueError(f"source exceeds {MAX_BYTES} byte network cap")
        data = response.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError(f"source exceeds {MAX_BYTES} byte network cap")
    outer = zipfile.ZipFile(io.BytesIO(data))
    if any("raw/phone/accel/" in name.lower() for name in outer.namelist()):
        return outer, len(data), 0
    inner_names = [name for name in outer.namelist() if name.lower().endswith("wisdm-dataset.zip")]
    if len(inner_names) != 1:
        raise ValueError(f"expected one wisdm-dataset.zip inner member, got {inner_names[:5]}")
    info = outer.getinfo(inner_names[0])
    if info.file_size > MAX_BYTES:
        raise ValueError("inner archive exceeds bounded memory")
    inner_data = outer.read(inner_names[0])
    return zipfile.ZipFile(io.BytesIO(inner_data)), len(data), len(inner_data)


def find_member(zf: zipfile.ZipFile, suffix: str) -> str | None:
    matches = [name for name in zf.namelist() if name.lower().endswith(suffix.lower())
               and not name.startswith("__MACOSX/")]
    if len(matches) > 1:
        raise ValueError(f"ambiguous archive member {suffix}: {matches[:5]}")
    return matches[0] if matches else None


def parse_activity_key(zf: zipfile.ZipFile) -> tuple[str, dict[str, str]]:
    name = find_member(zf, "activity_key.txt")
    if name is None:
        raise ValueError("official activity_key.txt absent")
    text = zf.read(name).decode("utf-8", errors="replace")
    mapping = {}
    for line in text.splitlines():
        m = re.match(r"^\s*([A-S])\s*[,;:=\t-]\s*(.+?)\s*$", line, flags=re.I)
        if m:
            mapping[m.group(1).upper()] = m.group(2).strip()
            continue
        m = re.match(r"^\s*([A-S])\s+(.+?)\s*$", line, flags=re.I)
        if m:
            mapping[m.group(1).upper()] = m.group(2).strip()
    # The official key may put the activity name before its single-letter code.
    # This fallback only accepts exact frozen names and a standalone code on one line.
    for line in text.splitlines():
        for code, name in CODES.items():
            if (re.search(rf"(?<![A-Za-z]){code}(?![A-Za-z])", line, flags=re.I)
                    and re.search(rf"(?<![A-Za-z]){re.escape(name)}(?![A-Za-z])", line, flags=re.I)):
                mapping[code] = name
    return name, mapping


def scan_file(zf: zipfile.ZipFile, name: str | None, subject: int) -> dict:
    result = {code: {"valid_rows": 0, "invalid_rows": 0, "wrong_subject_rows": 0,
                     "min_timestamp": None, "max_timestamp": None,
                     "nondecreasing_steps": 0, "compared_steps": 0} for code in CODES}
    if name is None:
        return {"member": None, "by_activity": result, "file_missing": True}
    last_timestamp = {code: None for code in CODES}
    with zf.open(name) as stream:
        for raw in stream:
            line = raw.strip().rstrip(b";")
            if not line:
                continue
            fields = line.split(b",")
            if len(fields) < 2:
                continue
            code = fields[1].decode("ascii", errors="replace").strip()
            if code not in CODES:
                continue
            item = result[code]
            if len(fields) != 6:
                item["invalid_rows"] += 1
                continue
            try:
                observed_subject = int(fields[0])
                timestamp = int(fields[2])
                values = [float(field) for field in fields[3:]]
            except ValueError:
                item["invalid_rows"] += 1
                continue
            if observed_subject != subject:
                item["wrong_subject_rows"] += 1
                continue
            if not all(math.isfinite(value) for value in values):
                item["invalid_rows"] += 1
                continue
            item["valid_rows"] += 1
            lo, hi = item["min_timestamp"], item["max_timestamp"]
            item["min_timestamp"] = timestamp if lo is None else min(lo, timestamp)
            item["max_timestamp"] = timestamp if hi is None else max(hi, timestamp)
            prev = last_timestamp[code]
            if prev is not None:
                item["compared_steps"] += 1
                item["nondecreasing_steps"] += int(timestamp >= prev)
            last_timestamp[code] = timestamp
    return {"member": name, "by_activity": result, "file_missing": False}


def overlap(a: dict, g: dict) -> float | None:
    alo, ahi = a["min_timestamp"], a["max_timestamp"]
    glo, ghi = g["min_timestamp"], g["max_timestamp"]
    if None in (alo, ahi, glo, ghi) or ahi <= alo or ghi <= glo:
        return None
    return max(0, min(ahi, ghi) - max(alo, glo)) / min(ahi - alo, ghi - glo)


def main() -> None:
    zf, download_bytes, inner_bytes = get_archive()
    activity_key_member, mapping = parse_activity_key(zf)
    mapping_matches = all(mapping.get(code, "").strip().lower() == name.lower()
                          for code, name in CODES.items())
    result = {"research_id": "STAT-PSYMOE-EXP070-20261002-001",
              "attempt_id": "EXP070-SOURCE-001", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "official_url": URL, "official_dataset_page": "https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata",
              "citation": "Weiss, G. (2019). WISDM Smartphone and Smartwatch Activity and Biometrics Dataset. UCI. doi:10.24432/C5HK59; CC BY 4.0.",
              "download_bytes": download_bytes, "inner_zip_bytes": inner_bytes,
              "activity_key_member": activity_key_member,
              "selected_activity_mapping": {code: mapping.get(code) for code in CODES},
              "mapping_matches_frozen": mapping_matches,
              "candidate_subjects": list(range(1600, 1651)),
              "qualified_subjects": [], "subjects": {},
              "model_fits": 0}
    if not mapping_matches:
        result["gate_result"] = "STOP_WISDM_PAIRED_PERSON_SUPPORT"
        (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"mapping": result["selected_activity_mapping"], "gate_result": result["gate_result"]}))
        return
    for subject in range(1600, 1651):
        accel_name = find_member(zf, f"raw/phone/accel/data_{subject}_accel_phone.txt")
        gyro_name = find_member(zf, f"raw/phone/gyro/data_{subject}_gyro_phone.txt")
        accel = scan_file(zf, accel_name, subject)
        gyro = scan_file(zf, gyro_name, subject)
        activities = {}
        qualified = True
        for code in CODES:
            a, g = accel["by_activity"][code], gyro["by_activity"][code]
            ratio = overlap(a, g)
            enough = (a["valid_rows"] >= 1000 and g["valid_rows"] >= 1000
                      and a["wrong_subject_rows"] == 0 and g["wrong_subject_rows"] == 0
                      and ratio is not None and ratio >= 0.5)
            qualified &= enough
            activities[code] = {"accel": a, "gyro": g, "span_overlap_ratio": ratio,
                                "qualified": enough}
        result["subjects"][str(subject)] = {"accel_member": accel_name, "gyro_member": gyro_name,
                                             "activities": activities, "qualified": qualified}
        if qualified:
            result["qualified_subjects"].append(subject)
    result["qualified_count"] = len(result["qualified_subjects"])
    result["gate_result"] = ("WISDM_THREE_ACTIVITY_PAIRED_SOURCE_READY_FOR_DESIGN"
                             if mapping_matches and result["qualified_count"] >= 40
                             else "STOP_WISDM_PAIRED_PERSON_SUPPORT")
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"download_bytes": download_bytes, "inner_zip_bytes": inner_bytes,
                      "activity_mapping": result["selected_activity_mapping"],
                      "qualified_count": result["qualified_count"],
                      "qualified_subjects": result["qualified_subjects"],
                      "gate_result": result["gate_result"]}, indent=2))


if __name__ == "__main__":
    main()
