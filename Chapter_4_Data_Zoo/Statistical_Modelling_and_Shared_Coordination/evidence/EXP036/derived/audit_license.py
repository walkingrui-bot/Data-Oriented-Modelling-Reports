"""EXP036-LICENSE-001: bounded official Zenodo metadata lookup, no data bytes."""

import json
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "SOURCE_METADATA.json"
URL = "https://zenodo.org/api/records/15672744"
CAP = 1024 * 1024


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    result = {"run_id": "EXP036-LICENSE-001", "metadata_url": URL, "requests": 1,
              "bytes_read": 0, "license_gate": "UNKNOWN"}
    try:
        request = urllib.request.Request(URL, headers={"User-Agent": "Research source metadata audit EXP036"})
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read(CAP + 1)
            result["http_status"] = response.status
        result["bytes_read"] = len(body)
        if len(body) > CAP:
            raise ValueError("API_METADATA_CAP_EXCEEDED")
        record = json.loads(body)
        metadata = record.get("metadata", {})
        license_value = metadata.get("license")
        files = [{"key": f.get("key"), "size": f.get("size"),
                  "download": f.get("links", {}).get("self") or f.get("links", {}).get("content")}
                 for f in record.get("files", [])]
        result.update({"record_id": record.get("id"), "doi": metadata.get("doi"),
                       "title": metadata.get("title"), "publication_date": metadata.get("publication_date"),
                       "access_right": metadata.get("access_right"), "license": license_value,
                       "files": files})
        license_id = license_value.get("id") if isinstance(license_value, dict) else license_value
        result["license_gate"] = "PASS_EXPLICIT_CC" if license_id in {
            "cc-by-4.0", "cc-by-sa-4.0", "cc0-1.0", "odc-by-1.0"} else "STOP_LICENSE_UNKNOWN"
    except Exception as exc:
        result["license_gate"] = "STOP_LICENSE_UNKNOWN"
        result["error"] = f"{type(exc).__name__}:{str(exc)[:240]}"
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
