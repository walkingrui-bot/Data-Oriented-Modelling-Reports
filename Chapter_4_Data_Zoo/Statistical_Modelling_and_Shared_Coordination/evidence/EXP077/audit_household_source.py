"""EXP077: stream the UCI235 original archive and emit aggregate provenance only."""

from __future__ import annotations

import io
import json
import math
import urllib.request
import zipfile
from collections import deque
from datetime import datetime, timedelta
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption.zip"
MEMBER = "household_power_consumption.txt"
COLUMNS = ("Date", "Time", "Global_active_power", "Global_reactive_power", "Voltage",
           "Global_intensity", "Sub_metering_1", "Sub_metering_2", "Sub_metering_3")
NUMERIC = COLUMNS[2:]
YEARS = (2007, 2008, 2009, 2010)
HOUR = timedelta(hours=1)
MINUTE = timedelta(minutes=1)


def new_year() -> dict:
    return {"rows": 0, "four_channel_complete_rows": 0, "valid_global_target_rows": 0,
            "positive_submeter_rows": {name: 0 for name in COLUMNS[6:]},
            "exact_one_hour_future_pairs": 0, "candidate_offset60_pairs": 0,
            "different_dates": set()}


def parse_date(date: str, time: str) -> datetime:
    # Source day/month may omit leading zero; preserve dd/mm/yyyy meaning.
    day, month, year = (int(part) for part in date.split("/"))
    hour, minute, second = (int(part) for part in time.split(":"))
    return datetime(year, month, day, hour, minute, second)


def main() -> None:
    with urllib.request.urlopen(URL, timeout=120) as response:
        archive_bytes = response.read(30_000_001)
    if len(archive_bytes) > 30_000_000:
        raise ValueError("network budget exceeded")
    yearly = {year: new_year() for year in YEARS}
    missing = {name: 0 for name in NUMERIC}
    invalid_numeric = {name: 0 for name in NUMERIC}
    row_count = 0
    bad_field_count = 0
    invalid_calendar = 0
    duplicate_or_backward = 0
    nonminute_forward = 0
    negative_residual_rows = 0
    previous = None
    first = None
    last = None
    # Exactly 60 preceding *rows*: require calendar difference to reject gaps/DST artifacts.
    past = deque(maxlen=60)
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = archive.namelist()
        if MEMBER not in members:
            raise ValueError("official expected archive member unavailable")
        member_info = archive.getinfo(MEMBER)
        with archive.open(MEMBER) as binary, io.TextIOWrapper(binary, encoding="utf-8-sig") as handle:
            header = handle.readline().strip().split(";")
            if tuple(header) != COLUMNS:
                raise ValueError(f"official column order differs: {header}")
            for line in handle:
                row_count += 1
                parts = line.rstrip("\r\n").split(";")
                if len(parts) != len(COLUMNS):
                    bad_field_count += 1
                    past.append((None, False))
                    continue
                try:
                    stamp = parse_date(parts[0], parts[1])
                except (ValueError, IndexError):
                    invalid_calendar += 1
                    past.append((None, False))
                    continue
                if first is None:
                    first = stamp
                last = stamp
                if previous is not None:
                    delta = stamp - previous
                    if delta <= timedelta(0):
                        duplicate_or_backward += 1
                    elif delta != MINUTE:
                        nonminute_forward += 1
                previous = stamp
                values = {}
                for name, raw in zip(NUMERIC, parts[2:]):
                    if raw == "" or raw == "?":
                        missing[name] += 1
                        values[name] = None
                        continue
                    try:
                        number = float(raw)
                        if not math.isfinite(number):
                            raise ValueError("nonfinite")
                    except ValueError:
                        invalid_numeric[name] += 1
                        values[name] = None
                    else:
                        values[name] = number
                year = stamp.year
                target_good = values["Global_active_power"] is not None and values["Global_active_power"] >= 0
                origin_good = target_good and all(values[name] is not None and values[name] >= 0 for name in COLUMNS[6:])
                if year in yearly:
                    group = yearly[year]
                    group["rows"] += 1
                    group["different_dates"].add(stamp.date().isoformat())
                    group["valid_global_target_rows"] += int(target_good)
                    group["four_channel_complete_rows"] += int(origin_good)
                    for name in COLUMNS[6:]:
                        group["positive_submeter_rows"][name] += int(values[name] is not None and values[name] > 0)
                if origin_good:
                    residual = values["Global_active_power"] * 1000 / 60 - sum(values[name] for name in COLUMNS[6:])
                    negative_residual_rows += int(residual < -1e-9)
                if len(past) == 60 and year in yearly:
                    origin_stamp, origin_complete = past[0]
                    if origin_complete and target_good:
                        group = yearly[year]
                        group["candidate_offset60_pairs"] += 1
                        group["exact_one_hour_future_pairs"] += int(origin_stamp is not None and stamp - origin_stamp == HOUR)
                past.append((stamp, origin_good))
    for group in yearly.values():
        group["different_dates"] = len(group["different_dates"])
        group["four_channel_complete_fraction"] = group["four_channel_complete_rows"] / group["rows"] if group["rows"] else 0
    checks = {
        "official_member_and_columns": True,
        "at_least_two_million_rows": row_count >= 2_000_000,
        "no_invalid_calendar_or_row_width": invalid_calendar == 0 and bad_field_count == 0,
        "each_year_at_least_250_dates": all(yearly[y]["different_dates"] >= 250 for y in YEARS),
        "each_year_four_channel_complete_at_least_95pct": all(yearly[y]["four_channel_complete_fraction"] >= .95 for y in YEARS),
        "each_year_each_submeter_at_least_1000_positive_rows": all(
            all(yearly[y]["positive_submeter_rows"][name] >= 1000 for name in COLUMNS[6:]) for y in YEARS),
        "train_2007_2008_at_least_300000_exact_hour_pairs":
            sum(yearly[y]["exact_one_hour_future_pairs"] for y in (2007, 2008)) >= 300_000,
        "validation_2009_at_least_100000_exact_hour_pairs": yearly[2009]["exact_one_hour_future_pairs"] >= 100_000,
        "test_2010_at_least_100000_exact_hour_pairs": yearly[2010]["exact_one_hour_future_pairs"] >= 100_000,
    }
    decision = ("FOUR_CHANNEL_YEAR_SPLIT_SOURCE_READY_FOR_DESIGN" if all(checks.values())
                else "STOP_MULTICHANNEL_SOURCE_SUPPORT")
    result = {
        "research_id": "STAT-PSYMOE-EXP077-20261002-001",
        "attempt_id": "EXP077-SOURCE-002",
        "official_page": "https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption",
        "official_zip_url": URL, "archive_member": MEMBER, "download_bytes": len(archive_bytes),
        "archive_member_count": len(members), "uncompressed_member_bytes": member_info.file_size,
        "actual_columns": header, "source_rows": row_count,
        "first_calendar_value": first.isoformat(sep=" ") if first else None,
        "last_calendar_value": last.isoformat(sep=" ") if last else None,
        "source_timezone": "not established; dates treated as naive source calendar values",
        "bad_field_count_rows": bad_field_count, "invalid_calendar_rows": invalid_calendar,
        "duplicate_or_backward_calendar_steps": duplicate_or_backward,
        "forward_steps_other_than_one_minute": nonminute_forward,
        "true_missing_field_rows_by_column": missing,
        "invalid_numeric_rows_by_column": invalid_numeric,
        "negative_physical_residual_rows_among_four_channel_complete": negative_residual_rows,
        "by_target_year": {str(year): yearly[year] for year in YEARS},
        "checks": checks, "gate_result": decision, "model_fits": 0,
        "validation_performance_scores": 0, "test_performance_scores": 0,
    }
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("source_rows", "first_calendar_value", "last_calendar_value",
                    "duplicate_or_backward_calendar_steps", "forward_steps_other_than_one_minute",
                    "by_target_year", "checks", "gate_result")}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
