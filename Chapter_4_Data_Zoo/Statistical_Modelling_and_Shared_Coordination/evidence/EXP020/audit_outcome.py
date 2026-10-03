#!/usr/bin/env python3
"""Aggregate-only feasibility audit of the original and 26.06 clinical data."""

from __future__ import annotations

import csv
import importlib.util
import io
import json
import sys
from pathlib import Path

import duckdb


HERE = Path(__file__).resolve().parent
EXP017 = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
SPEC = importlib.util.spec_from_file_location("exp017_access_probe", EXP017 / "access_probe.py")
assert SPEC and SPEC.loader
ACCESS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ACCESS
SPEC.loader.exec_module(ACCESS)


def as_dicts(cursor):
    keys = [x[0] for x in cursor.description]
    return [dict(zip(keys, row)) for row in cursor.fetchall()]


def main() -> None:
    out = HERE / "outcome_chronology_audit.json"
    if out.exists():
        raise RuntimeError(f"Preserving existing output: {out}")
    original = list(csv.DictReader(io.StringIO(ACCESS.get(ACCESS.COHORT).decode("utf-8"))))
    con = duckdb.connect()
    con.execute("SET threads=3")
    con.execute("SET memory_limit='4GB'")
    urls = {table: ACCESS.parquet_urls(table) for table in
            ("clinical_report", "clinical_indication", "clinical_target")}
    for table, objects in urls.items():
        assert len(objects) == 1
        con.execute(f"CREATE VIEW {table} AS SELECT * FROM read_parquet('{objects[0]}')")
    con.execute(f"CREATE VIEW old_cohort AS SELECT * FROM read_parquet('{EXP017 / 'cohort_mapped.parquet'}')")
    all_stage = as_dicts(con.execute("""
        SELECT source, clinicalStage, COUNT(*) AS reports,
               COUNT(trialStartDate) AS trial_start_present,
               COUNT(year) AS year_present,
               COUNT_IF(trialStartDate > DATE '2026-10-02') AS trial_start_after_audit_date,
               COUNT_IF(year > 2026) AS year_after_audit_year
        FROM clinical_report GROUP BY 1, 2 ORDER BY 1, 2
    """))
    con.execute("""
        CREATE TEMP VIEW mapped_drug_pairs AS
        WITH ct AS (
          SELECT DISTINCT drugId, targetId, d.diseaseId AS diseaseId
          FROM clinical_target, UNNEST(diseases) AS x(d)
        )
        SELECT DISTINCT c.targetId, c.diseaseId, c.label, ct.drugId
        FROM old_cohort c
        JOIN ct ON c.targetId=ct.targetId AND c.diseaseId=ct.diseaseId
    """)
    con.execute("""
        CREATE TEMP VIEW mapped_report_links AS
        SELECT DISTINCT m.targetId, m.diseaseId, m.label, m.drugId, rid AS reportId
        FROM mapped_drug_pairs m
        JOIN clinical_indication ci ON ci.drugId=m.drugId AND ci.diseaseId=m.diseaseId,
             UNNEST(ci.clinicalReportIds) AS x(rid)
    """)
    link_summary = as_dicts(con.execute("""
        SELECT
          (SELECT COUNT(*) FROM old_cohort) AS old_mapped_pairs,
          (SELECT SUM(label) FROM old_cohort) AS old_positive_pairs,
          (SELECT COUNT(*) FROM mapped_drug_pairs) AS drug_target_disease_rows,
          (SELECT COUNT(DISTINCT (targetId,diseaseId)) FROM mapped_drug_pairs) AS old_pairs_with_current_drug_link,
          (SELECT COUNT(DISTINCT (targetId,diseaseId)) FROM mapped_drug_pairs WHERE label=1) AS old_positive_pairs_with_current_drug_link,
          (SELECT COUNT(DISTINCT drugId) FROM mapped_drug_pairs) AS distinct_drugs,
          (SELECT COUNT(*) FROM mapped_report_links) AS drug_target_disease_report_links,
          (SELECT COUNT(DISTINCT reportId) FROM mapped_report_links) AS distinct_linked_reports
    """))[0]
    multiplicity = as_dicts(con.execute("""
        SELECT COUNT(*) AS pairs_with_multiple_drugs, MAX(drug_count) AS max_drugs_per_pair
        FROM (SELECT targetId,diseaseId,COUNT(DISTINCT drugId) AS drug_count
              FROM mapped_drug_pairs GROUP BY 1,2)
        WHERE drug_count > 1
    """))[0]
    linked_stage = as_dicts(con.execute("""
        SELECT r.source,r.clinicalStage,COUNT(*) AS report_links,
               COUNT(r.trialStartDate) AS trial_start_present,
               COUNT(r.year) AS year_present,
               COUNT_IF(r.trialStartDate > DATE '2026-10-02') AS trial_start_after_audit_date,
               COUNT(DISTINCT (l.targetId,l.diseaseId)) AS old_pairs_linked,
               COUNT(DISTINCT l.drugId) AS drugs_linked
        FROM mapped_report_links l JOIN clinical_report r ON r.id=l.reportId
        GROUP BY 1,2 ORDER BY 1,2
    """))
    output = {
        "run_id": "EXP020-AUDIT-001", "scope": "FEASIBILITY_NOT_BENCHMARK",
        "audit_as_of": "2026-10-02", "release": "26.06",
        "old_terminal_source_url": ACCESS.COHORT,
        "old_terminal_source_rows": len(original),
        "old_terminal_fields": list(original[0]),
        "old_terminal_has_drug_id": "drug_id" in original[0] or "drugId" in original[0],
        "old_terminal_has_event_date": any("date" in c.lower() or "year" in c.lower() for c in original[0]),
        "official_26_06_urls": {k: v[0] for k, v in urls.items()},
        "official_26_06_table_counts": {k: int(con.execute(f"SELECT COUNT(*) FROM {k}").fetchone()[0]) for k in urls},
        "current_mapping_of_old_cohort_diagnostic_only": {**link_summary, **multiplicity},
        "full_clinical_report_source_stage_date_counts": all_stage,
        "old_cohort_linked_source_stage_date_counts": linked_stage,
        "date_semantics": {
            "trialStartDate": "Trial start date; may be actual/estimated in upstream registry; not an approval date or proof of prior public availability",
            "year": "Available primarily for withdrawal sources; no approval event year in linked authoritative approval reports",
            "historical_release": "26.06 clinical_report/target mapping is a current snapshot; earlier 25.12 FTP does not provide clinical_report directory",
        },
        "outcome_date_status": "OUTCOME_DATE_UNAVAILABLE_FOR_APPROVAL_BASED_TERMINAL_BENCHMARK",
        "old_cohort_as_historical_universe": False,
    }
    out.write_text(json.dumps(output, ensure_ascii=False, indent=2, default=str) + "\n")
    print(json.dumps({"output": str(out), "link_summary": output["current_mapping_of_old_cohort_diagnostic_only"],
                      "approval_report_count": sum(x["reports"] for x in all_stage if x["clinicalStage"] == "APPROVAL"),
                      "approval_reports_with_trial_start": sum(x["trial_start_present"] for x in all_stage if x["clinicalStage"] == "APPROVAL"),
                      "approval_reports_with_year": sum(x["year_present"] for x in all_stage if x["clinicalStage"] == "APPROVAL")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
