#!/usr/bin/env python3
"""Read-only EXP018 native table and saved six-source model preflight."""

from __future__ import annotations

import json
from pathlib import Path
import sys

import duckdb
import torch


HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / "STAT-PSYMOE-EXP017-20261002-001"
sys.path.insert(0, str(PARENT))
from access_probe import parquet_urls  # noqa: E402


TABLES = {
    "clingen": "evidence_clingen",
    "gene2phenotype": "evidence_gene2phenotype",
    "orphanet": "evidence_orphanet",
}
OUT = HERE / "preflight.json"


def main() -> None:
    if OUT.exists():
        raise RuntimeError(f"Preserve existing preflight: {OUT}")
    con = duckdb.connect()
    tables = {}
    for ds, table in TABLES.items():
        urls = parquet_urls(table)
        fields = [{"name": row[0], "type": row[1]} for row in con.execute(
            "DESCRIBE SELECT * FROM read_parquet(?)", [urls[0]]
        ).fetchall()]
        names = {f["name"] for f in fields}
        tables[ds] = {
            "table": table,
            "first_file_url": urls[0],
            "files": len(urls),
            "first_file_rows": int(con.execute("SELECT count(*) FROM read_parquet(?)", [urls[0]]).fetchone()[0]),
            "fields": fields,
            "has_pair_and_score": {"targetId", "diseaseId", "score"}.issubset(names),
            "date_fields": sorted(n for n in names if any(word in n.lower() for word in ("date", "year", "time"))),
        }
    models = {}
    for seed in (101, 202, 303):
        p = PARENT / f"results/native_six/EXP017-NATIVE-TRAIN-001/ganglion_seed_{seed}.pt"
        obj = torch.load(p, map_location="cpu", weights_only=True)
        keys = list(obj["state_dict"])
        models[str(seed)] = {
            "path": str(p),
            "best_epoch": int(obj["best_epoch"]),
            "six_old_interfaces": all(f"interfaces.{j}.0.weight" in keys for j in range(6)),
            "has_core_and_outcome": all(k in keys for k in (
                "core.0.weight", "core.0.bias", "outcome.weight", "outcome.bias"
            )),
            "state_keys": keys,
        }
    result = {
        "run_id": "EXP018-PREFLIGHT-001",
        "release": "26.06",
        "native_tables": tables,
        "saved_six_source_models": models,
        "training_not_started": True,
    }
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"sources": {k: {"files": v["files"], "fields": [f["name"] for f in v["fields"]]}
                                  for k, v in tables.items()},
                      "checkpoints": {k: {"best_epoch": v["best_epoch"],
                                          "valid_structure": v["six_old_interfaces"] and v["has_core_and_outcome"]}
                                      for k, v in models.items()}}, indent=2))


if __name__ == "__main__":
    main()
