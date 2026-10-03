"""Read the three FDA source families in memory and record release metadata only."""

from __future__ import annotations

import csv
import io
import json
import urllib.request
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
EXP021 = ROOT.parent / "STAT-PSYMOE-EXP021-20261002-001"
PRIOR = json.loads((EXP021 / "SOURCE_INDEX.json").read_text())["sources"]
OUT = ROOT / "SOURCE_INDEX.json"


def fetch(name: str) -> tuple[bytes, dict]:
    source_url = PRIOR[name]["source_url"]
    request = urllib.request.Request(source_url, headers={"User-Agent": "Mozilla/5.0 EXP022 source-semantics research"})
    with urllib.request.urlopen(request, timeout=90) as response:
        blob = response.read()
        metadata = {
            "source_url": source_url,
            "resolved_url": response.url,
            "http_status": response.status,
            "content_type": response.headers.get("Content-Type"),
            "last_modified": response.headers.get("Last-Modified"),
            "bytes_read": len(blob),
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "exp021_last_modified": PRIOR[name]["last_modified"],
            "exp021_bytes_read": PRIOR[name]["bytes_read"],
        }
        metadata["same_metadata_as_exp021"] = (
            metadata["last_modified"] == metadata["exp021_last_modified"]
            and metadata["bytes_read"] == metadata["exp021_bytes_read"]
        )
    return blob, metadata


def table_meta(archive: zipfile.ZipFile, filename: str, delimiter: str) -> dict:
    with archive.open(filename) as raw:
        stream = io.TextIOWrapper(raw, encoding="utf-8-sig", errors="replace", newline="")
        reader = csv.reader(stream, delimiter=delimiter)
        columns = next(reader)
        count = sum(1 for _ in reader)
    return {"columns": columns, "physical_rows_after_header": count}


def main() -> None:
    if OUT.exists():
        raise RuntimeError("EXP022 source index exists; preserve this run state")
    output = {"run_id": "EXP022-SOURCE-001", "sources": {}, "purple_semantic_diagnostic": {}}
    for name in ("drugs_at_fda", "orange_book", "purple_book_august_2026_xlsx", "purple_book_august_2026"):
        blob, metadata = fetch(name)
        if name == "drugs_at_fda":
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                metadata["members"] = {m: table_meta(z, m, "\t") for m in
                    ("Applications.txt", "Submissions.txt", "Products.txt", "ApplicationDocs.txt", "SubmissionClass_Lookup.txt")}
        elif name == "orange_book":
            with zipfile.ZipFile(io.BytesIO(blob)) as z:
                metadata["members"] = {"products.txt": table_meta(z, "products.txt", "~")}
        elif name == "purple_book_august_2026_xlsx":
            workbook = openpyxl.load_workbook(io.BytesIO(blob), read_only=True, data_only=True)
            sheet = list(workbook.active.iter_rows(values_only=True))
            header = list(sheet[34])
            rows = [dict(zip(header, r)) for r in sheet[35:] if len(r) == len(header) and r[2] is not None]
            metadata["physical_rows"] = len(sheet)
            metadata["full_section_rows"] = len(rows)
            metadata["full_section_header"] = header
            selected = [r for r in rows if r["License Type"] == "351(a)" and r["Submission Type"] == "Original"]
            by_bla = defaultdict(set)
            date_first = defaultdict(set)
            for r in selected:
                key = str(r["BLA Number"]).zfill(6)
                by_bla[key].add(str(r["Approval Date"]))
                date_first[key].add(str(r["Date of First Licensure"]))
            output["purple_semantic_diagnostic"] = {
                "selected_351a_original_product_rows": len(selected),
                "unique_bla": len(by_bla),
                "bla_with_multiple_approval_dates": sum(len(v) > 1 for v in by_bla.values()),
                "bla_with_multiple_first_licensure_values": sum(len(v) > 1 for v in date_first.values()),
                "nonblank_date_of_first_licensure_rows": sum(bool(r["Date of First Licensure"]) for r in selected),
                "sample_multi_date_bla": {k: sorted(v) for k, v in list((k, v) for k, v in by_bla.items() if len(v) > 1)[:8]},
                "license_type_counts": dict(Counter(str(r["License Type"]) for r in rows)),
                "submission_type_counts": dict(Counter(str(r["Submission Type"]) for r in rows)),
            }
        else:
            reader = list(csv.reader(io.StringIO(blob.decode("utf-8-sig", errors="replace"))))
            metadata["physical_rows"] = len(reader)
            metadata["full_section_header"] = reader[34]
        output["sources"][name] = metadata
        print(name, metadata["last_modified"], metadata["bytes_read"], metadata["same_metadata_as_exp021"])
    OUT.write_text(json.dumps(output, indent=2, ensure_ascii=False, default=str) + "\n")
    print(json.dumps(output["purple_semantic_diagnostic"], indent=2))


if __name__ == "__main__":
    main()
