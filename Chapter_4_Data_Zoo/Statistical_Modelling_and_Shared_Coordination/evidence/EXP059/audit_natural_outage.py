#!/usr/bin/env python3
"""EXP059 official-source audit of natural PM2.5 outages with real 24h outcomes."""

from __future__ import annotations

import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
P46 = HERE.parent / "STAT-PSYMOE-EXP046-20261002-001"
P47 = HERE.parent / "STAT-PSYMOE-EXP047-20261002-001"
META = json.loads((P46 / "SOURCE_METADATA.json").read_text())
PREVIOUS = json.loads((P47 / "NUMERIC_SUMMARY.json").read_text())
MAX_BYTES = 20 * 1024 * 1024
HELD_OUT = ("Aotizhongxin", "Wanshouxigong")
THRESHOLDS = {
    "train_same10": 500, "validation_same10": 100, "future_same10": 40,
    "station_2016": 40, "future_station_2": 10,
}


def load_original():
    request = urllib.request.Request(META["official_download"],
                                     headers={"User-Agent": "EXP059-natural-outage-source-audit/1"})
    with urllib.request.urlopen(request, timeout=120) as response:
        declared = response.headers.get("Content-Length")
        if declared and int(declared) > MAX_BYTES:
            raise RuntimeError("Official outer ZIP exceeds registered 20 MiB budget")
        body = response.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise RuntimeError("Official outer ZIP exceeds registered 20 MiB budget")
    frames = {}
    with zipfile.ZipFile(io.BytesIO(body)) as outer:
        nested_name = "PRSA2017_Data_20130301-20170228.zip"
        nested = outer.read(nested_name)
    with zipfile.ZipFile(io.BytesIO(nested)) as inner:
        for item in inner.infolist():
            basename = Path(item.filename).name
            match = re.fullmatch(r"PRSA_Data_(.+)_20130301-20170228\.csv", basename)
            if not match:
                continue
            station = match.group(1)
            with inner.open(item) as stream:
                frame = pd.read_csv(stream, na_values=["NA"])
            needed = {"year", "month", "day", "hour", "station", "PM2.5", "TEMP", "PRES", "WSPM"}
            if not needed <= set(frame.columns):
                raise RuntimeError(f"Missing original columns at {station}")
            if len(frame) != 35064 or set(frame.station.dropna().unique()) != {station}:
                raise RuntimeError(f"Original station identity or length failed: {station}")
            frame["time"] = pd.to_datetime(frame[["year", "month", "day", "hour"]])
            frame = frame.sort_values("time").set_index("time")
            if not frame.index.is_unique or len(frame.index) != 35064:
                raise RuntimeError(f"Original hourly uniqueness failed: {station}")
            frames[station] = frame[["PM2.5", "TEMP", "PRES", "WSPM"]]
    if set(frames) != set(PREVIOUS["qualifying_stations"]) or len(frames) != 12:
        raise RuntimeError("Twelve original qualified stations not present")
    first = next(iter(frames.values())).index
    if not all(first.equals(frame.index) for frame in frames.values()):
        raise RuntimeError("Station hourly grids differ")
    if first[0] != pd.Timestamp("2013-03-01 00:00:00") or first[-1] != pd.Timestamp("2017-02-28 23:00:00"):
        raise RuntimeError("Original hourly period differs")
    if not (first[24:] == first[:-24] + pd.Timedelta(hours=24)).all():
        raise RuntimeError("Future target index is not exact 24 hours")
    return frames, len(body), nested_name


def main():
    for name in ("SOURCE_SUPPORT.json", "STATION_YEAR_COUNTS.csv", "FAILURE.json"):
        if (HERE / name).exists():
            raise FileExistsError("Preserve existing attempt output: " + name)
    frames, response_bytes, nested_name = load_original()
    stations = sorted(frames)
    hours = frames[stations[0]].index
    pm = pd.DataFrame({station: frames[station]["PM2.5"] for station in stations}, index=hours)
    valid_pm = pd.DataFrame(np.isfinite(pm.to_numpy(float)) & (pm.to_numpy(float) >= 0),
                            index=hours, columns=stations)
    neighbor_total = valid_pm.sum(axis=1).to_numpy(dtype=int)
    station_rows = []
    domain_rows = {name: {} for name in THRESHOLDS}
    attrition = {name: {step: 0 for step in (
        "origin_original_na", "plus_real_24h_target", "plus_station_meteorology",
        "plus_eight_neighbor_PM", "eligible")}
        for name in THRESHOLDS}
    for station in stations:
        frame = frames[station]
        now = frame["PM2.5"].to_numpy(float)
        future = frame["PM2.5"].shift(-24).to_numpy(float)
        missing_now = np.isnan(now)
        valid_future = np.isfinite(future) & (future >= 0)
        met = frame[["TEMP", "PRES", "WSPM"]].to_numpy(float)
        valid_met = np.isfinite(met).all(axis=1)
        other_count = neighbor_total - valid_pm[station].to_numpy(dtype=int)
        enough_neighbors = other_count >= 8
        eligible = missing_now & valid_future & valid_met & enough_neighbors
        train_site = station not in HELD_OUT
        times = hours
        domains = {
            "train_same10": train_site & (times >= "2013-03-01") & (times < "2015-12-31"),
            "validation_same10": train_site & (times >= "2016-01-01") & (times < "2016-12-31"),
            "future_same10": train_site & (times >= "2017-01-01") & (times < "2017-02-28"),
            "station_2016": (not train_site) & (times >= "2016-01-01") & (times < "2016-12-31"),
            "future_station_2": (not train_site) & (times >= "2017-01-01") & (times < "2017-02-28"),
        }
        for name, window in domains.items():
            count = int((eligible & window).sum())
            domain_rows[name][station] = count
            attrition[name]["origin_original_na"] += int((missing_now & window).sum())
            attrition[name]["plus_real_24h_target"] += int((missing_now & valid_future & window).sum())
            attrition[name]["plus_station_meteorology"] += int((missing_now & valid_future & valid_met & window).sum())
            attrition[name]["plus_eight_neighbor_PM"] += count
            attrition[name]["eligible"] += count
        for year in (2013, 2014, 2015, 2016, 2017):
            year_window = times.year == year
            station_rows.append({
                "station": station, "year": year,
                "original_hours": int(year_window.sum()),
                "origin_original_na": int((missing_now & year_window).sum()),
                "na_with_true_24h_target": int((missing_now & valid_future & year_window).sum()),
                "na_target_and_station_meteorology": int((missing_now & valid_future & valid_met & year_window).sum()),
                "eligible_with_eight_neighbors": int((eligible & year_window).sum()),
            })
        print(station, "train", domain_rows["train_same10"][station],
              "validation", domain_rows["validation_same10"][station], flush=True)
    totals = {name: int(sum(station.values())) for name, station in domain_rows.items()}
    active = {name: {station: count for station, count in per_station.items() if count}
              for name, per_station in domain_rows.items()}
    train_sites = [station for station, n in domain_rows["train_same10"].items() if n >= 20]
    validation_sites = [station for station, n in domain_rows["validation_same10"].items() if n >= 10]
    future_sites = [station for station, n in domain_rows["future_same10"].items() if n >= 5]
    support = all(totals[name] >= THRESHOLDS[name] for name in THRESHOLDS)
    support &= len(train_sites) >= 5 and len(validation_sites) >= 5 and len(future_sites) >= 4
    support &= all(domain_rows["station_2016"][station] >= 10 and
                   domain_rows["future_station_2"][station] >= 3 for station in HELD_OUT)
    summary = {
        "run_id": "EXP059-SOURCE-001", "official_original_url": META["official_download"],
        "network_requests": 1, "response_bytes": response_bytes,
        "nested_original_member": nested_name, "original_station_count": len(stations),
        "common_original_hours": len(hours), "original_row_count": len(stations) * len(hours),
        "qualification": "natural original PM2.5 NA at origin, real exact 24h outcome, observed station meteorology, >=8 observed other stations",
        "thresholds": THRESHOLDS, "domain_counts": totals,
        "domain_by_station": domain_rows, "nonzero_station_counts": active,
        "attrition": attrition,
        "train_stations_at_least_20": train_sites,
        "validation_stations_at_least_10": validation_sites,
        "future_stations_at_least_5": future_sites,
        "held_out_stations": HELD_OUT,
        "gate": "NATURAL_OUTAGE_SOURCE_READY_FOR_DESIGN" if support else "STOP_NATURAL_OUTAGE_SUPPORT",
        "models_run": False,
    }
    pd.DataFrame(station_rows).to_csv(HERE / "STATION_YEAR_COUNTS.csv", index=False)
    (HERE / "SOURCE_SUPPORT.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print("GATE", summary["gate"], "COUNTS", json.dumps(totals), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not (HERE / "FAILURE.json").exists():
            (HERE / "FAILURE.json").write_text(json.dumps({
                "run_id": "EXP059-SOURCE-001", "error_type": type(exc).__name__,
                "error": str(exc), "existing_direct_outputs": sorted(p.name for p in HERE.iterdir()),
            }, ensure_ascii=False, indent=2) + "\n")
        raise
