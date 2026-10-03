"""Read official BLA-level Original Approval Date pages serially.

No HTML bodies are saved. Each response/result is appended to the one audit
file so a source block or interruption remains visible.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "BLA_PAGE_AUDIT.csv"
EVENTS = ROOT / "derived/BLA_ORIGINAL_LICENSURE_CANDIDATES.parquet"
DIAG = ROOT / "derived/BLA_PAGE_DIAGNOSTICS.json"
PREVIOUS = ROOT / "BLA_PAGE_AVAILABILITY.csv"


def read_page(bla: str) -> dict:
    url = f"https://purplebooksearch.fda.gov/index.cfm?blaNo={bla}&event=productdetails"
    result = {"bla_number": bla, "source_url": url, "http_status": "", "retrieved_at_utc": "",
              "original_approval_date": "", "last_modified": "", "content_bytes": "", "issue": "", "attempts": 0,
              "retrieval_segment": "EXP022-BLA-SOURCE-002"}
    for attempt in (1, 2):
        result["attempts"] = attempt
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP022 BLA source audit"})
            with urllib.request.urlopen(request, timeout=25) as response:
                blob = response.read()
                body = blob.decode("utf-8", errors="replace")
                result["http_status"] = str(response.status)
                result["retrieved_at_utc"] = datetime.now(timezone.utc).isoformat()
                result["last_modified"] = response.headers.get("Last-Modified") or ""
                result["content_bytes"] = len(blob)
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
        time.sleep(0.2)
    return result


def main() -> None:
    if AUDIT.exists() or EVENTS.exists() or DIAG.exists():
        raise RuntimeError("BLA source-002 output exists; preserve previous attempt")
    products = pd.read_parquet(ROOT / "derived/SOURCE_SEMANTIC_CANDIDATES.parquet")
    products = products[products["application_type"] == "BLA"]
    bla_ids = sorted(products["application_no"].unique())
    assert len(bla_ids) == 750
    earlier = {}
    with PREVIOUS.open(newline="") as stream:
        for row in csv.DictReader(stream):
            earlier[row["bla_number"]] = row
    assert len(earlier) == 15 and set(earlier) <= set(bla_ids)
    columns = ["bla_number", "source_url", "http_status", "retrieved_at_utc", "original_approval_date",
               "last_modified", "content_bytes", "issue", "attempts", "retrieval_segment"]
    results = []
    bytes_read = 0
    with AUDIT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for i, bla in enumerate(bla_ids, 1):
            if bla in earlier:
                old = earlier[bla]
                row = {**{k: "" for k in columns}, **old, "retrieval_segment": "EXP022-BLA-SOURCE-001"}
            else:
                row = read_page(bla)
                bytes_read += int(row["content_bytes"] or 0)
                time.sleep(0.12)
            writer.writerow({k: row.get(k, "") for k in columns})
            stream.flush()
            results.append(row)
            if i % 50 == 0:
                print(f"BLA pages {i}/{len(bla_ids)}; dates={sum(bool(x['original_approval_date']) for x in results)}; bytes={bytes_read}", flush=True)
            if bytes_read > 4 * 1024**3:
                raise RuntimeError("EXP022 4 GiB network budget reached; partial audit retained")
    product_by_bla = defaultdict(list)
    for row in products.to_dict("records"):
        product_by_bla[row["application_no"]].append(row)
    events = []
    relations = Counter()
    for row in results:
        if not row["original_approval_date"]:
            continue
        bla = row["bla_number"]
        dates = sorted({x["event_date"] for x in product_by_bla[bla]})
        original = row["original_approval_date"]
        if original < dates[0]:
            relation = "PAGE_BEFORE_ALL_PRODUCT_ROWS"
        elif original > dates[-1]:
            relation = "PAGE_AFTER_ALL_PRODUCT_ROWS"
        elif original in dates:
            relation = "PAGE_EQUALS_A_PRODUCT_ROW"
        else:
            relation = "PAGE_BETWEEN_PRODUCT_DATES"
        relations[relation] += 1
        events.append({
            "event_id": f"FDA:PB:BLA:ORIGINAL:{bla}:{original}",
            "drug_regulatory_id": f"BLA:{bla}", "application_no": bla,
            "application_type": "BLA", "product_no": None,
            "event_type": "BLA_ORIGINAL_LICENSURE", "event_scope": "BLA_LICENSE",
            "event_date": original, "document_date": None, "document_signature_date": None,
            "source": "purple_book_product_details", "source_url": row["source_url"],
            "source_row_key": f"BLA:{bla}:Original Approval Date",
            "source_snapshot": f"live page retrieved {row['retrieved_at_utc']}",
            "source_release_date": row["last_modified"] or None,
            "retrieved_at": row["retrieved_at_utc"], "public_first_date": None,
            "license_type": "351(a)", "is_derived": False, "derivation_rule": None,
            "quality_tier": "PENDING_MANUAL_GATES",
            "product_rows_in_august_snapshot": len(product_by_bla[bla]),
            "product_row_date_relation": relation,
            "product_row_dates": "|".join(dates),
            "transformation_script": "derived/build_bla_original_pages.py v0.1",
        })
    frame = pd.DataFrame(events)
    if len(frame):
        assert frame["application_no"].is_unique and frame["event_id"].is_unique
    frame.to_parquet(EVENTS, index=False)
    diag = {"run_id": "EXP022-BLA-SOURCE-002", "attempted_unique_bla": len(bla_ids),
            "prior_15_reused": len(earlier), "successful_page_dates": len(events),
            "failure_counts": dict(Counter(x["issue"] for x in results if x["issue"])),
            "page_vs_monthly_product_relation": dict(relations),
            "new_network_bytes_read": bytes_read,
            "source_note": "Official current product-details pages give BLA-level Original Approval Date; August 2026 monthly product rows have separate Approval Date. Pages are not historical first-public evidence."}
    DIAG.write_text(json.dumps(diag, indent=2) + "\n")
    print(json.dumps(diag, indent=2), flush=True)


if __name__ == "__main__":
    main()
