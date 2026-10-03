"""Probe fixed, new BLA semantic-sample product pages for BLA-level dates."""

from __future__ import annotations

import csv
import re
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "BLA_PAGE_AVAILABILITY.csv"


def read_page(bla: str) -> dict:
    url = f"https://purplebooksearch.fda.gov/index.cfm?blaNo={bla}&event=productdetails"
    result = {"bla_number": bla, "source_url": url, "http_status": "", "retrieved_at_utc": "",
              "original_approval_date": "", "issue": "", "attempts": 0}
    for attempt in (1, 2):
        result["attempts"] = attempt
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP022 BLA source audit"})
            with urllib.request.urlopen(request, timeout=25) as response:
                body = response.read().decode("utf-8", errors="replace")
                result["http_status"] = str(response.status)
                result["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
            number = re.search(r"BLA Number</strong>\s*<br>\s*(\d+)", body, re.I)
            date = re.search(r"Original Approval Date</strong>\s*<br>\s*([^<]+)", body, re.I)
            if not number or number.group(1).zfill(6) != bla:
                result["issue"] = "BLA_NUMBER_NOT_CONFIRMED"
            elif not date or not date.group(1).strip():
                result["issue"] = "ORIGINAL_APPROVAL_DATE_ABSENT"
            else:
                result["original_approval_date"] = datetime.strptime(date.group(1).strip(), "%B %d, %Y").date().isoformat()
            return result
        except Exception as exc:
            result["issue"] = f"{type(exc).__name__}: {exc}"
    return result


def main() -> None:
    if OUT.exists():
        raise RuntimeError("BLA page availability output exists; preserve prior attempt")
    with (ROOT / "GATE_B_SAMPLE.csv").open(newline="") as stream:
        rows = [r for r in csv.DictReader(stream) if r["stratum"] == "B_PURPLE_BLA"]
    results = [read_page(r["application_no"]) for r in rows]
    with OUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(results[0]))
        writer.writeheader()
        writer.writerows(results)
    print({"attempted": len(results), "full_year_page_dates": sum(bool(r["original_approval_date"]) for r in results),
           "issues": {x: sum(r["issue"] == x for r in results) for x in sorted({r["issue"] for r in results})}})


if __name__ == "__main__":
    main()
