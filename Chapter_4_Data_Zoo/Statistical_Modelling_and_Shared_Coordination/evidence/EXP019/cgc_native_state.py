#!/usr/bin/env python3
"""One cohort-limited pair state for eligible 26.06 Cancer Gene Census evidence."""

from __future__ import annotations

import json
import math
import sys
import traceback
from pathlib import Path

import duckdb
import pandas as pd


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
sys.path.insert(0, str(PARENT))
from access_probe import RELEASE  # noqa: E402
from train_source_level_six import split_name  # noqa: E402


SOURCE = "cancer_gene_census"
RUN_ID = "EXP019-CGC-NATIVE-002"
STATE = HERE / "native_cancer_gene_census_pair_features.parquet"
MANIFEST = HERE / "cgc_native_manifest.json"
FAILURE = HERE / "cgc_native_failure_002.json"


def safe_float(value) -> float | None:
    converted = float(value)
    return converted if math.isfinite(converted) else None


def main() -> None:
    if any(x.exists() for x in (STATE, MANIFEST, FAILURE)):
        raise RuntimeError("Preserve existing native state; use a new run ID")
    gate = json.loads((HERE / "eligibility_train_validation.json").read_text())
    if gate["release"] != RELEASE or gate["eligible_datasources"] != [SOURCE]:
        raise RuntimeError("Frozen eligibility does not authorize this source")
    source = next(x for x in gate["candidates"] if x["datasource"] == SOURCE)
    urls = source["original_parquet_urls"]
    con = duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET memory_limit='4GB'")
    con.execute("CREATE TABLE cohort AS SELECT targetId,diseaseId FROM read_parquet(?)",
                [str(PARENT / "cohort_mapped.parquet")])
    query = """
        SELECT e.targetId,e.diseaseId,
               count(*) AS native_evidence_rows,
               count(e.score) AS scored_rows,
               max(e.score) AS max_native_score,
               avg(e.score) AS mean_native_score,
               max(e.resourceScore) AS max_resource_score,
               avg(e.resourceScore) AS mean_resource_score,
               sum(coalesce(array_length(e.mutatedSamples),0)) AS mutation_sample_context_rows,
               sum(coalesce(list_sum(list_transform(e.mutatedSamples,
                   x -> coalesce(x.numberMutatedSamples,0))),0)) AS mutated_sample_count,
               sum(coalesce(list_sum(list_transform(e.mutatedSamples,
                   x -> coalesce(x.numberSamplesTested,0))),0)) AS tested_sample_count,
               sum(coalesce(list_sum(list_transform(e.mutatedSamples,
                   x -> coalesce(x.numberSamplesWithMutationType,0))),0)) AS typed_mutation_sample_count,
               count(DISTINCT e.studyId) AS distinct_studies,
               sum(coalesce(array_length(e.literature),0)) AS publication_reference_count,
               sum(coalesce(array_length(e.qualityControls),0)) AS quality_control_entry_count,
               count(DISTINCT e.directionOnTrait) AS distinct_trait_directions,
               count(DISTINCT e.directionOnTarget) AS distinct_target_directions,
               min(e.publicationDate) AS earliest_publication_date,
               max(e.publicationDate) AS latest_publication_date,
               min(e.evidenceDate) AS earliest_evidence_date,
               max(e.evidenceDate) AS latest_evidence_date,
               min(e.studyId) AS provenance_study_key,
               count(DISTINCT e.diseaseFromSourceMappedId) AS mapped_cancer_contexts
        FROM read_parquet(?) e
        JOIN cohort c ON e.targetId=c.targetId AND e.diseaseId=c.diseaseId
        WHERE e.datasourceId='cancer_gene_census'
        GROUP BY e.targetId,e.diseaseId
    """
    pair = con.execute(query, [urls]).df()
    if len(pair) != source["cohort_pairs"] or pair.duplicated(["targetId", "diseaseId"]).any():
        raise RuntimeError("Derived CGC pair identity differs from frozen support gate")
    if not pair.max_native_score.between(0, 1).all():
        raise RuntimeError("CGC score outside [0,1]")
    cohort = pd.read_parquet(PARENT / "cohort_mapped.parquet")[["targetId", "diseaseId", "label"]]
    cohort["split"] = cohort.targetId.map(split_name)
    part = pair.merge(cohort, on=["targetId", "diseaseId"], validate="one_to_one", how="left")
    known_rows = int(part.loc[part.split.isin(("train", "validation")), "native_evidence_rows"].sum())
    if known_rows != sum(source[s]["native_rows_within_cohort"] for s in ("train", "validation")):
        raise RuntimeError("Derived CGC train/validation evidence rows differ from frozen support gate")
    pair.to_parquet(STATE, index=False)
    detail = {}
    for split in ("train", "validation"):
        frame = part.loc[part.split == split]
        detail[split] = {
            "pairs": int(len(frame)), "events": int(frame.label.sum()),
            "scores": {str(k): int(v) for k, v in frame.max_native_score.value_counts().sort_index().items()},
            "null_pairs": {name: int(frame[name].isna().sum()) for name in pair.columns if name not in ("targetId", "diseaseId")},
            "numeric_ranges": {name: {"min": safe_float(frame[name].min()),
                                      "median": safe_float(frame[name].median()),
                                      "max": safe_float(frame[name].max())}
                               for name in ("max_resource_score", "mutation_sample_context_rows",
                                            "mutated_sample_count", "tested_sample_count",
                                            "typed_mutation_sample_count", "distinct_studies",
                                            "publication_reference_count", "quality_control_entry_count")},
        }
    MANIFEST.write_text(json.dumps({
        "run_id": RUN_ID, "release": RELEASE, "source": SOURCE,
        "passport_id": "DP-SOM-01", "original_parquet_urls": urls,
        "cohort_path": str(PARENT / "cohort_mapped.parquet"),
        "derived_state_path": str(STATE), "pair_rows": int(len(pair)),
        "native_evidence_rows_within_cohort": int(pair.native_evidence_rows.sum()),
        "fields": list(pair.columns), "train_validation_diagnostics": detail,
        "time_role": "quality diagnostic only; no decision-date lock",
        "evidence_note": "mutatedSamples nested counts summarize only pairs in frozen cohort; raw rows not stored",
    }, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"pair_rows": len(pair), "diagnostics": detail}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not FAILURE.exists():
            FAILURE.write_text(json.dumps({"run_id": RUN_ID,
                                           "error_type": type(exc).__name__, "error": str(exc),
                                           "traceback": traceback.format_exc()}, ensure_ascii=False, indent=2) + "\n")
        raise
