"""Deterministic manual-review register with in-memory FDA document reads."""

from __future__ import annotations

import csv
import html
import io
import random
import re
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261003


def sample() -> list[dict]:
    events = pd.read_parquet(ROOT / "derived" / "REGULATORY_EVENT_A.parquet").fillna("")
    audit = pd.read_csv(ROOT / "crosswalk_audit.csv", dtype=str).fillna("")
    previous = pd.read_csv(ROOT / "derived" / "failed_MANUAL_A_002" / "MANUAL_VALIDATION.csv", dtype=str).fillna("")
    prior_apps = set(previous.loc[previous["review_type"] != "DATE_SCOPE_CONFLICT", "application_number"])
    prior_conflicts = set(previous.loc[previous["review_type"] == "DATE_SCOPE_CONFLICT", "record_id"])
    rng = random.Random(SEED)
    selected = []
    for typ, n in (("NDA", 30), ("BLA", 10)):
        eligible = events[(events["event_scope"] == "APPLICATION") & (events["application_type"] == typ)]
        eligible = eligible[~eligible["application_number"].isin(prior_apps)]
        eligible = eligible[eligible["original_document_url"].str.match(r"^https?://[^; ]+\.pdf$", case=False)]
        # Exactly one original approval candidate per application for this review stratum.
        eligible = eligible.sort_values(["approval_date", "event_id"]).drop_duplicates("application_number")
        for _, e in eligible.iloc[rng.sample(range(len(eligible)), n)].iterrows():
            selected.append({"review_type": "ORIGINAL_APPROVAL_LETTER", "record_id": e["event_id"],
                             "automated_value": e["approval_date"], "application_number": e["application_number"],
                             "product_number": "", "application_type": typ, "checked_source": e["original_document_url"],
                             "secondary_source": e["source_url"], "right_date": "", "left_source": e["approval_source"]})
    purple = events[(events["approval_source"] == "FDA_PURPLE_BOOK_AUGUST_2026_XLSX")]
    fda_apps = set(events.loc[events["approval_source"] == "DRUGS_AT_FDA_SUBMISSIONS", "application_number"])
    purple = purple[~purple["application_number"].isin(fda_apps)]
    purple = purple[~purple["application_number"].isin(prior_apps)]
    purple = purple.sort_values(["approval_date", "event_id"]).drop_duplicates("application_number")
    for _, e in purple.iloc[rng.sample(range(len(purple)), 10)].iterrows():
        selected.append({"review_type": "PURPLE_ORIGINAL_APPROVAL_PAGE", "record_id": e["event_id"],
                         "automated_value": e["approval_date"], "application_number": e["application_number"],
                         "product_number": e["product_number"], "application_type": "BLA",
                         "checked_source": f"https://purplebooksearch.fda.gov/index.cfm?blaNo={e['application_number']}&event=productdetails",
                         "secondary_source": e["source_url"], "right_date": "", "left_source": e["approval_source"]})
    conflict = audit[(audit["comparison_status"] == "CONFLICT") & (audit["left_source"] == "FDA_ORANGE_BOOK_PRODUCTS")]
    conflict = conflict[~conflict["audit_id"].isin(prior_conflicts)]
    for _, a in conflict.iloc[rng.sample(range(len(conflict)), 20)].iterrows():
        selected.append({"review_type": "DATE_SCOPE_CONFLICT", "record_id": a["audit_id"],
                         "automated_value": a["left_date"], "application_number": a["application_number"],
                         "product_number": a["product_number"], "application_type": "NDA",
                         "checked_source": f"https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo={a['application_number']}",
                         "secondary_source": "https://www.fda.gov/media/76860/download?attachment",
                         "right_date": a["right_dates"], "left_source": a["left_source"]})
    assert len(selected) == 70
    return selected


def load(url: str) -> tuple[bytes, str]:
    request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP021 research"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read(), f"HTTP {response.status}; {response.headers.get('Content-Type', '')}"


def text_window(raw: str, needle: str, span: int = 150) -> str:
    pos = raw.lower().find(needle.lower())
    if pos < 0:
        return ""
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", raw[max(0, pos-span):pos+len(needle)+span]))).strip()


def inspect(row: dict) -> dict:
    row = dict(row)
    row.update({"verified_value": "", "source_excerpt": "", "match": "PENDING_HUMAN", "issue_type": "",
                "note": "", "fetch_status": "", "manual_reviewer": ""})
    for attempt in (1, 2):
        try:
            blob, status = load(row["checked_source"])
            row["fetch_status"] = f"{status}; bytes={len(blob)}; attempt={attempt}"
            break
        except Exception as error:
            row["fetch_status"] = f"{type(error).__name__}: {error}; attempt={attempt}"
    else:
        row["issue_type"] = "SOURCE_UNREACHABLE"
        return row
    if row["review_type"] == "ORIGINAL_APPROVAL_LETTER":
        if not blob.startswith(b"%PDF"):
            row["issue_type"] = "NON_PDF_RETURN"
            return row
        try:
            pdf = PdfReader(io.BytesIO(blob))
            first = pdf.pages[0].extract_text() or ""
            last = pdf.pages[-1].extract_text() or ""
            signatures = re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", last)
            parsed = []
            for item in signatures:
                try:
                    parsed.append(datetime.strptime(item, "%m/%d/%Y").date().isoformat())
                except ValueError:
                    pass
            row["verified_value"] = "|".join(sorted(set(parsed)))
            row["source_excerpt"] = re.sub(r"\s+", " ", first[:500] + " SIGNATURE_PAGE: " + last[-450:])
            if not row["verified_value"]:
                row["issue_type"] = "NO_EXTRACTABLE_SIGNATURE_DATE"
        except Exception as error:
            row["issue_type"] = f"PDF_PARSE_{type(error).__name__}"
    elif row["review_type"] == "PURPLE_ORIGINAL_APPROVAL_PAGE":
        body = blob.decode("utf-8", errors="replace")
        match = re.search(r"Original Approval Date</strong>\s*<br>\s*([^<]+)", body, re.I)
        if match:
            try:
                row["verified_value"] = datetime.strptime(match.group(1).strip(), "%B %d, %Y").date().isoformat()
            except ValueError:
                row["issue_type"] = "PURPLE_DATE_PARSE"
        else:
            row["issue_type"] = "PURPLE_ORIGINAL_DATE_ABSENT"
        row["source_excerpt"] = text_window(body, "BLA Number", 70) + " || " + text_window(body, "Original Approval Date", 70)
    else:
        body = blob.decode("utf-8", errors="replace")
        left_display = datetime.fromisoformat(row["automated_value"]).strftime("%m/%d/%Y")
        right_display = "|".join(datetime.fromisoformat(d).strftime("%m/%d/%Y") for d in row["right_date"].split("|") if d)
        row["verified_value"] = ("LEFT_FOUND" if left_display in body else "LEFT_MISSING") + ";" + ("ORIG_FOUND" if any(d in body for d in right_display.split("|")) else "ORIG_MISSING")
        row["source_excerpt"] = "PRODUCT_DATE: " + text_window(body, left_display, 190) + " || APPLICATION_DATE: " + text_window(body, right_display.split("|")[0], 190)
    return row


def main() -> None:
    selected = sample()
    with ThreadPoolExecutor(max_workers=4) as pool:
        result = list(pool.map(inspect, selected))
    fields = ["review_type", "record_id", "automated_value", "application_number", "product_number",
              "application_type", "checked_source", "secondary_source", "right_date", "left_source",
              "verified_value", "source_excerpt", "match", "issue_type", "note", "fetch_status", "manual_reviewer"]
    with (ROOT / "MANUAL_VALIDATION.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(result)
    print(pd.DataFrame(result).groupby(["review_type", "issue_type", "verified_value"], dropna=False).size().reset_index(name="n").head(30).to_string(index=False))
    print(f"SAMPLE_ROWS={len(result)} SOURCE_ERRORS={sum(bool(r['issue_type']) for r in result)}")


if __name__ == "__main__":
    main()
