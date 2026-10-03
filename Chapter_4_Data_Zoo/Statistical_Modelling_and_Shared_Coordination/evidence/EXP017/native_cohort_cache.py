#!/usr/bin/env python3
"""Materialise only cohort-limited native pair statistics from 26.06 evidence."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from access_probe import RELEASE, parquet_urls


HERE = Path(__file__).resolve().parent
SOURCES = (
    ("gene_burden", "evidence_gene_burden"),
    ("gwas_credible_sets", "evidence_gwas_credible_sets"),
    ("eva", "evidence_eva"),
    ("expression_atlas", "evidence_expression_atlas"),
    ("impc", "evidence_impc"),
    ("europepmc", "evidence_europepmc"),
)
EXTRA = {
    "gwas_credible_sets": """
        count(DISTINCT e.studyLocusId) AS distinct_study_loci,
        max(e.resourceScore) AS max_resource_score,
        avg(e.resourceScore) AS mean_resource_score,
        count(DISTINCT e.literature[1]) AS distinct_publications
    """,
    "gene_burden": """
        max(CASE WHEN e.pValueMantissa > 0 THEN -log10(e.pValueMantissa) - e.pValueExponent END) AS strongest_neglog10_p,
        max(abs(e.beta)) AS max_abs_beta,
        avg(e.beta) AS mean_beta,
        count(DISTINCT e.cohortId) AS distinct_cohorts,
        count(DISTINCT e.projectId) AS distinct_projects,
        max(e.studySampleSize) AS max_study_sample_size
    """,
    "eva": """
        count(DISTINCT e.variantId) AS distinct_variants,
        count(DISTINCT e.studyId) AS distinct_studies,
        count(DISTINCT e.clinicalSignificances::VARCHAR) AS distinct_significance_sets,
        count(DISTINCT e.confidence) AS distinct_confidence_levels
    """,
    "expression_atlas": """
        count(DISTINCT e.studyId) AS distinct_studies,
        count(DISTINCT e.contrast) AS distinct_contrasts,
        avg(e.log2FoldChangeValue) AS mean_signed_log2fc,
        avg(abs(e.log2FoldChangeValue)) AS mean_abs_log2fc,
        max(abs(e.log2FoldChangeValue)) AS max_abs_log2fc,
        sum(CASE WHEN e.log2FoldChangeValue > 0 THEN 1 ELSE 0 END) AS positive_direction_rows,
        sum(CASE WHEN e.log2FoldChangeValue < 0 THEN 1 ELSE 0 END) AS negative_direction_rows
    """,
    "impc": """
        count(DISTINCT e.biologicalModelId) AS distinct_models,
        max(e.resourceScore) AS max_resource_score,
        avg(e.resourceScore) AS mean_resource_score,
        max(array_length(e.diseaseModelAssociatedModelPhenotypes)) AS max_mouse_phenotype_count,
        max(array_length(e.diseaseModelAssociatedHumanPhenotypes)) AS max_human_phenotype_count
    """,
    "europepmc": """
        count(DISTINCT e.literature[1]) AS distinct_publications,
        min(e.publicationYear) AS earliest_publication_year,
        max(e.publicationYear) AS latest_publication_year,
        max(e.resourceScore) AS max_resource_score,
        avg(e.resourceScore) AS mean_resource_score
    """,
}
OUT_MANIFEST = HERE / "native_cache_manifest.json"


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    if OUT_MANIFEST.exists():
        raise SystemExit(f"Existing manifest is preserved: {OUT_MANIFEST}")
    con = duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET memory_limit='4GB'")
    con.execute("CREATE TABLE cohort AS SELECT targetId,diseaseId FROM read_parquet(?)", [str(HERE / "cohort_mapped.parquet")])
    if con.execute("SELECT count(*) FROM cohort").fetchone()[0] != 26235:
        raise RuntimeError("Native cache cohort identity changed")
    manifest = {
        "run_id": "EXP017-NATIVE-CACHE-001",
        "release": RELEASE,
        "cohort_pairs": 26235,
        "qualification": "Retrospective native evidence pair summaries; no point-in-time decision-date lock.",
        "sources": {},
    }
    current = None
    try:
        for datasource, table in SOURCES:
            current = datasource
            out = HERE / f"native_{datasource}_pair_features.parquet"
            if out.exists():
                raise RuntimeError(f"Existing native state is preserved: {out}")
            urls = parquet_urls(table)
            common = """
                count(*) AS native_evidence_rows,
                count(e.score) AS scored_evidence_rows,
                max(e.score) AS max_native_score,
                avg(e.score) AS mean_native_score,
                stddev_pop(e.score) AS std_native_score,
                min(e.evidenceDate) AS earliest_evidence_date,
                max(e.evidenceDate) AS latest_evidence_date
            """
            query = f"""
                COPY (
                    SELECT e.targetId,e.diseaseId,
                           {common},
                           {EXTRA[datasource]}
                    FROM read_parquet(?) AS e
                    INNER JOIN cohort AS c
                      ON e.targetId = c.targetId AND e.diseaseId = c.diseaseId
                    WHERE e.datasourceId = {quote(datasource)}
                    GROUP BY e.targetId,e.diseaseId
                ) TO {quote(str(out))} (FORMAT PARQUET, COMPRESSION ZSTD)
            """
            con.execute(query, [urls])
            rows, evidence_rows, pair_unique = con.execute(
                "SELECT count(*),sum(native_evidence_rows),count(DISTINCT targetId || '|' || diseaseId) "
                "FROM read_parquet(?)", [str(out)]
            ).fetchone()
            if not rows or rows != pair_unique:
                raise RuntimeError(f"Empty or duplicate native pair state: {datasource}")
            if con.execute(
                "SELECT count(*) FROM read_parquet(?) WHERE max_native_score IS NULL OR max_native_score < 0 OR max_native_score > 1",
                [str(out)],
            ).fetchone()[0]:
                raise RuntimeError(f"Missing or out-of-range native score: {datasource}")
            fields = [row[0] for row in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [str(out)]).fetchall()]
            manifest["sources"][datasource] = {
                "original_table": table,
                "original_parquet_urls": urls,
                "pair_state_path": str(out),
                "pair_rows": rows,
                "native_evidence_rows_within_cohort": evidence_rows,
                "fields": fields,
            }
            print(json.dumps({"source": datasource, "pair_rows": rows, "native_evidence_rows": evidence_rows}), flush=True)
        OUT_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    except Exception as exc:
        failure = HERE / "native_cache_failure.json"
        failure.write_text(json.dumps({
            "run_id": "EXP017-NATIVE-CACHE-001",
            "current_source": current,
            "completed_sources": sorted(manifest["sources"]),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "existing_native_outputs": sorted(x.name for x in HERE.glob("native_*_pair_features.parquet")),
        }, indent=2) + "\n")
        raise


if __name__ == "__main__":
    main()
