#!/usr/bin/env python3
"""EXP062: directory-derived bounded 2024 AURN London-region PM2.5 audit."""

import html
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urljoin, urlparse

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "STAT-PSYMOE-EXP061-20261002-001"))
from audit_external_source import GRID, Links, fetch, parse_csv  # noqa: E402

MAX_BYTES = 60 * 1024 * 1024
BBOX = {"latitude_min": 51.25, "latitude_max": 51.75,
        "longitude_min": -0.55, "longitude_max": 0.35}
QUERY = {"action": "results", "view": "advanced", "group_id": "4",
         "pollutant": "6", "closed": "true", "country_id": "9999",
         "region_id": "9999", "location_type": "9999", "site_name": ""}
SEARCH = "https://uk-air.defra.gov.uk/networks/find-sites?" + urlencode(QUERY)


def parse_directory(raw):
    page = raw.decode("utf-8", "replace")
    required = ("Automatic Urban and Rural Monitoring Network (AURN)",
                "Particulate Matter (PM2.5)", "Closed monitoring sites included")
    if not all(x in page for x in required):
        raise ValueError("directory search summary does not confirm filters")
    count_match = re.search(r"<strong>(\d+)</strong> monitoring sites matched your criteria", page)
    if not count_match:
        raise ValueError("directory result count absent")
    expected = int(count_match.group(1))
    found = []
    for row in re.findall(r"<tr\b[^>]*>.*?</tr>", page, re.S | re.I):
        id_match = re.search(r"UK-AIR ID:\s*(UKA\d+)", row)
        coord = re.search(r"Location:\s*([-+\d.]+)\s*,\s*([-+\d.]+)", row)
        if not id_match or not coord:
            continue
        cells = re.findall(r"<td\b[^>]*>(.*?)</td>", row, re.S | re.I)
        if len(cells) < 2:
            raise ValueError("directory site row lacks second cell")
        name = html.unescape(re.sub(r"<[^>]+>", "", cells[1].split("<div")[0])).strip()
        info = re.search(r'href="(site-info\?uka_id=[^" ]+)', row)
        if not info:
            raise ValueError("site-info URL absent for " + id_match.group(1))
        found.append({"name": name, "uka_id": id_match.group(1),
                      "latitude": float(coord.group(1)),
                      "longitude": float(coord.group(2)),
                      "site_info_url": urljoin(SEARCH, html.unescape(info.group(1))),
                      "listed_closed": "closed_row" in row})
    if len(found) != expected or len({x["uka_id"] for x in found}) != expected:
        raise ValueError(f"directory result incomplete/duplicate: {len(found)} vs {expected}")
    selected = [x for x in found if BBOX["latitude_min"] <= x["latitude"] <= BBOX["latitude_max"]
                and BBOX["longitude_min"] <= x["longitude"] <= BBOX["longitude_max"]]
    return expected, selected


def code_from_info(raw):
    page = raw.decode("utf-8", "replace")
    codes = set(re.findall(r"/site-photos/([A-Za-z0-9]+)_(?:site|n|e|s|w)\.jpg", page))
    if len(codes) != 1:
        raise ValueError("official site-info photo path did not yield unique site code: " + repr(sorted(codes)))
    return codes.pop()


def main():
    total = 0
    raw, meta = fetch(SEARCH, MAX_BYTES)
    total += len(raw)
    expected, selected = parse_directory(raw)
    directory = {"id": "STAT-PSYMOE-EXP062-20261002-001",
                 "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
                 "query": SEARCH, "query_result_count": expected,
                 "bbox": BBOX, "selected_count": len(selected),
                 "selected_sites": selected, "bytes": len(raw),
                 "response_url": meta["response_url"]}
    (HERE / "DIRECTORY.json").write_text(json.dumps(directory, indent=2) + "\n")
    print("official_directory_results", expected, "bbox_candidates", len(selected))
    if len(selected) > 40:
        raise RuntimeError("selected candidates exceed fixed 40-site budget")
    source = {"retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "directory_ref": "DIRECTORY.json", "year": 2024,
              "grid_start": GRID[0].isoformat(), "grid_end": GRID[-1].isoformat(),
              "grid_hours": len(GRID), "sites": []}
    observations = {}
    for candidate in selected:
        item = dict(candidate)
        try:
            site_info, _ = fetch(candidate["site_info_url"], MAX_BYTES - total)
            total += len(site_info)
            site = code_from_info(site_info)
            item["site"] = site
            page = f"https://uk-air.defra.gov.uk/data/flat_files?site_id={site}"
            item["flat_files_url"] = page
            h, _ = fetch(page, MAX_BYTES - total)
            total += len(h)
            links = Links()
            links.feed(h.decode("utf-8", "replace"))
            choices = [urljoin(page, href) for href, _ in links.links
                       if urlparse(urljoin(page, href)).path.endswith(f"/site_data/{site}_2024.csv")]
            if not choices:
                item["source_note"] = "2024 all-hourly site file absent"
                item["counts"] = {"valid_ratified_pm": 0}
                item["schema_ok"] = False
                print(site, candidate["name"], "NO_2024_FILE")
            elif len(choices) != 1:
                raise ValueError("2024 all-hourly link not unique")
            else:
                csv_url = choices[0]
                data, csv_meta = fetch(csv_url, MAX_BYTES - total)
                total += len(data)
                parsed, observed = parse_csv(data, site)
                item.update(parsed)
                item.update({"csv_url": csv_url, "csv_bytes": len(data),
                             "csv_response": csv_meta})
                observations[site] = observed
                print(site, candidate["name"], "valid", item["counts"].get("valid_ratified_pm", 0),
                      "blank", item["counts"].get("explicit_blank_pm", 0),
                      "schema_ok", item["schema_ok"])
        except Exception as exc:
            item["error"] = type(exc).__name__ + ": " + str(exc)
            print(candidate["uka_id"], candidate["name"], "ERROR", item["error"])
        source["sites"].append(item)
    source["downloaded_bytes_total"] = total
    source["directory_selected_count"] = len(selected)
    source["candidate_codes_unique"] = len({x["site"] for x in source["sites"] if "site" in x}) == sum(
        "site" in x for x in source["sites"])
    qualified = [x["site"] for x in source["sites"] if x.get("schema_ok")
                 and x.get("counts", {}).get("valid_ratified_pm", 0) >= 6000]
    source["qualified_sites_min_6000"] = qualified
    (HERE / "SOURCE_MATRIX.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")

    support = {"qualified_sites": qualified, "counts_by_target": {}, "pair_count": 0,
               "unique_target_dates": 0, "neighbor_count_distribution": {},
               "natural_missing_definition": "explicit blank PM in an existing hour row",
               "target_definition": "R, finite nonnegative PM exactly 24 GMT hours later"}
    dates = set()
    neighbors_dist = Counter()
    for site in qualified:
        obs = observations[site]
        counts = Counter()
        for i in range(len(GRID) - 24):
            origin = obs.get(i)
            if origin is None or origin[0] != "blank":
                continue
            counts["blank_origin_with_future_grid"] += 1
            future = obs.get(i + 24)
            if future is None or future[0] != "valid":
                counts["future_not_ratified_measured"] += 1
                continue
            counts["true_future_target"] += 1
            n = sum(observations[other].get(i, (None, None))[0] == "valid"
                    for other in qualified if other != site)
            neighbors_dist[n] += 1
            if n >= 8:
                counts["eligible_pair"] += 1
                dates.add(GRID[i].date().isoformat())
        support["counts_by_target"][site] = dict(counts)
    support["pair_count"] = sum(c.get("eligible_pair", 0) for c in support["counts_by_target"].values())
    support["unique_target_dates"] = len(dates)
    support["neighbor_count_distribution"] = dict(sorted(neighbors_dist.items()))
    support["target_sites_at_least_10"] = [s for s, c in support["counts_by_target"].items()
                                           if c.get("eligible_pair", 0) >= 10]
    (HERE / "PAIR_SUPPORT.json").write_text(json.dumps(support, indent=2) + "\n")
    print("downloaded_bytes_total", total)
    print("qualified_sites", len(qualified), qualified)
    print("eligible_pairs", support["pair_count"],
          "sites_at_least_10", len(support["target_sites_at_least_10"]),
          "unique_dates", support["unique_target_dates"])


if __name__ == "__main__":
    main()
