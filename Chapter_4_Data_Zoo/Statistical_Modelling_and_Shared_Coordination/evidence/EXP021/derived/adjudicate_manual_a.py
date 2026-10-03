"""Record human inspection of the fixed 70-row EVENT_A-005 source excerpts."""

from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "MANUAL_VALIDATION.csv"


def main() -> None:
    with CSV.open(newline="") as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        rows = list(reader)
    assert fields and len(rows) == 70 and all(r["match"] == "PENDING_HUMAN" for r in rows)
    for row in rows:
        typ = row["review_type"]
        app = row["application_number"]
        row["manual_reviewer"] = "Codex; 2026-10-02; displayed FDA source excerpt and record identifiers reviewed"
        if typ == "ORIGINAL_APPROVAL_LETTER":
            if app == "205909":
                row.update(match="FAIL", issue_type="MEDICAL_GAS_CORRECTION_LETTER",
                           note="NDA 205909 PDF says deemed granted medical gas certification; 2015 signature cannot validate 2013 original therapeutic approval. Exclude from innovator EVENT_A.")
            elif app == "219627":
                row.update(match="UNVERIFIED", issue_type="CORRECTED_LETTER_DATE",
                           note="PDF URL explicitly says corrected letter; signature 2026-09-16 differs from Drugs@FDA 2026-06-12 action date. Original action date requires a separate original document/UI check.")
            elif app == "020887":
                row.update(match="UNVERIFIED", issue_type="NO_EXTRACTABLE_DATE",
                           note="PDF first/signature pages yielded no usable date in the retained extraction; cannot independently confirm 1998-09-14.")
            elif row["automated_value"] in row["verified_value"].split("|"):
                row.update(match="MATCH", issue_type="", note="FDA approval letter identifier and electronic signature date agree with ORIG/AP action date.")
            else:
                expected = datetime.fromisoformat(row["automated_value"]).strftime("%-m/%-d/%y")
                # Old approval letters often print two-digit years in the signature, not the current parser format.
                excerpt = row["source_excerpt"]
                short_matches = re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{2})\b", excerpt)
                expected_tuple = tuple(map(int, expected.split("/")))
                if tuple(map(int, short_matches[-1])) == expected_tuple if short_matches else False:
                    row.update(match="MATCH", verified_value=row["automated_value"], issue_type="TWO_DIGIT_SIGNATURE_YEAR",
                               note="Signature page uses a two-digit year; month/day/year digits agree with the FDA event and contemporaneous letter context.")
                elif app == "125387" and "November 18, 2011" in excerpt:
                    row.update(match="MATCH", verified_value="2011-11-18", issue_type="DATE_IN_LETTER_HEADER",
                               note="Paper BLA letter first page states November 18, 2011 and BLA 125387.")
                else:
                    row.update(match="UNVERIFIED", issue_type="DATE_NOT_ESTABLISHED_FROM_EXCERPT",
                               note="Retained excerpt does not independently establish action date; no inference.")
        elif typ == "PURPLE_ORIGINAL_APPROVAL_PAGE":
            if row["automated_value"] == row["verified_value"]:
                row.update(match="MATCH", issue_type="", note="FDA Purple product page gives BLA number and full-year original approval date.")
            else:
                row.update(match="FAIL", issue_type="PURPLE_TWO_DIGIT_CENTURY_ERROR",
                           note="FDA Purple CSV short year parsed as 2024; official BLA page explicitly says 1924. EVENT_A-005 candidate date is invalid.")
        else:
            if row["verified_value"] == "LEFT_FOUND;ORIG_FOUND":
                row.update(match="INDETERMINATE", issue_type="PRODUCT_APPLICATION_SCOPE_DIFFERENCE",
                           note="FDA online application page displays both dates; page excerpt does not prove which product action created the later Orange product date. No date is silently chosen.")
            else:
                row.update(match="INDETERMINATE", issue_type="ORANGE_PRODUCT_DATE_NOT_ON_APPLICATION_PAGE",
                           note="FDA online application page shows ORIG date but not the Orange product date in the inspected page; product/letter lineage remains unresolved.")
    assert all(r["match"] != "PENDING_HUMAN" for r in rows)
    with CSV.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    from collections import Counter
    print(Counter((r["review_type"], r["match"]) for r in rows))


if __name__ == "__main__":
    main()
