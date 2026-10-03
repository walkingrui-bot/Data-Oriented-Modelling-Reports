"""EXP026-SPLIT-001: freeze one person-level stratified split from EXP025 audit."""

import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT.parent / "STAT-PSYMOE-EXP025-20261002-001" / "SUBJECT_AUDIT.csv"
OUT = ROOT / "SPLIT_MANIFEST.csv"
QA = ROOT / "SPLIT_AUDIT.json"
LABELS = {"Healthy": 0, "Parkinson's": 1, "Other Movement Disorders": 2, "Atypical Parkinsonism": 2, "Multiple Sclerosis": 2, "Essential Tremor": 2}


def main():
    if OUT.exists() or QA.exists():
        raise FileExistsError("Split already frozen")
    with AUDIT.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 469 or len({r["subject_id"] for r in rows}) != 469:
        raise ValueError("Expected 469 unique persons")
    grouped = defaultdict(list)
    for row in rows:
        if row["source_error"] or row["patient_id_match"] != "True" or row["movement_id_match"] != "True" or row["questionnaire_id_match"] != "True" or row["condition_match"] != "True":
            raise ValueError(f"Identity gate failed: {row['subject_id']}")
        grouped[LABELS[row["condition"]]].append(row["subject_id"])
    if dict(sorted((k, len(v)) for k, v in grouped.items())) != {0: 79, 1: 276, 2: 114}:
        raise ValueError("Cohort counts changed")
    rng = random.Random(20261002)
    output = []
    for label in sorted(grouped):
        ids = sorted(grouped[label])
        rng.shuffle(ids)
        n_train, n_val = int(0.60 * len(ids)), int(0.20 * len(ids))
        for ix, subject_id in enumerate(ids):
            split = "train" if ix < n_train else "validation" if ix < n_train + n_val else "test"
            output.append({"subject_id": subject_id, "label": label, "split": split})
    output.sort(key=lambda r: r["subject_id"])
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["subject_id", "label", "split"])
        writer.writeheader()
        writer.writerows(output)
    count = Counter((r["split"], r["label"]) for r in output)
    QA.write_text(json.dumps({"run_id": "EXP026-SPLIT-001", "seed": 20261002, "persons": len(output), "unique_persons": len({r["subject_id"] for r in output}), "counts": {f"{s}_{l}": n for (s, l), n in sorted(count.items())}, "label_order": {"0": "HC", "1": "PD", "2": "DD"}}, indent=2) + "\n")
    print(QA.read_text())


if __name__ == "__main__":
    main()
