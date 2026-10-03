"""EXP023-SUPPORT-001: bounded action/label metadata availability audit."""

import csv
import io
import json
import urllib.request
import zipfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EXP022 = ROOT.parent / "STAT-PSYMOE-EXP022-20261002-001"
DERIVED = EXP022 / "derived"
OUT = ROOT / "SOURCE_SUPPORT.json"


def table(z, name):
    with z.open(name) as raw:
        return list(csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline=""), delimiter="\t"))


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    src = json.loads((EXP022 / "SOURCE_INDEX.json").read_text())["sources"]["drugs_at_fda"]
    req = urllib.request.Request(src["source_url"], headers={"User-Agent": "Mozilla/5.0 EXP023 source support"})
    with urllib.request.urlopen(req, timeout=90) as response:
        body = response.read()
        last_modified = response.headers.get("Last-Modified")
    if last_modified != src["last_modified"] or len(body) != src["bytes_read"]:
        raise RuntimeError("Drugs@FDA source metadata differs from EXP022; freeze a new source version first")
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        classes = table(z, "SubmissionClass_Lookup.txt")
        doc_types = table(z, "ApplicationsDocsType_Lookup.txt")
    lookup = {r["SubmissionClassCodeID"].strip(): r["SubmissionClassCode"].strip() for r in classes}
    types = {r["ApplicationDocsType_Lookup_ID"].strip(): r["ApplicationDocsType_Lookup_Description"].strip() for r in doc_types}
    if "EFFICACY" not in lookup.values() or "Label" not in types.values():
        raise RuntimeError("Official class or document lookup lacks the prespecified labels")

    a = pd.read_parquet(DERIVED / "FDA_APPLICATION_ACTION.parquet")
    d = pd.read_parquet(DERIVED / "REGULATORY_DOCUMENT.parquet")
    h = pd.read_parquet(DERIVED / "REGULATORY_EVENT_HIGH_CONFIDENCE.parquet")
    allowed = set(zip(h.application_type, h.application_no))
    a = a[a.apply(lambda r: (r.application_type, r.application_no) in allowed, axis=1)].copy()
    a = a[(a.approved_status_code == True) & a.event_date.notna() & a.event_date.ne("")]
    keys = ["application_type", "application_no", "submission_type", "submission_no"]
    duplicate_actions = int(a.duplicated(keys).sum())
    if duplicate_actions:
        raise RuntimeError(f"Nonunique action key: {duplicate_actions}")
    d = d[d.apply(lambda r: (r.application_type, r.application_no) in allowed, axis=1)].copy()
    label = d[(d.document_type_label == "Label") & d.document_url.notna() & d.document_url.ne("")]
    label_counts = label.groupby(keys).size().rename("same_key_label_count")
    a = a.join(label_counts, on=keys)
    a["same_key_label_count"] = a.same_key_label_count.fillna(0).astype(int)
    arms = {
        "ORIG_APPROVED": a[a.submission_type == "ORIG"],
        "EFFICACY_SUPPL_APPROVED": a[(a.submission_type == "SUPPL") & (a.submission_class == "EFFICACY")],
    }
    stats = {}
    for name, arm in arms.items():
        stats[name] = {
            "actions": int(len(arm)),
            "applications": int(arm[["application_type", "application_no"]].drop_duplicates().shape[0]),
            "actions_with_same_key_label_url": int((arm.same_key_label_count > 0).sum()),
            "applications_with_same_key_label_url": int(arm.loc[arm.same_key_label_count > 0, ["application_type", "application_no"]].drop_duplicates().shape[0]),
            "action_count_by_type": {str(k): int(v) for k, v in arm.application_type.value_counts().items()},
            "label_candidate_count_distribution": {str(k): int(v) for k, v in arm.same_key_label_count.value_counts().sort_index().items()},
            "action_date_range": [str(arm.event_date.min()) if len(arm) else None, str(arm.event_date.max()) if len(arm) else None],
        }
    result = {
        "run_id": "EXP023-SUPPORT-001",
        "status": "COMPLETED",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "source_url": src["source_url"],
        "source_last_modified": last_modified,
        "source_bytes_read": len(body),
        "official_lookup_efficacy_code": [k for k, v in lookup.items() if v == "EFFICACY"],
        "official_lookup_label_type_id": [k for k, v in types.items() if v == "Label"],
        "allowed_event_applications": len(allowed),
        "eligible": stats,
        "support_gate": "PASS" if all(v["applications"] >= 20 for v in stats.values()) else "STOP_SUPPORT",
        "interpretation": "Metadata support only; a Label type and same submission key do not prove document role, public date, or indication approval.",
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
