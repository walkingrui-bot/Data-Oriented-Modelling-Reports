"""EXP082: audit original UCI492 archive in memory, retain derived counts only."""

from __future__ import annotations

import csv
import gzip
import io
import json
import math
import statistics
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/492/metro%2Binterstate%2Btraffic%2Bvolume.zip"
MEMBER = "Metro_Interstate_Traffic_Volume.csv.gz"
NEEDED = ("date_time", "traffic_volume", "temp", "rain_1h", "snow_1h", "clouds_all")
WEATHER = ("temp", "rain_1h", "snow_1h", "clouds_all")


def write(result: dict) -> None:
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def number(raw: str) -> float | None:
    if raw.strip() in ("", "?"):
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if math.isfinite(value) else None


def main() -> None:
    with urllib.request.urlopen(URL, timeout=90) as response:
        archive_bytes = response.read(2_000_001)
    if len(archive_bytes) > 2_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = archive.namelist()
        if MEMBER not in members:
            result = {"official_zip_url": URL, "archive_members": members,
                      "gate_result": "STOP_OFFICIAL_MEMBER_MISMATCH", "model_fits": 0}
            write(result)
            print(json.dumps(result, indent=2))
            return
        with archive.open(MEMBER) as handle:
            csv_bytes = gzip.decompress(handle.read())
    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
    columns = tuple(reader.fieldnames or ())
    if not all(name in columns for name in NEEDED):
        result = {"official_zip_url": URL, "archive_members": members,
                  "actual_columns": columns, "gate_result": "STOP_REQUIRED_COLUMNS", "model_fits": 0}
        write(result)
        print(json.dumps(result, indent=2))
        return
    raw_rows = 0
    invalid_dates = 0
    missing_or_nonfinite = {name: 0 for name in NEEDED if name != "date_time"}
    negative_traffic = 0
    fully_complete = 0
    by_hour = defaultdict(list)
    for row in reader:
        raw_rows += 1
        try:
            stamp = datetime.strptime(row["date_time"].strip(), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            invalid_dates += 1
            continue
        data = {name: number(row[name]) for name in NEEDED if name != "date_time"}
        for name, value in data.items():
            missing_or_nonfinite[name] += int(value is None)
        if data["traffic_volume"] is not None and data["traffic_volume"] < 0:
            negative_traffic += 1
        fully_complete += int(all(value is not None for value in data.values()))
        by_hour[stamp].append(data)
    duplicate_hours = 0
    extra_duplicate_rows = 0
    conflicting_outcome_hours = 0
    weather_conflicts = {name: 0 for name in WEATHER}
    weather_max_range = {name: 0.0 for name in WEATHER}
    collapsed = {}
    for stamp, entries in by_hour.items():
        duplicate_hours += int(len(entries) > 1)
        extra_duplicate_rows += len(entries) - 1
        outcomes = [entry["traffic_volume"] for entry in entries]
        outcome_ok = all(value is not None for value in outcomes) and len(set(outcomes)) == 1 and outcomes[0] >= 0
        if len(entries) > 1 and not outcome_ok:
            conflicting_outcome_hours += 1
        weather = {}
        for name in WEATHER:
            values = [entry[name] for entry in entries]
            if all(value is not None for value in values):
                weather[name] = float(statistics.median(values))
                spread = max(values) - min(values)
                weather_conflicts[name] += int(len(entries)>1 and spread>0)
                weather_max_range[name] = max(weather_max_range[name], spread)
            else:
                weather[name] = None
        collapsed[stamp] = {"traffic_volume": outcomes[0] if outcome_ok else None, "weather": weather}
    periods = {"train_2013_2016": {"pairs": 0, "target_dates": set()},
               "validation_2017": {"pairs": 0, "target_dates": set()},
               "test_2018": {"pairs": 0, "target_dates": set()}}
    for stamp, entry in collapsed.items():
        target = stamp + timedelta(hours=1)
        future = collapsed.get(target)
        if future is None or entry["traffic_volume"] is None or future["traffic_volume"] is None:
            continue
        if any(value is None for value in entry["weather"].values()):
            continue
        if 2013 <= target.year <= 2016:
            period = "train_2013_2016"
        elif target.year == 2017:
            period = "validation_2017"
        elif target.year == 2018:
            period = "test_2018"
        else:
            continue
        periods[period]["pairs"] += 1
        periods[period]["target_dates"].add(target.date().isoformat())
    for item in periods.values():
        item["target_dates"] = len(item["target_dates"])
    checks = {
        "expected_unique_archive_member_and_required_columns": members == [MEMBER] and all(name in columns for name in NEEDED),
        "at_least_45000_rows": raw_rows >= 45_000,
        "at_least_40000_unique_calendar_hours": len(by_hour) >= 40_000,
        "calendar_parse_complete": invalid_dates == 0,
        "at_least_95pct_full_numeric_rows": fully_complete / raw_rows >= .95,
        "no_negative_traffic": negative_traffic == 0,
        "duplicate_outcome_consistent": conflicting_outcome_hours == 0,
        "train_at_least_20000_pairs_800_dates": periods["train_2013_2016"]["pairs"] >= 20_000 and periods["train_2013_2016"]["target_dates"] >= 800,
        "validation_at_least_5000_pairs_250_dates": periods["validation_2017"]["pairs"] >= 5_000 and periods["validation_2017"]["target_dates"] >= 250,
        "test_at_least_5000_pairs_250_dates": periods["test_2018"]["pairs"] >= 5_000 and periods["test_2018"]["target_dates"] >= 250,
    }
    decision = ("STOP_DUPLICATE_OUTCOME_SEMANTICS" if conflicting_outcome_hours else
                "TRAFFIC_WEATHER_HOURLY_SOURCE_READY_FOR_DESIGN" if all(checks.values()) else
                "STOP_TRAFFIC_WEATHER_SOURCE_SUPPORT")
    result = {
        "research_id": "STAT-PSYMOE-EXP082-20261002-001", "attempt_id": "EXP082-SOURCE-002",
        "official_page": "https://archive.ics.uci.edu/dataset/492/metro%2Binterstate%2Btraffic%2Bvolume",
        "official_zip_url": URL, "archive_member": MEMBER,
        "archive_members": members, "download_bytes": len(archive_bytes),
        "source_csv_bytes": len(csv_bytes), "actual_columns": columns,
        "source_rows": raw_rows, "calendar_parse_failures": invalid_dates,
        "first_unique_hour": min(by_hour).isoformat(sep=" ") if by_hour else None,
        "last_unique_hour": max(by_hour).isoformat(sep=" ") if by_hour else None,
        "source_timezone": "UCI page describes local CST; no DST/as-of proof",
        "unique_calendar_hours": len(by_hour),
        "duplicate_calendar_hours": duplicate_hours, "extra_duplicate_rows": extra_duplicate_rows,
        "conflicting_duplicate_outcome_hours": conflicting_outcome_hours,
        "numeric_weather_conflicting_duplicate_hours_by_column": weather_conflicts,
        "numeric_weather_max_within_hour_range_by_column": weather_max_range,
        "fully_complete_numeric_rows": fully_complete,
        "missing_or_nonfinite_by_column": missing_or_nonfinite,
        "negative_traffic_rows": negative_traffic,
        "one_hour_pair_support_by_target_year": periods,
        "checks": checks, "gate_result": decision,
        "model_fits": 0, "validation_performance_scores": 0, "test_performance_scores": 0,
    }
    write(result)
    print(json.dumps({key: result[key] for key in (
        "source_rows", "unique_calendar_hours", "duplicate_calendar_hours",
        "conflicting_duplicate_outcome_hours", "numeric_weather_conflicting_duplicate_hours_by_column",
        "one_hour_pair_support_by_target_year", "checks", "gate_result")}, indent=2))


if __name__ == "__main__":
    main()
