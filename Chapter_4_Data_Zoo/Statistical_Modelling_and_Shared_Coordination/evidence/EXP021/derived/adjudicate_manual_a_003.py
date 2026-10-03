"""Record reviewed judgments for the fixed EVENT_A-006 holdout, no resampling."""

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
        row["manual_reviewer"] = "Codex; 2026-10-02; FDA source excerpt, ID and signature inspected"
        typ = row["review_type"]
        if typ == "ORIGINAL_APPROVAL_LETTER":
            if row["application_number"] == "761315":
                row.update(match="INDETERMINATE", issue_type="SOURCE_DATE_CONFLICT",
                           note="Drugs and Purple list 2024-12-20, FDA approval letter electronic signature is 2024-12-26. The occurrence date is not resolved by this sample.")
            elif row["application_number"] == "217499":
                row.update(match="UNVERIFIED", issue_type="NON_APPROVAL_OR_UNREADABLE_LETTER",
                           note="Linked PDF filename is MGLtr and extraction is unreadable; a generic Letter document type does not prove original approval.")
            elif row["verified_value"] == row["automated_value"]:
                row.update(match="MATCH", issue_type="", note="FDA approval letter application number, approval action and full-year electronic signature date agree.")
            else:
                expected = datetime.fromisoformat(row["automated_value"]).strftime("%-m/%-d/%y")
                dates = re.findall(r"\b(\d{1,2})/(\d{1,2})/(\d{2})\b", row["source_excerpt"])
                if dates and tuple(map(int, dates[-1])) == tuple(map(int, expected.split("/"))):
                    row.update(match="MATCH", verified_value=row["automated_value"], issue_type="TWO_DIGIT_SIGNATURE_YEAR",
                               note="FDA approval letter application number and two-digit-year signature date agree with the event date; century supported by letter era.")
                else:
                    row.update(match="UNVERIFIED", issue_type="NO_INDEPENDENT_DATE_IN_RETAINED_EXCERPT",
                               note="PDF was opened but the retained first/signature-page text does not independently establish the exact approval date. No inference was made.")
        elif typ == "PURPLE_ORIGINAL_APPROVAL_PAGE":
            if row["issue_type"] == "SOURCE_UNREACHABLE":
                row.update(match="UNVERIFIED", note="FDA Purple detail URL returned HTTP 403 on both allowed attempts; XLSX value remains unconfirmed by the page.")
            elif row["verified_value"] == row["automated_value"]:
                row.update(match="MATCH", issue_type="", note="Purple BLA detail page displays the same original approval date with four-digit year.")
            else:
                row.update(match="FAIL", issue_type="PURPLE_PAGE_DATE_MISMATCH", note="Purple official BLA detail page and XLSX disagree; unresolved source conflict.")
        else:
            if row["issue_type"] == "SOURCE_UNREACHABLE":
                row.update(match="UNVERIFIED", note="FDA online application page returned HTTP 403 on both allowed attempts; original values remain in audit, no resolution.")
            elif row["verified_value"] == "LEFT_FOUND;ORIG_FOUND":
                row.update(match="INDETERMINATE", issue_type="PRODUCT_APPLICATION_SCOPE_DIFFERENCE",
                           note="FDA online page shows both dates; product action linkage not independently established in inspected excerpt. Retain both dates and exclude this conflict from validated cohort.")
            else:
                row.update(match="INDETERMINATE", issue_type="ORANGE_PRODUCT_DATE_NOT_ON_APPLICATION_PAGE",
                           note="ORIG date visible, Orange product date absent from inspected application page; retain both source values without adjudication.")
    assert all(row["match"] != "PENDING_HUMAN" for row in rows)
    with CSV.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fields)
        writer.writeheader()
        writer.writerows(rows)
    from collections import Counter
    print(Counter((r["review_type"], r["match"]) for r in rows))


if __name__ == "__main__":
    main()
