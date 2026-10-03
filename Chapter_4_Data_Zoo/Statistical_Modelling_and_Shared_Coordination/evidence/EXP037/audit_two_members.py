"""EXP037 registered, bounded read of two original Zenodo ZIP members.

The source bytes live only in memory; this program writes derived diagnostics.
"""

import csv
import io
import json
import math
import struct
import urllib.request
import zipfile
import zlib
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
PREV = HERE.parent / "STAT-PSYMOE-EXP036-20261002-001"
METADATA = json.loads((PREV / "SOURCE_METADATA.json").read_text())
URL = METADATA["files"][0]["download"]
ZIP_SIZE = METADATA["files"][0]["size"]
NAMES = {
    "PD01": "Parkinson Dataset/Parkinson patients/1_10mSlow/01-RTSOCS - 2022.10.04-10.00.47.csv",
    "HC01": "Parkinson Dataset/Healthy patients/1_10mSlow/01RTSOCS - 2023.02.06-09.42.36.csv",
}


def get_range(start, end, budget):
    size = end - start + 1
    if size <= 0 or size > budget:
        raise ValueError(f"range size {size} exceeds request budget {budget}")
    req = urllib.request.Request(URL, headers={"Range": f"bytes={start}-{end}", "User-Agent": "EXP037-source-audit/1"})
    with urllib.request.urlopen(req, timeout=60) as response:
        status = response.status
        content_range = response.headers.get("Content-Range", "")
        if status != 206 or not content_range.startswith(f"bytes {start}-{end}/"):
            raise RuntimeError(f"range response invalid: {status}, {content_range}")
        body = response.read(size + 1)
    if len(body) != size:
        raise RuntimeError(f"range length {len(body)} != {size}")
    return body


def get_csv_member(info, tail_start):
    absolute_offset = tail_start + info.header_offset
    # Local name/extra may be at most 1 KiB for this bounded request.
    body = get_range(absolute_offset, absolute_offset + 1023 + info.compress_size, 1024 * 1024)
    if body[:4] != b"PK\x03\x04":
        raise RuntimeError("local ZIP header signature mismatch")
    name_len, extra_len = struct.unpack_from("<HH", body, 26)
    data_offset = 30 + name_len + extra_len
    if data_offset > 1024:
        raise RuntimeError(f"local header {data_offset} exceeds bounded allowance")
    packed = body[data_offset : data_offset + info.compress_size]
    if len(packed) != info.compress_size:
        raise RuntimeError("compressed member truncated")
    if info.compress_type == zipfile.ZIP_DEFLATED:
        raw = zlib.decompress(packed, -15)
    elif info.compress_type == zipfile.ZIP_STORED:
        raw = packed
    else:
        raise RuntimeError(f"unsupported ZIP method {info.compress_type}")
    if len(raw) != info.file_size:
        raise RuntimeError("uncompressed member length mismatch")
    return raw


def parse_member(raw):
    # UTF-8-sig handles BOM without changing the raw source.
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    columns = reader.fieldnames or []
    foot_col = next((c for c in columns if c.strip().lower() == "foot"), None)
    time_col = next((c for c in columns if c.strip().lower() in ("timestamp", "time", "time_stamp")), None)
    foot_counts = Counter()
    numeric = defaultdict(lambda: {"nonempty": 0, "finite": 0})
    times_by_foot = defaultdict(list)
    rows = 0
    for row in reader:
        rows += 1
        foot = (row.get(foot_col) or "").strip() if foot_col else ""
        foot_counts[foot] += 1
        if time_col:
            value = (row.get(time_col) or "").strip()
            try:
                number = float(value)
            except (ValueError, TypeError):
                number = math.nan
            times_by_foot[foot].append(number)
        for col in columns:
            if col == foot_col or col == time_col or col.startswith("p_"):
                continue
            value = (row.get(col) or "").strip()
            if value:
                numeric[col]["nonempty"] += 1
                try:
                    if math.isfinite(float(value)):
                        numeric[col]["finite"] += 1
                except ValueError:
                    pass
    time_diag = {}
    for foot, values in times_by_foot.items():
        finite = sum(math.isfinite(v) for v in values)
        increasing = all(math.isfinite(a) and math.isfinite(b) and b > a for a, b in zip(values, values[1:]))
        steps = sorted(b - a for a, b in zip(values, values[1:]) if math.isfinite(a) and math.isfinite(b))
        time_diag[foot] = {"finite": finite, "strictly_increasing": increasing, "median_raw_step": steps[len(steps) // 2] if steps else None}
    return {
        "row_count": rows,
        "columns": columns,
        "foot_column": foot_col,
        "time_column": time_col,
        "foot_counts": dict(foot_counts),
        "time_by_foot": time_diag,
        "numeric_nonpressure_columns": dict(numeric),
    }


def main():
    tail_start = ZIP_SIZE - 4 * 1024 * 1024
    tail = get_range(tail_start, ZIP_SIZE - 1, 4 * 1024 * 1024)
    with zipfile.ZipFile(io.BytesIO(tail)) as archive:
        infos = {info.filename: info for info in archive.infolist()}
    output = {"run_id": "EXP037-SCHEMA-001", "zip_url": URL, "tail_bytes": len(tail), "members": {}}
    for label, name in NAMES.items():
        info = infos[name]
        if info.file_size > 2 * 1024 * 1024 or info.compress_size > 1024 * 1024 - 1024:
            raise RuntimeError(f"member exceeds budget: {label}")
        raw = get_csv_member(info, tail_start)
        output["members"][label] = {"original_member_path": name, "compressed_bytes": info.compress_size, "uncompressed_bytes": info.file_size, **parse_member(raw)}
    (HERE / "SOURCE_AUDIT.json").write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"run_id": output["run_id"], "tail_bytes": output["tail_bytes"], "members": {k: {"rows": v["row_count"], "foot_counts": v["foot_counts"], "time_column": v["time_column"]} for k, v in output["members"].items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
