#!/usr/bin/env python3
"""EXP019 fixed-release native support gate; test is added only after gate freeze."""

from __future__ import annotations

import csv
import json
import sys
import traceback
from pathlib import Path

import duckdb
import pandas as pd


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
sys.path.insert(0, str(PARENT))
from access_probe import RELEASE, parquet_urls  # noqa: E402
from train_source_level_six import split_name  # noqa: E402


SOURCES = (
    ("DP-GEN-04", "genomics_england", "evidence_genomics_england"),
    ("DP-GEN-05", "gene2phenotype", "evidence_gene2phenotype"),
    ("DP-GEN-06", "uniprot_literature", "evidence_uniprot_literature"),
    ("DP-GEN-07", "uniprot_variants", "evidence_uniprot_variants"),
    ("DP-GEN-08", "orphanet", "evidence_orphanet"),
    ("DP-GEN-09", "clingen", "evidence_clingen"),
    ("DP-SOM-01", "cancer_gene_census", "evidence_cancer_gene_census"),
    ("DP-SOM-02", "intogen", "evidence_intogen"),
    ("DP-PWY-01", "cancer_biomarkers", "evidence_cancer_biomarkers"),
    ("DP-PWY-02", "crispr_screen", "evidence_crispr_screen"),
    ("DP-PWY-03", "crispr", "evidence_crispr"),
    ("DP-PWY-04", "reactome", "evidence_reactome"),
)
TRAIN_VAL = HERE / "eligibility_train_validation.json"
SUPPORT = HERE / "source_support.json"
CSV = HERE / "source_support.csv"
FAILURE = HERE / "support_preflight_failure.json"


def ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def quote(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def candidate_scalar(name: str, typ: str) -> bool:
    low = name.lower()
    if low in {"score", "targetid", "diseaseid", "datasourceid", "datatypeid"}:
        return False
    if low.endswith("id") or any(x in low for x in ("date", "year", "time", "phase", "approval", "clinicalstatus")):
        return False
    if any(x in low for x in ("url", "description", "literature", "pubmed", "pmid")):
        return False
    return typ.upper().split("(")[0] in {
        "VARCHAR", "BOOLEAN", "TINYINT", "SMALLINT", "INTEGER", "BIGINT", "HUGEINT",
        "UTINYINT", "USMALLINT", "UINTEGER", "UBIGINT", "FLOAT", "DOUBLE", "DECIMAL",
    }


def stats(frame: pd.DataFrame, split: str) -> dict:
    part = frame.loc[frame.split == split]
    return {
        "pairs": int(len(part)),
        "targets": int(part.targetId.nunique()),
        "events": int(part.label.sum()),
        "nonzero_score_pairs": int(part.max_native_score.fillna(0).gt(0).sum()),
        "unique_nonmissing_pair_scores": int(part.max_native_score.nunique(dropna=True)),
        "score_missing_pairs": int(part.max_native_score.isna().sum()),
        "native_rows_within_cohort": int(part.native_evidence_rows.sum()),
    }


def extra_variability(con: duckdb.DuckDBPyConnection, urls: list[str], datasource: str,
                      fields: list[dict], train_pairs: pd.DataFrame) -> dict:
    """Only called when score and pair row count are both constant in train."""
    candidates = [f for f in fields if candidate_scalar(f["name"], f["type"])]
    if not candidates or train_pairs.empty:
        return {"candidate_fields": [x["name"] for x in candidates], "variable_fields": []}
    con.register("train_supported", train_pairs[["targetId", "diseaseId"]])
    # Pair-level minima and distinct-within-pair counts are native states;
    # collect all candidate scalars in one remote projection, never raw rows.
    expressions = []
    for i, f in enumerate(candidates):
        col = ident(f["name"])
        expressions.extend((f"min(CAST(e.{col} AS VARCHAR)) AS {ident('value_' + str(i))}",
                            f"count(DISTINCT e.{col}) AS {ident('levels_' + str(i))}"))
    query = f"""
        SELECT e.targetId,e.diseaseId,{','.join(expressions)}
        FROM read_parquet(?) e
        JOIN train_supported c
          ON e.targetId=c.targetId AND e.diseaseId=c.diseaseId
        WHERE e.datasourceId={quote(datasource)}
        GROUP BY e.targetId,e.diseaseId
    """
    state = con.execute(query, [urls]).df()
    variable = []
    observed = {}
    for i, f in enumerate(candidates):
        value = state[f"value_{i}"]
        levels = state[f"levels_{i}"].where(value.notna())
        n = int(value.notna().sum())
        unique_values = int(value.nunique(dropna=True))
        unique_levels = int(levels.nunique(dropna=True))
        observed[f["name"]] = {"observed_pairs": n, "unique_pair_values": unique_values,
                               "unique_pair_level_counts": unique_levels}
        if n >= 10 and (unique_values >= 2 or unique_levels >= 2):
            variable.append(f["name"])
    return {"candidate_fields": [x["name"] for x in candidates],
            "variable_fields": variable, "observed": observed}


def inspect(con: duckdb.DuckDBPyConnection, passport: str, datasource: str, table: str,
            cohort: pd.DataFrame) -> tuple[dict, pd.DataFrame | None]:
    result = {"passport_id": passport, "datasource": datasource, "native_table": table,
              "release": RELEASE, "original_directory_url":
              f"https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/{RELEASE}/output/{table}/"}
    urls = parquet_urls(table)
    result["original_parquet_urls"] = urls
    result["parquet_files"] = len(urls)
    fields = [{"name": row[0], "type": row[1]} for row in
              con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [urls[0]]).fetchall()]
    result["native_schema"] = fields
    names = {f["name"] for f in fields}
    required = {"targetId", "diseaseId", "datasourceId", "score"}
    if not required.issubset(names):
        raise RuntimeError(f"Missing native columns: {sorted(required - names)}")
    result["native_rows"] = int(con.execute("SELECT count(*) FROM read_parquet(?)", [urls]).fetchone()[0])
    date_cols = [f["name"] for f in fields if any(t in f["name"].lower() for t in ("date", "year", "time"))
                 and candidate_scalar_date_type(f["type"])]
    result["date_fields"] = date_cols
    dates = ", ".join(f"count(e.{ident(name)}) AS {ident('date_count_' + str(i))}"
                      for i, name in enumerate(date_cols))
    if dates:
        dates = ", " + dates
    query = f"""
        SELECT e.targetId,e.diseaseId,
               count(*) AS native_evidence_rows,
               count(e.score) AS scored_rows,
               max(e.score) AS max_native_score,
               sum(CASE WHEN e.score > 0 THEN 1 ELSE 0 END) AS positive_score_rows{dates}
        FROM read_parquet(?) e
        JOIN cohort_keys c
          ON e.targetId=c.targetId AND e.diseaseId=c.diseaseId
        WHERE e.datasourceId={quote(datasource)}
        GROUP BY e.targetId,e.diseaseId
    """
    pair = con.execute(query, [urls]).df()
    if pair.duplicated(["targetId", "diseaseId"]).any():
        raise RuntimeError("Native pair aggregate contains duplicates")
    pair = pair.merge(cohort[["targetId", "diseaseId", "label", "split"]],
                      on=["targetId", "diseaseId"], how="left", validate="one_to_one")
    if pair.label.isna().any():
        raise RuntimeError("Native pair is outside frozen cohort")
    result["cohort_pairs"] = int(len(pair))
    train = pair.loc[pair.split == "train"]
    validation = pair.loc[pair.split == "validation"]
    tr = stats(pair, "train")
    va = stats(pair, "validation")
    result["train"] = tr
    result["validation"] = va
    result["score_unique_train"] = tr["unique_nonmissing_pair_scores"]
    result["nonzero_score_pairs_train_validation"] = tr["nonzero_score_pairs"] + va["nonzero_score_pairs"]
    result["missingness_train_validation"] = {
        "score_missing_rows": int((train.native_evidence_rows - train.scored_rows).sum() +
                                  (validation.native_evidence_rows - validation.scored_rows).sum()),
        "score_missing_pairs": tr["score_missing_pairs"] + va["score_missing_pairs"],
    }
    result["date_coverage_train_validation"] = {
        name: {"nonmissing_rows": int(train[f"date_count_{i}"].sum() +
                                      validation[f"date_count_{i}"].sum()),
               "native_rows": int(train.native_evidence_rows.sum() + validation.native_evidence_rows.sum())}
        for i, name in enumerate(date_cols)
    }
    score_varies = train.max_native_score.nunique(dropna=True) >= 2 and train.max_native_score.notna().sum() >= 10
    count_varies = train.native_evidence_rows.nunique(dropna=True) >= 2 and len(train) >= 10
    state = {"score_varies": bool(score_varies), "evidence_count_varies": bool(count_varies),
             "variable_native_fields": []}
    if not score_varies and not count_varies:
        extra = extra_variability(con, urls, datasource, fields, train)
        state["variable_native_fields"] = extra["variable_fields"]
        state["native_field_probe"] = extra
    result["native_state_variability_train"] = state
    reasons = []
    if tr["pairs"] < 200:
        reasons.append("FAIL_TRAIN_SUPPORT")
    if va["pairs"] < 50:
        reasons.append("FAIL_VALIDATION_SUPPORT")
    if tr["events"] < 10:
        reasons.append("FAIL_TRAIN_EVENT_SUPPORT")
    if va["events"] < 3:
        reasons.append("FAIL_VALIDATION_EVENT_SUPPORT")
    if not (score_varies or count_varies or state["variable_native_fields"]):
        reasons.append("FAIL_CONSTANT_STATE")
    result["eligibility"] = "PASS" if not reasons else "FAIL"
    result["fail_reasons"] = reasons
    return result, pair


def candidate_scalar_date_type(typ: str) -> bool:
    return typ.upper().split("(")[0] in {"VARCHAR", "DATE", "TIMESTAMP", "TIMESTAMP_NS",
                                       "INTEGER", "BIGINT", "SMALLINT", "DOUBLE", "FLOAT"}


def main() -> None:
    if any(p.exists() for p in (TRAIN_VAL, SUPPORT, CSV, FAILURE)):
        raise RuntimeError("Existing EXP019 support output must be preserved; use a new run ID")
    if RELEASE != "26.06":
        raise RuntimeError("Unexpected release")
    cohort = pd.read_parquet(PARENT / "cohort_mapped.parquet")[["targetId", "diseaseId", "label"]]
    if len(cohort) != 26235 or cohort.duplicated(["targetId", "diseaseId"]).any():
        raise RuntimeError("Frozen cohort identity changed")
    cohort["split"] = cohort.targetId.map(split_name)
    if set(cohort.split) != {"train", "validation", "test"}:
        raise RuntimeError("Frozen split naming changed")
    con = duckdb.connect()
    con.execute("SET threads=4")
    con.execute("SET memory_limit='4GB'")
    con.register("cohort_keys", cohort[["targetId", "diseaseId"]])
    entries = []
    pair_frames = {}
    for passport, datasource, table in SOURCES:
        try:
            row, pair = inspect(con, passport, datasource, table, cohort)
            pair_frames[datasource] = pair
            entries.append(row)
            print(json.dumps({"datasource": datasource, "train": row["train"]["pairs"],
                              "validation": row["validation"]["pairs"],
                              "eligibility": row["eligibility"]}), flush=True)
        except Exception as exc:
            entries.append({"passport_id": passport, "datasource": datasource,
                            "native_table": table, "release": RELEASE,
                            "eligibility": "FAIL", "fail_reasons": ["FAIL_NATIVE_ACCESS_OR_SCHEMA"],
                            "error_type": type(exc).__name__, "error": str(exc)})
            print(json.dumps({"datasource": datasource, "error": str(exc)}), flush=True)
    # Eligibility is materialised before accessing any test labels or test support.
    gate = {"run_id": "EXP019-SUPPORT-001", "research_id": "STAT-PSYMOE-EXP019-20261002-001",
            "release": RELEASE, "selection_partitions": ["train", "validation"],
            "test_previously_observed": True,
            "thresholds": {"train_pairs": 200, "validation_pairs": 50,
                           "train_events": 10, "validation_events": 3,
                           "train_state_min_observed_pairs": 10,
                           "train_state_min_unique_values": 2},
            "candidates": entries, "eligible_datasources":
            [row["datasource"] for row in entries if row["eligibility"] == "PASS"]}
    TRAIN_VAL.write_text(json.dumps(gate, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    for row in entries:
        pair = pair_frames.get(row["datasource"])
        if pair is not None:
            row["test_report_only"] = stats(pair, "test")
            row["nonzero_score_pairs_all_splits"] = (
                row["nonzero_score_pairs_train_validation"] + row["test_report_only"]["nonzero_score_pairs"])
    support = {"run_id": "EXP019-SUPPORT-001", "release": RELEASE,
               "gate_file": str(TRAIN_VAL), "test_role": "retrospective reporting only",
               "candidates": entries, "eligible_count": len(gate["eligible_datasources"]),
               "eligible_datasources": gate["eligible_datasources"]}
    SUPPORT.write_text(json.dumps(support, ensure_ascii=False, indent=2, allow_nan=False) + "\n")
    columns = ["passport_id", "datasource", "native_table", "native_rows", "cohort_pairs",
               "train_pairs", "validation_pairs", "test_pairs", "train_events", "validation_events",
               "test_events", "score_unique_train", "nonzero_score_pairs_all_splits", "score_missing_rows_train_validation",
               "date_coverage_train_validation", "native_state_variability_train", "eligibility", "fail_reasons"]
    with CSV.open("w", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=columns)
        writer.writeheader()
        for row in entries:
            splits = {s: row.get(s, {}) for s in ("train", "validation", "test_report_only")}
            writer.writerow({
                "passport_id": row["passport_id"], "datasource": row["datasource"],
                "native_table": row["native_table"], "native_rows": row.get("native_rows"),
                "cohort_pairs": row.get("cohort_pairs"),
                "train_pairs": splits["train"].get("pairs"),
                "validation_pairs": splits["validation"].get("pairs"),
                "test_pairs": splits["test_report_only"].get("pairs"),
                "train_events": splits["train"].get("events"),
                "validation_events": splits["validation"].get("events"),
                "test_events": splits["test_report_only"].get("events"),
                "score_unique_train": row.get("score_unique_train"),
                "nonzero_score_pairs_all_splits": row.get("nonzero_score_pairs_all_splits"),
                "score_missing_rows_train_validation": row.get("missingness_train_validation", {}).get("score_missing_rows"),
                "date_coverage_train_validation": json.dumps(row.get("date_coverage_train_validation", {}), ensure_ascii=False),
                "native_state_variability_train": json.dumps(row.get("native_state_variability_train", {}), ensure_ascii=False),
                "eligibility": row["eligibility"], "fail_reasons": ";".join(row["fail_reasons"]),
            })
    print(json.dumps({"eligible_datasources": gate["eligible_datasources"],
                      "gate_file": str(TRAIN_VAL), "support_file": str(SUPPORT)}), flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        if not FAILURE.exists():
            FAILURE.write_text(json.dumps({"run_id": "EXP019-SUPPORT-001",
                                           "error_type": type(exc).__name__, "error": str(exc),
                                           "traceback": traceback.format_exc()}, ensure_ascii=False, indent=2) + "\n")
        raise
