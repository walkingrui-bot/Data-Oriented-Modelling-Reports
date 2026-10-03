"""EXP025-TIMESERIES-QA-001: fixed 25 persons, one bilateral task each."""

import csv
import io
import math
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASE = "https://physionet.org/files/parkinsons-disease-smartwatch/1.0.0/movement/timeseries/"
OUT = ROOT / "TIMESERIES_QA.csv"
FILE_CAP = 500_000


def inspect(subject_id, wrist):
    url = BASE + f"{subject_id}_Relaxed_{wrist}Wrist.txt"
    row = {"subject_id": subject_id, "wrist": wrist, "source_url": url, "http_status": "", "bytes_read": 0, "rows": 0, "columns": "", "numeric_cells": 0, "missing_cells": 0, "nonfinite_cells": 0, "status": ""}
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP025 timeseries QA"})
        with urllib.request.urlopen(request, timeout=35) as response:
            body = response.read(FILE_CAP + 1)
            row["http_status"] = response.status
        row["bytes_read"] = len(body)
        if len(body) > FILE_CAP:
            raise ValueError("FILE_OVER_500KB")
        reader = csv.reader(io.StringIO(body.decode("utf-8-sig")))
        counts = set()
        for values in reader:
            if not values:
                continue
            counts.add(len(values))
            row["rows"] += 1
            for value in values:
                if not value.strip():
                    row["missing_cells"] += 1
                    continue
                v = float(value)
                row["numeric_cells"] += 1
                row["nonfinite_cells"] += not math.isfinite(v)
        row["columns"] = ";".join(map(str, sorted(counts)))
        row["status"] = "READABLE_NUMERIC" if counts == {7} and row["rows"] == 2048 and row["missing_cells"] == 0 and row["nonfinite_cells"] == 0 else "NUMERIC_SHAPE_DIFFERENCE"
    except Exception as exc:
        row["status"] = f"{type(exc).__name__}:{str(exc)[:140]}"
    return row


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    tasks = [(f"{i:03d}", w) for i in range(1, 26) for w in ("Left", "Right")]
    rows = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(inspect, i, w): (i, w) for i, w in tasks}
        for future in as_completed(futures):
            rows.append(future.result())
    rows.sort(key=lambda r: (r["subject_id"], r["wrist"]))
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    print({"rows": len(rows), "readable_numeric": sum(r["status"] == "READABLE_NUMERIC" for r in rows), "bytes": sum(int(r["bytes_read"]) for r in rows), "statuses": sorted({r["status"] for r in rows})})


if __name__ == "__main__":
    main()
