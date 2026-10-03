#!/usr/bin/env python3
"""Preserve EVA clinical significance and review-category counts by cohort pair."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from access_probe import parquet_urls


HERE = Path(__file__).resolve().parent
OUT = HERE / "native_eva_category_features.parquet"
META = HERE / "native_eva_category_definition.json"


def quote(text: str) -> str:
    return "'" + text.replace("'", "''") + "'"


def main() -> None:
    if OUT.exists() or META.exists():
        raise SystemExit("Existing EVA category state is preserved")
    con = duckdb.connect()
    con.execute("CREATE TABLE cohort AS SELECT targetId,diseaseId FROM read_parquet(?)", [str(HERE / "cohort_mapped.parquet")])
    urls = parquet_urls("evidence_eva")
    query = f"""
        COPY (
          SELECT e.targetId,e.diseaseId,
                 count(*) AS category_evidence_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'pathogenic') THEN 1 ELSE 0 END) AS pathogenic_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'likely pathogenic') THEN 1 ELSE 0 END) AS likely_pathogenic_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'benign') THEN 1 ELSE 0 END) AS benign_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'likely benign') THEN 1 ELSE 0 END) AS likely_benign_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'uncertain significance')
                                OR list_contains(e.clinicalSignificances, 'uncertain risk allele') THEN 1 ELSE 0 END) AS uncertain_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'conflicting classifications of pathogenicity')
                                OR lower(e.confidence) LIKE '%conflict%' THEN 1 ELSE 0 END) AS conflict_rows,
                 sum(CASE WHEN list_contains(e.clinicalSignificances, 'evidence only')
                                OR list_contains(e.clinicalSignificances, 'not provided') THEN 1 ELSE 0 END) AS evidence_only_rows,
                 sum(CASE WHEN e.confidence = 'reviewed by expert panel' THEN 1 ELSE 0 END) AS expert_panel_rows
          FROM read_parquet(?) e
          INNER JOIN cohort c ON e.targetId = c.targetId AND e.diseaseId = c.diseaseId
          WHERE e.datasourceId = 'eva'
          GROUP BY e.targetId,e.diseaseId
        ) TO {quote(str(OUT))} (FORMAT PARQUET, COMPRESSION ZSTD)
    """
    con.execute(query, [urls])
    pair_rows, total = con.execute("SELECT count(*),sum(category_evidence_rows) FROM read_parquet(?)", [str(OUT)]).fetchone()
    if pair_rows != 797 or total != 7389:
        raise RuntimeError(f"EVA category state unexpected coverage: {pair_rows}/{total}")
    META.write_text(json.dumps({
        "run_id": "EXP017-EVA-CATEGORY-001",
        "input": "Open Targets 26.06 evidence_eva original URL list in native_cache_manifest.json",
        "output": str(OUT),
        "pair_rows": pair_rows,
        "evidence_rows": total,
        "semantics": "Counts are nonexclusive when one evidence row has multiple clinicalSignificances. No category is treated as outcome label.",
        "classification": {
            "pathogenic_rows": "exact array item pathogenic",
            "likely_pathogenic_rows": "exact array item likely pathogenic",
            "benign_rows": "exact array item benign",
            "likely_benign_rows": "exact array item likely benign",
            "uncertain_rows": "exact uncertain significance or uncertain risk allele",
            "conflict_rows": "conflicting classifications item or confidence mentions conflict",
            "evidence_only_rows": "exact evidence only or not provided",
            "expert_panel_rows": "confidence exactly reviewed by expert panel",
        },
    }, indent=2) + "\n")
    print(json.dumps({"pair_rows": pair_rows, "evidence_rows": total, "output": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
