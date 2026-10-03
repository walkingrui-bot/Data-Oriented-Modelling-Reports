"""EXP050 original-source audit without saving compressed or raw city records."""

import io
import json
import re
import subprocess
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RUN_ID = "EXP050-SOURCE-001"
PAGE = "https://archive.ics.uci.edu/dataset/394/pm25dataoffivechinesecitiesUCI"
DOWNLOAD = "https://archive.ics.uci.edu/static/public/394/pm2%2B5%2Bdata%2Bof%2Bfive%2Bchinese%2Bcities.zip"
CITIES = ("Beijing", "Shanghai", "Guangzhou", "Chengdu", "Shenyang")
MAX_BYTES = 10 * 1024 * 1024


def save(name, obj):
    (HERE / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def rar_listing(raw):
    result = subprocess.run(["/usr/bin/bsdtar", "-tf", "-"], input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90, check=False)
    return result, result.stdout.decode("utf-8", errors="replace").splitlines()


def rar_member(raw, member):
    result = subprocess.run(["/usr/bin/bsdtar", "-xOf", "-", member], input=raw, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90, check=False)
    if result.returncode:
        raise RuntimeError(f"RAR member {member}: {result.stderr.decode('utf-8', errors='replace')[:500]}")
    return result.stdout


def city_from_path(path):
    hits = [city for city in CITIES if re.search(city, Path(path).name, re.IGNORECASE)]
    return hits[0] if len(hits) == 1 else None


def numeric_support(city, path, body):
    frame = pd.read_csv(io.BytesIO(body), na_values=["NA"])
    fields = list(frame.columns)
    lower = {str(col).lower(): col for col in fields}
    required = {name: lower.get(name.lower()) for name in ("year", "month", "day", "hour", "TEMP", "PRES")}
    pm_fields = [col for col in fields if re.fullmatch(r"PM(?:_.+)?|pm2[.]5", str(col), re.IGNORECASE)]
    result = {"city": city, "original_archive_member": path, "rows": int(len(frame)), "fields": fields, "required_fields": required, "pm_fields": pm_fields, "pm_support": {}}
    if any(value is None for value in required.values()) or not pm_fields:
        result["status"] = "STOP_REQUIRED_FIELDS"
        return result
    time = pd.to_datetime(pd.DataFrame({name: pd.to_numeric(frame[col], errors="coerce") for name, col in required.items() if name in ("year", "month", "day", "hour")}), errors="coerce")
    result["invalid_time_rows"] = int(time.isna().sum())
    result["duplicate_valid_hour_rows"] = int(time[time.notna()].duplicated().sum())
    result["first_valid_hour"] = time.min().isoformat() if time.notna().any() else None
    result["last_valid_hour"] = time.max().isoformat() if time.notna().any() else None
    result["calendar_span_days"] = int((time.max() - time.min()).days) if time.notna().any() else 0
    weather = {}
    for name in ("TEMP", "PRES"):
        values = pd.to_numeric(frame[required[name]], errors="coerce")
        valid = np.isfinite(values)
        weather[name] = {"finite_count": int(valid.sum()), "min": float(values[valid].min()) if valid.any() else None, "max": float(values[valid].max()) if valid.any() else None}
    result["weather_numeric"] = weather
    if result["invalid_time_rows"] or result["duplicate_valid_hour_rows"]:
        result["status"] = "STOP_TIME_IDENTITY"
        return result
    row = pd.DataFrame({"time": time, "TEMP": pd.to_numeric(frame[required["TEMP"]], errors="coerce"), "PRES": pd.to_numeric(frame[required["PRES"]], errors="coerce")}).set_index("time")
    common = np.isfinite(row["TEMP"]) & np.isfinite(row["PRES"]) & (row["PRES"] > 0)
    for field in pm_fields:
        pm = pd.to_numeric(frame[field], errors="coerce")
        observed = np.isfinite(pm) & (pm >= 0)
        row["pm"] = pm.to_numpy(dtype=float)
        # Timestamp lookup forbids row-offset substitution across missing hours.
        future = row["pm"].reindex(row.index + pd.Timedelta(hours=24)).to_numpy(dtype=float)
        pair = common.to_numpy() & observed.to_numpy() & np.isfinite(future) & (future >= 0)
        result["pm_support"][field] = {
            "observed_nonnegative_pm_rows": int(observed.sum()),
            "complete_real_24h_pairs": int(pair.sum()),
            "excluded_from_24h_pairs": int(len(row) - pair.sum()),
            "min_observed_pm": float(pm[observed].min()) if observed.any() else None,
            "max_observed_pm": float(pm[observed].max()) if observed.any() else None,
        }
    result["status"] = "NUMERIC_AUDIT_COMPLETE"
    return result


def main():
    for name in ("SOURCE_METADATA.json", "ARCHIVE_AUDIT.json", "NUMERIC_SUPPORT.json"):
        if (HERE / name).exists():
            raise FileExistsError(f"EXP050 existing result {name}; preserve prior attempt")
    source = {
        "run_id": RUN_ID, "official_page": PAGE, "official_original_download": DOWNLOAD,
        "UCI_ID": 394, "DOI": "10.24432/C52K58", "license_on_official_page": "CC BY 4.0",
        "official_description": "Five cities; hourly PM2.5 and meteorology; 2010-01-01 to 2015-12-31; NA missing",
        "known_schema_incompatibility": "Iws is cumulated wind speed, not EXP048's contemporaneous WSPM",
        "raw_copy_created": False,
    }
    save("SOURCE_METADATA.json", source)
    request = urllib.request.Request(DOWNLOAD, headers={"User-Agent": "EXP050-source-audit/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_BYTES:
            raise RuntimeError("official source exceeds frozen 10 MiB network budget")
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise RuntimeError("official source response exceeds frozen 10 MiB network budget")
    archive = {"run_id": RUN_ID, "network_requests": 1, "response_bytes": len(body), "outer_zip_members": [], "nested_archive_member": None, "inner_members": [], "status": None}
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as outer:
            archive["outer_zip_members"] = [{"path": info.filename, "uncompressed_bytes": info.file_size} for info in outer.infolist()]
            candidates = [info for info in outer.infolist() if info.filename.lower().endswith(".rar")]
            if len(candidates) != 1:
                archive["status"] = "STOP_RAR_MEMBER_NOT_UNIQUE"
                save("ARCHIVE_AUDIT.json", archive)
                print(archive["status"], flush=True)
                return
            rar_info = candidates[0]
            archive["nested_archive_member"] = rar_info.filename
            raw_rar = outer.read(rar_info)
    except zipfile.BadZipFile as exc:
        archive["status"] = "STOP_OUTER_ARCHIVE_PARSE"
        archive["error"] = repr(exc)
        save("ARCHIVE_AUDIT.json", archive)
        print(archive["status"], flush=True)
        return
    listed, members = rar_listing(raw_rar)
    archive["rar_listing_exit_code"] = listed.returncode
    archive["rar_listing_stderr"] = listed.stderr.decode("utf-8", errors="replace")[:1000]
    archive["inner_members"] = members
    if listed.returncode:
        archive["status"] = "STOP_RAR_PIPE_PARSE"
        save("ARCHIVE_AUDIT.json", archive)
        print(archive["status"], flush=True)
        return
    archive["status"] = "ARCHIVE_LISTED"
    save("ARCHIVE_AUDIT.json", archive)
    numeric = {"run_id": RUN_ID, "city_files": [], "non_beijing_qualifying_cities": [], "gate": None}
    for member in members:
        if not member.lower().endswith(".csv"):
            continue
        city = city_from_path(member)
        if city is None:
            numeric["city_files"].append({"original_archive_member": member, "status": "STOP_CITY_IDENTITY_UNKNOWN"})
            continue
        try:
            result = numeric_support(city, member, rar_member(raw_rar, member))
        except Exception as exc:
            result = {"city": city, "original_archive_member": member, "status": "STOP_MEMBER_NUMERIC_PARSE", "error": repr(exc)}
        numeric["city_files"].append(result)
    qualified = set()
    for result in numeric["city_files"]:
        if result.get("city") == "Beijing" or result.get("status") != "NUMERIC_AUDIT_COMPLETE" or result.get("calendar_span_days", 0) < 365:
            continue
        if any(entry["complete_real_24h_pairs"] >= 15000 for entry in result["pm_support"].values()):
            qualified.add(result["city"])
    numeric["non_beijing_qualifying_cities"] = sorted(qualified)
    numeric["gate"] = "EXTERNAL_COMMON_SCHEMA_SOURCE_READY" if len(qualified) >= 3 else "STOP_EXTERNAL_COMMON_SCHEMA_SOURCE_SUPPORT"
    save("NUMERIC_SUPPORT.json", numeric)
    print("CITY_FILES", len(numeric["city_files"]), "QUALIFIED", numeric["non_beijing_qualifying_cities"], "GATE", numeric["gate"], flush=True)


if __name__ == "__main__":
    main()
