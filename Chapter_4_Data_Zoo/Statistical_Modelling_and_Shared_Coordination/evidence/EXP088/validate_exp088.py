"""Local independent recomputation of EXP088 event-level validation and stop."""

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


here = Path(__file__).resolve().parent
with (here / "EVENT_FEATURES.csv").open(newline="") as handle:
    events = list(csv.DictReader(handle))
with (here / "VALIDATION_PREDICTIONS.csv").open(newline="") as handle:
    predictions = list(csv.DictReader(handle))
source = json.loads((here / "SOURCE_RECHECK.json").read_text())
support = json.loads((here / "MODEL_SUPPORT.json").read_text())
selection = json.loads((here / "TRAIN_CV_SELECTION.json").read_text())
metrics = json.loads((here / "VALIDATION_METRICS.json").read_text())
day = defaultdict(lambda: [[], []])
level = defaultdict(lambda: [[], []])
for row in predictions:
    y = float(row["co_ppm"])
    b = abs(float(row["base_pred_ppm"]) - y)
    m = abs(float(row["multi_pred_ppm"]) - y)
    day[row["date"]][0].append(b)
    day[row["date"]][1].append(m)
    level[row["concentration_level_0_1ppm"]][0].append(b)
    level[row["concentration_level_0_1ppm"]][1].append(m)
base = np.mean([np.mean(v[0]) for v in day.values()])
multi = np.mean([np.mean(v[1]) for v in day.values()])
gain = (base - multi) / base * 100
improved_days = sum(np.mean(v[1]) < np.mean(v[0]) for v in day.values())
improved_levels = sum(np.mean(v[1]) < np.mean(v[0]) for v in level.values())
checks = {
    "source_recheck_all_pass": source["gate_result"] == "SOURCE_EPISODES_MATCH" and all(source["checks"].values()),
    "event_support_all_pass": support["gate_result"] == "MODEL_SUPPORT_PASS" and all(support["checks"].values()),
    "1300_event_keys_unique": len(events) == len({(row["date"], row["window_index"]) for row in events}) == 1300,
    "split_counts_700_300_300": Counter(row["split"] for row in events) == {"train": 700, "validation": 300, "later_day": 300},
    "train_cv_choice_is_best": selection["selected_comparator"] == min(selection["candidate_day_equal_mae"],
                                                                   key=selection["candidate_day_equal_mae"].get),
    "validation_300_event_predictions": len(predictions) == 300 and len({(row["date"], row["window_index"]) for row in predictions}) == 300,
    "validation_only_three_dates": len(day) == 3 and set(day) == {row["date"] for row in events if row["split"] == "validation"},
    "day_equal_base_recomputed": np.isclose(base, metrics["base_day_equal_mae_ppm"]),
    "day_equal_multi_recomputed": np.isclose(multi, metrics["multi_day_equal_mae_ppm"]),
    "relative_gain_recomputed": np.isclose(gain, metrics["relative_multi_gain_pct"]),
    "days_and_levels_recomputed": improved_days == metrics["improved_days"] == 2 and improved_levels == metrics["improved_levels"] == 9,
    "frozen_dev_gate_failed": metrics["checks"] == {"gain_at_least_5pct": True,
                                                    "all_three_days_improve": False,
                                                    "at_least_seven_of_ten_levels_improve": True} and not metrics["three_gate_pass"],
    "later_day_unscored": not (here / "LATER_DAY_METRICS.json").exists() and not (here / "LATER_DAY_PREDICTIONS.csv").exists(),
}
result = {"checks": {key: bool(value) for key, value in checks.items()},
          "passed": sum(bool(value) for value in checks.values()), "total": len(checks),
          "local_validation": "PASS" if all(checks.values()) else "FAIL"}
(here / "LOCAL_VALIDATION.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
if not all(checks.values()):
    raise SystemExit(1)
