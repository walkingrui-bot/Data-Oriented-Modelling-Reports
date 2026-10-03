"""Independently parse 25 fixed new BLA pages and four known anomalies."""

from __future__ import annotations

import csv
import random
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401

from select_gate_samples import prior_apps

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "BLA_PAGE_QA.csv"
ANOMALIES = ROOT / "BLA_ANOMALY_REVIEW.csv"


class TextTokens(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.tokens = []

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if cleaned:
            self.tokens.append(cleaned)


def parse_page(bla: str) -> tuple[str, str, int]:
    url = f"https://purplebooksearch.fda.gov/index.cfm?blaNo={bla}&event=productdetails"
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP022 BLA independent QA"})
    with urllib.request.urlopen(request, timeout=25) as response:
        body = response.read()
        status = response.status
    tokens = TextTokens()
    tokens.feed(body.decode("utf-8", errors="replace"))
    number = tokens.tokens[tokens.tokens.index("BLA Number") + 1].zfill(6)
    date = tokens.tokens[tokens.tokens.index("Original Approval Date") + 1]
    return number, date, status


def main() -> None:
    if QA.exists() or ANOMALIES.exists():
        raise RuntimeError("BLA QA outputs exist; preserve prior attempt")
    events = pd.read_parquet(ROOT / "derived/BLA_ORIGINAL_LICENSURE_CANDIDATES.parquet")
    used = prior_apps()
    for name in ("GATE_A_SAMPLE.csv", "GATE_B_SAMPLE.csv"):
        with (ROOT / name).open(newline="") as stream:
            used.update(row["application_no"] for row in csv.DictReader(stream))
    anomalies = set(events.loc[events.product_row_date_relation != "PAGE_EQUALS_A_PRODUCT_ROW", "application_no"])
    pool = sorted(set(events.loc[events.product_row_date_relation == "PAGE_EQUALS_A_PRODUCT_ROW", "application_no"]) - used)
    rng = random.Random(20261024)
    rng.shuffle(pool)
    chosen = pool[:25]
    assert len(chosen) == 25 and len(set(chosen)) == 25 and not (set(chosen) & used)
    by_bla = events.set_index("application_no").to_dict("index")
    reviewed = []
    for i, bla in enumerate(chosen, 1):
        row = by_bla[bla]
        number, date, status = parse_page(bla)
        reviewed.append({"sample_id": f"BLA-QA-{i:02d}", "bla_number": bla,
                         "source_url": row["source_url"], "http_status": status,
                         "page_bla_number": number, "page_original_date_text": date,
                         "first_extraction_date_iso": row["event_date"],
                         "page_date_equals_first_extraction": pd.to_datetime(date).date().isoformat() == row["event_date"],
                         "agent_decision": "PENDING", "agent_note": ""})
    with QA.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reviewed[0]))
        writer.writeheader()
        writer.writerows(reviewed)
    diagnostic = []
    for bla in sorted(anomalies):
        row = by_bla[bla]
        number, date, status = parse_page(bla)
        diagnostic.append({"bla_number": bla, "source_url": row["source_url"], "http_status": status,
                           "page_bla_number": number, "page_original_date_text": date,
                           "first_extraction_date_iso": row["event_date"],
                           "month_product_dates": row["product_row_dates"],
                           "relation": row["product_row_date_relation"],
                           "agent_decision": "PENDING", "agent_note": ""})
    with ANOMALIES.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(diagnostic[0]))
        writer.writeheader()
        writer.writerows(diagnostic)
    print({"qa_25": len(reviewed), "date_matches": sum(r["page_date_equals_first_extraction"] for r in reviewed),
           "number_matches": sum(r["bla_number"] == r["page_bla_number"] for r in reviewed),
           "known_anomalies": len(diagnostic)})


if __name__ == "__main__":
    main()
