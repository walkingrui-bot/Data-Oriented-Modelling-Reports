"""EXP086: stream UCI487 original daily sensor files without saving a copy."""

from __future__ import annotations

import io
import json
import math
import re
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation.zip"
DATE = re.compile(r"(\d{8})_(\d{6})")
SPLIT = re.compile(r"[\s,;]+")


def write(result: dict) -> None:
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def date_info(path: str) -> tuple[str, str] | None:
    match = DATE.search(Path(path).name)
    if match is None:
        return None
    try:
        stamp = datetime.strptime("_".join(match.groups()), "%Y%m%d_%H%M%S")
    except ValueError:
        return None
    return stamp.date().isoformat(), stamp.isoformat(sep=" ")


def audit_day(archive: zipfile.ZipFile, name: str, day: str, start_stamp: str) -> dict:
    nonempty = width20 = valid_all = header_or_invalid = 0
    sensor_cells = sensor_finite = reference_finite = 0
    co_levels = set()
    co_out_of_range = 0
    first_time = last_time = None
    backwards_steps = equal_steps = 0
    with archive.open(name) as handle:
        for raw in handle:
            line = raw.decode("utf-8-sig", errors="replace").strip()
            if not line:
                continue
            nonempty += 1
            tokens = [token for token in SPLIT.split(line) if token]
            if len(tokens) != 20:
                header_or_invalid += 1
                continue
            width20 += 1
            try:
                values = [float(token) for token in tokens]
            except ValueError:
                header_or_invalid += 1
                continue
            sensor_cells += 14
            sensor_finite += sum(math.isfinite(value) for value in values[6:20])
            reference_finite += int(all(math.isfinite(value) for value in values[1:6]))
            if not all(math.isfinite(value) for value in values):
                continue
            valid_all += 1
            stamp = values[0]
            if first_time is None:
                first_time = stamp
            if last_time is not None and stamp < last_time:
                backwards_steps += 1
            if last_time is not None and stamp == last_time:
                equal_steps += 1
            last_time = stamp
            co_levels.add(round(values[1], 6))
            co_out_of_range += int(values[1] < 0 or values[1] > 20)
    return {"path": name, "date": day, "filename_start": start_stamp,
            "nonempty_rows": nonempty, "width20_rows": width20,
            "all20_finite_rows": valid_all, "header_or_invalid_rows": header_or_invalid,
            "all20_finite_fraction": valid_all / nonempty if nonempty else 0.0,
            "reference_fields_finite_fraction": reference_finite / width20 if width20 else 0.0,
            "fourteen_sensor_finite_fraction": sensor_finite / sensor_cells if sensor_cells else 0.0,
            "first_time_s": first_time, "last_time_s": last_time,
            "time_span_s": last_time - first_time if first_time is not None else None,
            "equal_time_steps": equal_steps, "backwards_time_steps": backwards_steps,
            "distinct_co_levels_rounded_6dp": len(co_levels),
            "min_co_ppm": min(co_levels) if co_levels else None,
            "max_co_ppm": max(co_levels) if co_levels else None,
            "co_out_of_range_rows": co_out_of_range}


def main() -> None:
    with urllib.request.urlopen(URL, timeout=120) as response:
        blob = response.read(210_000_001)
    if len(blob) > 210_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(blob)) as outer:
        outer_files = [path for path in outer.namelist() if not path.endswith("/")]
        inner_paths = [path for path in outer_files if path.lower().endswith(".zip")]
        if len(inner_paths) == 1:
            inner_blob = outer.read(inner_paths[0])
            archive = zipfile.ZipFile(io.BytesIO(inner_blob))
            packaging = "one_nested_zip"
        else:
            archive = outer
            packaging = "direct_outer_zip"
        try:
            files = [path for path in archive.namelist() if not path.endswith("/")]
            dated = [(path, date_info(path)) for path in files]
            dated = [(path, info) for path, info in dated if info is not None]
            days = [audit_day(archive, path, info[0], info[1]) for path, info in dated]
        finally:
            if archive is not outer:
                archive.close()
    checks = {
        "thirteen_distinct_dated_files": len(days) == 13 and len({row["date"] for row in days}) == 13,
        "all_days_at_least_280000_valid_rows": len(days) == 13 and all(row["all20_finite_rows"] >= 280_000 for row in days),
        "at_least_4000000_valid_rows_total": sum(row["all20_finite_rows"] for row in days) >= 4_000_000,
        "all_days_at_least_99pct_full_numeric": len(days) == 13 and all(row["all20_finite_fraction"] >= .99 for row in days),
        "all_days_monotone_at_least_24h": len(days) == 13 and all(row["backwards_time_steps"] == 0 and row["time_span_s"] is not None and row["time_span_s"] >= 86_400 for row in days),
        "all_days_five_co_levels_0_to_20": len(days) == 13 and all(row["distinct_co_levels_rounded_6dp"] >= 5 and row["co_out_of_range_rows"] == 0 for row in days),
        "all_days_99pct_reference_and_fourteen_sensors": len(days) == 13 and all(row["reference_fields_finite_fraction"] >= .99 and row["fourteen_sensor_finite_fraction"] >= .99 for row in days),
    }
    result = {"research_id": "STAT-PSYMOE-EXP086-20261002-001", "attempt_id": "EXP086-SOURCE-001",
              "official_page": "https://archive.ics.uci.edu/dataset/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation",
              "official_zip_url": URL, "download_bytes": len(blob),
              "packaging": packaging, "outer_file_names": outer_files,
              "inner_file_count": len(files), "dated_file_count": len(days),
              "days": sorted(days, key=lambda row: row["date"]),
              "total_all20_finite_rows": sum(row["all20_finite_rows"] for row in days),
              "checks": checks,
              "gate_result": "DATED_REAL_CO_SENSOR_SOURCE_READY_FOR_EPISODE_AUDIT" if all(checks.values()) else "STOP_CO_SENSOR_SOURCE_SCHEMA_OR_SUPPORT",
              "model_fits": 0, "validation_performance_scores": 0, "test_performance_scores": 0}
    write(result)
    print(json.dumps({key: result[key] for key in ("packaging", "outer_file_names", "inner_file_count",
                       "dated_file_count", "total_all20_finite_rows", "checks", "gate_result")}, indent=2))


if __name__ == "__main__":
    main()
