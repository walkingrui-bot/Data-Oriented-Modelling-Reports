"""Select two disjoint manual gate samples using the prospectively frozen strata."""

from __future__ import annotations

import csv
import random
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXP021 = ROOT.parent / "STAT-PSYMOE-EXP021-20261002-001"
DERIVED = ROOT / "derived"


def prior_apps() -> set[str]:
    seen = {"101382", "101384", "102219", "103955", "125789"}
    for path in (EXP021 / "MANUAL_VALIDATION.csv", EXP021 / "derived/failed_MANUAL_A_002/MANUAL_VALIDATION.csv"):
        with path.open(newline="") as stream:
            for row in csv.DictReader(stream):
                raw = row.get("application_number", "").strip()
                if raw:
                    seen.add(raw.zfill(6))
    return seen


def select(pool: list[dict], number: int, rng: random.Random, excluded: set[str], stratum: str) -> list[dict]:
    items = sorted(pool, key=lambda x: x["event_id"])
    rng.shuffle(items)
    selected = []
    for item in items:
        application = item["application_no"]
        if application in excluded:
            continue
        excluded.add(application)
        selected.append({
            "sample_id": f"{stratum}-{len(selected)+1:02d}",
            "stratum": stratum,
            "event_id": item["event_id"],
            "application_no": application,
            "product_no": item.get("product_no", "") or "",
            "event_type": item["event_type"],
            "source_row_key": item["source_row_key"],
            "derived_event_date": item.get("event_date", "") or "",
            "review_status": "PENDING",
        })
        if len(selected) == number:
            break
    if len(selected) != number:
        raise RuntimeError(f"Insufficient new independent applications for {stratum}: {len(selected)}/{number}")
    return selected


def write(path: Path, rows: list[dict]) -> None:
    if path.exists():
        raise RuntimeError(f"Preserve prior sample: {path}")
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    events = pd.read_parquet(DERIVED / "SOURCE_SEMANTIC_CANDIDATES.parquet").fillna("").to_dict("records")
    actions = pd.read_parquet(DERIVED / "FDA_APPLICATION_ACTION.parquet").fillna("").to_dict("records")
    old = prior_apps()
    used = set(old)
    rng_a = random.Random(20261022)
    a = []
    a += select([r for r in events if r["event_type"] == "NDA_PRODUCT_APPROVAL"], 25, rng_a, used, "A_ORANGE")
    a += select([r for r in events if r["event_type"] == "BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL"], 25, rng_a, used, "A_PURPLE")
    for typ, subtyp, count in (("NDA", "ORIG", 10), ("NDA", "SUPPL", 10), ("BLA", "ORIG", 3), ("BLA", "SUPPL", 2)):
        a += select([r for r in actions if r["application_type"] == typ and r["submission_type"] == subtyp],
                    count, rng_a, used, f"A_DRUGS_{typ}_{subtyp}")
    write(ROOT / "GATE_A_SAMPLE.csv", a)

    rng_b = random.Random(20261023)
    b = []
    b += select([r for r in events if r["event_type"] == "NDA_PRODUCT_APPROVAL"], 15, rng_b, used, "B_ORANGE_NDA")
    for typ, subtyp, count in (("NDA", "ORIG", 7), ("NDA", "SUPPL", 8)):
        b += select([r for r in actions if r["application_type"] == typ and r["submission_type"] == subtyp],
                    count, rng_b, used, f"B_DRUGS_{typ}_{subtyp}")
    b += select([r for r in events if r["event_type"] == "BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL"],
                15, rng_b, used, "B_PURPLE_BLA")
    for typ, subtyp, count in (("BLA", "ORIG", 2), ("BLA", "SUPPL", 3)):
        b += select([r for r in actions if r["application_type"] == typ and r["submission_type"] == subtyp],
                    count, rng_b, used, f"B_DRUGS_{typ}_{subtyp}")
    write(ROOT / "GATE_B_SAMPLE.csv", b)
    print({"prior_seen_applications": len(old), "gate_a_rows": len(a), "gate_b_rows": len(b),
           "all_unique_applications": len({r["application_no"] for r in a + b}) == 125,
           "gate_a_strata": {x: sum(r["stratum"] == x for r in a) for x in sorted({r["stratum"] for r in a})},
           "gate_b_strata": {x: sum(r["stratum"] == x for r in b) for x in sorted({r["stratum"] for r in b})}})


if __name__ == "__main__":
    main()
