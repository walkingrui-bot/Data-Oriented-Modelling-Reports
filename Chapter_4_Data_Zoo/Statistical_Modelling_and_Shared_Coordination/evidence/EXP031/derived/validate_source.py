"""EXP031-VERIFY-001: local consistency of this experiment's derived source outputs."""

import csv
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "LOCAL_VALIDATION.json"
NAMES = [f"{side}_{stat}" for side in ("left", "right") for stat in
         ("mean", "std", "p95p05", "contact_fraction")]
NAMES += ["mean_asymmetry_abs", "left_right_corr", "total_dominant_hz", "total_band_ratio"]


def read_rows(name):
    with (ROOT / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    cohort = [row for row in read_rows("COHORT_AUDIT.csv") if row["eligible"] == "True"]
    features = read_rows("FORCE_FEATURES.csv")
    audit = read_rows("SOURCE_AUDIT.csv")
    summary = json.loads((ROOT / "SOURCE_SUMMARY.json").read_text())
    by_id = lambda rows: {row["subject_id"]: row for row in rows}
    c, f, a = by_id(cohort), by_id(features), by_id(audit)
    checks = {}
    checks["person_keys_unique_and_aligned"] = all(len(rows) == 165 for rows in (cohort, features, audit)) and len(c) == len(f) == len(a) == 165 and set(c) == set(f) == set(a)
    counts = Counter((row["study"], row["group"]) for row in audit if row["status"] == "READABLE_NUMERIC")
    denoms = Counter((row["study"], row["group"]) for row in audit)
    checks["source_counts_match_summary"] = all(
        counts[(study, group)] == summary["numeric_by_study_group"][f"{study}_{group}"]
        and denoms[(study, group)] == summary["denominator_by_study_group"][f"{study}_{group}"]
        for study in ("Ga", "Ju", "Si") for group in ("PD", "HC")
    )
    checks["source_status_and_feature_values"] = all(
        a[sid]["study"] == c[sid]["study"] == f[sid]["study"]
        and a[sid]["group"] == c[sid]["group"]
        and int(f[sid]["label"]) == (1 if c[sid]["group"] == "PD" else 0)
        and (all(math.isfinite(float(f[sid][name])) for name in NAMES)
             if a[sid]["status"] == "READABLE_NUMERIC"
             else all(f[sid][name] == "" for name in NAMES))
        for sid in c
    )
    checks["budget_and_gate_recompute"] = (summary["requests"] == 166
        and summary["bytes_read"] == 164521028
        and summary["requests"] <= 180 and summary["bytes_read"] <= 250*1024*1024
        and counts[("Ju", "PD")] == 25 and denoms[("Ju", "PD")] == 29
        and counts[("Ju", "PD")] / denoms[("Ju", "PD")] < .9
        and summary["source_gate"] == "STOP_NUMERIC_SOURCE")
    reported_retry = summary["retries"]
    observed_final_failure_retry = sum("|" in row["error"] for row in audit if row["status"] != "READABLE_NUMERIC")
    output = {
        "run_id": "EXP031-VERIFY-001",
        "scope": "derived cohort, features, audit, and summary only; no original-file reread or model fit",
        "checks": checks,
        "critical_pass": all(checks.values()),
        "source_gate": summary["source_gate"],
        "metadata_correction": {
            "summary_retries_reported": reported_retry,
            "failed_file_retries_visible_in_audit": observed_final_failure_retry,
            "note": "SOURCE_SUMMARY retries omitted failed-file retries; request count 166 correctly includes them. Original summary retained."
        }
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))
    if not output["critical_pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
