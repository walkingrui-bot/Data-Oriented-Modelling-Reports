#!/usr/bin/env python3
"""Read-only date inventory of the seven 26.06 native evidence tables.

Only aggregate counts and original URL indexes are saved. This does not create
historical feature states, a cohort, or model inputs.
"""

from __future__ import annotations

import csv
import importlib.util
import json
import sys
from pathlib import Path

import duckdb


HERE = Path(__file__).resolve().parent
EXP017 = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
EXP019 = HERE.parent / "STAT-PSYMOE-EXP019-20261002-001"
SPEC = importlib.util.spec_from_file_location("exp017_access_probe", EXP017 / "access_probe.py")
assert SPEC and SPEC.loader
ACCESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ACCESS
SPEC.loader.exec_module(ACCESS)

AS_OF = "2026-10-02"
SOURCES = (
    "gwas_credible_sets", "gene_burden", "eva", "expression_atlas",
    "impc", "europepmc", "cancer_gene_census",
)
LEGACY = json.loads((EXP017 / "native_diagnostics.json").read_text())["sources"]
LEGACY_URLS = json.loads((EXP017 / "native_cache_manifest.json").read_text())["sources"]
CGC_OLD = next(x for x in json.loads((EXP019 / "source_support.json").read_text())["candidates"]
               if x["datasource"] == "cancer_gene_census")


def ident(x: str) -> str:
    assert x.replace("_", "").isalnum()
    return '"' + x + '"'


def date_parts(field: str, typ: str) -> tuple[str, str, str]:
    col = ident(field)
    if field.lower().endswith("year") and typ.upper() in ("BIGINT", "INTEGER", "SMALLINT"):
        valid = f"({col} BETWEEN 1500 AND 9999)"
        invalid = f"({col} IS NOT NULL AND NOT {valid})"
        future = f"({valid} AND {col} > 2026)"
    else:
        parsed = f"TRY_CAST({col} AS DATE)"
        valid = f"({parsed} IS NOT NULL)"
        invalid = f"({col} IS NOT NULL AND {parsed} IS NULL)"
        future = f"({parsed} > DATE '{AS_OF}')"
    return valid, invalid, future


def main() -> None:
    if (HERE / "historical_source_support.json").exists() or (HERE / "historical_source_support.csv").exists():
        raise RuntimeError("Completed source-support output already exists; preserve it")
    con = duckdb.connect()
    con.execute("SET threads=3")
    con.execute("SET memory_limit='4GB'")
    summary = []
    for source in SOURCES:
        table = "evidence_" + source
        urls = (LEGACY_URLS[source]["original_parquet_urls"] if source != "cancer_gene_census"
                else CGC_OLD["original_parquet_urls"])
        out = HERE / f"leakage_audit_{source}.json"
        if out.exists():
            record = json.loads(out.read_text())
            print(f"REUSE COMPLETED {source} original={out}", flush=True)
            summary.append({"source": source, "scope": record["scope"], "total_rows": record["total_rows"],
                            "dated_rows": record["dated_rows"], "invalid_dates": record["invalid_dates"],
                            "future_dates_as_of_audit": record["future_dates_as_of_audit"],
                            "unknown_dates": record["unknown_dates"],
                            "included_before_cutoff": None, "excluded_after_cutoff": None,
                            "legacy_2026_cohort_supported_pairs_reference_only":
                                record["legacy_2026_cohort_supported_pairs_reference_only"],
                            "historical_eligible_pairs": None, "historical_terminal_events": None})
            continue
        fields = [(x[0], x[1]) for x in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [urls[0]]).fetchall()]
        date_fields = [(f, t) for f, t in fields if any(k in f.lower() for k in ("date", "year", "time"))]
        clauses = ["COUNT(*) AS total_rows"]
        valid, invalid, future = [], [], []
        for name, typ in date_fields:
            v, i, fu = date_parts(name, typ)
            valid.append(v); invalid.append(i); future.append(fu)
            clauses += [
                f"COUNT_IF({ident(name)} IS NOT NULL) AS {ident(name + '_non_null')}",
                f"COUNT_IF({v}) AS {ident(name + '_parsed')}",
                f"COUNT_IF({i}) AS {ident(name + '_invalid_format')}",
                f"COUNT_IF({fu}) AS {ident(name + '_future_as_of_audit')}",
            ]
        clauses += [
            "COUNT_IF(" + " OR ".join(valid) + ") AS dated_rows",
            "COUNT_IF(NOT (" + " OR ".join(valid) + ")) AS unknown_date_rows",
            "COUNT_IF(" + " OR ".join(invalid) + ") AS invalid_format_rows",
            "COUNT_IF(" + " OR ".join(future) + ") AS future_date_rows_as_of_audit",
        ]
        print(f"AUDITING {source} {len(urls)} parquet files", flush=True)
        cur = con.execute("SELECT " + ", ".join(clauses) + " FROM read_parquet(?)", [urls])
        row = dict(zip([x[0] for x in cur.description], cur.fetchone()))
        prior_pairs = LEGACY[source]["pairs"] if source in LEGACY else CGC_OLD["cohort_pairs"]
        record = {
            "run_id": "EXP020-LEAK-002", "parent_run_id": "EXP020-LEAK-001",
            "source": source, "release": "26.06",
            "audit_as_of": AS_OF, "scope": "FULL_26_06_NATIVE_TABLE_DATE_INVENTORY_ONLY",
            "original_directory_url": ACCESS.FTP + table + "/",
            "original_parquet_file_count": len(urls),
            "first_original_parquet_url": urls[0],
            "last_original_parquet_url": urls[-1],
            "historical_release_25_12_directory_url":
                "https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/25.12/output/" + table + "/",
            "source_schema_date_fields": [{"name": n, "type": t} for n, t in date_fields],
            "date_inventory": {k: int(v or 0) for k, v in row.items()},
            "total_rows": int(row["total_rows"]),
            "dated_rows": int(row["dated_rows"]),
            "invalid_dates": int(row["invalid_format_rows"]),
            "future_dates_as_of_audit": int(row["future_date_rows_as_of_audit"]),
            "unknown_dates": int(row["unknown_date_rows"]),
            "included_before_cutoff": None,
            "excluded_after_cutoff": None,
            "cutoff_status": "NOT_SELECTED_BECAUSE_OUTCOME_CHRONOLOGY_GATE_PENDING",
            "date_semantics_status": "FIELD_PRESENCE_ONLY_NOT_PROOF_OF_HISTORICAL_ROW_STATE",
            "ontology_mapping_version": "Open Targets 26.06 disease/target IDs in prior EXP017 bridge; no historical mapping frozen",
            "legacy_2026_cohort_supported_pairs_reference_only": prior_pairs,
            "legacy_support_is_historical_support": False,
            "current_only_fields_pending_historical_reconstruction":
                [x for x in ("score", "resourceScore", "qualityControls", "directionOnTrait", "directionOnTarget")
                 if x in {f for f, _ in fields}],
            "explicitly_forbidden_feature_fields":
                ["clinical", "overall_score", "label", "phase", "current max clinical phase",
                 "approval flag", "drug success", "post-cutoff literature and curation"],
            "possible_post_outcome_contamination_routes": [
                "26.06 source row/score may have been added or revised after candidate decision date",
                "publication or evidence date alone does not prove 26.06 target/disease mapping and curated state were known then",
            ],
            "prior_exact_url_index": str(EXP017 / "native_cache_manifest.json") if source != "cancer_gene_census"
                else str(EXP019 / "source_support.json"),
        }
        if source == "europepmc":
            record["possible_post_outcome_contamination_routes"].append(
                "post-trial/approval publications and impossible publicationYear must be excluded")
        if source == "eva":
            record["possible_post_outcome_contamination_routes"].append(
                "current ClinVar assertion/review can postdate the original submission")
        if source == "cancer_gene_census":
            record["possible_post_outcome_contamination_routes"].append(
                "later cancer curation, score and publication linkage may reflect clinical outcome")
        out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
        summary.append({"source": source, "scope": record["scope"], "total_rows": record["total_rows"],
                        "dated_rows": record["dated_rows"], "invalid_dates": record["invalid_dates"],
                        "future_dates_as_of_audit": record["future_dates_as_of_audit"],
                        "unknown_dates": record["unknown_dates"],
                        "included_before_cutoff": None, "excluded_after_cutoff": None,
                        "legacy_2026_cohort_supported_pairs_reference_only": prior_pairs,
                        "historical_eligible_pairs": None, "historical_terminal_events": None})
        print(f"DONE {source} total={record['total_rows']} dated={record['dated_rows']} unknown={record['unknown_dates']}", flush=True)
    (HERE / "historical_source_support.json").write_text(json.dumps({
        "run_id": "EXP020-LEAK-002", "meaning": "Feasibility inventory, not historical support or training data",
        "rows": summary}, ensure_ascii=False, indent=2) + "\n")
    with (HERE / "historical_source_support.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(summary[0])); writer.writeheader(); writer.writerows(summary)


if __name__ == "__main__":
    main()
