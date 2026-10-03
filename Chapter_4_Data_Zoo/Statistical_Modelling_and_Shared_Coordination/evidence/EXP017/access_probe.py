#!/usr/bin/env python3
"""EXP017 read-only source inspection; never materialises raw input files."""

from __future__ import annotations

import csv
import io
import json
import re
import urllib.request
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import bedrock_bio as bb
import duckdb


RELEASE = "26.06"
FTP = f"https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/{RELEASE}/output/"
COHORT = (
    "https://api.github.com/repos/vi-c-ky/"
    "Human-genetic-evidence-associated-with-drug-approval/git/blobs/"
    "d7102b1357aaeb780c73d286318fea297d0dbcb4"
)
TRAINING_ZIP = Path("/Users/rui/Downloads/INTERNAL_COORDINATION_LOCAL_TRAINING_016.zip")
OUT = Path(__file__).with_name("access_probe.json")


def get(url: str) -> bytes:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "StatPsyMoE-EXP017/0.1", "Accept": "application/vnd.github.raw+json"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        return response.read()


def parquet_urls(directory: str) -> list[str]:
    html = get(FTP + directory + "/").decode()
    names = re.findall(r'href="([^"/]+\.parquet)"', html)
    if not names:
        raise RuntimeError(f"No Parquet objects listed for {directory}")
    return [FTP + directory + "/" + name for name in names]


def columns(meta: dict) -> list[str]:
    return [c["name"] if isinstance(c, dict) else str(c) for c in meta.get("columns", [])]


def main() -> None:
    with zipfile.ZipFile(TRAINING_ZIP) as archive:
        name = next(n for n in archive.namelist() if n.endswith("config/pipeline_registry.json"))
        registry = json.loads(archive.read(name))
    assert len(registry) == 18
    assert len({r["passport_id"] for r in registry}) == 18
    assert len({r["datasource_id"] for r in registry}) == 18

    available = set(bb.list_tables("open_targets"))
    bedrock = {}
    for short in ("association_by_datasource_direct", "disease"):
        name = "open_targets." + short
        meta = bb.describe_table(name)
        version_key = next((v for v in ("release", "version") if v in columns(meta)), None)
        sample = None
        if version_key:
            sample = (
                bb.load_table(name)
                .filter(f"{version_key} = '{RELEASE}'")
                .select(version_key)
                .limit(1)
                .fetchone()
            )
        bedrock[short] = {
            "version_field": version_key,
            "partition_keys": list(meta.get("partitions", {})),
            "requested_release_has_row": sample is not None,
        }

    con = duckdb.connect()
    association = parquet_urls("association_by_datasource_direct")
    disease = parquet_urls("disease")
    assoc_cols = [x[0] for x in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [association[0]]).fetchall()]
    disease_cols = [x[0] for x in con.execute("DESCRIBE SELECT * FROM read_parquet(?)", [disease[0]]).fetchall()]
    for required in ("targetId", "diseaseId", "aggregationValue", "associationScore", "evidenceCount"):
        assert required in assoc_cols, required
    for required in ("id", "obsoleteTerms", "obsoleteXRefs", "dbXRefs"):
        assert required in disease_cols, required

    native_routes = {}
    for row in registry:
        directory = row["native_table"]
        urls = parquet_urls(directory)
        native_routes[row["passport_id"]] = {
            "datasource_id": row["datasource_id"],
            "table": directory,
            "file_count": len(urls),
            "bedrock_table_visible": "open_targets." + directory in available,
        }

    cohort_rows = list(csv.DictReader(io.StringIO(get(COHORT).decode("utf-8"))))
    cohort_diseases = {r["efo_id_norm"] for r in cohort_rows}
    cohort_targets = {r["ensembl_id"] for r in cohort_rows}
    label_counts = defaultdict(int)
    for row in cohort_rows:
        label_counts[row["label"]] += 1
    assert len(cohort_rows) == 26278
    assert set(label_counts) == {"0", "1"}
    assert all(x.startswith("ENSG") for x in cohort_targets)

    # A current ID wins over every historical reference. Ambiguous historical
    # references remain unresolved instead of being overwritten by row order.
    disease_rows = con.execute(
        "SELECT id, obsoleteTerms, obsoleteXRefs, dbXRefs FROM read_parquet(?)", [disease]
    ).fetchall()
    current = {str(row[0]) for row in disease_rows}
    candidates = defaultdict(set)
    for identifier, *arrays in disease_rows:
        for array in arrays:
            for prior in array or []:
                prior = str(prior)
                if prior in cohort_diseases and prior not in current:
                    candidates[prior].add(str(identifier))
    resolved = {prior for prior in cohort_diseases if prior in current or len(candidates[prior]) == 1}
    ambiguous = {prior: sorted(candidates[prior]) for prior in cohort_diseases if prior not in current and len(candidates[prior]) > 1}
    unresolved = sorted(cohort_diseases - resolved - set(ambiguous))
    bridge = {prior: prior if prior in current else next(iter(candidates[prior])) for prior in resolved}
    source_pairs = defaultdict(set)
    mapped_pairs = defaultdict(set)
    for row in cohort_rows:
        source_pairs[(row["ensembl_id"], row["efo_id_norm"])].add((row["label"], row["phase"]))
        if row["efo_id_norm"] in bridge:
            mapped_pairs[(row["ensembl_id"], bridge[row["efo_id_norm"]])].add((row["label"], row["phase"]))

    report = {
        "study": "STAT-PSYMOE-EXP017-20261002-001",
        "release_path": FTP,
        "bedrock_current": bedrock,
        "official_ftp": {
            "association_parquet_files": len(association),
            "association_columns": assoc_cols,
            "disease_parquet_files": len(disease),
            "disease_columns_required_present": True,
            "native_routes": native_routes,
        },
        "terminal_cohort": {
            "git_blob_url": COHORT,
            "rows": len(cohort_rows),
            "unique_targets": len(cohort_targets),
            "unique_disease_ids": len(cohort_diseases),
            "label_counts": dict(label_counts),
            "duplicate_source_pair_rows": len(cohort_rows) - len(source_pairs),
            "source_pair_label_or_phase_conflicts": sum(len(values) > 1 for values in source_pairs.values()),
            "duplicate_mapped_pair_rows": len(cohort_rows) - len(mapped_pairs),
            "mapped_pair_label_or_phase_conflicts": sum(len(values) > 1 for values in mapped_pairs.values()),
            "disease_ids_resolved": len(resolved),
            "disease_ids_ambiguous": ambiguous,
            "disease_ids_unresolved": unresolved,
        },
        "limits": "Metadata and disease bridge only; datasource association rows and model performance not tested.",
    }
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({
        "bedrock": bedrock,
        "ftp_association_files": len(association),
        "native_routes": len(native_routes),
        "cohort_rows": len(cohort_rows),
        "disease_resolved": len(resolved),
        "disease_ambiguous": len(ambiguous),
        "disease_unresolved": len(unresolved),
        "duplicate_mapped_pair_rows": len(cohort_rows) - len(mapped_pairs),
        "mapped_pair_conflicts": sum(len(values) > 1 for values in mapped_pairs.values()),
        "output": str(OUT),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
