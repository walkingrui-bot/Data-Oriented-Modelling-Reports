"""EXP084: trial-level audit of original UCI309 wind-tunnel source in memory."""

from __future__ import annotations

import io
import json
import math
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/309/gas%2Bsensor%2Barray%2Bexposed%2Bto%2Bturbulent%2Bgas%2Bmixtures.zip"
NAME = re.compile(r"^(\d{3})_Et_([nLMH])_(Me|CO)_([nLMH])(?:\.txt)?$", re.IGNORECASE)
SPLIT = re.compile(r"[\s,;]+")


def parse_path(path: str) -> tuple | None:
    hit = NAME.fullmatch(Path(path).name)
    if not hit:
        return None
    trial_id, et, gas, level = hit.groups()
    return int(trial_id), et.upper(), gas.upper(), level.upper()


def audit_member(archive: zipfile.ZipFile, name: str) -> dict:
    text = archive.read(name).decode("utf-8-sig", errors="replace")
    total_nonempty = valid = invalid = 0
    sensor_finite = sensor_cells = 0
    baseline = exposure = 0
    first = last = None
    monotonic = True
    equal_time_steps = backwards_time_steps = 0
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "%")):
            continue
        total_nonempty += 1
        tokens = [token for token in SPLIT.split(line) if token]
        if len(tokens) != 11:
            invalid += 1
            continue
        try:
            values = [float(token) for token in tokens]
        except ValueError:
            invalid += 1
            continue
        sensor_cells += 8
        sensor_finite += sum(math.isfinite(v) for v in values[3:])
        if not all(math.isfinite(value) for value in values):
            invalid += 1
            continue
        stamp = values[0]
        if first is None:
            first = stamp
        if last is not None and stamp == last:
            equal_time_steps += 1
        if last is not None and stamp < last:
            monotonic = False
            backwards_time_steps += 1
        last = stamp
        valid += 1
        baseline += int(0 <= stamp < 60)
        exposure += int(60 <= stamp < 240)
    return {"path": name, "nonempty_rows": total_nonempty, "valid_numeric_rows": valid,
            "invalid_rows": invalid, "first_time_s": first, "last_time_s": last,
            "time_span_s": last - first if first is not None else None,
            "nondecreasing_time": monotonic,
            "equal_time_steps": equal_time_steps, "backwards_time_steps": backwards_time_steps,
            "baseline_valid_rows_0_60s": baseline, "exposure_valid_rows_60_240s": exposure,
            "eight_sensor_finite_fraction": sensor_finite / sensor_cells if sensor_cells else 0.0}


def write(obj: dict) -> None:
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def main() -> None:
    with urllib.request.urlopen(URL, timeout=90) as response:
        blob = response.read(30_000_001)
    if len(blob) > 30_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(blob)) as archive:
        files = [name for name in archive.namelist() if not name.endswith("/")]
        raw = [name for name in files if "raw" in name.split("/")[0].lower()]
        down = [name for name in files if "raw" not in name.split("/")[0].lower()]
        parsed_raw = {name: parse_path(name) for name in raw}
        parsed_down = {name: parse_path(name) for name in down}
        raw_ids = {parts[0] for parts in parsed_raw.values() if parts}
        down_ids = {parts[0] for parts in parsed_down.values() if parts}
        trial_rows = []
        for name in down:
            parts = parsed_down[name]
            if parts is None:
                continue
            trial_id, et, gas, level = parts
            row = audit_member(archive, name)
            row.update({"trial_id": trial_id, "ethylene_level": et,
                        "second_gas_identity": gas, "second_gas_level": level,
                        "nonzero_second_gas": level != "N",
                        "configuration": f"Et_{et}_{gas}_{level}"})
            trial_rows.append(row)
    configs = Counter(row["configuration"] for row in trial_rows)
    nonzero = [row for row in trial_rows if row["nonzero_second_gas"]]
    nonzero_configs = Counter(row["configuration"] for row in nonzero)
    identities = Counter(row["second_gas_identity"] for row in nonzero)
    tests = {
        "exactly_180_raw_named_trials": len(raw) == 180 and len(raw_ids) == 180 and all(parsed_raw.values()),
        "exactly_180_downsampled_named_trials": len(down) == 180 and len(down_ids) == 180 and all(parsed_down.values()),
        "same_trial_ids_raw_downsampled": raw_ids == down_ids,
        "exactly_30_configs_each_6_repeats": len(configs) == 30 and all(n == 6 for n in configs.values()),
        "at_least_20_nonzero_configs_5_repeats_each": len(nonzero_configs) >= 20 and all(n >= 5 for n in nonzero_configs.values()),
        "at_least_50_nonzero_trials_each_identity": identities.get("CO", 0) >= 50 and identities.get("ME", 0) >= 50,
        "all_trials_time_and_numeric_support": len(trial_rows) == 180 and all(
            row["nondecreasing_time"] and row["time_span_s"] is not None and row["time_span_s"] >= 290
            and row["baseline_valid_rows_0_60s"] >= 450 and row["exposure_valid_rows_60_240s"] >= 1500
            and row["eight_sensor_finite_fraction"] >= .95 for row in trial_rows),
    }
    result = {"research_id": "STAT-PSYMOE-EXP084-20261002-001",
              "attempt_id": "EXP084-SOURCE-002", "official_page": "https://archive.ics.uci.edu/dataset/309/gas%2Bsensor%2Barray%2Bexposed%2Bto%2Bturbulent%2Bgas%2Bmixtures.",
              "official_zip_url": URL, "download_bytes": len(blob), "archive_file_count": len(files),
              "archive_parent_directories": sorted(set(name.split("/")[0] for name in files)),
              "raw_file_count": len(raw), "downsampled_file_count": len(down),
              "parsed_trial_count": len(trial_rows), "unique_trial_ids": len(down_ids),
              "all_configurations_counts": dict(sorted(configs.items())),
              "nonzero_second_gas_configuration_counts": dict(sorted(nonzero_configs.items())),
              "nonzero_second_gas_trial_counts": dict(identities),
              "trial_numeric_summary": {
                  "total_nonempty_rows": sum(row["nonempty_rows"] for row in trial_rows),
                  "total_invalid_rows": sum(row["invalid_rows"] for row in trial_rows),
                  "min_time_span_s": min((row["time_span_s"] for row in trial_rows if row["time_span_s"] is not None), default=None),
                  "min_baseline_valid_rows": min((row["baseline_valid_rows_0_60s"] for row in trial_rows), default=None),
                  "min_exposure_valid_rows": min((row["exposure_valid_rows_60_240s"] for row in trial_rows), default=None),
                  "min_eight_sensor_finite_fraction": min((row["eight_sensor_finite_fraction"] for row in trial_rows), default=None),
                  "equal_time_steps": sum(row["equal_time_steps"] for row in trial_rows),
                  "backwards_time_steps": sum(row["backwards_time_steps"] for row in trial_rows),
                  "nonmonotonic_trial_ids": [row["trial_id"] for row in trial_rows if not row["nondecreasing_time"]],
              },
              "checks": tests,
              "gate_result": "REAL_GAS_TRIAL_EIGHT_SENSOR_SOURCE_READY_FOR_DESIGN" if all(tests.values()) else "STOP_GAS_TRIAL_SOURCE_SUPPORT",
              "model_fits": 0, "validation_performance_scores": 0, "test_performance_scores": 0}
    write(result)
    print(json.dumps({key: result[key] for key in ("archive_parent_directories", "raw_file_count", "downsampled_file_count",
                       "parsed_trial_count", "nonzero_second_gas_trial_counts", "trial_numeric_summary", "checks", "gate_result")}, indent=2))


if __name__ == "__main__":
    main()
