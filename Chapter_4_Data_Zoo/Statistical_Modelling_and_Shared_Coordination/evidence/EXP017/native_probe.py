#!/usr/bin/env python3
"""Inspect the six original 26.06 native evidence routes without caching rows."""

from __future__ import annotations

import json
from pathlib import Path

import duckdb

from access_probe import parquet_urls


TABLES = {
    "gwas_credible_sets": "evidence_gwas_credible_sets",
    "gene_burden": "evidence_gene_burden",
    "eva": "evidence_eva",
    "expression_atlas": "evidence_expression_atlas",
    "impc": "evidence_impc",
    "europepmc": "evidence_europepmc",
}
OUT = Path(__file__).with_name("native_probe.json")


def main() -> None:
    if OUT.exists():
        raise SystemExit(f"Existing result is preserved: {OUT}")
    con = duckdb.connect()
    result = {"run_id": "EXP017-NATIVE-PREFLIGHT-001", "release": "26.06", "tables": {}}
    for datasource, table in TABLES.items():
        urls = parquet_urls(table)
        schema = con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [urls[0]]).fetchall()
        fields = [{"name": row[0], "type": row[1]} for row in schema]
        names = {row["name"] for row in fields}
        result["tables"][datasource] = {
            "table": table,
            "file_count": len(urls),
            "first_file_url": urls[0],
            "first_file_rows_from_footer": int(con.execute("SELECT count(*) FROM read_parquet(?)", [urls[0]]).fetchone()[0]),
            "fields": fields,
            "has_target_and_disease_id": {"targetId", "diseaseId"}.issubset(names),
            "has_score": "score" in names,
            "date_fields": sorted(n for n in names if any(word in n.lower() for word in ("date", "year", "time"))),
        }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({ds: {
        "files": entry["file_count"],
        "first_file_rows": entry["first_file_rows_from_footer"],
        "fields": [x["name"] for x in entry["fields"]],
    } for ds, entry in result["tables"].items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
