#!/usr/bin/env python3
"""EXP067: retrospective, prediction-time known outage age versus B0 error."""

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P62 = HERE.parent / "STAT-PSYMOE-EXP062-20261002-001"
P63 = HERE.parent / "STAT-PSYMOE-EXP063-20261002-001"
P64 = HERE.parent / "STAT-PSYMOE-EXP064-20261002-001"
P65 = HERE.parent / "STAT-PSYMOE-EXP065-20261002-001"
sys.path.insert(0, str(HERE.parent / "STAT-PSYMOE-EXP061-20261002-001"))
import audit_external_source as audit  # noqa: E402

SITES = "BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR".split()
GRIDS = {
    2024: [datetime(2024, 1, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(8784)],
    2025: [datetime(2025, 1, 1, 1, tzinfo=timezone.utc) + timedelta(hours=i) for i in range(8760)],
}
MAX_BYTES = 50 * 1024 * 1024


def ages(observed, length):
    answer = {}
    age = 0
    censored = False
    for i in range(length):
        current = observed.get(i)
        if current is None or current[0] != "blank":
            age = 0
            censored = current is None
            continue
        if i == 0 or observed.get(i - 1) is None:
            age = 1
            censored = True
        elif observed[i - 1][0] == "blank":
            age += 1
        else:
            age = 1
            censored = False
        answer[i] = (age, censored)
    return answer


def group(age, censored):
    if censored:
        return "LEFT_CENSORED_OR_UNKNOWN_START"
    if age <= 2:
        return "SHORT_1_2"
    if age >= 6:
        return "LONG_6_PLUS"
    return "MIDDLE_3_5"


def describe(rows):
    return {"n": len(rows), "stations": sorted({r["site"] for r in rows}),
            "station_count": len({r["site"] for r in rows}),
            "days": len({r["day"] for r in rows}),
            "B0_MAE": sum(r["B0_abs_error"] for r in rows) / len(rows) if rows else None,
            "target_mean": sum(r["target"] for r in rows) / len(rows) if rows else None}


def bootstrap_long_short(rows):
    days = sorted({r["day"] for r in rows})
    day_rows = defaultdict(list)
    for r in rows:
        day_rows[r["day"]].append(r)
    short_sum = np.array([sum(x["B0_abs_error"] for x in day_rows[d] if x["group"] == "SHORT_1_2") for d in days])
    short_n = np.array([sum(x["group"] == "SHORT_1_2" for x in day_rows[d]) for d in days])
    long_sum = np.array([sum(x["B0_abs_error"] for x in day_rows[d] if x["group"] == "LONG_6_PLUS") for d in days])
    long_n = np.array([sum(x["group"] == "LONG_6_PLUS" for x in day_rows[d]) for d in days])
    rng = np.random.default_rng(20261002)
    index = rng.integers(0, len(days), size=(1000, len(days)))
    sn, ln = short_n[index].sum(axis=1), long_n[index].sum(axis=1)
    valid = (sn > 0) & (ln > 0)
    if not valid.all():
        return {"block": "GMT_origin_day_all_stations_together", "resamples": 1000,
                "valid_resamples": int(valid.sum()), "seed": 20261002,
                "bootstrap_95ci": None, "reason": "zero group in at least one resample"}
    diff = long_sum[index].sum(axis=1) / ln - short_sum[index].sum(axis=1) / sn
    return {"block": "GMT_origin_day_all_stations_together", "resamples": 1000,
            "valid_resamples": 1000, "seed": 20261002,
            "bootstrap_95ci": np.quantile(diff, [.025, .975]).tolist()}


def main():
    for name in ("SOURCE_RECHECK.json", "RISK_ROWS.csv", "METRICS.json"):
        if (HERE / name).exists():
            raise FileExistsError("preserve prior attempt output: " + name)
    sources = {
        2024: json.loads((P62 / "SOURCE_MATRIX.json").read_text()),
        2025: json.loads((P64 / "SOURCE_MATRIX.json").read_text()),
    }
    pred_files = {2024: P63 / "PREDICTIONS.csv", 2025: P65 / "PREDICTIONS.csv"}
    expected_n = {2024: 667, 2025: 589}
    recheck = {"run_id": "EXP067-RISK-001",
               "checked_at_utc": datetime.now(timezone.utc).isoformat(),
               "per_year_site": {}, "per_year_prediction_match": {}, "total_bytes": 0}
    rows = []
    total = 0
    for year in (2024, 2025):
        grid = GRIDS[year]
        index = {t: i for i, t in enumerate(grid)}
        audit.GRID = grid
        audit.TIME_TO_INDEX = index
        source = {x["site"]: x for x in sources[year]["sites"] if x.get("site") in SITES}
        obs = {}
        checks = {}
        for site in SITES:
            expected = source[site]
            data, _ = audit.fetch(expected["csv_url"], MAX_BYTES - total)
            total += len(data)
            parsed, observed = audit.parse_csv(data, site)
            checks[site] = (parsed["schema_ok"] and parsed["counts"] == expected["counts"]
                            and parsed["units"] == expected["units"]
                            and parsed["statuses"] == expected["statuses"])
            obs[site] = observed
            print("SOURCE", year, site, "match", checks[site], flush=True)
        recheck["per_year_site"][str(year)] = checks
        if not all(checks.values()):
            recheck["total_bytes"] = total
            (HERE / "SOURCE_RECHECK.json").write_text(json.dumps(recheck, indent=2) + "\n")
            raise RuntimeError("STOP_SOURCE_VERSION_DRIFT")
        age_by_site = {site: ages(obs[site], len(grid)) for site in SITES}
        source_predictions = list(csv.DictReader(pred_files[year].open()))
        okay = len(source_predictions) == expected_n[year]
        for r in source_predictions:
            site = r["site"]
            when = datetime.fromisoformat(r["origin_time_gmt_end"])
            i = index[when]
            target_when = datetime.fromisoformat(r["target_time_gmt_end"])
            if site not in SITES or target_when != when + timedelta(hours=24):
                okay = False
                continue
            if obs[site].get(i, (None, None))[0] != "blank" or obs[site].get(i + 24, (None, None))[0] != "valid":
                okay = False
                continue
            if not math.isclose(float(r["target"]), obs[site][i + 24][1], rel_tol=0, abs_tol=1e-10):
                okay = False
            age, censored = age_by_site[site][i]
            rows.append({"year": year, "site": site, "origin_time_gmt_end": when.isoformat(),
                         "day": when.date().isoformat(), "outage_age_hours": age,
                         "group": group(age, censored), "target": float(r["target"]),
                         "B0_abs_error": abs(float(r["target"]) - float(r["B0"]))})
        recheck["per_year_prediction_match"][str(year)] = okay
        print("PREDICTIONS", year, len(source_predictions), "match", okay, flush=True)
    recheck["total_bytes"] = total
    (HERE / "SOURCE_RECHECK.json").write_text(json.dumps(recheck, indent=2) + "\n")
    if not all(recheck["per_year_prediction_match"].values()):
        raise RuntimeError("STOP_SOURCE_VERSION_DRIFT: predictions no longer match source")

    with (HERE / "RISK_ROWS.csv").open("w", newline="") as handle:
        names = ["year", "site", "origin_time_gmt_end", "day", "outage_age_hours",
                 "group", "B0_abs_error"]
        writer = csv.DictWriter(handle, fieldnames=names)
        writer.writeheader()
        writer.writerows({k: r[k] for k in names} for r in rows)
    per_year = {}
    for year in (2024, 2025):
        year_rows = [r for r in rows if r["year"] == year]
        groups = {g: describe([r for r in year_rows if r["group"] == g])
                  for g in ("SHORT_1_2", "MIDDLE_3_5", "LONG_6_PLUS",
                            "LEFT_CENSORED_OR_UNKNOWN_START")}
        short, long = groups["SHORT_1_2"], groups["LONG_6_PLUS"]
        support_conditions = {g: groups[g]["n"] >= 30 and groups[g]["station_count"] >= 3
                              and groups[g]["days"] >= 20 for g in ("SHORT_1_2", "LONG_6_PLUS")}
        support_ok = all(support_conditions.values())
        ratio = long["B0_MAE"] / short["B0_MAE"] if short["B0_MAE"] and long["B0_MAE"] else None
        bootstrap = bootstrap_long_short([r for r in year_rows if r["group"] in ("SHORT_1_2", "LONG_6_PLUS")]) if support_ok else None
        risk_conditions = {"long_short_MAE_ratio_at_least_1_5": ratio is not None and ratio >= 1.5,
                           "day_block_CI_lower_above_zero": bootstrap is not None and
                           bootstrap["bootstrap_95ci"] is not None and bootstrap["bootstrap_95ci"][0] > 0}
        per_year[str(year)] = {"all_pairs": len(year_rows), "groups": groups,
                               "support_conditions": support_conditions,
                               "support_pass": support_ok,
                               "long_short_MAE_ratio": ratio,
                               "long_minus_short_day_block": bootstrap,
                               "risk_conditions": risk_conditions,
                               "risk_pass": support_ok and all(risk_conditions.values())}
    support_both = all(per_year[str(y)]["support_pass"] for y in (2024, 2025))
    risk_both = support_both and all(per_year[str(y)]["risk_pass"] for y in (2024, 2025))
    if not support_both:
        code = "STOP_OUTAGE_AGE_SUPPORT"
    elif risk_both:
        code = "LONG_OUTAGE_B0_RISK_REPEATS_EXPLORATORY"
    else:
        code = "NO_REPEATED_LONG_OUTAGE_RISK"
    metrics = {"run_id": "EXP067-RISK-001", "qualification": "retrospective; 2024/2025 B0 scores exposed earlier",
               "per_year": per_year, "support_both_years": support_both,
               "risk_both_years": risk_both, "gate_code": code}
    (HERE / "METRICS.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print("TOTAL_BYTES", total, flush=True)
    for year in (2024, 2025):
        m = per_year[str(year)]
        print(year, "SHORT", m["groups"]["SHORT_1_2"]["n"], m["groups"]["SHORT_1_2"]["B0_MAE"],
              "LONG", m["groups"]["LONG_6_PLUS"]["n"], m["groups"]["LONG_6_PLUS"]["B0_MAE"],
              "SUPPORT", m["support_pass"], "RISK", m["risk_pass"], flush=True)
    print("GATE", code, flush=True)


if __name__ == "__main__":
    main()
