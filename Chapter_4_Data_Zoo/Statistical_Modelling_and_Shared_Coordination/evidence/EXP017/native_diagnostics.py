#!/usr/bin/env python3
"""Check native summary quality and the EVA zero-score exception."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd

from access_probe import parquet_urls


HERE = Path(__file__).resolve().parent
OUT = HERE / "native_diagnostics.json"
SOURCES = ("gwas_credible_sets", "gene_burden", "eva", "expression_atlas", "impc", "europepmc")


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"Existing result is preserved: {OUT}")
    con = duckdb.connect()
    association = pd.read_parquet(HERE / "association_cohort_18.parquet")
    result = {"run_id": "EXP017-NATIVE-DIAG-001", "sources": {}}
    for datasource in SOURCES:
        frame = pd.read_parquet(HERE / f"native_{datasource}_pair_features.parquet")
        numbers = frame.select_dtypes(include="number")
        result["sources"][datasource] = {
            "pairs": len(frame),
            "native_evidence_rows": int(frame.native_evidence_rows.sum()),
            "numeric_null_counts": {name: int(numbers[name].isna().sum()) for name in numbers},
            "numeric_ranges": {name: [float(numbers[name].min()), float(numbers[name].max())]
                               for name in numbers if numbers[name].notna().any()},
        }
    eva = pd.read_parquet(HERE / "native_eva_pair_features.parquet")
    assoc_eva = association.loc[association.aggregationValue == "eva", ["targetId", "diseaseId"]]
    extra = eva[["targetId", "diseaseId", "max_native_score"]].merge(
        assoc_eva.assign(in_association=True), on=["targetId", "diseaseId"], how="left", validate="one_to_one"
    )
    extra = extra.loc[extra.in_association.isna()]
    if len(extra) != 638 or not np.all(extra.max_native_score.to_numpy() == 0):
        raise RuntimeError("EVA zero-score exception no longer matches observed 26.06 state")
    con.register("extra_eva_pairs", extra[["targetId", "diseaseId"]])
    urls = parquet_urls("evidence_eva")
    category_rows = con.execute("""
        SELECT e.clinicalSignificances::VARCHAR AS significance_set,
               count(*) AS evidence_rows,
               count(DISTINCT e.targetId || '|' || e.diseaseId) AS pairs,
               min(e.score) AS min_score,
               max(e.score) AS max_score
        FROM read_parquet(?) e
        INNER JOIN extra_eva_pairs c
          ON e.targetId = c.targetId AND e.diseaseId = c.diseaseId
        WHERE e.datasourceId = 'eva'
        GROUP BY significance_set
        ORDER BY evidence_rows DESC
    """, [urls]).fetchall()
    result["eva_native_only"] = {
        "pairs": len(extra),
        "all_pair_max_score_zero": True,
        "category_rows": [dict(zip(("significance_set", "evidence_rows", "pairs", "min_score", "max_score"), row)) for row in category_rows],
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"eva_native_only": result["eva_native_only"],
                      "source_numeric_null_fields": {ds: {k: v for k, v in item["numeric_null_counts"].items() if v}
                                                     for ds, item in result["sources"].items()}},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
