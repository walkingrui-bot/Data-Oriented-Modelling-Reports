#!/usr/bin/env python3
"""EXP018 cohort-limited native value diagnostic; writes aggregate counts only."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
PREFLIGHT = HERE / "preflight.json"
OUT = HERE / "native_diagnostics.json"
CATEGORIES = (
    "confidence", "allelicRequirements", "variantFunctionalConsequenceId",
    "directionOnTrait", "directionOnTarget", "qualityControls", "alleleOrigins",
)


def normalized(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, (list, tuple, dict, np.ndarray)):
        return json.dumps(value.tolist() if isinstance(value, np.ndarray) else value, ensure_ascii=False, sort_keys=True)
    if pd.isna(value):
        return None
    return str(value)


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"Preserve existing diagnostic: {OUT}")
    preflight = json.loads(PREFLIGHT.read_text())
    con = duckdb.connect()
    result = {"run_id": "EXP018-NATIVE-DIAG-001", "release": "26.06", "sources": {}}
    for ds, info in preflight["native_tables"].items():
        source = con.execute(
            "SELECT e.* FROM read_parquet(?) e INNER JOIN read_parquet(?) c "
            "ON e.targetId=c.targetId AND e.diseaseId=c.diseaseId",
            [info["first_file_url"], str(PARENT / "cohort_mapped.parquet")],
        ).df()
        if source.empty:
            raise RuntimeError(f"No cohort-matched native rows: {ds}")
        if source[["targetId", "diseaseId"]].isna().any().any():
            raise RuntimeError(f"Missing pair ID in {ds}")
        scores = source.score.to_numpy(float)
        if not np.isfinite(scores).all() or (scores < 0).any() or (scores > 1).any():
            raise RuntimeError(f"Invalid score in {ds}")
        categories = {}
        for field in CATEGORIES:
            if field not in source.columns:
                continue
            counter = Counter(normalized(v) for v in source[field])
            categories[field] = {
                "distinct_nonnull": sum(k is not None for k in counter),
                "missing_rows": counter.get(None, 0),
                "value_counts": [{"value": k, "rows": n} for k, n in counter.most_common(50)],
            }
        dates = {}
        for field in info["date_fields"]:
            vals = source[field].dropna().astype(str)
            dates[field] = {"nonmissing_rows": int(len(vals)), "min": vals.min() if len(vals) else None,
                            "max": vals.max() if len(vals) else None}
        result["sources"][ds] = {
            "native_rows_in_cohort": int(len(source)),
            "distinct_pairs": int(source[["targetId", "diseaseId"]].drop_duplicates().shape[0]),
            "score_min": float(scores.min()), "score_max": float(scores.max()),
            "score_zero_rows": int((scores == 0).sum()),
            "categories": categories,
            "dates_not_used_as_features": dates,
        }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({ds: {k: v for k, v in info.items() if k != "categories"}
                      for ds, info in result["sources"].items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
