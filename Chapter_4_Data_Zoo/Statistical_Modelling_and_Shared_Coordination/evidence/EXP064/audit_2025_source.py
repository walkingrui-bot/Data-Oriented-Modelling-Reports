#!/usr/bin/env python3
"""EXP064: same ten UK-AIR sites, 2025 ratified natural-outage source only."""

import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
P62 = HERE.parent / "STAT-PSYMOE-EXP062-20261002-001"
sys.path.insert(0, str(HERE.parent / "STAT-PSYMOE-EXP061-20261002-001"))
import audit_external_source as audit  # noqa: E402

SITES = "BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR".split()
GRID = [datetime(2025, 1, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(8760)]
MAX_BYTES = 30 * 1024 * 1024


def main():
    for name in ("SOURCE_MATRIX.json", "PAIR_SUPPORT.json"):
        if (HERE / name).exists():
            raise FileExistsError("preserve previous attempt output " + name)
    original = json.loads((P62 / "PAIR_SUPPORT.json").read_text())
    if original["qualified_sites"] != SITES:
        raise ValueError("fixed EXP062 ten-site set changed")
    # Reuse the EXP061 source parser without copying its implementation.
    audit.GRID = GRID
    audit.TIME_TO_INDEX = {t: i for i, t in enumerate(GRID)}
    source = {"run_id": "EXP064-SOURCE-001",
              "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "year": 2025, "time_basis": "GMT hour ending; 24:00 next-day 00:00",
              "grid_start": GRID[0].isoformat(), "grid_end": GRID[-1].isoformat(),
              "grid_hours": len(GRID), "sites": []}
    obs = {}
    total = 0
    for site in SITES:
        page = f"https://uk-air.defra.gov.uk/data/flat_files?site_id={site}"
        item = {"site": site, "flat_files_url": page}
        try:
            html, _ = audit.fetch(page, MAX_BYTES - total)
            total += len(html)
            links = audit.Links()
            links.feed(html.decode("utf-8", "replace"))
            choices = [urljoin(page, href) for href, _ in links.links
                       if urlparse(urljoin(page, href)).path.endswith(f"/site_data/{site}_2025.csv")]
            if len(choices) != 1:
                raise ValueError("expected one official 2025 all-hourly file: " + str(len(choices)))
            data, meta = audit.fetch(choices[0], MAX_BYTES - total)
            total += len(data)
            parsed, observed = audit.parse_csv(data, site)
            item.update(parsed)
            item.update({"csv_url": choices[0], "csv_bytes": len(data),
                         "csv_response": meta})
            obs[site] = observed
            print(site, "valid", item["counts"].get("valid_ratified_pm", 0),
                  "blank", item["counts"].get("explicit_blank_pm", 0),
                  "schema_ok", item["schema_ok"], flush=True)
        except Exception as exc:
            item["error"] = type(exc).__name__ + ": " + str(exc)
            print(site, "ERROR", item["error"], flush=True)
        source["sites"].append(item)
    source["downloaded_bytes_total"] = total
    source["all_ten_retrieved"] = len(obs) == 10
    qualified = [x["site"] for x in source["sites"] if x.get("schema_ok")
                 and x.get("counts", {}).get("valid_ratified_pm", 0) >= 6000]
    source["qualified_sites_min_6000"] = qualified
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(source, indent=2) + "\n")
    support = {"qualified_sites": qualified, "pair_count": 0,
               "unique_origin_dates": 0, "counts_by_target": {},
               "neighbor_count_distribution": {},
               "natural_origin": "PM field explicitly blank in existing hour row",
               "future_target": "R finite nonnegative PM exactly 24 GMT hours later"}
    if source["all_ten_retrieved"]:
        dates = set()
        neighbor_dist = Counter()
        for site in qualified:
            station = obs[site]
            counts = Counter()
            for i in range(len(GRID) - 24):
                origin = station.get(i)
                if origin is None or origin[0] != "blank":
                    continue
                counts["blank_origin_with_future_grid"] += 1
                target = station.get(i + 24)
                if target is None or target[0] != "valid":
                    counts["future_not_ratified_measured"] += 1
                    continue
                counts["true_future_target"] += 1
                neighbors = sum(obs[other].get(i, (None, None))[0] == "valid"
                                for other in qualified if other != site)
                neighbor_dist[neighbors] += 1
                if neighbors >= 8:
                    counts["eligible_pair"] += 1
                    dates.add(GRID[i].date().isoformat())
            support["counts_by_target"][site] = dict(counts)
        support["pair_count"] = sum(x.get("eligible_pair", 0)
                                    for x in support["counts_by_target"].values())
        support["unique_origin_dates"] = len(dates)
        support["neighbor_count_distribution"] = dict(sorted(neighbor_dist.items()))
    support["target_sites_at_least_10"] = [s for s, c in support["counts_by_target"].items()
                                           if c.get("eligible_pair", 0) >= 10]
    (HERE / "PAIR_SUPPORT.json").write_text(json.dumps(support, indent=2) + "\n")
    print("total_bytes", total, "all_ten_retrieved", source["all_ten_retrieved"], flush=True)
    print("qualified_sites", len(qualified), qualified, flush=True)
    print("eligible_pairs", support["pair_count"],
          "target_sites_at_least_10", len(support["target_sites_at_least_10"]),
          "dates", support["unique_origin_dates"], flush=True)


if __name__ == "__main__":
    main()
