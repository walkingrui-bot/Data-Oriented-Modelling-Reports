"""Promote only scoped source events after fixed ETL and semantic gates pass."""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "derived"
HC = DERIVED / "REGULATORY_EVENT_HIGH_CONFIDENCE.parquet"
NDA_FIRST = DERIVED / "NDA_FIRST_OBSERVED_PRODUCT_APPROVAL.parquet"
NDA_TIMELINE = DERIVED / "NDA_APPLICATION_TIMELINE.parquet"
BLA_TIMELINE = DERIVED / "BLA_LICENSE_TIMELINE.parquet"
DIAG = DERIVED / "AGGREGATION_DIAGNOSTICS.json"


def rows(path: Path) -> list[dict]:
    with path.open(newline="") as stream:
        return list(csv.DictReader(stream))


def unique_sorted(values) -> str:
    return "|".join(sorted({str(v) for v in values if pd.notna(v) and str(v)}))


def main() -> None:
    if any(p.exists() for p in (HC, NDA_FIRST, NDA_TIMELINE, BLA_TIMELINE, DIAG)):
        raise RuntimeError("Aggregation output exists; preserve prior run")
    gate_a = rows(ROOT / "GATE_A_REVIEW.csv")
    gate_b = rows(ROOT / "GATE_B_REVIEW.csv")
    page_qa = rows(ROOT / "BLA_PAGE_QA.csv")
    anomaly = rows(ROOT / "BLA_ANOMALY_REVIEW.csv")
    assert len(gate_a) == 75 and all(r["agent_decision"] == "EXACT" for r in gate_a)
    assert len(gate_b) == 50 and all(r["agent_decision"] == "SEMANTIC_CORRECT" and r["catastrophic_scope_flag"] == "False" for r in gate_b)
    assert len(page_qa) == 25 and all(r["agent_decision"] == "MATCH" for r in page_qa)
    assert len(anomaly) == 4 and all(r["agent_decision"] == "TIER_C_UNRESOLVED_SCOPE" for r in anomaly)

    product = pd.read_parquet(DERIVED / "SOURCE_SEMANTIC_CANDIDATES.parquet").fillna("")
    action = pd.read_parquet(DERIVED / "FDA_APPLICATION_ACTION.parquet").fillna("")
    doc = pd.read_parquet(DERIVED / "REGULATORY_DOCUMENT.parquet").fillna("")
    bla_page = pd.read_parquet(DERIVED / "BLA_ORIGINAL_LICENSURE_CANDIDATES.parquet").fillna("")
    orange = product[product.event_type == "NDA_PRODUCT_APPROVAL"].copy()
    purple = product[product.event_type == "BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL"].copy()
    page_a = bla_page[bla_page.product_row_date_relation == "PAGE_EQUALS_A_PRODUCT_ROW"].copy()
    page_c = bla_page[bla_page.product_row_date_relation != "PAGE_EQUALS_A_PRODUCT_ROW"].copy()
    assert len(orange) == 8209 and len(purple) == 1488 and len(page_a) == 746 and len(page_c) == 4
    orange["quality_tier"] = "TIER_A"
    page_a["quality_tier"] = "TIER_A"
    page_a["product_no"] = None
    standard = ["event_id", "drug_regulatory_id", "application_no", "application_type", "product_no",
                "event_type", "event_scope", "event_date", "document_date", "document_signature_date",
                "source", "source_url", "source_row_key", "source_snapshot", "source_release_date",
                "retrieved_at", "public_first_date", "is_derived", "derivation_rule", "quality_tier",
                "license_type", "ingredient", "trade_name", "dosage_route", "strength", "transformation_script"]
    high = pd.concat([orange.reindex(columns=standard), page_a.reindex(columns=standard)], ignore_index=True)
    high["public_first_date"] = None
    high["document_date"] = None
    high["document_signature_date"] = None
    assert high.event_id.is_unique and high.public_first_date.isna().all()
    high.to_parquet(HC, index=False)

    firsts = []
    orange_by_app = {app: frame for app, frame in orange.groupby("application_no", sort=True)}
    for app, frame in orange_by_app.items():
        first_day = frame.event_date.min()
        source_ids = sorted(frame.loc[frame.event_date == first_day, "event_id"].tolist())
        firsts.append({"event_id": f"FDA:OB:NDA:FIRST_OBSERVED:{app}:{first_day}",
                       "drug_regulatory_id": f"NDA:{app}", "application_no": app,
                       "application_type": "NDA", "product_no": None,
                       "event_type": "NDA_FIRST_OBSERVED_PRODUCT_APPROVAL",
                       "event_scope": "APPLICATION_AGGREGATION_OF_PRODUCT_ROWS", "event_date": first_day,
                       "source": "orange_book_derived", "source_row_key": unique_sorted(frame.loc[frame.event_date == first_day, "source_row_key"]),
                       "source_snapshot": frame.source_snapshot.iloc[0], "source_url": frame.source_url.iloc[0],
                       "retrieved_at": frame.retrieved_at.iloc[0], "source_release_date": frame.source_release_date.iloc[0],
                       "public_first_date": None, "is_derived": True,
                       "derivation_rule": "MIN_EXACT_ORANGE_NDA_PRODUCT_APPROVAL_IN_CURRENT_SNAPSHOT",
                       "quality_tier": "TIER_B", "contributing_product_events": len(source_ids),
                       "contributing_event_ids": "|".join(source_ids)})
    first_frame = pd.DataFrame(firsts)
    assert first_frame.application_no.is_unique
    first_frame.to_parquet(NDA_FIRST, index=False)

    action_by_app = {app: frame for app, frame in action.groupby("application_no", sort=True)}
    doc_by_app = {app: frame for app, frame in doc.groupby("application_no", sort=True)}
    nda_apps = sorted(set(orange.application_no) | set(action.loc[action.application_type == "NDA", "application_no"]))
    nda_rows = []
    for app in nda_apps:
        frame = orange_by_app.get(app)
        actions = action_by_app.get(app)
        documents = doc_by_app.get(app)
        first_day = frame.event_date.min() if frame is not None else None
        later = frame.loc[frame.event_date > first_day] if frame is not None else None
        original_actions = actions.loc[(actions.submission_type == "ORIG") & actions.approved_status_code] if actions is not None else None
        supplement_actions = actions.loc[(actions.submission_type == "SUPPL") & actions.approved_status_code] if actions is not None else None
        nda_rows.append({
            "application_no": app, "drug_regulatory_id": f"NDA:{app}",
            "earliest_observed_product_approval_date": first_day,
            "first_product_event_ids": unique_sorted(frame.loc[frame.event_date == first_day, "event_id"]) if frame is not None else "",
            "later_product_approval_dates": unique_sorted(later.event_date) if later is not None else "",
            "later_product_event_ids": unique_sorted(later.event_id) if later is not None else "",
            "product_rows": len(frame) if frame is not None else 0,
            "unique_products": frame.product_no.nunique() if frame is not None else 0,
            "unique_strengths": frame.strength.nunique() if frame is not None else 0,
            "unique_dosage_routes": frame.dosage_route.nunique() if frame is not None else 0,
            "drugs_original_approved_action_dates": unique_sorted(original_actions.event_date) if original_actions is not None else "",
            "drugs_supplement_approved_action_dates": unique_sorted(supplement_actions.event_date) if supplement_actions is not None else "",
            "drugs_original_action_count": len(original_actions) if original_actions is not None else 0,
            "drugs_supplement_action_count": len(supplement_actions) if supplement_actions is not None else 0,
            "document_record_count": len(documents) if documents is not None else 0,
            "document_ids": unique_sorted(documents.document_id) if documents is not None else "",
            "document_registry": "derived/REGULATORY_DOCUMENT.parquet",
            "source_scope_note": "Product rows and application actions remain distinct; document IDs link to metadata but do not set an event date.",
        })
    nda_frame = pd.DataFrame(nda_rows)
    assert nda_frame.application_no.is_unique
    nda_frame.to_parquet(NDA_TIMELINE, index=False)

    purple_by_bla = {app: frame for app, frame in purple.groupby("application_no", sort=True)}
    bla_rows = []
    for row in bla_page.to_dict("records"):
        app = row["application_no"]
        products = purple_by_bla[app]
        actions = action_by_app.get(app)
        documents = doc_by_app.get(app)
        original_actions = actions.loc[(actions.submission_type == "ORIG") & actions.approved_status_code] if actions is not None else None
        supplement_actions = actions.loc[(actions.submission_type == "SUPPL") & actions.approved_status_code] if actions is not None else None
        bla_rows.append({
            "application_no": app, "drug_regulatory_id": f"BLA:{app}",
            "original_licensure_page_date": row["event_date"],
            "original_licensure_event_id": row["event_id"],
            "quality_tier": "TIER_A" if row["product_row_date_relation"] == "PAGE_EQUALS_A_PRODUCT_ROW" else "TIER_C_UNRESOLVED_SCOPE",
            "page_product_date_relation": row["product_row_date_relation"],
            "product_approval_dates": unique_sorted(products.event_date),
            "product_rows": len(products), "unique_products": products.product_no.nunique(),
            "proper_names_current_snapshot": unique_sorted(products.ingredient),
            "proprietary_names_current_snapshot": unique_sorted(products.trade_name),
            "license_type": "351(a)", "biosimilar_status": "NOT_351K_IN_AUGUST_2026_SOURCE",
            "reference_product_status": "UNKNOWN",
            "drugs_original_approved_action_dates": unique_sorted(original_actions.event_date) if original_actions is not None else "",
            "drugs_supplement_approved_action_dates": unique_sorted(supplement_actions.event_date) if supplement_actions is not None else "",
            "drugs_original_action_count": len(original_actions) if original_actions is not None else 0,
            "drugs_supplement_action_count": len(supplement_actions) if supplement_actions is not None else 0,
            "document_record_count": len(documents) if documents is not None else 0,
            "document_ids": unique_sorted(documents.document_id) if documents is not None else "",
            "document_registry": "derived/REGULATORY_DOCUMENT.parquet",
            "page_source_url": row["source_url"], "page_retrieved_at": row["retrieved_at"],
            "source_scope_note": "BLA-level page date and monthly product approval dates retained separately.",
        })
    bla_frame = pd.DataFrame(bla_rows)
    assert bla_frame.application_no.is_unique
    bla_frame.to_parquet(BLA_TIMELINE, index=False)

    diag = {
        "run_id": "EXP022-AGG-001", "high_confidence_event_rows": len(high),
        "tier_a_by_event_type": dict(Counter(high.event_type)),
        "tier_b_nda_first_observed": len(first_frame),
        "nda_application_timeline_rows": len(nda_frame),
        "nda_with_orange_product_date": int(nda_frame.earliest_observed_product_approval_date.notna().sum()),
        "nda_with_later_product_approval": int(nda_frame.later_product_approval_dates.ne("").sum()),
        "bla_license_timeline_rows": len(bla_frame),
        "bla_tier_c_unresolved_scope": int(bla_frame.quality_tier.ne("TIER_A").sum()),
        "bla_with_drugs_original_action": int(bla_frame.drugs_original_action_count.gt(0).sum()),
        "public_first_known_events": 0,
        "same_scope_cross_source_comparators": 0,
        "true_date_conflict_rate": None,
        "scope_note": "High-confidence source events are regulatory-layer records, not indication-specific or historical prediction outcomes.",
    }
    DIAG.write_text(json.dumps(diag, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(diag, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
