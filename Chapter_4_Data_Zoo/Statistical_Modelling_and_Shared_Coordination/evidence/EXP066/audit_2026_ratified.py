#!/usr/bin/env python3
"""EXP066: bounded 2026 ratified natural-outage source audit, no model scoring."""

import json
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "STAT-PSYMOE-EXP061-20261002-001"))
import audit_external_source as audit  # noqa: E402

SITES = "BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR".split()
GRID = [datetime(2026, 1, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(8760)]
WINDOW_END = datetime(2026, 9, 1, tzinfo=timezone.utc)
ORIGIN_INDICES = [i for i, t in enumerate(GRID[:-24]) if t < WINDOW_END]
MAX_BYTES = 30 * 1024 * 1024


def main():
    for name in ("SOURCE_MATRIX.json", "PAIR_SUPPORT.json"):
        if (HERE / name).exists():
            raise FileExistsError("preserve prior attempt: " + name)
    audit.GRID = GRID
    audit.TIME_TO_INDEX = {t: i for i, t in enumerate(GRID)}
    source = {"run_id": "EXP066-SOURCE-001",
              "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "year": 2026, "time_basis": "GMT hour ending; 24:00 next-day 00:00",
              "origin_window_start": GRID[0].isoformat(),
              "origin_window_end_exclusive": WINDOW_END.isoformat(),
              "origin_window_hours": len(ORIGIN_INDICES),
              "full_year_grid_hours": len(GRID), "sites": []}
    observations = {}
    total = 0
    for site in SITES:
        page = f"https://uk-air.defra.gov.uk/data/flat_files?site_id={site}"
        item = {"site": site, "flat_files_url": page}
        try:
            html, _ = audit.fetch(page, MAX_BYTES - total)
            total += len(html)
            links = audit.Links()
            links.feed(html.decode("utf8", "replace"))
            urls = [urljoin(page, href) for href, _ in links.links
                    if urlparse(urljoin(page, href)).path.endswith(f"/site_data/{site}_2026.csv")]
            if len(urls) != 1:
                raise ValueError("expected one official 2026 all-hourly file: " + str(len(urls)))
            data, meta = audit.fetch(urls[0], MAX_BYTES - total)
            total += len(data)
            parsed, observed = audit.parse_csv(data, site)
            item.update(parsed)
            item.update({"csv_url": urls[0], "csv_bytes": len(data),
                         "csv_response": meta,
                         "ratified_valid_in_origin_window": sum(
                             observed.get(i, (None, None))[0] == "valid" for i in ORIGIN_INDICES)})
            observations[site] = observed
            print(site, "R_window", item["ratified_valid_in_origin_window"],
                  "blank_full_csv", item["counts"].get("explicit_blank_pm", 0),
                  "schema_ok", item["schema_ok"], flush=True)
        except Exception as exc:
            item["error"] = type(exc).__name__ + ": " + str(exc)
            print(site, "ERROR", item["error"], flush=True)
        source["sites"].append(item)
    source["downloaded_bytes_total"] = total
    source["all_ten_retrieved"] = len(observations) == 10
    qualified = [x["site"] for x in source["sites"] if x.get("schema_ok")
                 and x.get("ratified_valid_in_origin_window", 0) >= 4000]
    source["qualified_sites_min_4000_R_window"] = qualified
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(source, indent=2) + "\n")
    support = {"qualified_sites": qualified, "counts_by_target": {},
               "pair_count": 0, "unique_origin_dates": 0,
               "neighbor_count_distribution": {},
               "origin_window_end_exclusive": WINDOW_END.isoformat(),
               "origin_definition": "explicit blank PM in existing hour row",
               "target_definition": "ratified finite nonnegative PM exactly 24 GMT hours later"}
    if source["all_ten_retrieved"]:
        dates = set()
        nd = Counter()
        for site in qualified:
            obs = observations[site]
            counts = Counter()
            for i in ORIGIN_INDICES:
                origin = obs.get(i)
                if origin is None or origin[0] != "blank":
                    continue
                counts["blank_origin"] += 1
                target = obs.get(i + 24)
                if target is None or target[0] != "valid":
                    counts["future_not_ratified_measured"] += 1
                    continue
                counts["true_future_target"] += 1
                n = sum(observations[s].get(i, (None, None))[0] == "valid"
                        for s in qualified if s != site)
                nd[n] += 1
                if n >= 8:
                    counts["eligible_pair"] += 1
                    dates.add(GRID[i].date().isoformat())
            support["counts_by_target"][site] = dict(counts)
        support["pair_count"] = sum(x.get("eligible_pair", 0)
                                    for x in support["counts_by_target"].values())
        support["unique_origin_dates"] = len(dates)
        support["neighbor_count_distribution"] = dict(sorted(nd.items()))
    support["target_sites_at_least_10"] = [s for s, c in support["counts_by_target"].items()
                                           if c.get("eligible_pair", 0) >= 10]
    (HERE / "PAIR_SUPPORT.json").write_text(json.dumps(support, indent=2) + "\n")
    print("total_bytes", total, "all_ten_retrieved", source["all_ten_retrieved"], flush=True)
    print("qualified", len(qualified), qualified, flush=True)
    print("pairs", support["pair_count"], "stations10", len(support["target_sites_at_least_10"]),
          "days", support["unique_origin_dates"], flush=True)


if __name__ == "__main__":
    main()
