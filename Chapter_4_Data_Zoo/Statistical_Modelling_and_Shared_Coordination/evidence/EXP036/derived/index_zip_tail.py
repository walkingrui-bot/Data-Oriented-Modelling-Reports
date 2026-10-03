"""EXP036-ZIPINDEX-001: bounded tail-range ZIP central directory, paths only."""

import csv
import io
import json
import urllib.request
import zipfile
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
METADATA = ROOT / "SOURCE_METADATA.json"
INDEX = ROOT / "ZIP_MEMBER_INDEX.csv"
DIAG = ROOT / "ZIP_DIAGNOSTICS.json"
TAIL_CAP = 4 * 1024 * 1024


def main():
    if INDEX.exists() or DIAG.exists():
        raise FileExistsError("Preserve EXP036-ZIPINDEX-001 output")
    meta = json.loads(METADATA.read_text())
    if meta["license_gate"] != "PASS_EXPLICIT_CC" or len(meta["files"]) != 1:
        raise ValueError("License gate or archive identity not passed")
    url = meta["files"][0]["download"]
    result = {"run_id": "EXP036-ZIPINDEX-001", "source_zip_url": url,
              "range": f"bytes=-{TAIL_CAP}", "request_count": 1,
              "body_bytes_read": 0, "status": "UNKNOWN", "raw_archive_saved": False}
    try:
        request = urllib.request.Request(url, headers={
            "User-Agent": "Research ZIP directory audit EXP036", "Range": f"bytes=-{TAIL_CAP}"})
        with urllib.request.urlopen(request, timeout=40) as response:
            result["http_status"] = response.status
            result["content_range"] = response.headers.get("Content-Range")
            body = response.read(TAIL_CAP+1)
        result["body_bytes_read"] = len(body)
        if result["http_status"] != 206 or not result["content_range"] or len(body) > TAIL_CAP:
            raise ValueError("RANGE_NOT_SUPPORTED_WITHIN_FROZEN_CAP")
        with zipfile.ZipFile(io.BytesIO(body)) as zf:
            infos = zf.infolist()
        with INDEX.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["member_path", "uncompressed_bytes", "compressed_bytes", "directory"])
            writer.writeheader()
            for info in infos:
                writer.writerow({"member_path": info.filename, "uncompressed_bytes": info.file_size,
                                 "compressed_bytes": info.compress_size, "directory": info.is_dir()})
        result["status"] = "CENTRAL_DIRECTORY_INDEXED"
        result["member_count"] = len(infos)
        result["file_count"] = sum(not info.is_dir() for info in infos)
        result["top_level"] = dict(Counter(info.filename.split("/")[0] for info in infos))
        result["first_file_paths"] = [info.filename for info in infos if not info.is_dir()][:20]
    except Exception as exc:
        result["status"] = "STOP_ZIP_INDEX_UNAVAILABLE"
        result["error"] = f"{type(exc).__name__}:{str(exc)[:240]}"
    DIAG.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    if result["status"] != "CENTRAL_DIRECTORY_INDEXED":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
