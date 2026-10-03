#!/usr/bin/env python3
"""Build one cohort-restricted 26.06 source-level cache from original URLs."""

from __future__ import annotations

import csv
import io
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import duckdb

from access_probe import COHORT, RELEASE, TRAINING_ZIP, get, parquet_urls


HERE = Path(__file__).resolve().parent
COHORT_OUT = HERE / "cohort_mapped.parquet"
ASSOCIATION_OUT = HERE / "association_cohort_18.parquet"
MANIFEST_OUT = HERE / "cache_manifest.json"
RUN_ID = "EXP017-CACHE-002"
SIX = (
    "gwas_credible_sets",
    "gene_burden",
    "eva",
    "expression_atlas",
    "impc",
    "europepmc",
)


def registry() -> list[dict]:
    with zipfile.ZipFile(TRAINING_ZIP) as archive:
        name = next(n for n in archive.namelist() if n.endswith("config/pipeline_registry.json"))
        return json.loads(archive.read(name))


def bridge(cohort_disease_ids: set[str], con: duckdb.DuckDBPyConnection, urls: list[str]) -> dict[str, str]:
    rows = con.execute(
        "SELECT id, obsoleteTerms, obsoleteXRefs, dbXRefs FROM read_parquet(?)", [urls]
    ).fetchall()
    current = {str(row[0]) for row in rows}
    candidates: dict[str, set[str]] = defaultdict(set)
    for identifier, *arrays in rows:
        for array in arrays:
            for prior in array or []:
                prior = str(prior)
                if prior in cohort_disease_ids and prior not in current:
                    candidates[prior].add(str(identifier))
    mapping = {}
    ambiguous = {}
    missing = []
    for source_id in cohort_disease_ids:
        if source_id in current:
            mapping[source_id] = source_id
        elif len(candidates[source_id]) == 1:
            mapping[source_id] = next(iter(candidates[source_id]))
        elif candidates[source_id]:
            ambiguous[source_id] = sorted(candidates[source_id])
        else:
            missing.append(source_id)
    if ambiguous or missing:
        raise RuntimeError(f"Disease bridge incomplete: ambiguous={ambiguous}, missing={missing}")
    return mapping


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def main() -> None:
    for path in (COHORT_OUT, ASSOCIATION_OUT, MANIFEST_OUT):
        if path.exists():
            raise SystemExit(f"Existing output is preserved: {path}")

    registered = registry()
    datasource_ids = [r["datasource_id"] for r in registered]
    assert len(registered) == len(set(datasource_ids)) == 18
    assert set(SIX).issubset(datasource_ids)
    assert all(re.fullmatch(r"[a-z][a-z0-9_]*", x) for x in datasource_ids)
    assert not set(datasource_ids).intersection({"clinical", "overall_score", "chembl"})

    association_urls = parquet_urls("association_by_datasource_direct")
    disease_urls = parquet_urls("disease")
    assert len(association_urls) == 14 and len(disease_urls) == 1
    rows = list(csv.DictReader(io.StringIO(get(COHORT).decode("utf-8"))))
    assert len(rows) == 26278
    assert set(r["label"] for r in rows) == {"0", "1"}
    assert all(r["label"] == str(int(r["phase"] == "4")) for r in rows)

    con = duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET memory_limit='4GB'")
    mapping = bridge({r["efo_id_norm"] for r in rows}, con, disease_urls)

    # The source cohort contains 41 exact duplicate pair rows. The pair is the
    # statistical unit, so duplicate rows are counted but not double-weighted.
    by_pair: dict[tuple[str, str], dict] = {}
    for row in rows:
        target = row["ensembl_id"]
        if not re.fullmatch(r"ENSG[0-9]+", target):
            raise RuntimeError(f"Unexpected target identifier: {target}")
        current_disease = mapping[row["efo_id_norm"]]
        key = (target, current_disease)
        candidate = (int(row["label"]), int(row["phase"]))
        if key in by_pair:
            if by_pair[key]["label"] != candidate[0]:
                raise RuntimeError(f"Conflicting terminal labels after disease bridge: {key}")
            by_pair[key]["phases"].add(candidate[1])
            by_pair[key]["source_disease_ids"].add(row["efo_id_norm"])
        else:
            by_pair[key] = {
                "label": candidate[0],
                "phases": {candidate[1]},
                "source_disease_ids": {row["efo_id_norm"]},
            }
    con.execute(
        "CREATE TABLE cohort (targetId VARCHAR, diseaseId VARCHAR, label INTEGER, phases VARCHAR, sourceDiseaseIds VARCHAR)"
    )
    cohort_values = [
        (target, disease, value["label"], ";".join(map(str, sorted(value["phases"]))), ";".join(sorted(value["source_disease_ids"])))
        for (target, disease), value in sorted(by_pair.items())
    ]
    con.executemany("INSERT INTO cohort VALUES (?, ?, ?, ?, ?)", cohort_values)
    con.execute(
        f"COPY cohort TO {sql_literal(str(COHORT_OUT))} (FORMAT PARQUET, COMPRESSION ZSTD)"
    )

    quoted = ",".join(sql_literal(ds) for ds in datasource_ids)
    query = f"""
        COPY (
            SELECT a.targetId, a.diseaseId, a.aggregationValue,
                   a.associationScore, a.evidenceCount, a.currentNovelty
            FROM read_parquet(?) AS a
            INNER JOIN cohort AS c
              ON a.targetId = c.targetId AND a.diseaseId = c.diseaseId
            WHERE a.aggregationType = 'datasourceId'
              AND a.aggregationValue IN ({quoted})
        ) TO {sql_literal(str(ASSOCIATION_OUT))}
          (FORMAT PARQUET, COMPRESSION ZSTD)
    """
    con.execute(query, [association_urls])
    association_count = con.execute(
        "SELECT count(*) FROM read_parquet(?)", [str(ASSOCIATION_OUT)]
    ).fetchone()[0]
    association_count_repeat = con.execute(
        "SELECT count(*) FROM read_parquet(?)", [str(ASSOCIATION_OUT)]
    ).fetchone()[0]
    if association_count != association_count_repeat:
        raise RuntimeError("Filtered cache failed repeat-read row-count check")
    stats = con.execute(
        "SELECT aggregationValue, count(*), count(DISTINCT targetId || '|' || diseaseId) "
        "FROM read_parquet(?) GROUP BY aggregationValue ORDER BY aggregationValue",
        [str(ASSOCIATION_OUT)],
    ).fetchall()
    if any(count != unique_pairs for _, count, unique_pairs in stats):
        raise RuntimeError("Duplicate datasource/pair rows in filtered association cache")
    coverage = {ds: {"rows": count, "pair_count": pairs} for ds, count, pairs in stats}
    missing_six = [ds for ds in SIX if coverage.get(ds, {}).get("rows", 0) == 0]
    if missing_six:
        raise RuntimeError(f"Six-pipeline cohort coverage is empty: {missing_six}")
    output_columns = {
        row[0] for row in con.execute(
            "DESCRIBE SELECT * FROM read_parquet(?)", [str(ASSOCIATION_OUT)]
        ).fetchall()
    }
    if output_columns.intersection({"clinical", "overall_score", "label", "phase"}):
        raise RuntimeError("Terminal or outcome-adjacent field entered source cache")

    manifest = {
        "research_id": "STAT-PSYMOE-EXP017-20261002-001",
        "run_id": RUN_ID,
        "release": RELEASE,
        "source_identity": {
            "open_targets_association_files": association_urls,
            "open_targets_disease_files": disease_urls,
            "terminal_git_blob": COHORT,
        },
        "cohort": {
            "source_rows": len(rows),
            "mapped_unique_pair_rows": len(by_pair),
            "removed_duplicate_pair_rows": len(rows) - len(by_pair),
            "pairs_with_multiple_phases": sum(len(v["phases"]) > 1 for v in by_pair.values()),
            "unique_targets": len({k[0] for k in by_pair}),
            "positive_pairs": sum(v["label"] for v in by_pair.values()),
            "negative_pairs": sum(1 - v["label"] for v in by_pair.values()),
            "disease_bridge_count": len(mapping),
        },
        "association": {
            "cohort_restricted_rows": association_count,
            "repeat_read_rows": association_count_repeat,
            "datasource_coverage": coverage,
            "missing_registry_datasources_in_cohort": sorted(set(datasource_ids) - set(coverage)),
        },
        "outputs": [str(COHORT_OUT), str(ASSOCIATION_OUT)],
        "qualification": "Retrospective 26.06 datasource-level association cache; not native raw or point-in-time evidence.",
    }
    MANIFEST_OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "cohort_unique_pairs": len(by_pair),
        "removed_duplicate_rows": len(rows) - len(by_pair),
        "association_rows": association_count,
        "datasources_with_cohort_rows": len(coverage),
        "six_coverage": {ds: coverage[ds]["rows"] for ds in SIX},
        "manifest": str(MANIFEST_OUT),
    }, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        failure = HERE / "cache_failure_002.json"
        failure.write_text(json.dumps({
            "run_id": RUN_ID,
            "error_type": type(exc).__name__,
            "error": str(exc),
            "existing_outputs": [str(x) for x in (COHORT_OUT, ASSOCIATION_OUT, MANIFEST_OUT) if x.exists()],
        }, indent=2) + "\n")
        raise
