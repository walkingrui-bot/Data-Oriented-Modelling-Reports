"""EXP046 one-request in-memory audit of UCI's original nested ZIP."""

import csv
import io
import json
import math
import re
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
META = json.loads((HERE / "SOURCE_METADATA.json").read_text())
MAX_BYTES = 20 * 1024 * 1024


def number(value):
    if value is None:
        return None
    try:
        parsed = float(value)
    except (ValueError, TypeError):
        return None
    return parsed if math.isfinite(parsed) else None


def main():
    assert META["gate"] == "PROVENANCE_PASS_FOR_BOUNDED_NUMERIC_AUDIT"
    req = urllib.request.Request(META["official_download"], headers={"User-Agent": "EXP046-source-audit/1"})
    with urllib.request.urlopen(req, timeout=120) as response:
        content_length = response.headers.get("Content-Length")
        if content_length is not None and int(content_length) > MAX_BYTES:
            raise RuntimeError("original ZIP exceeds registered 20 MiB response budget")
        outer_bytes = response.read(MAX_BYTES + 1)
        final_url = response.url
    if len(outer_bytes) > MAX_BYTES:
        raise RuntimeError("original ZIP response exceeded registered 20 MiB budget")
    with zipfile.ZipFile(io.BytesIO(outer_bytes)) as outer:
        outer_members = [item.filename for item in outer.infolist() if not item.is_dir()]
        nested = [name for name in outer_members if name.endswith("PRSA2017_Data_20130301-20170228.zip")]
        if len(nested) != 1:
            raise RuntimeError(f"expected one named raw source ZIP, found {nested}")
        inner_bytes = outer.read(nested[0])
    audits = []
    grids = {}
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        csv_members = [item for item in inner.infolist() if not item.is_dir() and re.search(r"PRSA_Data_.+_20130301-20170228\.csv$", item.filename)]
        for info in sorted(csv_members, key=lambda item: item.filename):
            expected_match = re.search(r"PRSA_Data_(.+)_20130301-20170228\.csv$", info.filename)
            expected_station = expected_match.group(1)
            row_count = 0
            timestamps = set()
            duplicate_count = 0
            invalid_time = 0
            pm_valid = 0
            pm_negative = 0
            met_valid = 0
            stations_in_file = set()
            with inner.open(info) as binary:
                rows = csv.DictReader(io.TextIOWrapper(binary, encoding="utf-8-sig", newline=""))
                required = {"year", "month", "day", "hour", "PM2.5", "TEMP", "PRES", "WSPM", "station"}
                if not required <= set(rows.fieldnames or []):
                    raise RuntimeError(f"missing required fields in {info.filename}")
                for row in rows:
                    row_count += 1
                    station = (row["station"] or "").strip()
                    stations_in_file.add(station)
                    try:
                        stamp = datetime(int(row["year"]), int(row["month"]), int(row["day"]), int(row["hour"]))
                    except (ValueError, TypeError):
                        invalid_time += 1
                        continue
                    if stamp in timestamps:
                        duplicate_count += 1
                    else:
                        timestamps.add(stamp)
                    pm = number(row["PM2.5"])
                    if pm is not None:
                        if pm >= 0:
                            pm_valid += 1
                        else:
                            pm_negative += 1
                    if all(number(row[column]) is not None for column in ("TEMP", "PRES", "WSPM")):
                        met_valid += 1
            label_agrees = stations_in_file == {expected_station}
            audits.append({"original_member_path": info.filename, "station": expected_station, "source_station_labels": "|".join(sorted(stations_in_file)), "station_label_agrees": label_agrees, "rows": row_count, "unique_valid_hour_timestamps": len(timestamps), "duplicate_hours": duplicate_count, "invalid_timestamp_rows": invalid_time, "PM2_5_valid_nonnegative_hours": pm_valid, "PM2_5_negative_rows": pm_negative, "TEMP_PRES_WSPM_all_finite_hours": met_valid})
            grids[expected_station] = timestamps
            print(expected_station, row_count, pm_valid, met_valid, flush=True)
    qualified = [row for row in audits if row["station_label_agrees"] and row["unique_valid_hour_timestamps"] >= 30000 and row["duplicate_hours"] == 0 and row["PM2_5_valid_nonnegative_hours"] >= 25000 and row["TEMP_PRES_WSPM_all_finite_hours"] >= 25000]
    common = set.intersection(*(grids[row["station"]] for row in qualified)) if qualified else set()
    gate = "REAL_MULTISITE_SOURCE_READY" if len(qualified) >= 10 and len(common) >= 20000 else "STOP_NUMERIC_SOURCE_SUPPORT"
    summary = {"run_id": "EXP046-NUMERIC-001", "official_download": META["official_download"], "resolved_url": final_url, "network_responses": 1, "response_bytes": len(outer_bytes), "outer_members": outer_members, "nested_original_member_path": nested[0], "station_csv_count": len(audits), "total_rows": sum(row["rows"] for row in audits), "qualifying_stations": [row["station"] for row in qualified], "qualified_station_count": len(qualified), "common_original_hour_grid_count": len(common), "gate": gate}
    with (HERE / "STATION_AUDIT.csv").open("x", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(audits[0]))
        writer.writeheader()
        writer.writerows(audits)
    (HERE / "NUMERIC_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
