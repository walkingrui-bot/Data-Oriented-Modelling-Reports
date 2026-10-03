"""EXP024-DOC-001: read the frozen official Label URLs only in memory."""

import csv
import io
import re
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from pypdf import PdfReader


ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "SAMPLE.csv"
OUT = ROOT / "DOCUMENT_AUDIT.csv"
FILE_CAP = 20 * 1024 * 1024
TOTAL_CAP = 512 * 1024 * 1024


def section_signal(pages):
    candidates = []
    for page_index, text in enumerate(pages, start=1):
        patterns = [
            r"(?im)^\s*(?:1\s*[.:-]?\s*)?INDICATIONS\s+(?:AND|&)\s+USAGE\s*$",
            r"(?im)INDICATIONS\s+(?:AND|&)\s+USAGE",
        ]
        for priority, pattern in enumerate(patterns):
            for match in re.finditer(pattern, text):
                after = text[match.end():match.end() + 1300]
                words = len(after.split())
                candidates.append((priority, -words, page_index, match.start(), after))
    if not candidates:
        return "", "", ""
    # Heading-like matches take precedence; later matches often reach full PI
    # rather than the highlights or table of contents.
    candidates.sort(key=lambda x: (x[0], x[1], -x[2]))
    _, _, page, offset, after = candidates[0]
    compact = re.sub(r"\s+", " ", after).strip()
    return str(page), str(offset), compact[:600]


def fetch(url, budget_remaining):
    url = url.replace("http://www.accessdata.fda.gov/", "https://www.accessdata.fda.gov/", 1)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 EXP024 source audit", "Accept": "application/pdf,*/*"})
    with urllib.request.urlopen(req, timeout=50) as response:
        blob = response.read(min(FILE_CAP + 1, budget_remaining + 1))
        info = {"http_status": response.status, "content_type": response.headers.get("Content-Type", ""), "resolved_url": response.url}
    if len(blob) > FILE_CAP:
        raise ValueError("SINGLE_FILE_OVER_20_MIB")
    if len(blob) > budget_remaining:
        raise ValueError("TOTAL_NETWORK_OVER_512_MIB")
    return blob, info


def inspect_pdf(blob):
    if not blob.startswith(b"%PDF"):
        raise ValueError("RESPONSE_NOT_PDF")
    pdf = PdfReader(io.BytesIO(blob), strict=False)
    if pdf.is_encrypted:
        try:
            pdf.decrypt("")
        except Exception as exc:
            raise ValueError("PDF_ENCRYPTED") from exc
    pages = [(p.extract_text() or "") for p in pdf.pages]
    page, offset, excerpt = section_signal(pages)
    joined = "\n".join(pages)
    first_page = re.sub(r"\s+", " ", pages[0])[:250] if pages else ""
    role_signal = any(x in joined.upper() for x in ("FULL PRESCRIBING INFORMATION", "HIGHLIGHTS OF PRESCRIBING INFORMATION", "PRESCRIBING INFORMATION"))
    revised = re.search(r"(?i)(revised\s*[:/]\s*\d{1,2}[/\-]\d{4})", joined)
    return {
        "pdf_pages": len(pages), "extractable_characters": len(joined),
        "prescribing_information_signal": role_signal,
        "indications_heading_page": page, "indications_heading_offset": offset,
        "indications_excerpt": excerpt, "first_page_excerpt": first_page,
        "revised_date_excerpt": revised.group(1) if revised else "",
    }


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    with SAMPLE.open(newline="") as f:
        sample = list(csv.DictReader(f))
    if len(sample) != 40 or len({x["application_no"] for x in sample}) != 40:
        raise RuntimeError("Frozen sample does not contain 40 distinct applications")
    fields = ["sample_id", "stratum", "application_type", "application_no", "submission_type", "submission_no", "action_date", "document_id", "document_date", "document_url", "resolved_url", "http_status", "content_type", "bytes_read", "attempts", "fetch_status", "parse_status", "pdf_pages", "extractable_characters", "prescribing_information_signal", "indications_heading_page", "indications_heading_offset", "indications_excerpt", "first_page_excerpt", "revised_date_excerpt", "document_action_day_delta", "agent_decision", "agent_note"]
    total_bytes = 0
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in sample:
            record = {
                "sample_id": row["sample_id"], "stratum": row["stratum"],
                "application_type": row["application_type"], "application_no": row["application_no"],
                "submission_type": row["submission_type"], "submission_no": row["submission_no"],
                "action_date": row["action_date"], "document_id": row["selected_document_id"],
                "document_date": row["selected_document_date"], "document_url": row["selected_document_url"],
                "agent_decision": "PENDING_AGENT", "agent_note": "",
            }
            if not row["selected_document_url"]:
                record.update(fetch_status="NO_SAME_KEY_LABEL_URL", parse_status="NOT_ATTEMPTED", attempts=0)
                writer.writerow(record); f.flush(); continue
            for attempt in (1, 2):
                record["attempts"] = attempt
                try:
                    blob, info = fetch(row["selected_document_url"], TOTAL_CAP - total_bytes)
                    total_bytes += len(blob)
                    record.update(info)
                    record["bytes_read"] = len(blob)
                    record["fetch_status"] = "SUCCESS"
                    break
                except Exception as exc:
                    record["fetch_status"] = f"{type(exc).__name__}:{str(exc)[:160]}"
                    if attempt == 2:
                        blob = None
            if record["fetch_status"] == "SUCCESS":
                try:
                    record.update(inspect_pdf(blob))
                    record["parse_status"] = "EXTRACTED"
                except Exception as exc:
                    record["parse_status"] = f"{type(exc).__name__}:{str(exc)[:160]}"
            else:
                record["parse_status"] = "NOT_FETCHED"
            if record["document_date"] and record["action_date"]:
                record["document_action_day_delta"] = (date.fromisoformat(record["document_date"]) - date.fromisoformat(record["action_date"])).days
            writer.writerow(record)
            f.flush()
            print(record["sample_id"], record["fetch_status"], record["parse_status"], record.get("indications_heading_page", ""), "bytes", record.get("bytes_read", 0), flush=True)
    print("TOTAL_BYTES", total_bytes)


if __name__ == "__main__":
    main()
