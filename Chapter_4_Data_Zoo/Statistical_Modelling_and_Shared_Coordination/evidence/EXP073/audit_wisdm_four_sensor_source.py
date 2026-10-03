"""EXP073 source-only audit of WISDM 18 activities across four actual sensors."""

from __future__ import annotations

import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXP070 = HERE.parent / "STAT-PSYMOE-EXP070-20261002-001"
sys.path.insert(0, str(EXP070))
from audit_wisdm_source import find_member, get_archive  # noqa: E402

CODES = "ABCDEFGHIJKLMOPQRS"
TOKENS = {
    "A": ("walking",), "B": ("jogging",), "C": ("stairs",),
    "D": ("sitting",), "E": ("standing",), "F": ("typing",),
    "G": ("teeth",), "H": ("soup",),
    "I": ("chips",), "J": ("pasta",),
    "K": ("drinking",), "L": ("sandwich",),
    "M": ("kicking",), "O": ("catch",),
    "P": ("dribbling",), "Q": ("writing",),
    "R": ("clapping",), "S": ("folding",),
}
SENSORS = (("phone", "accel"), ("phone", "gyro"),
           ("watch", "accel"), ("watch", "gyro"))


def activity_mapping(zf) -> tuple[str, dict[str, str]]:
    name = find_member(zf, "activity_key.txt")
    if name is None:
        raise ValueError("official activity_key.txt absent")
    text = zf.read(name).decode("utf-8", errors="replace")
    mapping = {}
    for line in text.splitlines():
        lower = re.sub(r"[^a-z0-9]+", " ", line.lower())
        for code, tokens in TOKENS.items():
            if (re.search(rf"(?<![A-Za-z]){code}(?![A-Za-z])", line, flags=re.I)
                    and all(token in lower for token in tokens)):
                mapping[code] = line.strip()
    return name, mapping


def scan(zf, subject: int, device: str, sensor: str) -> dict:
    name = find_member(zf, f"raw/{device}/{sensor}/data_{subject}_{sensor}_{device}.txt")
    by_code = {code: {"valid_rows": 0, "invalid_rows": 0, "wrong_subject_rows": 0,
                      "min_timestamp": None, "max_timestamp": None,
                      "order_inversions": 0, "last_timestamp": None} for code in CODES}
    if name is None:
        return {"member": None, "missing_file": True, "by_activity": by_code}
    with zf.open(name) as stream:
        for raw in stream:
            parts = raw.strip().rstrip(b";").split(b",")
            if len(parts) < 2:
                continue
            code = parts[1].decode("ascii", errors="replace").strip()
            if code not in by_code:
                continue
            item = by_code[code]
            if len(parts) != 6:
                item["invalid_rows"] += 1
                continue
            try:
                actual_subject = int(parts[0])
                timestamp = int(parts[2])
                xyz = [float(v) for v in parts[3:]]
            except ValueError:
                item["invalid_rows"] += 1
                continue
            if actual_subject != subject:
                item["wrong_subject_rows"] += 1
                continue
            if not all(math.isfinite(v) for v in xyz):
                item["invalid_rows"] += 1
                continue
            item["valid_rows"] += 1
            lo, hi = item["min_timestamp"], item["max_timestamp"]
            item["min_timestamp"] = timestamp if lo is None else min(lo, timestamp)
            item["max_timestamp"] = timestamp if hi is None else max(hi, timestamp)
            if item["last_timestamp"] is not None and timestamp < item["last_timestamp"]:
                item["order_inversions"] += 1
            item["last_timestamp"] = timestamp
    for item in by_code.values():
        item.pop("last_timestamp")
    return {"member": name, "missing_file": False, "by_activity": by_code}


def overlap(groups: list[dict]) -> float | None:
    limits = [(g["min_timestamp"], g["max_timestamp"]) for g in groups]
    if any(lo is None or hi is None or hi <= lo for lo, hi in limits):
        return None
    intersection = max(0, min(hi for _, hi in limits) - max(lo for lo, _ in limits))
    return intersection / min(hi - lo for lo, hi in limits)


def main() -> None:
    zf, downloaded, inner_bytes = get_archive()
    key_member, mapped = activity_mapping(zf)
    key_matches = len(mapped) == 18 and set(mapped) == set(CODES)
    result = {"research_id": "STAT-PSYMOE-EXP073-20261002-001",
              "attempt_id": "EXP073-SOURCE-001", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "official_url": "https://archive.ics.uci.edu/static/public/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdataset.zip",
              "citation": "Weiss, G. (2019). WISDM Smartphone and Smartwatch Activity and Biometrics Dataset. UCI. doi:10.24432/C5HK59; CC BY 4.0.",
              "download_bytes": downloaded, "inner_zip_bytes": inner_bytes,
              "activity_key_member": key_member, "activity_codes_verified": sorted(mapped),
              "activity_key_matches_18": key_matches,
              "subjects": {}, "qualified_subjects": [], "model_fits": 0}
    if not key_matches:
        result["decision"] = "STOP_FOUR_SENSOR_18_CLASS_SUPPORT"
        (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps({"activity_codes_verified": result["activity_codes_verified"],
                          "decision": result["decision"]}))
        return
    for subject in range(1600, 1651):
        files = {f"{device}_{sensor}": scan(zf, subject, device, sensor)
                 for device, sensor in SENSORS}
        activities = {}
        all_qualified = True
        for code in CODES:
            groups = {name: files[name]["by_activity"][code] for name in files}
            ratio = overlap(list(groups.values()))
            okay = (ratio is not None and ratio >= 0.5
                    and all(g["valid_rows"] >= 500 and g["invalid_rows"] == 0
                            and g["wrong_subject_rows"] == 0 for g in groups.values()))
            all_qualified &= okay
            activities[code] = {"sensors": groups, "four_span_overlap_ratio": ratio,
                                "qualified": okay}
        result["subjects"][str(subject)] = {"members": {k: v["member"] for k, v in files.items()},
                                             "activities": activities,
                                             "all_18_qualified": all_qualified}
        if all_qualified:
            result["qualified_subjects"].append(subject)
    result["qualified_count"] = len(result["qualified_subjects"])
    result["decision"] = ("WISDM_18_ACTIVITY_FOUR_SENSOR_SOURCE_READY"
                          if result["qualified_count"] >= 40 else "STOP_FOUR_SENSOR_18_CLASS_SUPPORT")
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    min_rows = min(g["valid_rows"] for person in result["subjects"].values()
                   for act in person["activities"].values() for g in act["sensors"].values())
    ratios = [a["four_span_overlap_ratio"] for p in result["subjects"].values()
              for a in p["activities"].values() if a["four_span_overlap_ratio"] is not None]
    print(json.dumps({"download_bytes": downloaded, "activity_key_matches_18": key_matches,
                      "qualified_count": result["qualified_count"],
                      "qualified_subjects": result["qualified_subjects"],
                      "min_valid_rows_any_group": min_rows,
                      "min_four_span_overlap_ratio": min(ratios) if ratios else None,
                      "decision": result["decision"]}, indent=2))


if __name__ == "__main__":
    main()
