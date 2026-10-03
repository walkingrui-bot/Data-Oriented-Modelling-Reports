"""Resolve Purple Book two-digit year with official full-year BLA product pages."""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SOURCE = json.loads((ROOT / "SOURCE_INDEX.json").read_text())["sources"]["purple_book_august_2026"]
PAGE_PATTERN = "https://purplebooksearch.fda.gov/index.cfm?blaNo={}&event=productdetails"


def read_page(app: str) -> dict:
    url = PAGE_PATTERN.format(app)
    result = {"bla_number": app, "source_url": url, "original_approval_date_full_year": "",
              "retrieved_at_utc": "", "http_status": "", "issue": ""}
    for attempt in (1, 2):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP021 research"}), timeout=25) as response:
                body = response.read().decode("utf-8", errors="replace")
                result["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
                result["http_status"] = str(response.status)
            app_match = re.search(r"BLA Number</strong>\s*<br>\s*(\d+)", body, re.I)
            date_match = re.search(r"Original Approval Date</strong>\s*<br>\s*([^<]+)", body, re.I)
            if not app_match or app_match.group(1).zfill(6) != app:
                result["issue"] = "BLA_ID_MISMATCH_OR_ABSENT"
            elif not date_match or not date_match.group(1).strip():
                result["issue"] = "FULL_YEAR_DATE_ABSENT"
            else:
                result["original_approval_date_full_year"] = datetime.strptime(date_match.group(1).strip(), "%B %d, %Y").date().isoformat()
            return result
        except Exception as error:
            result["issue"] = f"{type(error).__name__}: {error}; attempt={attempt}"
    return result


def main() -> None:
    req = urllib.request.Request(SOURCE["source_url"], headers={"User-Agent": "Mozilla/5.0 EXP021 research"})
    with urllib.request.urlopen(req, timeout=60) as response:
        blob = response.read()
        if response.headers.get("Last-Modified") != SOURCE["last_modified"] or len(blob) != SOURCE["bytes_read"]:
            raise RuntimeError("Purple Book CSV changed; source preflight must be repeated")
    rows = list(csv.reader(io.StringIO(blob.decode("utf-8-sig", errors="replace"))))
    header = rows[34]
    apps = sorted({dict(zip(header, row))["BLA Number"].zfill(6) for row in rows[35:]
                   if len(row) == len(header) and row[2].strip() and row[5].strip() == "351(a)" and row[17].strip() == "Original"})
    with ThreadPoolExecutor(max_workers=16) as pool:
        result = list(pool.map(read_page, apps))
    frame = pd.DataFrame(result)
    frame.to_parquet(ROOT / "derived" / "PURPLE_FULL_YEAR_APPROVAL_DATES.parquet", index=False)
    diagnostic = {"run_id": "EXP021-PURPLE-YEAR-001", "input_unique_bla": len(apps),
                  "page_full_year_resolved": int((frame["original_approval_date_full_year"] != "").sum()),
                  "issue_counts": frame["issue"].value_counts().to_dict(),
                  "retrieved_at_utc": datetime.now(timezone.utc).isoformat()}
    (ROOT / "derived" / "PURPLE_YEAR_DIAGNOSTICS.json").write_text(json.dumps(diagnostic, indent=2) + "\n")
    print(json.dumps(diagnostic, indent=2))


if __name__ == "__main__":
    main()
