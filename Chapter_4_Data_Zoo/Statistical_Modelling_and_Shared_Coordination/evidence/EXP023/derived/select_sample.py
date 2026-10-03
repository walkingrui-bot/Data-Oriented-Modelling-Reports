"""EXP023-SAMPLE-001: fixed 20+20 application-disjoint audit sample."""

import csv
import random
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent
EXP021 = PARENT / "STAT-PSYMOE-EXP021-20261002-001"
EXP022 = PARENT / "STAT-PSYMOE-EXP022-20261002-001"
OUT = ROOT / "SAMPLE.csv"
KEY = ["application_type", "application_no", "submission_type", "submission_no"]


def read_excluded():
    paths = [
        (EXP021 / "MANUAL_VALIDATION.csv", "application_number"),
        (EXP021 / "derived/failed_MANUAL_A_002/MANUAL_VALIDATION.csv", "application_number"),
        (EXP022 / "GATE_A_SAMPLE.csv", "application_no"),
        (EXP022 / "GATE_B_SAMPLE.csv", "application_no"),
        (EXP022 / "BLA_PAGE_QA.csv", "bla_number"),
        (EXP022 / "BLA_PAGE_AVAILABILITY.csv", "bla_number"),
        (EXP022 / "BLA_ANOMALY_REVIEW.csv", "bla_number"),
    ]
    excluded = set()
    for path, column in paths:
        with path.open(newline="") as file:
            for row in csv.DictReader(file):
                value = str(row[column]).strip()
                if value:
                    excluded.add(value.zfill(6))
    excluded.update({"101382", "101384", "102219", "103955", "125789"})
    return excluded


def chosen_action_rows(actions, excluded):
    a = actions[~actions.application_no.isin(excluded)].copy()
    a = a[(a.approved_status_code == True) & a.event_date.notna() & a.event_date.ne("")]
    a["submission_no_numeric"] = pd.to_numeric(a.submission_no, errors="coerce")
    a.sort_values(["event_date", "submission_no_numeric", "event_id"], inplace=True)
    return a.drop_duplicates(["application_type", "application_no"], keep="first")


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    actions = pd.read_parquet(EXP022 / "derived/FDA_APPLICATION_ACTION.parquet")
    docs = pd.read_parquet(EXP022 / "derived/REGULATORY_DOCUMENT.parquet")
    hc = pd.read_parquet(EXP022 / "derived/REGULATORY_EVENT_HIGH_CONFIDENCE.parquet")
    allowed = set(zip(hc.application_type, hc.application_no))
    actions = actions[actions.apply(lambda x: (x.application_type, x.application_no) in allowed, axis=1)]
    excluded = read_excluded()

    orig = chosen_action_rows(actions[actions.submission_type == "ORIG"], excluded)
    orig = orig.sort_values(["application_type", "application_no"])
    orig_ids = random.Random(20261025).sample(list(orig.index), 20)
    orig_sample = orig.loc[orig_ids]
    excluded |= set(orig_sample.application_no)

    eff = chosen_action_rows(actions[(actions.submission_type == "SUPPL") & (actions.submission_class == "EFFICACY")], excluded)
    eff = eff.sort_values(["application_type", "application_no"])
    eff_ids = random.Random(20261026).sample(list(eff.index), 20)
    eff_sample = eff.loc[eff_ids]

    labels = docs[(docs.document_type_label == "Label") & docs.document_url.notna() & docs.document_url.ne("")].copy()
    labels["document_date_order"] = labels.document_date.fillna("9999-12-31")
    labels["document_id_numeric"] = pd.to_numeric(labels.document_id, errors="coerce")
    labels.sort_values(["document_date_order", "document_id_numeric", "source_row_key"], inplace=True)
    all_labels = labels.groupby(KEY, dropna=False)
    fields = ["sample_id", "arm", "application_type", "application_no", "submission_type", "submission_no", "submission_class", "action_event_id", "action_date", "same_key_label_count", "selected_document_id", "selected_document_date", "selected_document_url", "review_status"]
    with OUT.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for arm, sample in (("ORIG_APPROVED", orig_sample), ("EFFICACY_SUPPL_APPROVED", eff_sample)):
            for i, (_, row) in enumerate(sample.iterrows(), start=1):
                key = tuple(row[x] for x in KEY)
                group = all_labels.get_group(key) if key in all_labels.groups else None
                doc = group.iloc[0] if group is not None else None
                writer.writerow({
                    "sample_id": f"{arm[:4]}-{i:02d}", "arm": arm,
                    "application_type": row.application_type, "application_no": row.application_no,
                    "submission_type": row.submission_type, "submission_no": row.submission_no,
                    "submission_class": row.submission_class, "action_event_id": row.event_id,
                    "action_date": row.event_date, "same_key_label_count": len(group) if group is not None else 0,
                    "selected_document_id": doc.document_id if doc is not None else "",
                    "selected_document_date": doc.document_date if doc is not None and doc.document_date else "",
                    "selected_document_url": doc.document_url if doc is not None else "",
                    "review_status": "PENDING",
                })
    print({"ORIG_APPROVED": len(orig_sample), "EFFICACY_SUPPL_APPROVED": len(eff_sample), "distinct_applications": len(set(orig_sample.application_no) | set(eff_sample.application_no)), "output": str(OUT)})


if __name__ == "__main__":
    main()
