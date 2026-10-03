#!/usr/bin/env python3
"""Record terminal-label collisions created by the 26.06 ontology bridge."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter, defaultdict
from pathlib import Path

import duckdb

from access_probe import COHORT, get, parquet_urls
from cache_source_level import bridge


OUT = Path(__file__).with_name("bridge_conflicts.json")


def main() -> None:
    rows = list(csv.DictReader(io.StringIO(get(COHORT).decode("utf-8"))))
    mapping = bridge({r["efo_id_norm"] for r in rows}, duckdb.connect(), parquet_urls("disease"))
    grouped = defaultdict(list)
    for row in rows:
        key = (row["ensembl_id"], mapping[row["efo_id_norm"]])
        grouped[key].append({
            "source_disease_id": row["efo_id_norm"],
            "phase": row["phase"],
            "label": row["label"],
        })
    conflicts = []
    for (target, disease), records in sorted(grouped.items()):
        if len({(r["phase"], r["label"]) for r in records}) > 1:
            conflicts.append({
                "targetId": target,
                "currentDiseaseId": disease,
                "source_records": records,
            })
    source_pair_counts = Counter((r["ensembl_id"], r["efo_id_norm"]) for r in rows)
    summary = {
        "run_id": "EXP017-BRIDGE-DIAG-001",
        "source_rows": len(rows),
        "source_unique_pairs": len(source_pair_counts),
        "source_duplicate_rows": len(rows) - len(source_pair_counts),
        "mapped_unique_pairs": len(grouped),
        "mapped_duplicate_rows": len(rows) - len(grouped),
        "conflicting_mapped_pairs": len(conflicts),
        "conflicting_source_rows": sum(len(x["source_records"]) for x in conflicts),
        "conflicts": conflicts,
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "conflicts"}, indent=2))


if __name__ == "__main__":
    main()
