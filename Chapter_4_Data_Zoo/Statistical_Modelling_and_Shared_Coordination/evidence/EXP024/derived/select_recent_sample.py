"""EXP024-SAMPLE-001: freeze four application-disjoint recent action strata."""

import csv
import random
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
EXP021 = PARENT / "STAT-PSYMOE-EXP021-20261002-001"
EXP022 = PARENT / "STAT-PSYMOE-EXP022-20261002-001"
EXP023 = PARENT / "STAT-PSYMOE-EXP023-20261002-001"
OUT = ROOT / "SAMPLE.csv"
KEY = ["application_type", "application_no", "submission_type", "submission_no"]


def prior_applications():
    paths = [
        (EXP021 / "MANUAL_VALIDATION.csv", "application_number"),
        (EXP021 / "derived/failed_MANUAL_A_002/MANUAL_VALIDATION.csv", "application_number"),
        (EXP022 / "GATE_A_SAMPLE.csv", "application_no"),
        (EXP022 / "GATE_B_SAMPLE.csv", "application_no"),
        (EXP022 / "BLA_PAGE_QA.csv", "bla_number"),
        (EXP022 / "BLA_PAGE_AVAILABILITY.csv", "bla_number"),
        (EXP022 / "BLA_ANOMALY_REVIEW.csv", "bla_number"),
        (EXP023 / "SAMPLE.csv", "application_no"),
    ]
    result = {"101382", "101384", "102219", "103955", "125789"}
    for path, column in paths:
        with path.open(newline="") as f:
            result.update(str(r[column]).strip().zfill(6) for r in csv.DictReader(f) if r[column])
    return result


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    actions = pd.read_parquet(EXP022 / "derived/FDA_APPLICATION_ACTION.parquet")
    docs = pd.read_parquet(EXP022 / "derived/REGULATORY_DOCUMENT.parquet")
    hc = pd.read_parquet(EXP022 / "derived/REGULATORY_EVENT_HIGH_CONFIDENCE.parquet")
    allowed = set(zip(hc.application_type, hc.application_no))
    actions = actions[actions.apply(lambda r: (r.application_type, r.application_no) in allowed, axis=1)]
    actions = actions[(actions.approved_status_code == True) & (actions.event_date >= "2010-01-01") & (actions.event_date <= "2024-12-31")].copy()
    actions["submission_no_numeric"] = pd.to_numeric(actions.submission_no, errors="coerce")
    actions.sort_values(["event_date", "submission_no_numeric", "event_id"], inplace=True)

    labels = docs[(docs.document_type_label == "Label") & docs.document_url.notna() & docs.document_url.ne("")].copy()
    labels["date_order"] = labels.document_date.fillna("9999-12-31")
    labels["doc_numeric"] = pd.to_numeric(labels.document_id, errors="coerce")
    labels.sort_values(["date_order", "doc_numeric", "source_row_key"], inplace=True)
    labels_by_key = labels.groupby(KEY, dropna=False)

    excluded = prior_applications()
    strata = [
        ("ORIG_NDA", 20261027, 15, "ORIG", "NDA"),
        ("ORIG_BLA", 20261028, 5, "ORIG", "BLA"),
        ("EFFICACY_NDA", 20261029, 15, "SUPPL", "NDA"),
        ("EFFICACY_BLA", 20261030, 5, "SUPPL", "BLA"),
    ]
    output = []
    for stratum, seed, size, sub_type, app_type in strata:
        pool = actions[(actions.submission_type == sub_type) & (actions.application_type == app_type) & (~actions.application_no.isin(excluded))]
        if sub_type == "SUPPL":
            pool = pool[pool.submission_class == "EFFICACY"]
        pool = pool.drop_duplicates("application_no", keep="first").sort_values("application_no")
        if len(pool) < size:
            raise RuntimeError(f"Insufficient {stratum} pool after exclusions: {len(pool)}")
        for i, row_idx in enumerate(random.Random(seed).sample(list(pool.index), size), start=1):
            a = pool.loc[row_idx]
            key = tuple(a[k] for k in KEY)
            group = labels_by_key.get_group(key) if key in labels_by_key.groups else None
            doc = group.iloc[0] if group is not None else None
            output.append({
                "sample_id": f"{stratum}-{i:02d}", "stratum": stratum, "application_type": a.application_type,
                "application_no": a.application_no, "submission_type": a.submission_type,
                "submission_no": a.submission_no, "submission_class": a.submission_class,
                "action_event_id": a.event_id, "action_date": a.event_date,
                "same_key_label_count": len(group) if group is not None else 0,
                "selected_document_id": doc.document_id if doc is not None else "",
                "selected_document_date": doc.document_date if doc is not None and doc.document_date else "",
                "selected_document_url": doc.document_url if doc is not None else "",
                "review_status": "PENDING",
            })
            excluded.add(a.application_no)
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(output[0]))
        writer.writeheader()
        writer.writerows(output)
    print({"sample_rows": len(output), "unique_applications": len({x["application_no"] for x in output}), "with_label_url": {s: sum(bool(x["selected_document_url"]) for x in output if x["stratum"] == s) for s, *_ in strata}})


if __name__ == "__main__":
    main()
