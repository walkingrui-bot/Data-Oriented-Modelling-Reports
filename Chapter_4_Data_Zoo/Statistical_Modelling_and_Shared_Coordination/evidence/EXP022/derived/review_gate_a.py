"""Create field-level evidence for the fixed EXP022 ETL fidelity sample."""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401

sys.path.append("/Users/rui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages")
import openpyxl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads((ROOT / "SOURCE_INDEX.json").read_text())["sources"]
OUT = ROOT / "GATE_A_REVIEW.csv"


def fetch(name: str) -> bytes:
    src = SOURCES[name]
    request = urllib.request.Request(src["source_url"], headers={"User-Agent": "Mozilla/5.0 EXP022 gate-A fidelity audit"})
    with urllib.request.urlopen(request, timeout=90) as response:
        blob = response.read()
        if response.headers.get("Last-Modified") != src["last_modified"] or len(blob) != src["bytes_read"]:
            raise RuntimeError(f"Source metadata changed during Gate A: {name}")
    return blob


def row_by_physical_line(archive: zipfile.ZipFile, filename: str, delimiter: str, physical_lines: set[int]) -> dict[int, dict]:
    with archive.open(filename) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline=""), delimiter=delimiter)
        return {line: {k: v.strip() for k, v in row.items()} for line, row in enumerate(reader, 2) if line in physical_lines}


def padded(value: str, width: int) -> str:
    d = re.sub(r"\D", "", str(value))
    return d.zfill(width) if d else ""


def full_date(value: str) -> str:
    value = str(value).strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", value):
        return value[:10]
    for form in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value, form).date().isoformat()
        except ValueError:
            pass
    return ""


def main() -> None:
    if OUT.exists():
        raise RuntimeError("Gate A review output exists; preserve prior attempt")
    with (ROOT / "GATE_A_SAMPLE.csv").open(newline="") as stream:
        selected = list(csv.DictReader(stream))
    events = pd.read_parquet(ROOT / "derived/SOURCE_SEMANTIC_CANDIDATES.parquet").fillna("")
    actions = pd.read_parquet(ROOT / "derived/FDA_APPLICATION_ACTION.parquet").fillna("")
    derived = {r["event_id"]: r for r in events.to_dict("records") + actions.to_dict("records")}
    orange_blob, purple_blob, drugs_blob = fetch("orange_book"), fetch("purple_book_august_2026_xlsx"), fetch("drugs_at_fda")
    orange_lines = {int(r["source_row_key"].split(":")[-1]) for r in selected if r["stratum"] == "A_ORANGE"}
    drug_lines = {int(r["source_row_key"].split(":")[-1]) for r in selected if r["stratum"].startswith("A_DRUGS")}
    with zipfile.ZipFile(io.BytesIO(orange_blob)) as z:
        orange_rows = row_by_physical_line(z, "products.txt", "~", orange_lines)
    with zipfile.ZipFile(io.BytesIO(drugs_blob)) as z:
        drug_rows = row_by_physical_line(z, "Submissions.txt", "\t", drug_lines)
        app_rows = row_by_physical_line(z, "Applications.txt", "\t", set(range(2, 29379)))
        class_rows = row_by_physical_line(z, "SubmissionClass_Lookup.txt", "\t", set(range(2, 1000)))
    app_type = {padded(r["ApplNo"], 6): r["ApplType"] for r in app_rows.values()}
    class_code = {r["SubmissionClassCodeID"]: r["SubmissionClassCode"] for r in class_rows.values()}
    purple_book = openpyxl.load_workbook(io.BytesIO(purple_blob), read_only=True, data_only=True)
    purple_sheet = purple_book.active
    purple_header = [c.value for c in purple_sheet[35]]

    reviews = []
    for sample in selected:
        d = derived[sample["event_id"]]
        line = int(sample["source_row_key"].split(":")[-1])
        category = sample["stratum"]
        if category == "A_ORANGE":
            source = orange_rows[line]
            checks = {
                "application_type": (source["Appl_Type"], d["source_application_type_raw"]),
                "application_no": (padded(source["Appl_No"], 6), d["application_no"]),
                "product_no": (padded(source["Product_No"], 3), d["product_no"]),
                "ingredient": (source["Ingredient"], d["source_ingredient_raw"]),
                "trade_name": (source["Trade_Name"], d["trade_name"]),
                "dosage_route": (source["DF;Route"], d["source_dosage_route_raw"]),
                "strength": (source["Strength"], d["source_strength_raw"]),
                "source_date": (source["Approval_Date"], d["source_event_date_raw"]),
                "event_date": (full_date(source["Approval_Date"]), d["event_date"]),
            }
            source_url = SOURCES["orange_book"]["source_url"]
        elif category == "A_PURPLE":
            values = [c.value for c in purple_sheet[line]]
            source = {k: str(v).strip() if v is not None else "" for k, v in zip(purple_header, values)}
            checks = {
                "application_type": ("BLA", d["application_type"]),
                "application_no": (padded(source["BLA Number"], 6), d["application_no"]),
                "product_no": (padded(source["Product Number"], 3), d["product_no"]),
                "ingredient": (source["Proper Name"], d["source_ingredient_raw"]),
                "trade_name": (source["Proprietary Name"], d["trade_name"]),
                "license_type": (source["License Type"], d["source_license_type_raw"]),
                "submission_type": (source["Submission Type"], d["submission_type"]),
                "dosage_route": (f"{source['Dosage Form']};{source['Route of Administration']}", d["source_dosage_route_raw"]),
                "strength": (source["Strength"], d["source_strength_raw"]),
                "source_date": (source["Approval Date"], d["source_event_date_raw"]),
                "event_date": (full_date(source["Approval Date"]), d["event_date"]),
            }
            source_url = SOURCES["purple_book_august_2026_xlsx"]["source_url"]
        else:
            source = drug_rows[line]
            checks = {
                "application_type": (app_type[padded(source["ApplNo"], 6)], d["application_type"]),
                "application_no": (padded(source["ApplNo"], 6), d["application_no"]),
                "submission_no": (source["SubmissionNo"], d["submission_no"]),
                "submission_type": (source["SubmissionType"], d["submission_type"]),
                "submission_status": (source["SubmissionStatus"], d["submission_status"]),
                "submission_class": (class_code.get(source["SubmissionClassCodeID"], ""), d["submission_class"]),
                "source_date": (source["SubmissionStatusDate"], d["submission_status_date_raw"]),
                "event_date": (full_date(source["SubmissionStatusDate"]), d["event_date"]),
            }
            source_url = SOURCES["drugs_at_fda"]["source_url"]
        mismatches = [k for k, (source_value, derived_value) in checks.items() if str(source_value) != str(derived_value)]
        reviews.append({
            "sample_id": sample["sample_id"], "stratum": category,
            "event_id": sample["event_id"], "source_url": source_url,
            "source_row_key": sample["source_row_key"],
            "application_no": sample["application_no"], "product_no": sample["product_no"],
            "official_values": json.dumps({k: str(v[0]) for k, v in checks.items()}, ensure_ascii=False),
            "derived_values": json.dumps({k: str(v[1]) for k, v in checks.items()}, ensure_ascii=False),
            "mismatched_fields": "|".join(mismatches),
            "automated_field_equal": not mismatches,
            "agent_decision": "PENDING", "agent_note": "",
        })
    with OUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reviews[0]))
        writer.writeheader()
        writer.writerows(reviews)
    print({"rows": len(reviews), "automated_exact": sum(r["automated_field_equal"] for r in reviews),
           "mismatches": [(r["sample_id"], r["mismatched_fields"]) for r in reviews if r["mismatched_fields"]]})


if __name__ == "__main__":
    main()
