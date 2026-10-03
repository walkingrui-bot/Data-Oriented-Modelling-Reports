"""Build source-semantic FDA candidates and reclassify EXP021's scope audit.

Official source ZIP/XLSX bytes exist in memory only. No raw archive is written.
"""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401; parquet engine

# openpyxl is pure Python in the Codex bundled workspace runtime. Preserve the
# existing pyarrow/pandas runtime for Parquet; append only after those imports.
sys.path.append("/Users/rui/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages")
import openpyxl  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
EXP021 = ROOT.parent / "STAT-PSYMOE-EXP021-20261002-001"
SOURCES = json.loads((ROOT / "SOURCE_INDEX.json").read_text())["sources"]
DERIVED = ROOT / "derived"
RUN_ID = "EXP022-BUILD-002"
TRANSFORM = "derived/build_semantic_events.py v0.2"


def digits(value: object, width: int) -> str:
    result = re.sub(r"\D", "", str(value or ""))
    return result.zfill(width) if result else ""


def sql_date(value: object) -> str:
    value = str(value or "").strip()
    return value[:10] if re.match(r"^\d{4}-\d{2}-\d{2}", value) else ""


def word_date(value: object) -> str:
    value = str(value or "").strip()
    for pattern in ("%B %d, %Y", "%b %d, %Y", "%d-%b-%Y"):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    return ""


def fetch(name: str) -> bytes:
    source = SOURCES[name]
    request = urllib.request.Request(source["source_url"], headers={"User-Agent": "Mozilla/5.0 EXP022 source-semantics research"})
    with urllib.request.urlopen(request, timeout=90) as response:
        blob = response.read()
        if response.headers.get("Last-Modified") != source["last_modified"] or len(blob) != source["bytes_read"]:
            raise RuntimeError(f"Source metadata changed since EXP022-SOURCE-001: {name}")
    return blob


def read_zip_table(archive: zipfile.ZipFile, name: str, delimiter: str) -> tuple[list[tuple[int, dict[str, str]]], int]:
    valid = []
    invalid = 0
    with archive.open(name) as raw:
        reader = csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline=""), delimiter=delimiter)
        for physical_row, row in enumerate(reader, start=2):
            if None in row or any(v is None for v in row.values()):
                invalid += 1
                continue
            valid.append((physical_row, {k: v.strip() for k, v in row.items()}))
    return valid, invalid


def common(source_name: str, source_file: str, row_key: str) -> dict:
    src = SOURCES[source_name]
    return {
        "source": source_name,
        "source_url": src["source_url"],
        "source_file": source_file,
        "source_row_key": row_key,
        "source_snapshot": f"Last-Modified={src['last_modified']};bytes={src['bytes_read']}",
        "source_release_date": src["last_modified"],
        "retrieved_at": src["retrieved_at_utc"],
        "transformation_script": TRANSFORM,
        "public_first_date": None,
        "document_date": None,
        "document_signature_date": None,
    }


def main() -> None:
    outputs = [DERIVED / x for x in (
        "SOURCE_SEMANTIC_CANDIDATES.parquet", "FDA_APPLICATION_ACTION.parquet",
        "REGULATORY_DOCUMENT.parquet", "SOURCE_SEMANTIC_DIAGNOSTICS.json",
    )] + [ROOT / x for x in ("EVENT_SCOPE_AUDIT.csv", "TRUE_DATE_CONFLICTS.csv")]
    if any(p.exists() for p in outputs):
        raise RuntimeError("An EXP022-BUILD-001 output already exists; preserve prior attempt")

    drugs_blob, orange_blob, purple_blob = fetch("drugs_at_fda"), fetch("orange_book"), fetch("purple_book_august_2026_xlsx")
    malformed = Counter()
    with zipfile.ZipFile(io.BytesIO(drugs_blob)) as z:
        apps, malformed["Applications.txt"] = read_zip_table(z, "Applications.txt", "\t")
        subs, malformed["Submissions.txt"] = read_zip_table(z, "Submissions.txt", "\t")
        docs, malformed["ApplicationDocs.txt"] = read_zip_table(z, "ApplicationDocs.txt", "\t")
        drug_products, malformed["Products.txt"] = read_zip_table(z, "Products.txt", "\t")
        classes, malformed["SubmissionClass_Lookup.txt"] = read_zip_table(z, "SubmissionClass_Lookup.txt", "\t")
        doc_types, malformed["ApplicationsDocsType_Lookup.txt"] = read_zip_table(z, "ApplicationsDocsType_Lookup.txt", "\t")
    with zipfile.ZipFile(io.BytesIO(orange_blob)) as z:
        orange, malformed["orange/products.txt"] = read_zip_table(z, "products.txt", "~")
    workbook = openpyxl.load_workbook(io.BytesIO(purple_blob), read_only=True, data_only=True)
    sheet = list(workbook.active.iter_rows(values_only=True))
    header = list(sheet[34])
    purple = [(i, {k: str(v).strip() if v is not None else "" for k, v in zip(header, row)})
              for i, row in enumerate(sheet[35:], start=36) if len(row) == len(header) and row[2] is not None]

    app_type = {digits(row["ApplNo"], 6): row["ApplType"] for _, row in apps}
    class_map = {row["SubmissionClassCodeID"]: row["SubmissionClassCode"] for _, row in classes}
    doc_type_map = {row["ApplicationDocsType_Lookup_ID"]: row["ApplicationDocsType_Lookup_Description"] for _, row in doc_types}
    medgas = {digits(row["ApplNo"], 6) for _, row in subs if row["SubmissionType"] == "ORIG"
              and class_map.get(row["SubmissionClassCodeID"]) == "MEDGAS"}
    drug_product_by_key = defaultdict(list)
    for _, row in drug_products:
        drug_product_by_key[(digits(row["ApplNo"], 6), digits(row["ProductNo"], 3))].append(row)

    excluded = Counter()
    candidates = []
    candidate_lookup = defaultdict(list)
    for source_row, row in orange:
        if row["Appl_Type"] != "N":
            excluded["ORANGE_NOT_NDA"] += 1
            continue
        application = digits(row["Appl_No"], 6)
        product = digits(row["Product_No"], 3)
        if application in medgas:
            excluded["ORANGE_MEDGAS"] += 1
            continue
        date = word_date(row["Approval_Date"])
        if not date:
            excluded["ORANGE_NO_EXACT_DAY"] += 1
            continue
        identity = f"N|{application}|{product}"
        item = {
            "event_id": f"FDA:OB:NDA:{application}:{product}:row{source_row}",
            "drug_regulatory_id": f"NDA:{application}",
            "application_no": application, "application_type": "NDA", "product_no": product,
            "event_type": "NDA_PRODUCT_APPROVAL", "event_scope": "PRODUCT_STRENGTH_ROUTE",
            "event_date": date, "is_derived": False, "derivation_rule": None,
            "quality_tier": "PENDING_MANUAL_GATES", "ingredient": row["Ingredient"],
            "trade_name": row["Trade_Name"], "dosage_route": row["DF;Route"],
            "strength": row["Strength"], "license_type": None,
            "submission_type": None, "source_record_id": identity,
            "source_application_raw": row["Appl_No"], "source_product_raw": row["Product_No"],
            "source_ingredient_raw": row["Ingredient"], "source_event_date_raw": row["Approval_Date"],
            "source_application_type_raw": row["Appl_Type"], "source_license_type_raw": None,
            "source_strength_raw": row["Strength"], "source_dosage_route_raw": row["DF;Route"],
            **common("orange_book", "products.txt", f"products.txt:{source_row}"),
        }
        candidates.append(item)
        candidate_lookup[("ORANGE", application, product, date)].append(item)

    for source_row, row in purple:
        if row["License Type"] != "351(a)":
            excluded["PURPLE_NOT_351A"] += 1
            continue
        if row["Submission Type"] != "Original":
            excluded["PURPLE_NOT_ORIGINAL_PRODUCT_SUBMISSION"] += 1
            continue
        date = word_date(row["Approval Date"])
        if not date:
            excluded["PURPLE_NO_EXACT_DAY"] += 1
            continue
        application = digits(row["BLA Number"], 6)
        product = digits(row["Product Number"], 3)
        if not application or not product:
            excluded["PURPLE_NO_EXACT_BLA_PRODUCT_ID"] += 1
            continue
        identity = f"{application}|{product}|Original"
        item = {
            "event_id": f"FDA:PB:BLA:{application}:{product}:row{source_row}",
            "drug_regulatory_id": f"BLA:{application}",
            "application_no": application, "application_type": "BLA", "product_no": product,
            "event_type": "BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL", "event_scope": "PRODUCT_STRENGTH_ROUTE",
            "event_date": date, "is_derived": False, "derivation_rule": None,
            "quality_tier": "PENDING_MANUAL_GATES", "ingredient": row["Proper Name"],
            "trade_name": row["Proprietary Name"], "dosage_route": f"{row['Dosage Form']};{row['Route of Administration']}",
            "strength": row["Strength"], "license_type": row["License Type"],
            "submission_type": row["Submission Type"], "source_record_id": identity,
            "source_application_raw": row["BLA Number"], "source_product_raw": row["Product Number"],
            "source_ingredient_raw": row["Proper Name"], "source_event_date_raw": row["Approval Date"],
            "source_application_type_raw": "BLA", "source_license_type_raw": row["License Type"],
            "source_strength_raw": row["Strength"],
            "source_dosage_route_raw": f"{row['Dosage Form']};{row['Route of Administration']}",
            **common("purple_book_august_2026_xlsx", "purplebook-search-August-data-download.xlsx", f"sheet1:{source_row}"),
        }
        candidates.append(item)
        candidate_lookup[("PURPLE", application, product, date)].append(item)

    actions = []
    for source_row, row in subs:
        application = digits(row["ApplNo"], 6)
        typ = app_type.get(application, "")
        if typ not in {"NDA", "BLA"}:
            continue
        cls = class_map.get(row["SubmissionClassCodeID"], "")
        actions.append({
            "event_id": f"FDA:ACTION:{typ}:{application}:{row['SubmissionType']}:{row['SubmissionNo']}:row{source_row}",
            "drug_regulatory_id": f"{typ}:{application}",
            "application_no": application, "application_type": typ,
            "submission_no": row["SubmissionNo"], "submission_type": row["SubmissionType"],
            "submission_status": row["SubmissionStatus"], "submission_status_date_raw": row["SubmissionStatusDate"],
            "submission_class": cls, "event_type": "FDA_APPLICATION_ACTION", "event_scope": "APPLICATION_SUBMISSION",
            "event_date": sql_date(row["SubmissionStatusDate"]) or None,
            "approved_status_code": row["SubmissionStatus"] == "AP",
            "medical_gas_flag": application in medgas,
            "quality_tier": "AUXILIARY_ACTION_NOT_MARKET_ENTRY",
            "source_record_id": f"{application}|{row['SubmissionType']}|{row['SubmissionNo']}",
            **common("drugs_at_fda", "Submissions.txt", f"Submissions.txt:{source_row}"),
        })

    documents = []
    for source_row, row in docs:
        application = digits(row["ApplNo"], 6)
        typ = app_type.get(application, "")
        if typ not in {"NDA", "BLA"}:
            continue
        documents.append({
            **common("drugs_at_fda", "ApplicationDocs.txt", f"ApplicationDocs.txt:{source_row}"),
            "document_id": row["ApplicationDocsID"],
            "drug_regulatory_id": f"{typ}:{application}",
            "application_no": application, "application_type": typ,
            "submission_type": row["SubmissionType"], "submission_no": row["SubmissionNo"],
            "document_type_id": row["ApplicationDocsTypeID"],
            "document_type_label": doc_type_map.get(row["ApplicationDocsTypeID"], ""),
            "document_title": row["ApplicationDocsTitle"],
            "document_date_raw": row["ApplicationDocsDate"],
            "document_date": sql_date(row["ApplicationDocsDate"]) or None,
            "document_url": row["ApplicationDocsURL"],
            "document_scope": "APPLICATION_SUBMISSION_DOCUMENT",
            "verified_document_role": "UNKNOWN",
            "source_record_id": row["ApplicationDocsID"],
        })

    old_audit = pd.read_csv(EXP021 / "crosswalk_audit.csv", dtype=str, keep_default_na=False)
    audit = []
    for old in old_audit.to_dict("records"):
        application = old["application_number"]
        product = old["product_number"]
        left_date = old["left_date"]
        dates = [d for d in old["right_dates"].split("|") if d]
        if not dates:
            cls, reason, relation = "SOURCE_ONLY", "NO_DRUGS_ORIG_AP_DATE", "NO_COMPARATOR"
        elif left_date > max(dates):
            cls, reason, relation = "DIFFERENT_SCOPE_EXPECTED", "PRODUCT_LATER_THAN_ALL_ORIGINAL_APPLICATION_ACTIONS", "PRODUCT_LATER"
        elif left_date in dates:
            cls, reason, relation = "UNRESOLVED_SCOPE", "SAME_DAY_IS_NOT_PROOF_OF_SAME_EVENT", "SAME_DAY"
        elif left_date < min(dates):
            cls, reason, relation = "UNRESOLVED_SCOPE", "PRODUCT_EARLIER_THAN_ORIGINAL_ACTION_NEEDS_LINEAGE", "PRODUCT_EARLIER"
        else:
            cls, reason, relation = "UNRESOLVED_SCOPE", "MULTIPLE_APPLICATION_ACTION_DATES_BRACKET_PRODUCT", "BETWEEN_ACTIONS"
        src = "ORANGE" if old["left_source"] == "FDA_ORANGE_BOOK_PRODUCTS" else "PURPLE"
        matches = candidate_lookup.get((src, application, product, left_date), []) if product else []
        audit.append({
            "audit_id": old["audit_id"], "application_no": application, "product_no": product,
            "application_type": old["application_type"],
            "left_source": old["left_source"], "left_scope": old["left_scope"],
            "left_date": left_date, "left_source_record_id": old["left_source_record_id"],
            "left_source_row_keys": "|".join(m["source_row_key"] for m in matches),
            "left_ingredient": "|".join(dict.fromkeys(m["ingredient"] for m in matches)),
            "left_dosage_route": "|".join(dict.fromkeys(m["dosage_route"] for m in matches)),
            "left_strength": "|".join(dict.fromkeys(m["strength"] for m in matches)),
            "right_source": old["right_source"], "right_scope": old["right_scope"],
            "right_dates": old["right_dates"],
            "exp021_comparison_status": old["comparison_status"],
            "exp022_scope_class": cls, "date_relation": relation,
            "classification_reason": reason,
            "same_scope_assessable": False,
            "manual_review_status": "NOT_SELECTED",
        })

    event_frame = pd.DataFrame(candidates)
    action_frame = pd.DataFrame(actions)
    doc_frame = pd.DataFrame(documents)
    audit_frame = pd.DataFrame(audit)
    assert event_frame["event_id"].is_unique
    assert action_frame["event_id"].is_unique
    assert doc_frame["document_id"].is_unique
    assert len(audit_frame) == 10998
    event_frame.to_parquet(DERIVED / "SOURCE_SEMANTIC_CANDIDATES.parquet", index=False)
    action_frame.to_parquet(DERIVED / "FDA_APPLICATION_ACTION.parquet", index=False)
    doc_frame.to_parquet(DERIVED / "REGULATORY_DOCUMENT.parquet", index=False)
    audit_frame.to_csv(ROOT / "EVENT_SCOPE_AUDIT.csv", index=False)
    # This is a real empty adjudication queue: the source pair has no same-scope
    # comparator. The diagnostic records denominator=0, not a 0% conflict rate.
    pd.DataFrame(columns=["application_no", "product_no", "event_type", "left_source_row_key",
                          "right_source_row_key", "left_date", "right_date", "adjudication_status"]).to_csv(
        ROOT / "TRUE_DATE_CONFLICTS.csv", index=False)
    diag = {
        "run_id": RUN_ID,
        "source_release": {k: {"last_modified": v["last_modified"], "bytes": v["bytes_read"]} for k, v in SOURCES.items()},
        "candidate_rows": len(candidates), "candidate_event_types": dict(Counter(x["event_type"] for x in candidates)),
        "unique_regulatory_applications": {t: len({x["application_no"] for x in candidates if x["application_type"] == t}) for t in ("NDA", "BLA")},
        "unique_product_keys": {t: len({(x["application_no"], x["product_no"]) for x in candidates if x["application_type"] == t}) for t in ("NDA", "BLA")},
        "candidate_year_range": [min(x["event_date"] for x in candidates), max(x["event_date"] for x in candidates)],
        "application_action_rows": len(actions), "action_types": dict(Counter(f"{x['application_type']}/{x['submission_type']}" for x in actions)),
        "document_rows": len(documents), "document_role_counts": dict(Counter(x["verified_document_role"] for x in documents)),
        "scope_audit_rows": len(audit), "scope_class_counts": dict(Counter(x["exp022_scope_class"] for x in audit)),
        "date_relation_counts": dict(Counter(x["date_relation"] for x in audit)),
        "old_conflict_reclassification": dict(Counter(x["exp022_scope_class"] for x in audit if x["exp021_comparison_status"] == "CONFLICT")),
        "same_scope_assessable_pairs": 0, "true_date_conflict_rate": None,
        "excluded": dict(excluded), "malformed_rows_skipped": dict(malformed),
        "public_first_date_populated": 0,
        "note": "Candidates are not high-confidence release; Purple product-row Approval Date is not BLA-level Original Approval Date.",
    }
    (DERIVED / "SOURCE_SEMANTIC_DIAGNOSTICS.json").write_text(json.dumps(diag, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(diag, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
