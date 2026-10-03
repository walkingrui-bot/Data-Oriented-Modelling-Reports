"""EXP087: identify 100 scheduled real CO exposures per original day file."""

from __future__ import annotations

import io
import json
import math
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP086-20261002-001"
sys.path.insert(0, str(PARENT))
from audit_co_source import SPLIT, URL, date_info  # noqa: E402


def write(value: dict) -> None:
    (HERE / "EPISODE_MATRIX.json").write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def window_index(stamp: float, first: float) -> int:
    if stamp < first + 900:
        return -1
    return int((stamp - first - 900) // 900)


def audit_day(archive: zipfile.ZipFile, name: str, date: str) -> dict:
    counts = [0] * 100
    centers = [[] for _ in range(100)]
    first = previous = None
    valid_rows = clean_rows = after_rows = invalid_rows = 0
    backsteps = []
    with archive.open(name) as handle:
        for raw in handle:
            line = raw.decode("utf-8-sig", errors="replace").strip()
            if not line:
                continue
            tokens = [token for token in SPLIT.split(line) if token]
            if len(tokens) != 20:
                invalid_rows += 1
                continue
            try:
                values = [float(token) for token in tokens]
            except ValueError:
                invalid_rows += 1
                continue
            if not all(math.isfinite(value) for value in values):
                invalid_rows += 1
                continue
            valid_rows += 1
            stamp = values[0]
            if first is None:
                first = stamp
            idx = window_index(stamp, first)
            if previous is not None and stamp < previous:
                previous_index = window_index(previous, first)
                backsteps.append({"previous_time_s": previous, "current_time_s": stamp,
                                  "backstep_s": previous - stamp,
                                  "previous_window": previous_index, "current_window": idx,
                                  "crosses_window_boundary": previous_index != idx})
            previous = stamp
            if idx == -1:
                clean_rows += 1
            elif 0 <= idx < 100:
                counts[idx] += 1
                relative = stamp - first - 900 - 900 * idx
                if 300 <= relative < 840:
                    centers[idx].append(values[1])
            else:
                after_rows += 1
    windows = []
    for idx in range(100):
        values = np.asarray(centers[idx], dtype=float)
        median = float(np.median(values)) if len(values) else None
        iqr = float(np.quantile(values, .75) - np.quantile(values, .25)) if len(values) else None
        stable = counts[idx] >= 2500 and len(values) >= 1400 and median is not None and 0 <= median <= 20 and iqr <= .25
        windows.append({"window_index": idx, "full_numeric_rows": counts[idx],
                        "central_rows": len(values), "central_co_median_ppm": median,
                        "central_co_iqr_ppm": iqr, "stable_by_frozen_rule": stable})
    stable = [row for row in windows if row["stable_by_frozen_rule"]]
    level_count = len({round(row["central_co_median_ppm"], 1) for row in stable})
    return {"date": date, "path": name, "first_time_s": first, "last_time_s": previous,
            "full_numeric_rows": valid_rows, "invalid_rows": invalid_rows,
            "cleaning_rows": clean_rows, "after_100_windows_rows": after_rows,
            "time_backsteps": backsteps, "windows": windows,
            "windows_at_least_2500_rows": sum(row["full_numeric_rows"] >= 2500 for row in windows),
            "stable_windows": len(stable), "stable_rounded_0_1ppm_levels": level_count}


def main() -> None:
    with urllib.request.urlopen(URL, timeout=120) as response:
        blob = response.read(210_000_001)
    if len(blob) > 210_000_000:
        raise ValueError("network budget exceeded")
    old = json.loads((PARENT / "SOURCE_MATRIX.json").read_text())
    with zipfile.ZipFile(io.BytesIO(blob)) as outer:
        inner_paths = [name for name in outer.namelist() if name.lower().endswith(".zip")]
        if len(inner_paths) != 1:
            write({"outer_members": outer.namelist(), "gate_result": "STOP_CO_EPISODE_IDENTIFIABILITY", "model_fits": 0})
            print("STOP_CO_EPISODE_IDENTIFIABILITY: original nested package mismatch")
            return
        with zipfile.ZipFile(io.BytesIO(outer.read(inner_paths[0]))) as archive:
            dated = [(name, date_info(name)) for name in archive.namelist() if not name.endswith("/")]
            dated = [(name, info) for name, info in dated if info is not None]
            days = [audit_day(archive, name, info[0]) for name, info in dated]
    days.sort(key=lambda row: row["date"])
    old_rows = {row["date"]: row["all20_finite_rows"] for row in old["days"]}
    all_backsteps = [dict(date=row["date"], **item) for row in days for item in row["time_backsteps"]]
    checks = {
        "same_13_dates_and_valid_row_counts_as_exp086": len(days) == 13 and {row["date"]: row["full_numeric_rows"] for row in days} == old_rows,
        "each_day_100_windows_at_least_2500_rows": len(days) == 13 and all(row["windows_at_least_2500_rows"] == 100 for row in days),
        "each_day_at_least_90_stable_windows": len(days) == 13 and all(row["stable_windows"] >= 90 for row in days),
        "total_at_least_1200_stable_windows": sum(row["stable_windows"] for row in days) >= 1200,
        "each_day_at_least_8_co_levels": len(days) == 13 and all(row["stable_rounded_0_1ppm_levels"] >= 8 for row in days),
        "all_backsteps_small_and_within_window": all(item["backstep_s"] < 10 and not item["crosses_window_boundary"] for item in all_backsteps),
    }
    result = {"research_id": "STAT-PSYMOE-EXP087-20261002-001", "attempt_id": "EXP087-SOURCE-001",
              "official_zip_url": URL, "download_bytes": len(blob),
              "exp086_gate_retained": old["gate_result"], "exp086_full_numeric_rows": old["total_all20_finite_rows"],
              "days": days, "total_stable_windows": sum(row["stable_windows"] for row in days),
              "time_backsteps": all_backsteps, "checks": checks,
              "gate_result": "CO_EXPOSURE_EPISODES_IDENTIFIABLE_FOR_NEW_QUESTION" if all(checks.values()) else "STOP_CO_EPISODE_IDENTIFIABILITY",
              "model_fits": 0, "validation_performance_scores": 0, "test_performance_scores": 0}
    write(result)
    print(json.dumps({"dates": [row["date"] for row in days],
                      "per_day_stable_windows": {row["date"]: row["stable_windows"] for row in days},
                      "per_day_distinct_levels": {row["date"]: row["stable_rounded_0_1ppm_levels"] for row in days},
                      "total_stable_windows": result["total_stable_windows"],
                      "time_backsteps": all_backsteps, "checks": checks,
                      "gate_result": result["gate_result"]}, indent=2))


if __name__ == "__main__":
    main()
