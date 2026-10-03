"""EXP024-SUPPORT-001: recent same-submission Label URL metadata support."""

import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXP022 = ROOT.parent / "STAT-PSYMOE-EXP022-20261002-001"
EXP023 = ROOT.parent / "STAT-PSYMOE-EXP023-20261002-001"
OUT = ROOT / "SOURCE_SUPPORT.json"
KEY = ["application_type", "application_no", "submission_type", "submission_no"]


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    prior = json.loads((EXP023 / "SOURCE_SUPPORT.json").read_text())
    if prior["source_last_modified"] != json.loads((EXP022 / "SOURCE_INDEX.json").read_text())["sources"]["drugs_at_fda"]["last_modified"]:
        raise RuntimeError("Source snapshot provenance changed")
    a = pd.read_parquet(EXP022 / "derived/FDA_APPLICATION_ACTION.parquet")
    d = pd.read_parquet(EXP022 / "derived/REGULATORY_DOCUMENT.parquet")
    h = pd.read_parquet(EXP022 / "derived/REGULATORY_EVENT_HIGH_CONFIDENCE.parquet")
    allowed = set(zip(h.application_type, h.application_no))
    a = a[a.apply(lambda r: (r.application_type, r.application_no) in allowed, axis=1)].copy()
    a = a[(a.approved_status_code == True) & (a.event_date >= "2010-01-01") & (a.event_date <= "2024-12-31")]
    if a.duplicated(KEY).any():
        raise RuntimeError("Duplicate action key")
    labels = d[(d.document_type_label == "Label") & d.document_url.notna() & d.document_url.ne("")]
    label_keys = labels.groupby(KEY).size().rename("label_count")
    a = a.join(label_keys, on=KEY)
    a["label_count"] = a.label_count.fillna(0).astype(int)
    stats = {}
    for arm, arm_df in {
        "ORIG_APPROVED": a[a.submission_type == "ORIG"],
        "EFFICACY_SUPPL_APPROVED": a[(a.submission_type == "SUPPL") & (a.submission_class == "EFFICACY")],
    }.items():
        stats[arm] = {}
        for app_type, subset in arm_df.groupby("application_type"):
            stats[arm][str(app_type)] = {
                "actions": int(len(subset)),
                "applications": int(subset.application_no.nunique()),
                "actions_with_same_key_label_url": int((subset.label_count > 0).sum()),
                "applications_with_same_key_label_url": int(subset.loc[subset.label_count > 0, "application_no"].nunique()),
                "action_date_min": str(subset.event_date.min()),
                "action_date_max": str(subset.event_date.max()),
            }
    result = {
        "run_id": "EXP024-SUPPORT-001", "status": "COMPLETED", "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source": "EXP022 FDA application action/document and TIER_A application original paths; same snapshot as EXP023 lookup",
        "cohort_window": ["2010-01-01", "2024-12-31"], "strata": stats,
        "support_gate": "PASS" if all(stats.get(arm, {}).get(t, {}).get("applications", 0) >= 5 for arm in stats for t in ("NDA", "BLA")) else "STOP_SUPPORT",
        "note": "Label URL metadata support only; no PDF body or historical first-public evidence checked.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
