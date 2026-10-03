#!/usr/bin/env python3
"""EXP061: bounded in-memory audit of official UK-AIR annual site CSVs."""

import csv
import io
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

IDS = "BEX CA1 CLL2 HG4 HIL HORS HP1 HRL KC1 LON6 MY1 TED2".split()
ROOT = Path(__file__).resolve().parent
START = datetime(2024, 1, 1, 1, tzinfo=timezone.utc)
GRID = [START + timedelta(hours=i) for i in range(8784)]
TIME_TO_INDEX = {t: i for i, t in enumerate(GRID)}
MAX_BYTES = 30 * 1024 * 1024
USER_AGENT = "Stat-PsyMoE/EXP061 public-source research audit"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.href = None
        self.label = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.href = dict(attrs).get("href")
            self.label = []

    def handle_data(self, data):
        if self.href is not None:
            self.label.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self.href is not None:
            self.links.append((self.href, "".join(self.label).strip()))
            self.href = None


def fetch(url, remaining):
    if remaining <= 0:
        raise RuntimeError("download budget exhausted")
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=30) as response:
        data = response.read(remaining + 1)
        meta = {"content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
                "last_modified": response.headers.get("Last-Modified"),
                "response_url": response.url}
    if len(data) > remaining:
        raise RuntimeError("download budget exceeded")
    return data, meta


def parse_time(date_text, time_text):
    day = datetime.strptime(date_text.strip(), "%d-%m-%Y").replace(tzinfo=timezone.utc)
    clock = time_text.strip()
    if clock == "24:00":
        return day + timedelta(days=1)
    if not re.fullmatch(r"(?:0?[1-9]|1[0-9]|2[0-3]):00", clock):
        raise ValueError("non-hour-ending clock " + repr(clock))
    hour = int(clock.split(":")[0])
    return day + timedelta(hours=hour)


def plain_header(value):
    return re.sub(r"<[^>]+>", "", value).lower().strip()


def parse_csv(raw, site):
    reader = list(csv.reader(io.StringIO(raw.decode("utf-8-sig", "replace"))))
    preamble = [" ".join(row).strip() for row in reader[:3]]
    if not any("All Data GMT hour ending" in line for line in preamble):
        raise ValueError("GMT hour-ending declaration absent")
    if not any("R =Ratified" in line for line in preamble):
        raise ValueError("ratified status declaration absent")
    header_pos = next((i for i, row in enumerate(reader)
                       if len(row) >= 2 and row[0].strip().lower() == "date"
                       and row[1].strip().lower() == "time"), None)
    if header_pos is None:
        raise ValueError("Date/time header absent")
    header = reader[header_pos]
    matches = [i for i, name in enumerate(header)
               if plain_header(name).startswith("pm2.5 particulate matter")]
    if not matches:
        return ({"site": site, "pm_column_present": False,
                 "all_pollutant_header": header, "preamble": preamble,
                 "counts": {"valid_ratified_pm": 0}, "schema_ok": False,
                 "source_note": "plain PM2.5 column absent"}, {})
    if len(matches) != 1:
        raise ValueError(f"expected one plain PM2.5 column; found {matches}")
    p = matches[0]
    if len(header) < p + 3 or header[p + 1].strip().lower() != "status" or header[p + 2].strip().lower() != "unit":
        raise ValueError("PM2.5 value/status/unit triple absent")
    observed = {}
    stats = Counter()
    statuses = Counter()
    units = Counter()
    first_bad_rows = []
    for row in reader[header_pos + 1:]:
        if not row or all(not x.strip() for x in row):
            continue
        stats["nonempty_rows"] += 1
        try:
            when = parse_time(row[0], row[1])
        except (ValueError, IndexError):
            stats["unparsed_time_rows"] += 1
            if len(first_bad_rows) < 3:
                first_bad_rows.append(row[:2])
            continue
        if when not in TIME_TO_INDEX:
            stats["off_grid_rows"] += 1
            continue
        idx = TIME_TO_INDEX[when]
        if idx in observed:
            stats["duplicate_hour_rows"] += 1
            continue
        if len(row) < p + 3:
            stats["short_rows"] += 1
            continue
        value, status, unit = (row[p].strip(), row[p + 1].strip(), row[p + 2].strip())
        statuses[status or "<empty>"] += 1
        if unit:
            units[unit] += 1
        if not value:
            observed[idx] = ("blank", None)
            stats["explicit_blank_pm"] += 1
            continue
        try:
            pm = float(value)
        except ValueError:
            observed[idx] = ("non_numeric", None)
            stats["non_numeric_pm"] += 1
            continue
        if not math.isfinite(pm) or pm < 0:
            observed[idx] = ("nonfinite_or_negative", None)
            stats["nonfinite_or_negative_pm"] += 1
        elif status != "R":
            observed[idx] = ("not_ratified", None)
            stats["not_ratified_pm"] += 1
        elif not unit.startswith("ugm-3"):
            observed[idx] = ("wrong_unit", None)
            stats["wrong_unit_pm"] += 1
        else:
            observed[idx] = ("valid", pm)
            stats["valid_ratified_pm"] += 1
    stats["explicit_grid_rows"] = len(observed)
    stats["absent_grid_hours"] = len(GRID) - len(observed)
    item = {"site": site, "pm_column_present": True,
            "header": header[p:p + 3], "preamble": preamble,
            "counts": dict(stats), "statuses": dict(statuses), "units": dict(units),
            "first_bad_time_rows": first_bad_rows,
            "first_hour_present": 0 in observed,
            "last_hour_present": len(GRID) - 1 in observed}
    if stats["duplicate_hour_rows"] or stats["unparsed_time_rows"] or stats["off_grid_rows"] or stats["short_rows"]:
        item["schema_ok"] = False
    else:
        item["schema_ok"] = True
    return item, observed


def main():
    source = {"id": "STAT-PSYMOE-EXP061-20261002-001",
              "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
              "official_licence_page": "https://uk-air.defra.gov.uk/about-these-pages",
              "year": 2024, "time_basis": "GMT hour ending; 24:00 next day 00:00",
              "grid_start": GRID[0].isoformat(), "grid_end": GRID[-1].isoformat(),
              "grid_hours": len(GRID), "sites": []}
    data_by_site = {}
    total_bytes = 0
    for site in IDS:
        page = f"https://uk-air.defra.gov.uk/data/flat_files?site_id={site}"
        item = {"site": site, "source_page": page}
        try:
            html, page_meta = fetch(page, MAX_BYTES - total_bytes)
            total_bytes += len(html)
            links = Links()
            links.feed(html.decode("utf-8", "replace"))
            choices = [urljoin(page, href) for href, _ in links.links
                       if urlparse(urljoin(page, href)).path.endswith(f"/site_data/{site}_2024.csv")]
            if len(choices) != 1:
                raise ValueError(f"one all-pollutant 2024 CSV link expected; found {len(choices)}")
            csv_url = choices[0]
            raw, csv_meta = fetch(csv_url, MAX_BYTES - total_bytes)
            total_bytes += len(raw)
            parsed, observed = parse_csv(raw, site)
            item.update(parsed)
            item.update({"csv_url": csv_url, "page_bytes": len(html),
                         "csv_bytes": len(raw), "csv_response": csv_meta,
                         "page_response_url": page_meta["response_url"]})
            data_by_site[site] = observed
            print(site, "valid", item["counts"].get("valid_ratified_pm", 0),
                  "explicit_blank", item["counts"].get("explicit_blank_pm", 0),
                  "grid_rows", item["counts"].get("explicit_grid_rows", 0),
                  "schema_ok", item["schema_ok"])
        except Exception as exc:
            item["error"] = type(exc).__name__ + ": " + str(exc)
            print(site, "ERROR", item["error"])
        source["sites"].append(item)
    source["downloaded_bytes_total"] = total_bytes
    qualified = [x["site"] for x in source["sites"]
                 if x.get("schema_ok") and x.get("counts", {}).get("valid_ratified_pm", 0) >= 6000]
    source["qualified_sites_min_6000"] = qualified
    source["all_12_retrieved"] = len(data_by_site) == 12
    (ROOT / "SOURCE_MATRIX.json").write_text(json.dumps(source, ensure_ascii=False, indent=2) + "\n")

    support = {"qualified_sites": qualified, "counts_by_target": {}, "pair_count": 0,
               "unique_target_dates": 0, "neighbor_count_distribution": {},
               "natural_missing_definition": "explicit blank PM value in existing hour row",
               "target_definition": "ratified finite nonnegative PM exactly 24 GMT hours later"}
    days = set()
    neighbor_counts = Counter()
    if source["all_12_retrieved"]:
        for site in qualified:
            observed = data_by_site[site]
            counts = Counter()
            for i in range(len(GRID) - 24):
                origin = observed.get(i)
                if origin is None or origin[0] != "blank":
                    continue
                counts["explicit_blank_origin_with_future_grid"] += 1
                future = observed.get(i + 24)
                if future is None or future[0] != "valid":
                    counts["future_not_ratified_measured"] += 1
                    continue
                counts["true_future_target"] += 1
                neighbors = sum(data_by_site[other].get(i, (None, None))[0] == "valid"
                                for other in qualified if other != site)
                neighbor_counts[neighbors] += 1
                if neighbors >= 8:
                    counts["eligible_pair"] += 1
                    days.add(GRID[i].date().isoformat())
            support["counts_by_target"][site] = dict(counts)
        support["pair_count"] = sum(x.get("eligible_pair", 0)
                                    for x in support["counts_by_target"].values())
        support["unique_target_dates"] = len(days)
        support["neighbor_count_distribution"] = dict(sorted(neighbor_counts.items()))
    support["target_sites_at_least_10"] = [s for s, c in support["counts_by_target"].items()
                                           if c.get("eligible_pair", 0) >= 10]
    (ROOT / "PAIR_SUPPORT.json").write_text(json.dumps(support, ensure_ascii=False, indent=2) + "\n")
    print("downloaded_bytes_total", total_bytes)
    print("qualified_sites", len(qualified), qualified)
    print("eligible_pairs", support["pair_count"],
          "target_sites_at_least_10", len(support["target_sites_at_least_10"]),
          "unique_dates", support["unique_target_dates"])


if __name__ == "__main__":
    main()
