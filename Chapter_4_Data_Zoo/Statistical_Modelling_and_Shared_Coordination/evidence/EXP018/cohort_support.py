#!/usr/bin/env python3
"""Aggregate EXP018 overlap with the frozen EXP017 target split."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import duckdb
import pandas as pd


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
sys.path.insert(0, str(PARENT))
from train_source_level_six import split_name  # noqa: E402

OUT = HERE / "cohort_support.json"


def counts(frame: pd.DataFrame) -> dict:
    return {
        split: {
            "pairs": int(len(part)),
            "targets": int(part.targetId.nunique()),
            "positive_pairs": int(part.label.sum()),
            "negative_pairs": int(len(part) - part.label.sum()),
        }
        for split, part in frame.groupby("split", sort=False)
    }


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"Preserve existing output: {OUT}")
    preflight = json.loads((HERE / "preflight.json").read_text())
    con = duckdb.connect()
    cohort = pd.read_parquet(PARENT / "cohort_mapped.parquet")[["targetId", "diseaseId", "label"]]
    cohort["split"] = cohort.targetId.map(split_name)
    per_source = {}
    union_frames = []
    for ds, info in preflight["native_tables"].items():
        pair = con.execute("SELECT DISTINCT targetId,diseaseId FROM read_parquet(?)", [info["first_file_url"]]).df()
        matched = cohort.merge(pair, on=["targetId", "diseaseId"], how="inner", validate="one_to_one")
        per_source[ds] = counts(matched)
        union_frames.append(matched[["targetId", "diseaseId", "label", "split"]])
    union = pd.concat(union_frames).drop_duplicates(["targetId", "diseaseId"])
    result = {"run_id": "EXP018-SUPPORT-001", "per_source": per_source,
              "three_source_union": counts(union), "union_pairs": int(len(union)),
              "parent_cohort_pairs": int(len(cohort)), "test_was_previously_seen": True}
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
