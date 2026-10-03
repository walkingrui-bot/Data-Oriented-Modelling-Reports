#!/usr/bin/env python3
"""EXP063 zero-shot score of the unchanged Beijing EXP060 N1 on UK-AIR 2024."""

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
P60 = HERE.parent / "STAT-PSYMOE-EXP060-20261002-001"
P62 = HERE.parent / "STAT-PSYMOE-EXP062-20261002-001"
sys.path.insert(0, str(HERE.parent / "STAT-PSYMOE-EXP061-20261002-001"))
from audit_external_source import GRID, fetch, parse_csv  # noqa: E402

MAX_BYTES = 20 * 1024 * 1024
RUN_ID = "EXP063-TEST-001"


def score(rows):
    y = np.array([r["target"] for r in rows], dtype=float)
    b0 = np.array([r["B0"] for r in rows], dtype=float)
    n1 = np.array([r["N1"] for r in rows], dtype=float)
    return {"n": len(rows), "target_mean": float(y.mean()),
            "B0": {"MAE": float(np.mean(np.abs(y - b0))),
                   "RMSE": float(np.sqrt(np.mean((y - b0) ** 2))),
                   "prediction_mean": float(b0.mean())},
            "N1": {"MAE": float(np.mean(np.abs(y - n1))),
                   "RMSE": float(np.sqrt(np.mean((y - n1) ** 2))),
                   "prediction_mean": float(n1.mean())}}


def main():
    for file in ("SOURCE_RECHECK.json", "PREDICTIONS.csv", "METRICS.json"):
        if (HERE / file).exists():
            raise FileExistsError("preserve previous direct output: " + file)
    source = json.loads((P62 / "SOURCE_MATRIX.json").read_text())
    support = json.loads((P62 / "PAIR_SUPPORT.json").read_text())
    old = json.loads((P60 / "MODEL_STATES.json").read_text())
    model = old["N1"]
    if model["train_pairs"] != 3185 or len(model["features"]) != 8:
        raise ValueError("original N1 state unexpected")
    sites = support["qualified_sites"]
    if len(sites) != 10 or len(set(sites)) != 10:
        raise ValueError("EXP062 qualified site set changed")
    originals = {x["site"]: x for x in source["sites"] if x.get("site") in sites}
    obs_by_site = {}
    recheck = {"run_id": RUN_ID, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
               "source_index": str(P62 / "SOURCE_MATRIX.json"),
               "model_state": str(P60 / "MODEL_STATES.json"),
               "sites": [], "total_bytes": 0, "source_version_match": False,
               "pair_support_match": False}
    total = 0
    for site in sites:
        src = originals[site]
        raw, response = fetch(src["csv_url"], MAX_BYTES - total)
        total += len(raw)
        parsed, observed = parse_csv(raw, site)
        match = (parsed["schema_ok"] and parsed["counts"] == src["counts"]
                 and parsed["units"] == src["units"] and parsed["statuses"] == src["statuses"])
        recheck["sites"].append({"site": site, "csv_url": src["csv_url"],
                                 "response_bytes": len(raw),
                                 "last_modified": response["last_modified"],
                                 "valid_hours": parsed["counts"].get("valid_ratified_pm", 0),
                                 "source_counts_match_EXP062": match})
        obs_by_site[site] = observed
        print("SOURCE", site, "counts_match", match, "bytes", len(raw), flush=True)
    recheck["total_bytes"] = total
    recheck["source_version_match"] = all(x["source_counts_match_EXP062"] for x in recheck["sites"])
    (HERE / "SOURCE_RECHECK.json").write_text(json.dumps(recheck, indent=2) + "\n")
    if not recheck["source_version_match"]:
        raise RuntimeError("STOP_SOURCE_VERSION_DRIFT: per-site counts/status/units differ")

    rows = []
    counts = Counter()
    for site in sites:
        obs = obs_by_site[site]
        for i in range(len(GRID) - 24):
            origin = obs.get(i)
            if origin is None or origin[0] != "blank":
                continue
            future = obs.get(i + 24)
            if future is None or future[0] != "valid":
                continue
            values = [obs_by_site[s][i][1] for s in sites if s != site
                      and obs_by_site[s].get(i, (None, None))[0] == "valid"]
            if len(values) < 8:
                continue
            p25, median, p75 = np.percentile(np.asarray(values, dtype=float), [25, 50, 75])
            t = GRID[i]
            hour = float(t.hour)
            phase = (t.timetuple().tm_yday - 1 + hour / 24) / 365.25
            features = {"log_neighbor_p25": math.log1p(p25),
                        "log_neighbor_median": math.log1p(median),
                        "log_neighbor_p75": math.log1p(p75),
                        "neighbor_count": float(len(values)),
                        "sin_hour": math.sin(2 * math.pi * hour / 24),
                        "cos_hour": math.cos(2 * math.pi * hour / 24),
                        "sin_year": math.sin(2 * math.pi * phase),
                        "cos_year": math.cos(2 * math.pi * phase)}
            x = np.array([features[f] for f in model["features"]], dtype=float)
            scaled = (x - np.asarray(model["scaler_mean"])) / np.asarray(model["scaler_scale"])
            linear = float(np.dot(np.asarray(model["coef"]), scaled) + model["intercept"])
            prediction = max(0.0, float(np.expm1(linear)))
            row = {"site": site, "origin_time_gmt_end": t.isoformat(),
                   "target_time_gmt_end": GRID[i + 24].isoformat(),
                   "origin_day_gmt": t.date().isoformat(),
                   "neighbor_count": len(values), "target": float(future[1]),
                   "B0": float(median), "N1": prediction,
                   "N1_log_prediction": linear}
            if not all(math.isfinite(row[k]) for k in ("target", "B0", "N1", "N1_log_prediction")):
                raise ValueError("nonfinite prediction row")
            rows.append(row)
            counts[site] += 1
    expected = {s: c.get("eligible_pair", 0) for s, c in support["counts_by_target"].items()}
    recheck["paired_counts"] = dict(counts)
    recheck["pair_support_match"] = (len(rows) == support["pair_count"] == 667
                                    and all(counts[s] == expected[s] for s in sites))
    (HERE / "SOURCE_RECHECK.json").write_text(json.dumps(recheck, indent=2) + "\n")
    if not recheck["pair_support_match"]:
        raise RuntimeError("STOP_SOURCE_VERSION_DRIFT: pair counts differ")

    with (HERE / "PREDICTIONS.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    overall = score(rows)
    by_site = {s: score([r for r in rows if r["site"] == s]) for s in sites}
    day_groups = defaultdict(list)
    for r in rows:
        day_groups[r["origin_day_gmt"]].append(r)
    days = sorted(day_groups)
    day_sums = np.array([sum(abs(r["target"] - r["N1"]) - abs(r["target"] - r["B0"])
                             for r in day_groups[d]) for d in days], dtype=float)
    day_counts = np.array([len(day_groups[d]) for d in days], dtype=int)
    rng = np.random.default_rng(20261002)
    indices = rng.integers(0, len(days), size=(1000, len(days)))
    boot = day_sums[indices].sum(axis=1) / day_counts[indices].sum(axis=1)
    ci = np.quantile(boot, [0.025, 0.975]).tolist()
    improvement = 1 - overall["N1"]["MAE"] / overall["B0"]["MAE"]
    station_improvement = {s: 1 - by_site[s]["N1"]["MAE"] / by_site[s]["B0"]["MAE"]
                           for s in sites}
    checks = {"overall_N1_vs_B0_MAE_improvement_at_least_5pct": improvement >= 0.05,
              "day_block_95CI_upper_below_zero": ci[1] < 0,
              "at_least_7_of_10_sites_better": sum(v > 0 for v in station_improvement.values()) >= 7,
              "no_site_worse_over_20pct": min(station_improvement.values()) >= -0.20}
    metrics = {"run_id": RUN_ID,
               "qualification": "external retrospective geography exploratory; source inspected before score",
               "model_state_ref": str(P60 / "MODEL_STATES.json"),
               "source_ref": str(P62 / "SOURCE_MATRIX.json"),
               "n": len(rows), "days": len(days),
               "overall": overall, "by_site": by_site,
               "day_block_paired": {"block": "GMT_origin_day_all_stations_together",
                                    "resamples": 1000, "seed": 20261002,
                                    "N1_minus_B0_MAE": overall["N1"]["MAE"] - overall["B0"]["MAE"],
                                    "bootstrap_95ci": ci},
               "station_relative_MAE_improvement": station_improvement,
               "gate": {"relative_MAE_improvement": improvement,
                        "conditions": checks, "pass": all(checks.values()),
                        "code": "ZERO_SHOT_N1_TRANSPORT_SUPPORT" if all(checks.values())
                        else "ZERO_SHOT_N1_TRANSPORT_NOT_SUPPORTED"}}
    (HERE / "METRICS.json").write_text(json.dumps(metrics, indent=2) + "\n")
    print("PAIR_COUNT", len(rows), "DAYS", len(days), flush=True)
    print("MAE", "B0", overall["B0"]["MAE"], "N1", overall["N1"]["MAE"], flush=True)
    print("GATE", metrics["gate"]["code"], json.dumps(checks), flush=True)


if __name__ == "__main__":
    main()
