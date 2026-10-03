"""Scoped validation of EXP022-derived regulatory semantics and gates."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pandas as pd
import pyarrow  # noqa: F401

ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "derived"
OUT = DERIVED / "LOCAL_VALIDATION.json"


def csv_rows(name: str) -> list[dict]:
    with (ROOT / name).open(newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    if OUT.exists():
        raise RuntimeError("Local validation output exists; preserve prior attempt")
    sources = json.loads((ROOT / "SOURCE_INDEX.json").read_text())["sources"]
    assert all(v["same_metadata_as_exp021"] for v in sources.values())
    gate_a, gate_b, page_qa = (csv_rows(x) for x in ("GATE_A_REVIEW.csv", "GATE_B_REVIEW.csv", "BLA_PAGE_QA.csv"))
    assert len(gate_a) == 75 and all(x["agent_decision"] == "EXACT" for x in gate_a)
    assert len(gate_b) == 50 and all(x["agent_decision"] == "SEMANTIC_CORRECT" and x["catastrophic_scope_flag"] == "False" for x in gate_b)
    assert len(page_qa) == 25 and all(x["agent_decision"] == "MATCH" for x in page_qa)
    audit = pd.read_csv(ROOT / "EVENT_SCOPE_AUDIT.csv", dtype=str, keep_default_na=False)
    true = csv_rows("TRUE_DATE_CONFLICTS.csv")
    assert len(audit) == 10998 and not true and not audit.same_scope_assessable.eq("True").any()
    assert audit.exp022_scope_class.value_counts().to_dict() == {
        "UNRESOLVED_SCOPE": 7031, "SOURCE_ONLY": 2352, "DIFFERENT_SCOPE_EXPECTED": 1615}
    docs = pd.read_parquet(DERIVED / "REGULATORY_DOCUMENT.parquet")
    assert len(docs) == 74005 and docs.verified_document_role.eq("UNKNOWN").all()
    high = pd.read_parquet(DERIVED / "REGULATORY_EVENT_HIGH_CONFIDENCE.parquet")
    first = pd.read_parquet(DERIVED / "NDA_FIRST_OBSERVED_PRODUCT_APPROVAL.parquet")
    nda = pd.read_parquet(DERIVED / "NDA_APPLICATION_TIMELINE.parquet")
    bla = pd.read_parquet(DERIVED / "BLA_LICENSE_TIMELINE.parquet")
    page = pd.read_parquet(DERIVED / "BLA_ORIGINAL_LICENSURE_CANDIDATES.parquet")
    product = pd.read_parquet(DERIVED / "SOURCE_SEMANTIC_CANDIDATES.parquet")
    assert len(high) == 8955 and high.event_id.is_unique and high.quality_tier.eq("TIER_A").all()
    assert high.event_type.value_counts().to_dict() == {"NDA_PRODUCT_APPROVAL": 8209, "BLA_ORIGINAL_LICENSURE": 746}
    assert high.public_first_date.isna().all() and high.document_date.isna().all()
    assert set(high.loc[high.event_type == "BLA_ORIGINAL_LICENSURE", "source_url"]).issubset(set(page.source_url))
    assert set(page.loc[page.product_row_date_relation != "PAGE_EQUALS_A_PRODUCT_ROW", "application_no"]).isdisjoint(
        set(high.loc[high.event_type == "BLA_ORIGINAL_LICENSURE", "application_no"]))
    assert len(first) == 4099 and first.application_no.is_unique and first.quality_tier.eq("TIER_B").all()
    orange = product[product.event_type == "NDA_PRODUCT_APPROVAL"]
    minimum = orange.groupby("application_no").event_date.min()
    assert all(first.set_index("application_no").loc[minimum.index, "event_date"] == minimum)
    assert len(nda) == 5620 and nda.application_no.is_unique
    assert len(bla) == 750 and bla.application_no.is_unique and bla.quality_tier.value_counts().to_dict() == {
        "TIER_A": 746, "TIER_C_UNRESOLVED_SCOPE": 4}
    assert not any(x in high.columns for x in ("target_id", "disease_id", "indication_id"))
    result = {"run_id": "EXP022-VERIFY-001", "status": "PASS_SCOPED",
              "checked": ["source metadata lock", "75/75 ETL gate", "50/50 semantic gate", "25/25 page QA",
                          "10,998 full scope reclassification", "0 assessable same-scope pairs with rate null",
                          "document roles unknown", "8,955 unique Tier A events", "4 BLA anomalies excluded",
                          "4,099 NDA first-observed minima", "5,620 NDA and 750 BLA timelines",
                          "unknown public-first and document date remain null", "no target/disease/indication fields"],
              "not_checked": ["unrelated repository", "historical source release availability", "clinical indication",
                              "target or disease mapping", "prediction model"]}
    OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
