"""EXP080: bounded in-memory audit of the UCI849 original, no data copy."""

from __future__ import annotations

import csv
import io
import json
import math
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/849/power%2Bconsumption%2Bof%2Btetouan%2Bcity.zip"
MEMBER = "Tetuan City power consumption.csv"
COLUMNS = ("DateTime", "Temperature", "Humidity", "Wind Speed", "general diffuse flows",
           "diffuse flows", "Zone 1 Power Consumption", "Zone 2 Power Consumption",
           "Zone 3 Power Consumption")
ZONES = COLUMNS[6:]
DATE_FORMATS = (
    "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
    "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
    "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M",
)


def write(value: dict) -> None:
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_candidates(strings: list[str]) -> tuple[list[datetime] | None, dict]:
    evidence = {}
    accepted = []
    for pattern in DATE_FORMATS:
        stamps = []
        failures = 0
        for raw in strings:
            try:
                stamps.append(datetime.strptime(raw, pattern))
            except ValueError:
                failures += 1
                break
        if failures:
            evidence[pattern] = {"all_parse": False, "sample_failure_present": True}
            continue
        steps = [(b - a).total_seconds() / 60 for a, b in zip(stamps, stamps[1:])]
        nonincreasing = sum(step <= 0 for step in steps)
        ten_minute = sum(step == 10 for step in steps)
        fraction = ten_minute / len(steps) if steps else 0
        okay = nonincreasing == 0 and fraction >= .99
        evidence[pattern] = {"all_parse": True, "nonincreasing_steps": nonincreasing,
                             "ten_minute_steps": ten_minute, "ten_minute_fraction": fraction,
                             "calendar_accepted": okay}
        if okay:
            accepted.append((pattern, stamps))
    if len(accepted) != 1:
        return None, {"candidates": evidence, "accepted_patterns": [item[0] for item in accepted],
                      "gate": "STOP_AMBIGUOUS_SOURCE_CALENDAR"}
    return accepted[0][1], {"candidates": evidence, "accepted_pattern": accepted[0][0],
                           "gate": "UNIQUE_SOURCE_CALENDAR_ACCEPTED"}


def main() -> None:
    with urllib.request.urlopen(URL, timeout=90) as response:
        archive_bytes = response.read(5_000_001)
    if len(archive_bytes) > 5_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = archive.namelist()
        if MEMBER not in members:
            write({"official_zip_url": URL, "archive_members": members,
                   "gate_result": "STOP_OFFICIAL_MEMBER_MISMATCH", "model_fits": 0})
            print(json.dumps({"archive_members": members, "gate_result": "STOP_OFFICIAL_MEMBER_MISMATCH"}, indent=2))
            return
        with archive.open(MEMBER) as handle:
            raw = handle.read()
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")))
    raw_header = next(reader)
    header = tuple(" ".join(name.split()) for name in raw_header)
    rows = list(reader)
    if header != COLUMNS:
        result = {"official_zip_url": URL, "archive_members": members, "source_rows": len(rows),
                  "raw_header": raw_header, "normalized_header": header,
                  "gate_result": "STOP_SOURCE_COLUMNS_MISMATCH", "model_fits": 0}
        write(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    widths_bad = sum(len(row) != len(COLUMNS) for row in rows)
    if widths_bad:
        result = {"official_zip_url": URL, "archive_members": members, "source_rows": len(rows),
                  "columns": header, "bad_width_rows": widths_bad,
                  "gate_result": "STOP_SOURCE_ROW_WIDTH", "model_fits": 0}
        write(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    stamps, calendar = parse_candidates([row[0].strip() for row in rows])
    if stamps is None:
        result = {"official_zip_url": URL, "archive_members": members, "source_rows": len(rows),
                  "columns": header, "calendar": calendar,
                  "gate_result": "STOP_AMBIGUOUS_SOURCE_CALENDAR", "model_fits": 0}
        write(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    numeric = []
    missing_by_column = {name: 0 for name in COLUMNS[1:]}
    nonfinite_by_column = {name: 0 for name in COLUMNS[1:]}
    negative_zone_by_column = {name: 0 for name in ZONES}
    complete_count = 0
    positive_distinct = {zone: {q: set() for q in (1, 2, 3, 4)} for zone in ZONES}
    for stamp, row in zip(stamps, rows):
        parsed = []
        for name, raw_value in zip(COLUMNS[1:], row[1:]):
            raw_value = raw_value.strip()
            if raw_value in ("", "?"):
                missing_by_column[name] += 1
                parsed.append(None)
                continue
            try:
                value = float(raw_value)
            except ValueError:
                nonfinite_by_column[name] += 1
                parsed.append(None)
                continue
            if not math.isfinite(value):
                nonfinite_by_column[name] += 1
                parsed.append(None)
            else:
                parsed.append(value)
        numeric.append(parsed)
        if all(value is not None for value in parsed):
            complete_count += 1
        quarter = (stamp.month - 1) // 3 + 1
        for column, zone in enumerate(ZONES, start=5):
            value = parsed[column]
            if value is not None and value < 0:
                negative_zone_by_column[zone] += 1
            if value is not None and value > 0:
                positive_distinct[zone][quarter].add(value)
    by_stamp = {stamp: index for index, stamp in enumerate(stamps)}
    segments = {"train_jan_aug": {"pairs": 0, "target_dates": set()},
                "validation_sep_oct": {"pairs": 0, "target_dates": set()},
                "test_nov_dec": {"pairs": 0, "target_dates": set()}}
    for index, stamp in enumerate(stamps):
        target_stamp = stamp + timedelta(hours=1)
        target_index = by_stamp.get(target_stamp)
        if target_index is None:
            continue
        origin_values, target_values = numeric[index], numeric[target_index]
        if any(value is None for value in origin_values):
            continue
        if any(origin_values[column] < 0 for column in (5, 6, 7)):
            continue
        if any(target_values[column] is None or target_values[column] < 0 for column in (5, 6, 7)):
            continue
        if target_stamp.year != 2017:
            continue
        segment = ("train_jan_aug" if target_stamp.month <= 8 else
                   "validation_sep_oct" if target_stamp.month <= 10 else "test_nov_dec")
        segments[segment]["pairs"] += 1
        segments[segment]["target_dates"].add(target_stamp.date().isoformat())
    for value in segments.values():
        value["target_dates"] = len(value["target_dates"])
    cadence = calendar["candidates"][calendar["accepted_pattern"]]
    positive_counts = {zone: {str(q): len(values) for q, values in by_quarter.items()}
                       for zone, by_quarter in positive_distinct.items()}
    checks = {
        "official_member_and_nine_columns": members == [MEMBER] and header == COLUMNS,
        "at_least_50000_rows": len(rows) >= 50_000,
        "unique_calendar_and_at_least_99pct_ten_minute": calendar["gate"] == "UNIQUE_SOURCE_CALENDAR_ACCEPTED" and
             cadence["nonincreasing_steps"] == 0 and cadence["ten_minute_fraction"] >= .99,
        "nine_columns_complete_at_least_95pct": complete_count / len(rows) >= .95,
        "no_negative_zone_power": all(value == 0 for value in negative_zone_by_column.values()),
        "each_zone_each_quarter_at_least_100_distinct_positive": all(
            positive_counts[zone][str(q)] >= 100 for zone in ZONES for q in (1, 2, 3, 4)),
        "train_at_least_30000_pairs_50_dates": segments["train_jan_aug"]["pairs"] >= 30_000 and
             segments["train_jan_aug"]["target_dates"] >= 50,
        "validation_at_least_8000_pairs_50_dates": segments["validation_sep_oct"]["pairs"] >= 8_000 and
             segments["validation_sep_oct"]["target_dates"] >= 50,
        "test_at_least_8000_pairs_50_dates": segments["test_nov_dec"]["pairs"] >= 8_000 and
             segments["test_nov_dec"]["target_dates"] >= 50,
    }
    result = {
        "research_id": "STAT-PSYMOE-EXP080-20261002-001", "attempt_id": "EXP080-SOURCE-003",
        "official_page": "https://archive.ics.uci.edu/dataset/849/power%2Bconsumption%2Bof%2Btetouan%2Bcity",
        "official_zip_url": URL, "archive_member": MEMBER,
        "download_bytes": len(archive_bytes), "source_csv_bytes": len(raw),
        "archive_members": members, "raw_header": raw_header, "normalized_columns": header,
        "source_rows": len(rows), "first_calendar_value": stamps[0].isoformat(sep=" "),
        "last_calendar_value": stamps[-1].isoformat(sep=" "),
        "source_timezone": "not stated in UCI source page",
        "calendar": calendar, "complete_nine_column_rows": complete_count,
        "missing_by_column": missing_by_column, "invalid_or_nonfinite_by_column": nonfinite_by_column,
        "negative_zone_power_by_column": negative_zone_by_column,
        "distinct_positive_by_zone_quarter": positive_counts,
        "one_hour_pair_support_by_target_period": segments,
        "checks": checks,
        "gate_result": "THREE_ZONE_TEMPORAL_SOURCE_READY_FOR_DESIGN" if all(checks.values()) else "STOP_MULTI_ZONE_SOURCE_SUPPORT",
        "model_fits": 0, "validation_performance_scores": 0, "test_performance_scores": 0,
    }
    write(result)
    print(json.dumps({key: result[key] for key in (
        "source_rows", "first_calendar_value", "last_calendar_value", "calendar",
        "complete_nine_column_rows", "one_hour_pair_support_by_target_period", "checks", "gate_result")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
