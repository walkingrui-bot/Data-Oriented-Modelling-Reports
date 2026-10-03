"""EXP047 corrected station basename and observed-hour intersection audit."""

import csv
import importlib.util
import io
import json
import re
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
P46 = HERE.parent / "STAT-PSYMOE-EXP046-20261002-001"
spec = importlib.util.spec_from_file_location("exp046_original_reader", P46 / "audit_uci_original.py")
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
META = json.loads((P46 / "SOURCE_METADATA.json").read_text())
MAX_BYTES = 20 * 1024 * 1024


def main():
    req = urllib.request.Request(META["official_download"], headers={"User-Agent": "EXP047-source-audit/1"})
    with urllib.request.urlopen(req, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_BYTES:
            raise RuntimeError("ZIP exceeds registered network budget")
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise RuntimeError("ZIP response exceeded registered network budget")
    with zipfile.ZipFile(io.BytesIO(body)) as outer:
        nested = [item for item in outer.infolist() if not item.is_dir() and Path(item.filename).name == "PRSA2017_Data_20130301-20170228.zip"]
        if len(nested) != 1:
            raise RuntimeError("exactly one original nested ZIP required")
        inner_bytes = outer.read(nested[0])
    audits = []
    grids = {}
    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        members = []
        for item in inner.infolist():
            if not item.is_dir() and re.fullmatch(r"PRSA_Data_.+_20130301-20170228\.csv", Path(item.filename).name):
                members.append(item)
        for item in sorted(members, key=lambda x: x.filename):
            basename = Path(item.filename).name
            match = re.fullmatch(r"PRSA_Data_(.+)_20130301-20170228\.csv", basename)
            assert match
            station = match.group(1)
            labels = set()
            hours = set()
            rows = 0
            duplicates = 0
            bad_dates = 0
            valid_pm = 0
            negative_pm = 0
            valid_met = 0
            with inner.open(item) as handle:
                source = csv.DictReader(io.TextIOWrapper(handle, encoding="utf-8-sig", newline=""))
                required = {"year", "month", "day", "hour", "station", "PM2.5", "TEMP", "PRES", "WSPM"}
                if not required <= set(source.fieldnames or []):
                    raise RuntimeError("required fields absent in " + item.filename)
                for row in source:
                    rows += 1
                    labels.add((row["station"] or "").strip())
                    try:
                        stamp = datetime(int(row["year"]), int(row["month"]), int(row["day"]), int(row["hour"]))
                    except (ValueError, TypeError):
                        bad_dates += 1
                        continue
                    if stamp in hours:
                        duplicates += 1
                    else:
                        hours.add(stamp)
                    pm = prior.number(row["PM2.5"])
                    if pm is not None:
                        if pm >= 0:
                            valid_pm += 1
                        else:
                            negative_pm += 1
                    if all(prior.number(row[name]) is not None for name in ("TEMP", "PRES", "WSPM")):
                        valid_met += 1
            start = min(hours) if hours else None
            end = max(hours) if hours else None
            expected_start = datetime(2013, 3, 1, 0)
            expected_end = datetime(2017, 2, 28, 23)
            qualifies = (labels == {station} and rows >= 30000 and len(hours) >= 30000 and duplicates == 0 and bad_dates == 0 and start == expected_start and end == expected_end and valid_pm >= 25000 and valid_met >= 25000)
            audits.append({"original_member_path": item.filename, "station": station, "source_station_labels": "|".join(sorted(labels)), "station_label_agrees": labels == {station}, "rows": rows, "unique_hour_timestamps": len(hours), "duplicate_hours": duplicates, "invalid_timestamp_rows": bad_dates, "first_original_hour": start.isoformat() if start else "", "last_original_hour": end.isoformat() if end else "", "PM2_5_valid_nonnegative_hours": valid_pm, "PM2_5_negative_rows": negative_pm, "TEMP_PRES_WSPM_all_finite_hours": valid_met, "qualifies": qualifies})
            grids[station] = hours
            print(station, "qualified", qualifies, "PM", valid_pm, flush=True)
    qualified = [row for row in audits if row["qualifies"]]
    common = set.intersection(*(grids[row["station"]] for row in qualified)) if qualified else set()
    gate = "REAL_MULTISITE_SOURCE_READY" if len(qualified) >= 10 and len(common) >= 20000 else "STOP_NUMERIC_SOURCE_SUPPORT"
    summary = {"run_id": "EXP047-NUMERIC-001", "official_original_url": META["official_download"], "network_requests": 1, "response_bytes": len(body), "nested_original_member": nested[0].filename, "station_csv_count": len(audits), "total_rows": sum(row["rows"] for row in audits), "qualified_station_count": len(qualified), "qualifying_stations": [row["station"] for row in qualified], "common_original_hour_grid_count": len(common), "gate": gate}
    with (HERE / "STATION_AUDIT.csv").open("x", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=list(audits[0]))
        writer.writeheader()
        writer.writerows(audits)
    (HERE / "NUMERIC_SUMMARY.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
