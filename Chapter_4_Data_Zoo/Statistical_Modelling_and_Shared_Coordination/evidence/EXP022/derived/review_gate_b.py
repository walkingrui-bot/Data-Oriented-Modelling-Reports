"""Create official-row semantic evidence for the independent fixed EXP022 sample."""

from __future__ import annotations

import csv
import io
import json
import sys
import zipfile
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401

sys.path.append("/Users/rui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages")
import openpyxl  # noqa: E402

from review_gate_a import fetch, padded, row_by_physical_line, full_date

ROOT = Path(__file__).resolve().parents[1]
SOURCES = json.loads((ROOT / "SOURCE_INDEX.json").read_text())["sources"]
OUT = ROOT / "GATE_B_REVIEW.csv"


def main() -> None:
    if OUT.exists():
        raise RuntimeError("Gate B review output exists; preserve prior attempt")
    with (ROOT / "GATE_B_SAMPLE.csv").open(newline="") as stream:
        selected = list(csv.DictReader(stream))
    events = pd.read_parquet(ROOT / "derived/SOURCE_SEMANTIC_CANDIDATES.parquet").fillna("")
    actions = pd.read_parquet(ROOT / "derived/FDA_APPLICATION_ACTION.parquet").fillna("")
    derived = {r["event_id"]: r for r in events.to_dict("records") + actions.to_dict("records")}
    orange_blob, purple_blob, drugs_blob = fetch("orange_book"), fetch("purple_book_august_2026_xlsx"), fetch("drugs_at_fda")
    orange_lines = {int(r["source_row_key"].split(":")[-1]) for r in selected if r["stratum"] == "B_ORANGE_NDA"}
    drug_lines = {int(r["source_row_key"].split(":")[-1]) for r in selected if r["stratum"].startswith("B_DRUGS")}
    with zipfile.ZipFile(io.BytesIO(orange_blob)) as z:
        orange_rows = row_by_physical_line(z, "products.txt", "~", orange_lines)
    with zipfile.ZipFile(io.BytesIO(drugs_blob)) as z:
        drug_rows = row_by_physical_line(z, "Submissions.txt", "\t", drug_lines)
        app_rows = row_by_physical_line(z, "Applications.txt", "\t", set(range(2, 29379)))
    app_type = {padded(r["ApplNo"], 6): r["ApplType"] for r in app_rows.values()}
    purple_book = openpyxl.load_workbook(io.BytesIO(purple_blob), read_only=True, data_only=True)
    purple_sheet = purple_book.active
    purple_header = [c.value for c in purple_sheet[35]]

    reviews = []
    for sample in selected:
        item = derived[sample["event_id"]]
        line = int(sample["source_row_key"].split(":")[-1])
        category = sample["stratum"]
        if category == "B_ORANGE_NDA":
            source = orange_rows[line]
            official = {k: source[k] for k in ("Appl_Type", "Appl_No", "Product_No", "Ingredient", "DF;Route", "Strength", "Approval_Date")}
            expected_type = "NDA_PRODUCT_APPROVAL" if source["Appl_Type"] == "N" else "ANDA_PRODUCT_APPROVAL"
            expected_scope = "PRODUCT_STRENGTH_ROUTE"
            expected_date = full_date(source["Approval_Date"])
            classification_ok = (item["event_type"] == expected_type and item["event_scope"] == expected_scope
                                 and item["event_date"] == expected_date and item["application_type"] == "NDA")
            catastrophic = source["Appl_Type"] != "N" or item["application_type"] == "ANDA"
            note = "FDA Orange Product Approval_Date; no original application or indication claim."
            url = SOURCES["orange_book"]["source_url"]
        elif category == "B_PURPLE_BLA":
            source = {k: str(v).strip() if v is not None else "" for k, v in zip(purple_header, [c.value for c in purple_sheet[line]])}
            official = {k: source[k] for k in ("BLA Number", "Product Number", "Proper Name", "License Type", "Submission Type", "Approval Date", "Date of First Licensure")}
            expected_type = "BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL"
            expected_scope = "PRODUCT_STRENGTH_ROUTE"
            expected_date = full_date(source["Approval Date"])
            classification_ok = (item["event_type"] == expected_type and item["event_scope"] == expected_scope
                                 and item["event_date"] == expected_date and source["License Type"] == "351(a)"
                                 and source["Submission Type"] == "Original")
            catastrophic = (source["License Type"] != "351(a)" or source["Submission Type"] != "Original"
                            or item["event_type"] == "BLA_ORIGINAL_LICENSURE")
            note = "Purple monthly row Approval Date is product-submission date; BLA-level Original Approval Date requires product-details page."
            url = SOURCES["purple_book_august_2026_xlsx"]["source_url"]
        else:
            source = drug_rows[line]
            official = {k: source[k] for k in ("ApplNo", "SubmissionType", "SubmissionNo", "SubmissionStatus", "SubmissionStatusDate", "SubmissionClassCodeID")}
            expected_type = "FDA_APPLICATION_ACTION"
            expected_scope = "APPLICATION_SUBMISSION"
            expected_date = full_date(source["SubmissionStatusDate"])
            application = padded(source["ApplNo"], 6)
            classification_ok = (item["event_type"] == expected_type and item["event_scope"] == expected_scope
                                 and item["event_date"] == expected_date
                                 and item["submission_type"] == source["SubmissionType"]
                                 and item["approved_status_code"] == (source["SubmissionStatus"] == "AP")
                                 and item["application_type"] == app_type[application])
            catastrophic = (source["SubmissionType"] == "SUPPL" and item["event_type"] != "FDA_APPLICATION_ACTION")
            note = "Drugs Submissions action; AP is a status, ORIG and SUPPL remain separate; not product/licensure date."
            url = SOURCES["drugs_at_fda"]["source_url"]
        reviews.append({
            "sample_id": sample["sample_id"], "stratum": category,
            "application_no": sample["application_no"], "product_no": sample["product_no"],
            "source_url": url, "source_row_key": sample["source_row_key"],
            "official_fields": json.dumps(official, ensure_ascii=False),
            "derived_event_type": item["event_type"], "derived_scope": item["event_scope"],
            "derived_event_date": item["event_date"],
            "expected_event_type": expected_type, "expected_scope": expected_scope,
            "automated_semantic_consistent": classification_ok, "catastrophic_scope_flag": catastrophic,
            "semantic_note": note, "agent_decision": "PENDING", "agent_note": "",
        })
    with OUT.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(reviews[0]))
        writer.writeheader()
        writer.writerows(reviews)
    print({"rows": len(reviews), "automated_consistent": sum(r["automated_semantic_consistent"] for r in reviews),
           "catastrophic_flags": [(r["sample_id"], r["official_fields"]) for r in reviews if r["catastrophic_scope_flag"]]})


if __name__ == "__main__":
    main()
