"""Correct A-006 metadata semantics without re-reading or replacing source facts."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "derived" / "failed_EVENT_A_006"


def main() -> None:
    frame = pd.read_parquet(OLD / "REGULATORY_EVENT_A.parquet")
    assert (frame["database_ingest_date"] == frame["retrieved_at"]).all(), "Unexpected ingest semantics; stop"
    frame = frame.rename(columns={"original_document_url": "linked_letter_url",
                                  "original_document_date": "linked_letter_record_date"})
    frame["database_ingest_date"] = ""
    frame["linked_letter_role"] = frame["linked_letter_url"].map(lambda url: "UNVERIFIED_TYPE_1_LETTER" if url else "")
    frame["transformation_script"] = "derived/build_event_a.py v0.2; derived/repair_event_a_metadata.py v0.1"
    assert len(frame) == 15399 and frame["event_id"].is_unique
    frame.to_parquet(ROOT / "derived" / "REGULATORY_EVENT_A.parquet", index=False)
    diagnostics = json.loads((OLD / "EVENT_A_DIAGNOSTICS.json").read_text())
    diagnostics.update({"run_id": "EXP021-EVENT-A-007", "parent_run_id": "EXP021-EVENT-A-006",
                        "metadata_correction": "database_ingest_date cleared because source ingest is unknown; retrieved_at retained as retrieval time; generic type-1 letter URL relabelled unverified linked_letter, not proof of original approval",
                        "event_fact_changes": 0, "event_rows": len(frame)})
    (ROOT / "derived" / "EVENT_A_DIAGNOSTICS.json").write_text(json.dumps(diagnostics, indent=2) + "\n")
    print(json.dumps({"run_id": diagnostics["run_id"], "rows": len(frame), "public_date_known": int((frame["public_date"] != "").sum()),
                      "database_ingest_date_known": int((frame["database_ingest_date"] != "").sum()),
                      "linked_type_1_letters": int((frame["linked_letter_url"] != "").sum())}, indent=2))


if __name__ == "__main__":
    main()
