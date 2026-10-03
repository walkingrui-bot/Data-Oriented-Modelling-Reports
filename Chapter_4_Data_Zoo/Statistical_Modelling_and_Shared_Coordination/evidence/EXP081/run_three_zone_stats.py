"""EXP081: fixed traditional-statistics comparison on real three-zone load."""

from __future__ import annotations

import csv
import io
import json
import math
import sys
import time
import urllib.request
import zipfile
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
from sklearn.ensemble import HistGradientBoostingRegressor


HERE = Path(__file__).resolve().parent
SOURCE_DIR = HERE.parent / "STAT-PSYMOE-EXP080-20261002-001"
sys.path.insert(0, str(SOURCE_DIR))
from audit_tetouan_source import URL, MEMBER, COLUMNS, ZONES  # noqa: E402

SEED = 20261002
LAG_MINUTES = (0, 10, 60, 1440)
MODES = ("OWN", "PEER", "WEATHER", "JOINT")
TIE_PRIORITY = {"PEER": 0, "WEATHER": 1, "JOINT": 2}
DATE_PATTERN = "%m/%d/%Y %H:%M"


def write_json(name: str, value: dict) -> None:
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_source() -> tuple[list[datetime], np.ndarray, dict]:
    with urllib.request.urlopen(URL, timeout=90) as response:
        archive_bytes = response.read(5_000_001)
    if len(archive_bytes) > 5_000_000:
        raise ValueError("network budget exceeded")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        members = archive.namelist()
        if MEMBER not in members:
            raise ValueError("official source member missing")
        with archive.open(MEMBER) as handle:
            raw = handle.read()
    reader = csv.reader(io.StringIO(raw.decode("utf-8-sig")))
    raw_header = next(reader)
    header = tuple(" ".join(name.split()) for name in raw_header)
    if header != COLUMNS:
        raise ValueError(f"source column semantics differ: {raw_header}")
    stamps = []
    values = []
    for row in reader:
        if len(row) != len(COLUMNS):
            raise ValueError("source row width differs")
        stamps.append(datetime.strptime(row[0].strip(), DATE_PATTERN))
        numeric = [float(raw_value.strip()) for raw_value in row[1:]]
        values.append(numeric)
    array = np.asarray(values, dtype=np.float64)
    meta = {"official_zip_url": URL, "archive_members": members,
            "download_bytes": len(archive_bytes), "source_csv_bytes": len(raw),
            "source_rows": len(stamps), "raw_header": raw_header,
            "normalized_columns": list(header),
            "first_calendar_value": stamps[0].isoformat(sep=" "),
            "last_calendar_value": stamps[-1].isoformat(sep=" "),
            "calendar_pattern": DATE_PATTERN,
            "ten_minute_steps": sum(b-a == timedelta(minutes=10) for a,b in zip(stamps,stamps[1:])),
            "all_nine_columns_finite": bool(np.all(np.isfinite(array))),
            "all_zone_power_nonnegative": bool(np.all(array[:, 5:8] >= 0))}
    return stamps, array, meta


def build_samples(stamps: list[datetime], values: np.ndarray) -> dict:
    by_stamp = {stamp: index for index, stamp in enumerate(stamps)}
    result = {"weather_extra": [], "target_values": [], "origin_values": [],
              "target_date": [], "target_part": [], "candidate_origins": defaultdict(int),
              "excluded_incomplete": defaultdict(int),
              "own": {zone: [] for zone in ZONES},
              "peer_extra": {zone: [] for zone in ZONES}}
    for origin in stamps:
        target = origin + timedelta(hours=1)
        if target.year != 2017:
            continue
        part = 0 if target.month <= 8 else 1 if target.month <= 10 else 2
        result["candidate_origins"][part] += 1
        target_index = by_stamp.get(target)
        lag_indices = [by_stamp.get(origin - timedelta(minutes=lag)) for lag in LAG_MINUTES]
        weather_index = by_stamp.get(origin - timedelta(hours=1))
        if target_index is None or any(index is None for index in lag_indices) or weather_index is None:
            result["excluded_incomplete"][part] += 1
            continue
        if not np.all(np.isfinite(values[[*lag_indices, weather_index, target_index], :])):
            result["excluded_incomplete"][part] += 1
            continue
        if np.any(values[lag_indices, 5:8] < 0) or np.any(values[target_index, 5:8] < 0):
            result["excluded_incomplete"][part] += 1
            continue
        hour = target.hour + target.minute / 60
        weekday = target.weekday()
        annual = (target.timetuple().tm_yday - 1 + hour / 24) / 365
        calendar = [math.sin(2*math.pi*hour/24), math.cos(2*math.pi*hour/24),
                    math.sin(2*math.pi*weekday/7), math.cos(2*math.pi*weekday/7),
                    math.sin(2*math.pi*annual), math.cos(2*math.pi*annual)]
        for zone_index, zone in enumerate(ZONES):
            column = 5 + zone_index
            own = [float(values[index, column]) for index in lag_indices]
            peers = [5 + other for other in range(3) if other != zone_index]
            peer = [float(values[index, col]) for col in peers for index in (lag_indices[0], lag_indices[2])]
            result["own"][zone].append(own + calendar)
            result["peer_extra"][zone].append(peer)
        result["weather_extra"].append(values[weather_index, 0:5].tolist())
        result["target_values"].append(values[target_index, 5:8].tolist())
        result["origin_values"].append(values[lag_indices[0], 5:8].tolist())
        result["target_date"].append(target.date().isoformat())
        result["target_part"].append(part)
    for key in ("weather_extra", "target_values", "origin_values"):
        result[key] = np.asarray(result[key], dtype=float)
    result["target_part"] = np.asarray(result["target_part"], dtype=int)
    for zone in ZONES:
        result["own"][zone] = np.asarray(result["own"][zone], dtype=float)
        result["peer_extra"][zone] = np.asarray(result["peer_extra"][zone], dtype=float)
    return result


def support_gate(samples: dict) -> dict:
    names = ("train_jan_aug", "validation_sep_oct", "test_nov_dec")
    parts = samples["target_part"]
    output = {}
    for code, name in enumerate(names):
        mask = parts == code
        dates = [date for date, selected in zip(samples["target_date"], mask) if selected]
        counts = defaultdict(int)
        for date in dates:
            counts[date] += 1
        output[name] = {"pairs": int(mask.sum()), "target_dates": len(counts),
                        "evaluation_dates_at_least_100_pairs": sum(count>=100 for count in counts.values()),
                        "candidate_origins": samples["candidate_origins"].get(code,0),
                        "excluded_incomplete": samples["excluded_incomplete"].get(code,0)}
    checks = {"train_at_least_33000_pairs_240_dates":
                  output[names[0]]["pairs"] >= 33000 and output[names[0]]["target_dates"] >= 240,
              "validation_at_least_8500_pairs_60_eval_dates":
                  output[names[1]]["pairs"] >= 8500 and output[names[1]]["evaluation_dates_at_least_100_pairs"] >= 60,
              "test_at_least_8400_pairs_60_eval_dates":
                  output[names[2]]["pairs"] >= 8400 and output[names[2]]["evaluation_dates_at_least_100_pairs"] >= 60}
    return {"by_target_period": output, "checks": checks,
            "decision": "THREE_ZONE_MODEL_SUPPORT_READY" if all(checks.values()) else "STOP_MULTI_ZONE_MODEL_SUPPORT"}


def daily_mae(dates: list[str], y: np.ndarray, predictions: dict[str, np.ndarray], zone: str) -> tuple[list[dict], dict]:
    groups = defaultdict(list)
    for local, date in enumerate(dates):
        groups[date].append(local)
    rows = []
    for date, indices in sorted(groups.items()):
        if len(indices) < 100:
            continue
        chosen = np.asarray(indices, dtype=int)
        row = {"target_date": date, "zone": zone, "pairs": len(chosen)}
        for mode, prediction in predictions.items():
            row[f"{mode}_mae_source_units"] = float(np.mean(np.abs(y[chosen] - prediction[chosen])))
        rows.append(row)
    return rows, {"all_dates": len(groups), "evaluation_dates": len(rows),
                  "discarded_partial_dates": {date: len(indices) for date,indices in sorted(groups.items()) if len(indices)<100}}


def write_daily(name: str, rows: list[dict]) -> None:
    if not rows:
        raise ValueError("no full evaluation date")
    fields=list(dict.fromkeys(key for row in rows for key in row))
    with (HERE/name).open("w",newline="",encoding="utf-8") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields)
        writer.writeheader();writer.writerows(rows)


def comparison(rows: list[dict], candidate: str) -> dict:
    own = np.asarray([row["OWN_mae_source_units"] for row in rows])
    added = np.asarray([row[f"{candidate}_mae_source_units"] for row in rows])
    delta = added - own
    rng = np.random.default_rng(SEED)
    picks = rng.integers(0,len(rows),size=(2000,len(rows)))
    ci = np.quantile(delta[picks].mean(axis=1), [.025,.975])
    gain = float((own.mean()-added.mean())/own.mean())
    days_better = int(np.sum(delta<0))
    gates = {"relative_mae_gain_at_least_5pct": gain>=.05,
             "paired_day_ci_upper_below_zero": float(ci[1])<0,
             "at_least_60pct_days_better": days_better>=math.ceil(.6*len(rows))}
    return {"candidate":candidate,"evaluation_days":len(rows),
            "OWN_equal_day_mae_source_units":float(own.mean()),
            "candidate_equal_day_mae_source_units":float(added.mean()),
            "candidate_minus_OWN_mae_source_units":float(delta.mean()),
            "candidate_relative_mae_gain":gain,
            "paired_day_bootstrap_difference_95pct_ci_source_units":list(map(float,ci)),
            "days_candidate_better":days_better,"gates":gates,"qualified":all(gates.values()),
            "bootstrap_resamples":2000,"bootstrap_seed":SEED}


def overall_gate(by_zone: dict) -> dict:
    qualified = [zone for zone,item in by_zone.items() if item["qualified"]]
    no_degrade = all(item["candidate_relative_mae_gain"]>=-.02 for item in by_zone.values())
    share_qualified = [zone for zone in qualified if by_zone[zone]["candidate"] in ("PEER","JOINT")]
    return {"qualified_zones":qualified,"qualified_zone_count":len(qualified),
            "all_zones_no_more_than_2pct_degradation":no_degrade,
            "qualified_zones_selecting_peer_or_joint":share_qualified,
            "passes":len(qualified)>=2 and no_degrade}


def main() -> None:
    expected=json.loads((SOURCE_DIR/"SOURCE_MATRIX.json").read_text(encoding="utf-8"))
    stamps,values,source=read_source()
    checks={"official_member_only":source["archive_members"]==[expected["archive_member"]],
            "nine_columns_match":source["normalized_columns"]==expected["normalized_columns"],
            "rows_match":source["source_rows"]==expected["source_rows"],
            "first_last_match":source["first_calendar_value"]==expected["first_calendar_value"] and source["last_calendar_value"]==expected["last_calendar_value"],
            "full_ten_minute_cadence":source["ten_minute_steps"]==source["source_rows"]-1,
            "all_columns_finite":source["all_nine_columns_finite"],
            "zones_nonnegative":source["all_zone_power_nonnegative"]}
    source.update({"checks":checks,"decision":"SOURCE_STRUCTURE_MATCH" if all(checks.values()) else "STOP_SOURCE_VERSION_DRIFT"})
    write_json("SOURCE_RECHECK.json",source)
    if not all(checks.values()):
        print(json.dumps({"source_recheck":source["decision"],"checks":checks},indent=2));return
    samples=build_samples(stamps,values)
    support=support_gate(samples)
    write_json("MODEL_SUPPORT.json",support)
    if support["decision"]!="THREE_ZONE_MODEL_SUPPORT_READY":
        print(json.dumps({"model_support":support},indent=2));return
    parts=samples["target_part"]
    train,validation,test=parts==0,parts==1,parts==2
    all_val_daily=[]
    by_zone={}
    fitted={}
    fit_seconds={}
    dims={}
    for zone_index,zone in enumerate(ZONES):
        own=samples["own"][zone]
        peer=samples["peer_extra"][zone]
        weather=samples["weather_extra"]
        features={"OWN":own,"PEER":np.hstack((own,peer)),
                  "WEATHER":np.hstack((own,weather)),
                  "JOINT":np.hstack((own,peer,weather))}
        dims[zone]={mode:x.shape[1] for mode,x in features.items()}
        fitted[zone]={}
        fit_seconds[zone]={}
        pred={}
        target=samples["target_values"][:,zone_index]
        for mode in MODES:
            model=HistGradientBoostingRegressor(loss="absolute_error",max_iter=200,
                   max_leaf_nodes=15,min_samples_leaf=50,learning_rate=.05,
                   l2_regularization=10,early_stopping=False,random_state=SEED)
            started=time.perf_counter()
            model.fit(features[mode][train],target[train])
            fit_seconds[zone][mode]=time.perf_counter()-started
            fitted[zone][mode]=model
            pred[mode]=np.maximum(0,model.predict(features[mode][validation]))
        pred["PERSIST"]=samples["origin_values"][validation,zone_index]
        val_dates=[date for date,selected in zip(samples["target_date"],validation) if selected]
        rows,day_support=daily_mae(val_dates,target[validation],pred,zone)
        all_val_daily.extend(rows)
        means={mode:float(np.mean([row[f"{mode}_mae_source_units"] for row in rows])) for mode in (*MODES,"PERSIST")}
        selected=min(("PEER","WEATHER","JOINT"),key=lambda mode:(means[mode],TIE_PRIORITY[mode]))
        metric=comparison(rows,selected)
        metric.update({"equal_day_mae_source_units_by_model":means,"day_support":day_support})
        by_zone[zone]=metric
    write_daily("VALIDATION_DAILY_ERRORS.csv",all_val_daily)
    summary=overall_gate(by_zone)
    summary["decision"]="PASS_ADDITIONAL_ZONE_CHANNEL_DEV_GATE" if summary["passes"] else "STOP_ADDITIONAL_ZONE_CHANNEL_DEV_GATE"
    val_metrics={"by_zone":by_zone,"overall":summary,
                 "model_sample_counts":{"train":int(train.sum()),"validation":int(validation.sum()),"test":int(test.sum())},
                 "feature_dimensions_by_zone":dims,"fit_seconds_by_zone":fit_seconds,
                 "model_definition":"fixed HistGradientBoostingRegressor absolute_error, 200 iterations, leaves15, min_leaf50, lr0.05, L2=10, no early stopping",
                 "source_recheck":source["decision"],"model_support":support["decision"],
                 "test_performance_scored":False}
    write_json("VALIDATION_METRICS.json",val_metrics)
    print(json.dumps({"validation":{"by_zone":{zone:{key:item[key] for key in (
          "candidate","OWN_equal_day_mae_source_units","candidate_equal_day_mae_source_units",
          "candidate_relative_mae_gain","paired_day_bootstrap_difference_95pct_ci_source_units",
          "days_candidate_better","evaluation_days","gates","qualified")}
          for zone,item in by_zone.items()},"overall":summary}},ensure_ascii=False,indent=2))
    if not summary["passes"]:
        return
    test_daily=[]
    test_by_zone={}
    for zone_index,zone in enumerate(ZONES):
        own=samples["own"][zone]
        peer=samples["peer_extra"][zone]
        weather=samples["weather_extra"]
        selected=by_zone[zone]["candidate"]
        features={"OWN":own,"PEER":np.hstack((own,peer)),
                  "WEATHER":np.hstack((own,weather)),
                  "JOINT":np.hstack((own,peer,weather))}
        pred={"OWN":np.maximum(0,fitted[zone]["OWN"].predict(features["OWN"][test])),
              selected:np.maximum(0,fitted[zone][selected].predict(features[selected][test])),
              "PERSIST":samples["origin_values"][test,zone_index]}
        dates=[date for date,selected_row in zip(samples["target_date"],test) if selected_row]
        rows,day_support=daily_mae(dates,samples["target_values"][test,zone_index],pred,zone)
        test_daily.extend(rows)
        metric=comparison(rows,selected)
        metric.update({"equal_day_mae_source_units_by_model":{
            mode:float(np.mean([row[f"{mode}_mae_source_units"] for row in rows])) for mode in pred},
            "day_support":day_support})
        test_by_zone[zone]=metric
    write_daily("TEST_DAILY_ERRORS.csv",test_daily)
    test_summary=overall_gate(test_by_zone)
    test_summary["decision"]=("ADDITIONAL_INFORMATION_HOLDOUT_GAIN_WITHIN_ONE_CITY" if test_summary["passes"]
                              else "NO_LATER_MONTH_CHANNEL_GAIN")
    test_metrics={"by_zone":test_by_zone,"overall":test_summary,
                  "development_gate":summary["decision"],"test_performance_scored":True}
    write_json("TEST_METRICS.json",test_metrics)
    print(json.dumps({"test":{"by_zone":{zone:{key:item[key] for key in (
          "candidate","OWN_equal_day_mae_source_units","candidate_equal_day_mae_source_units",
          "candidate_relative_mae_gain","paired_day_bootstrap_difference_95pct_ci_source_units",
          "days_candidate_better","evaluation_days","gates","qualified")}
          for zone,item in test_by_zone.items()},"overall":test_summary}},ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
