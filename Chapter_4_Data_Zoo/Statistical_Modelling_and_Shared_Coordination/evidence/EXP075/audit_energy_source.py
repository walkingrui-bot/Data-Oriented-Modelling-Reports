"""EXP075 source-only chronology/support audit of UCI374, without raw copies."""

from __future__ import annotations

import csv
import io
import json
import math
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
URL = "https://archive.ics.uci.edu/static/public/374/appliances%2Benergy%2Bprediction.zip"
MAX_BYTES = 20 * 1024 * 1024
INDOOR = [v for i in range(1, 10) for v in (f"T{i}", f"RH_{i}")]
WEATHER = ["T_out", "Press_mm_hg", "RH_out", "Windspeed", "Visibility", "Tdewpoint"]
REQUIRED = ["date", "Appliances", *INDOOR, *WEATHER]


def fetch_csv() -> tuple[bytes, int, str, list[str]]:
    request = urllib.request.Request(URL, headers={"User-Agent": "StatPsyMoE-EXP075-source-audit/1.0"})
    with urllib.request.urlopen(request, timeout=90) as response:
        length = response.headers.get("Content-Length")
        if length is not None and int(length) > MAX_BYTES:
            raise ValueError("official archive above 20MiB budget")
        archive_bytes = response.read(MAX_BYTES + 1)
    if len(archive_bytes) > MAX_BYTES:
        raise ValueError("official archive above 20MiB budget")
    zf = zipfile.ZipFile(io.BytesIO(archive_bytes))
    found = [name for name in zf.namelist() if name.endswith("energydata_complete.csv")]
    if len(found) != 1:
        raise ValueError(f"official CSV member expected once, got {found}")
    info = zf.getinfo(found[0])
    if info.file_size > 25 * 1024 * 1024:
        raise ValueError("official CSV above 25MiB decompressed bound")
    return zf.read(found[0]), len(archive_bytes), found[0], zf.namelist()


def main() -> None:
    raw, download_bytes, csv_member, members = fetch_csv()
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig")))
    columns = list(reader.fieldnames or [])
    missing_columns = [name for name in REQUIRED if name not in columns]
    if missing_columns:
        result = {"missing_required_columns": missing_columns, "actual_columns": columns,
                  "gate_result": "STOP_ENERGY_CHRONOLOGY_OR_SUPPORT", "model_fits": 0}
        (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
        return
    dates, target, complete = [], [], []
    invalid_dates = 0
    negative_targets = 0
    per_column_bad = {name: 0 for name in REQUIRED if name != "date"}
    for row in reader:
        try:
            stamp = datetime.strptime(row["date"], "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            invalid_dates += 1
            stamp = None
        dates.append(stamp)
        finite = True
        for name in per_column_bad:
            try:
                value = float(row[name])
            except (ValueError, TypeError):
                value = float("nan")
            if not math.isfinite(value):
                per_column_bad[name] += 1
                finite = False
            if name == "Appliances":
                target.append(value)
                negative_targets += int(math.isfinite(value) and value < 0)
        complete.append(finite and stamp is not None)
    n = len(dates)
    chronological = invalid_dates == 0 and all(dates[i] < dates[i + 1] for i in range(n - 1))
    ten_min = sum(dates[i + 1] - dates[i] == timedelta(minutes=10)
                  for i in range(n - 1) if dates[i] is not None and dates[i + 1] is not None)
    candidate_count = max(0, n - 6)
    boundary_train, boundary_val = int(n * 0.70), int(n * 0.85)
    partitions = {name: {"pairs": 0, "target_days": set(), "first_target": None, "last_target": None}
                  for name in ("train", "validation", "test")}
    valid_pairs = 0
    for i in range(candidate_count):
        j = i + 6
        if not (complete[i] and math.isfinite(target[j]) and dates[i] is not None and dates[j] is not None
                and dates[j] - dates[i] == timedelta(hours=1)):
            continue
        valid_pairs += 1
        split = "train" if j < boundary_train else "validation" if j < boundary_val else "test"
        p = partitions[split]
        p["pairs"] += 1
        p["target_days"].add(dates[j].date().isoformat())
        iso = dates[j].isoformat(sep=" ")
        p["first_target"] = iso if p["first_target"] is None else p["first_target"]
        p["last_target"] = iso
    for p in partitions.values():
        p["different_target_dates"] = len(p.pop("target_days"))
    checks = {
        "required_columns_present": not missing_columns,
        "at_least_19000_rows": n >= 19000,
        "dates_unique_strictly_increasing": chronological,
        "ten_minute_adjacency_at_least_99pct": n > 1 and ten_min / (n - 1) >= 0.99,
        "required_fields_complete_at_least_95pct": n > 0 and sum(complete) / n >= 0.95,
        "no_negative_appliance_values": negative_targets == 0,
        "exact_one_hour_pairs_at_least_99pct": candidate_count > 0 and valid_pairs / candidate_count >= 0.99,
        "train_at_least_10000_pairs_60_days": partitions["train"]["pairs"] >= 10000 and partitions["train"]["different_target_dates"] >= 60,
        "validation_at_least_2000_pairs_20_days": partitions["validation"]["pairs"] >= 2000 and partitions["validation"]["different_target_dates"] >= 20,
        "test_at_least_2000_pairs_20_days": partitions["test"]["pairs"] >= 2000 and partitions["test"]["different_target_dates"] >= 20,
    }
    result = {"research_id": "STAT-PSYMOE-EXP075-20261002-001",
              "attempt_id": "EXP075-SOURCE-001", "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "official_url": URL, "official_page": "https://archive.ics.uci.edu/dataset/374/appliances-energy-prediction",
              "citation": "Candanedo, L. (2017). Appliances Energy Prediction. UCI. doi:10.24432/C5VC8G; CC BY 4.0.",
              "download_bytes": download_bytes, "csv_member": csv_member,
              "archive_member_count": len(members), "csv_bytes": len(raw),
              "actual_columns": columns, "required_columns": REQUIRED,
              "source_rows": n, "source_first_date": dates[0].isoformat(sep=" ") if dates[0] else None,
              "source_last_date": dates[-1].isoformat(sep=" ") if dates[-1] else None,
              "source_timezone": "not established in official data description",
              "invalid_dates": invalid_dates, "ten_minute_adjacencies": ten_min,
              "required_complete_rows": sum(complete), "negative_appliance_rows": negative_targets,
              "bad_values_by_required_column": per_column_bad,
              "target_position_boundaries": {"train_end_exclusive": boundary_train,
                                             "validation_end_exclusive": boundary_val},
              "candidate_one_hour_pairs": candidate_count, "valid_one_hour_pairs": valid_pairs,
              "partitions": partitions, "gates": checks,
              "gate_result": "REAL_ENERGY_TEMPORAL_SOURCE_READY_FOR_STAT_DESIGN" if all(checks.values()) else "STOP_ENERGY_CHRONOLOGY_OR_SUPPORT",
              "model_fits": 0, "test_performance_scores": 0}
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"download_bytes": download_bytes, "rows": n,
                      "first": result["source_first_date"], "last": result["source_last_date"],
                      "ten_minute_adjacency_ratio": ten_min / (n - 1),
                      "complete_rows": sum(complete), "valid_one_hour_pairs": valid_pairs,
                      "partitions": partitions, "gates": checks,
                      "decision": result["gate_result"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
