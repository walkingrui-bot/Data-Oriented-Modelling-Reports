"""Build scope-explicit FDA original application/product event candidates.

Reads FDA source ZIP/CSV in memory. Never stores source archives or extracted tables.
Application ORIG approval dates are never propagated to later product strengths.
"""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
SOURCE_INDEX = json.loads((ROOT / "SOURCE_INDEX.json").read_text())
SOURCES = SOURCE_INDEX["sources"]
RETRIEVED_AT = datetime.now(timezone.utc).isoformat()
TRANSFORM = "derived/build_event_a.py v0.2"
MALFORMED_INPUTS = Counter()


def fetch(name: str) -> bytes:
    expected = SOURCES[name]
    req = urllib.request.Request(expected["source_url"], headers={"User-Agent": "Mozilla/5.0 EXP021 research"})
    with urllib.request.urlopen(req, timeout=90) as response:
        blob = response.read()
        if response.headers.get("Last-Modified") != expected["last_modified"] or len(blob) != expected["bytes_read"]:
            raise RuntimeError(f"Source release changed during EXP021: {name}; do not blend releases")
    return blob


def table(archive: zipfile.ZipFile, name: str, delimiter: str) -> list[dict[str, str]]:
    with archive.open(name) as raw:
        stream = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
        result = []
        for row in csv.DictReader(stream, delimiter=delimiter):
            if None in row or any(value is None for value in row.values()):
                MALFORMED_INPUTS[name] += 1
                continue
            result.append({key: value.strip() for key, value in row.items()})
        return result


def app_no(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    return digits.zfill(6) if digits else ""


def product_no(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    return digits.zfill(3) if digits else ""


def sql_date(value: str) -> str:
    text = (value or "").strip()
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        return text[:10]
    return ""


def human_date(value: str) -> str:
    text = str(value or "").strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(text, fmt).date().isoformat()
        except ValueError:
            pass
    return ""


def event(**kwargs: str) -> dict[str, str]:
    base = {key: "" for key in (
        "event_id", "application_number", "application_type", "product_number", "drug_name",
        "active_ingredient", "fda_event_type", "event_scope", "approval_date", "occurrence_date",
        "public_date", "database_ingest_date", "approval_source", "source_record_id", "source_url",
        "source_file", "source_release_last_modified", "retrieved_at", "transformation_script",
        "submission_type", "submission_number", "submission_status", "submission_class", "license_type",
        "linked_letter_url", "linked_letter_record_date", "linked_letter_role", "date_precision", "identity_rule", "exclusion_reason",
    )}
    base.update(kwargs)
    return base


def main() -> None:
    if (ROOT / "derived" / "REGULATORY_EVENT_A.parquet").exists():
        raise RuntimeError("EVENT_A output exists; preserve the prior state and register a new run before rebuilding")
    drugs_blob = fetch("drugs_at_fda")
    orange_blob = fetch("orange_book")
    purple_blob = fetch("purple_book_august_2026")
    purple_xlsx_blob = fetch("purple_book_august_2026_xlsx")
    with zipfile.ZipFile(io.BytesIO(drugs_blob)) as z:
        apps = table(z, "Applications.txt", "\t")
        submissions = table(z, "Submissions.txt", "\t")
        products = table(z, "Products.txt", "\t")
        docs = table(z, "ApplicationDocs.txt", "\t")
        class_lookup = {r["SubmissionClassCodeID"]: r["SubmissionClassCode"] for r in table(z, "SubmissionClass_Lookup.txt", "\t")}
    with zipfile.ZipFile(io.BytesIO(orange_blob)) as z:
        orange = table(z, "products.txt", "~")
    purple_rows = list(csv.reader(io.StringIO(purple_blob.decode("utf-8-sig", errors="replace"))))
    purple_csv_count = sum(bool(len(row) == len(purple_rows[34]) and row[2].strip()) for row in purple_rows[35:])
    workbook = openpyxl.load_workbook(io.BytesIO(purple_xlsx_blob), read_only=True, data_only=True)
    sheet_rows = list(workbook.active.iter_rows(values_only=True))
    header = sheet_rows[34]
    purple = [dict(zip(header, [str(value or "").strip() for value in row])) for row in sheet_rows[35:]
              if len(row) == len(header) and row[2] and str(row[2]).strip()]
    if len(purple) != purple_csv_count:
        raise RuntimeError(f"Purple CSV/XLSX row-count conflict: {purple_csv_count} vs {len(purple)}")
    purple_license_by_app = defaultdict(set)
    for row in purple:
        purple_license_by_app[app_no(row["BLA Number"])].add(row["License Type"].strip())

    app_type = {app_no(row["ApplNo"]): row["ApplType"] for row in apps}
    medical_gas_apps = {app_no(row["ApplNo"]) for row in submissions
                        if row["SubmissionType"] == "ORIG" and class_lookup.get(row["SubmissionClassCodeID"]) == "MEDGAS"}
    fda_products = {(app_no(row["ApplNo"]), product_no(row["ProductNo"])): row for row in products}
    docs_by_submission = defaultdict(list)
    for row in docs:
        if row["SubmissionType"].strip() == "ORIG" and row["ApplicationDocsTypeID"] == "1" and row["ApplicationDocsURL"]:
            docs_by_submission[(app_no(row["ApplNo"]), row["SubmissionNo"])].append(row)

    events = []
    excluded = Counter()
    fda_dates = defaultdict(set)
    fda_orig_apps = set()
    for row in submissions:
        a = app_no(row["ApplNo"])
        typ = app_type.get(a, "")
        if row["SubmissionType"] != "ORIG":
            excluded["DRUGS_NON_ORIG"] += 1
            continue
        if typ not in {"NDA", "BLA"}:
            excluded["DRUGS_NON_INNOVATOR_APPLICATION"] += 1
            continue
        if a in medical_gas_apps:
            excluded["DRUGS_MEDICAL_GAS"] += 1
            continue
        if typ == "BLA" and any(license_type.startswith("351(k)") for license_type in purple_license_by_app.get(a, ())):
            excluded["DRUGS_BLA_351K_BIOSIMILAR"] += 1
            continue
        if row["SubmissionStatus"] != "AP":
            excluded[f"DRUGS_STATUS_{row['SubmissionStatus'] or 'BLANK'}"] += 1
            continue
        date = sql_date(row["SubmissionStatusDate"])
        if not date:
            excluded["DRUGS_NO_EXACT_DATE"] += 1
            continue
        subno = row["SubmissionNo"]
        matched_docs = docs_by_submission.get((a, subno), [])
        exact_docs = [d for d in matched_docs if sql_date(d["ApplicationDocsDate"]) == date]
        chosen_doc = (exact_docs or matched_docs or [None])[0]
        source_url = f"https://www.accessdata.fda.gov/scripts/cder/daf/index.cfm?event=overview.process&ApplNo={a}"
        events.append(event(
            event_id=f"FDA:ORIG:{typ}:{a}:{subno}:{date}", application_number=a,
            application_type=typ, fda_event_type="ORIGINAL_APPLICATION_APPROVAL", event_scope="APPLICATION",
            approval_date=date, occurrence_date=date,
            approval_source="DRUGS_AT_FDA_SUBMISSIONS", source_record_id=f"{a}|ORIG|{subno}",
            source_url=source_url, source_file="Submissions.txt", source_release_last_modified=SOURCES["drugs_at_fda"]["last_modified"],
            retrieved_at=RETRIEVED_AT, transformation_script=TRANSFORM, submission_type="ORIG", submission_number=subno,
            submission_status="AP", submission_class=class_lookup.get(row["SubmissionClassCodeID"], ""),
            linked_letter_url=chosen_doc["ApplicationDocsURL"] if chosen_doc else "",
            linked_letter_record_date=sql_date(chosen_doc["ApplicationDocsDate"]) if chosen_doc else "",
            linked_letter_role="UNVERIFIED_TYPE_1_LETTER" if chosen_doc else "",
            date_precision="DAY", identity_rule="EXACT_FDA_APPLICATION_NUMBER" + (";BIOLOGIC_LICENSE_TYPE_UNKNOWN" if typ == "BLA" and a not in purple_license_by_app else ""),
            license_type="351(a)" if typ == "BLA" and "351(a)" in purple_license_by_app.get(a, ()) else ("UNKNOWN" if typ == "BLA" else ""),
        ))
        fda_dates[a].add(date)
        fda_orig_apps.add(a)

    orange_rows = []
    for row in orange:
        if row["Appl_Type"] != "N":
            excluded["ORANGE_ANDA_GENERIC"] += 1
            continue
        if app_no(row["Appl_No"]) in medical_gas_apps:
            excluded["ORANGE_MEDICAL_GAS"] += 1
            continue
        date = human_date(row["Approval_Date"])
        if not date:
            excluded["ORANGE_CENSORED_OR_INVALID_DATE"] += 1
            continue
        a, p = app_no(row["Appl_No"]), product_no(row["Product_No"])
        product = fda_products.get((a, p), {})
        e = event(
            event_id=f"FDA:ORANGE:NDA:{a}:{p}:{date}", application_number=a, application_type="NDA",
            product_number=p, drug_name=row["Trade_Name"], active_ingredient=row["Ingredient"],
            fda_event_type="ORIGINAL_PRODUCT_APPROVAL", event_scope="PRODUCT", approval_date=date,
            occurrence_date=date, approval_source="FDA_ORANGE_BOOK_PRODUCTS",
            source_record_id=f"N|{a}|{p}", source_url="https://www.fda.gov/media/76860/download?attachment",
            source_file="products.txt", source_release_last_modified=SOURCES["orange_book"]["last_modified"],
            retrieved_at=RETRIEVED_AT, transformation_script=TRANSFORM, date_precision="DAY",
            identity_rule="EXACT_FDA_APPLICATION_AND_PRODUCT_NUMBER" if product else "ORANGE_ONLY_APPLICATION_AND_PRODUCT_NUMBER",
        )
        events.append(e)
        orange_rows.append(e)

    purple_events = []
    for row in purple:
        if row["License Type"].strip() != "351(a)":
            excluded["PURPLE_BIOSIMILAR_OR_OTHER_LICENSE"] += 1
            continue
        if row["Submission Type"].strip() != "Original":
            excluded["PURPLE_NON_ORIGINAL_SUBMISSION"] += 1
            continue
        date = human_date(row["Approval Date"])
        if not date:
            excluded["PURPLE_NO_EXACT_LICENSURE_DATE"] += 1
            continue
        a, p = app_no(row["BLA Number"]), product_no(row["Product Number"])
        e = event(
            event_id=f"FDA:PURPLE:BLA:{a}:{p}:{date}", application_number=a, application_type="BLA",
            product_number=p, drug_name=row["Proprietary Name"].strip(), active_ingredient=row["Proper Name"].strip(),
            fda_event_type="ORIGINAL_BIOLOGIC_PRODUCT_LICENSURE", event_scope="PRODUCT", approval_date=date,
            occurrence_date=date, approval_source="FDA_PURPLE_BOOK_AUGUST_2026_XLSX",
            source_record_id=f"{a}|{p}|Original", source_url=SOURCES["purple_book_august_2026_xlsx"]["source_url"],
            source_file="purplebook-search-August-data-download.xlsx", source_release_last_modified=SOURCES["purple_book_august_2026_xlsx"]["last_modified"],
            retrieved_at=RETRIEVED_AT, transformation_script=TRANSFORM, submission_type="Original",
            license_type="351(a)", date_precision="DAY", identity_rule="EXACT_BLA_AND_PRODUCT_NUMBER",
        )
        events.append(e)
        purple_events.append(e)

    audit = []
    def compare(e: dict[str, str]) -> None:
        dates = sorted(fda_dates.get(e["application_number"], set()))
        if not dates:
            status, delta = "SOURCE_ONLY", ""
        elif e["approval_date"] in dates:
            status, delta = "MATCH", "0"
        else:
            delta_num = min(abs((datetime.fromisoformat(e["approval_date"]) - datetime.fromisoformat(d)).days) for d in dates)
            status, delta = ("DAY_LEVEL_DIFFERENCE" if delta_num == 1 else "CONFLICT"), str(delta_num)
        audit.append({
            "audit_id": f"A:{e['event_id']}", "application_number": e["application_number"], "product_number": e["product_number"],
            "application_type": e["application_type"], "left_source": e["approval_source"], "left_scope": "PRODUCT",
            "left_date": e["approval_date"], "left_source_record_id": e["source_record_id"], "right_source": "DRUGS_AT_FDA_SUBMISSIONS",
            "right_scope": "APPLICATION", "right_dates": "|".join(dates), "comparison_status": status,
            "absolute_day_difference_min": delta, "interpretation": "PRODUCT_VS_APPLICATION_SCOPE; later strength may legitimately differ",
            "identity_rule": "EXACT_APPLICATION_NUMBER", "manual_review_status": "PENDING",
        })
    for e in orange_rows + purple_events:
        compare(e)
    for e in events:
        if e["event_scope"] == "APPLICATION" and not any(a["application_number"] == e["application_number"] for a in audit):
            audit.append({"audit_id": f"A:{e['event_id']}", "application_number": e["application_number"], "product_number": "",
                "application_type": e["application_type"], "left_source": e["approval_source"], "left_scope": "APPLICATION",
                "left_date": e["approval_date"], "left_source_record_id": e["source_record_id"], "right_source": "",
                "right_scope": "", "right_dates": "", "comparison_status": "SOURCE_ONLY", "absolute_day_difference_min": "",
                "interpretation": "NO_PRODUCT_SOURCE_JOIN", "identity_rule": "EXACT_APPLICATION_NUMBER", "manual_review_status": "PENDING"})

    event_frame = pd.DataFrame(events)
    audit_frame = pd.DataFrame(audit)
    assert event_frame["event_id"].is_unique, "Duplicate event ID must be resolved, not silently dropped"
    event_frame.to_parquet(ROOT / "derived" / "REGULATORY_EVENT_A.parquet", index=False)
    audit_frame.to_csv(ROOT / "crosswalk_audit.csv", index=False)
    diagnostics = {
        "run_id": "EXP021-EVENT-A-007", "retrieved_at_utc": RETRIEVED_AT,
        "source_release_last_modified": {k: v["last_modified"] for k, v in SOURCES.items()},
        "input_rows": {"applications": len(apps), "submissions": len(submissions), "fda_products": len(products),
                       "orange_products": len(orange), "purple_bottom_section_csv": purple_csv_count,
                       "purple_bottom_section_xlsx": len(purple)},
        "event_rows_by_source": dict(Counter(e["approval_source"] for e in events)),
        "unique_applications_by_type": {typ: len({e["application_number"] for e in events if e["application_type"] == typ}) for typ in ("NDA", "BLA")},
        "audit_status_counts": dict(Counter(a["comparison_status"] for a in audit)),
        "excluded_rows": dict(excluded), "malformed_input_rows_skipped": dict(MALFORMED_INPUTS),
        "public_date_note": "Not asserted from current bulk source; document date is separate and may not be publication date.",
    }
    (ROOT / "derived" / "EVENT_A_DIAGNOSTICS.json").write_text(json.dumps(diagnostics, indent=2) + "\n")
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
