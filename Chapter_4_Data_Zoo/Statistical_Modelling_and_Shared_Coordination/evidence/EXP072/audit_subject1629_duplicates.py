"""EXP072 read-only value semantics of repeated timestamps for WISDM subject 1629."""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXP070 = HERE.parent / "STAT-PSYMOE-EXP070-20261002-001"
EXP071 = HERE.parent / "STAT-PSYMOE-EXP071-20261002-001"
sys.path.insert(0, str(EXP070))
from audit_wisdm_source import find_member, get_archive  # noqa: E402


def inspect_member(zf, sensor: str) -> dict:
    name = find_member(zf, f"raw/phone/{sensor}/data_1629_{sensor}_phone.txt")
    if name is None:
        raise ValueError(f"missing original member for {sensor}")
    state = {code: {"rows": 0, "inversions": 0, "timestamp_counts": {},
                    "first_values": {}, "conflict_keys": set(),
                    "conflicting_extra_rows": 0, "max_axis_difference": 0.0,
                    "last_timestamp": None} for code in "ADE"}
    with zf.open(name) as stream:
        for line in stream:
            parts = line.strip().rstrip(b";").split(b",")
            if len(parts) < 2:
                continue
            code = parts[1].decode("ascii", errors="replace").strip()
            if code not in state:
                continue
            if len(parts) != 6:
                raise ValueError("malformed selected source row")
            try:
                subject = int(parts[0])
                timestamp = int(parts[2])
                xyz = tuple(float(value) for value in parts[3:])
            except ValueError as exc:
                raise ValueError("unparseable selected source row") from exc
            if subject != 1629 or not all(math.isfinite(value) for value in xyz):
                raise ValueError("wrong subject or nonfinite selected source row")
            group = state[code]
            group["rows"] += 1
            last = group["last_timestamp"]
            if last is not None and timestamp < last:
                group["inversions"] += 1
            group["last_timestamp"] = timestamp
            counts = group["timestamp_counts"]
            counts[timestamp] = counts.get(timestamp, 0) + 1
            if timestamp not in group["first_values"]:
                group["first_values"][timestamp] = xyz
            else:
                reference = group["first_values"][timestamp]
                differences = [abs(xyz[i] - reference[i]) for i in range(3)]
                maximum = max(differences)
                group["max_axis_difference"] = max(group["max_axis_difference"], maximum)
                if maximum != 0:
                    group["conflict_keys"].add(timestamp)
                    group["conflicting_extra_rows"] += 1
    summary = {}
    for code, group in state.items():
        counts = group["timestamp_counts"]
        duplicate_keys = sum(n > 1 for n in counts.values())
        extra = sum(n - 1 for n in counts.values())
        summary[code] = {
            "member": name,
            "valid_rows": group["rows"],
            "unique_timestamps": len(counts),
            "duplicate_timestamp_keys": duplicate_keys,
            "duplicate_extra_rows": extra,
            "max_multiplicity": max(counts.values()) if counts else 0,
            "original_inversions": group["inversions"],
            "conflicting_timestamp_keys": len(group["conflict_keys"]),
            "conflicting_extra_rows": group["conflicting_extra_rows"],
            "identical_extra_rows": extra - group["conflicting_extra_rows"],
            "max_absolute_axis_difference": group["max_axis_difference"],
        }
    return summary


def main() -> None:
    exp070 = json.loads((EXP070 / "SOURCE_MATRIX.json").read_text(encoding="utf-8"))
    exp071 = json.loads((EXP071 / "WINDOW_COUNTS.json").read_text(encoding="utf-8"))
    zf, download_bytes, inner_bytes = get_archive()
    summaries = {sensor: inspect_member(zf, sensor) for sensor in ("accel", "gyro")}
    checks = {}
    for sensor in ("accel", "gyro"):
        for code in "ADE":
            actual = summaries[sensor][code]
            earlier_source = exp070["subjects"]["1629"]["activities"][code][sensor]
            earlier_order = exp071["subjects"]["1629"]["activities"][code][f"{sensor}_order"]
            checks[f"{sensor}_{code}"] = (
                actual["valid_rows"] == earlier_source["valid_rows"]
                and actual["duplicate_extra_rows"] == earlier_order["duplicate_timestamps_collapsed"]
                and actual["original_inversions"] == earlier_order["original_inversions"] == 1
            )
    total_extra = sum(summaries[sensor][code]["duplicate_extra_rows"]
                      for sensor in ("accel", "gyro") for code in "ADE")
    checks["total_duplicate_extra_rows_21424"] = total_extra == 21424
    total_conflict_keys = sum(summaries[sensor][code]["conflicting_timestamp_keys"]
                              for sensor in ("accel", "gyro") for code in "ADE")
    if not all(checks.values()):
        decision = "STOP_SOURCE_VERSION_OR_ANOMALY_MISMATCH"
    elif total_conflict_keys == 0:
        decision = "IDENTICAL_DUPLICATE_ROWS_NO_MEAN_CHANGE"
    else:
        decision = "CONFLICTING_DUPLICATE_TIMESTAMPS_UNRESOLVED"
    result = {"research_id": "STAT-PSYMOE-EXP072-20261002-001",
              "attempt_id": "EXP072-ANOMALY-001", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "official_url": "https://archive.ics.uci.edu/static/public/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdataset.zip",
              "download_bytes": download_bytes, "inner_zip_bytes": inner_bytes,
              "subject": 1629, "groups": summaries, "version_checks": checks,
              "total_duplicate_extra_rows": total_extra,
              "total_conflicting_timestamp_keys": total_conflict_keys,
              "decision": decision, "model_fits": 0, "performance_scores": 0}
    (HERE / "ANOMALY_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"download_bytes": download_bytes, "version_checks_pass": all(checks.values()),
                      "total_duplicate_extra_rows": total_extra,
                      "total_conflicting_timestamp_keys": total_conflict_keys,
                      "groups": {f"{sensor}_{code}": summaries[sensor][code] for sensor in ("accel", "gyro") for code in "ADE"},
                      "decision": decision}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
