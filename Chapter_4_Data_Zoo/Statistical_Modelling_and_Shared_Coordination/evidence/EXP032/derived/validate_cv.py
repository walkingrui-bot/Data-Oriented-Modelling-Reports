"""EXP032-VERIFY-001: independent arithmetic audit of saved OOF outputs."""

import csv
import json
import math
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "LOCAL_VALIDATION.json"


def read_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def scored(rows, probability_key):
    by_class = {}
    for label in (0, 1):
        subset = [row for row in rows if int(row["label"]) == label]
        losses = []
        correct = 0
        for row in subset:
            p = float(row[probability_key])
            losses.append(-math.log(p if label == 1 else 1-p))
            correct += int((p >= .5) == bool(label))
        by_class[label] = {"loss": sum(losses)/len(losses), "recall": correct/len(subset)}
    return {"macro_log_loss": (by_class[0]["loss"]+by_class[1]["loss"])/2,
            "balanced_accuracy": (by_class[0]["recall"]+by_class[1]["recall"])/2}


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    splits = json.loads((ROOT / "SPLITS.json").read_text())["repetitions"]
    optimization = json.loads((ROOT / "OPTIMIZATION.json").read_text())
    metrics = json.loads((ROOT / "METRICS.json").read_text())
    preds = read_rows(ROOT / "PREDICTIONS.csv")
    source = ROOT.parent / "STAT-PSYMOE-EXP031-20261002-001"
    raw_audit = read_rows(source / "SOURCE_AUDIT.csv")
    si = {row["subject_id"]: row for row in raw_audit if row["study"] == "Si"}
    checks = {}
    checks["input_source_qualified"] = len(si) == 64 and all(row["status"] == "READABLE_NUMERIC" for row in si.values())
    checks["prediction_cardinality"] = len(preds) == 320 and len({(row["seed"], row["subject_id"]) for row in preds}) == 320
    checks["optimization_25_converged"] = len(optimization["fits"]) == 25 and all(row["converged"] for row in optimization["fits"].values())
    checks["split_assignment_and_prior"] = True
    checks["independent_metric_recompute"] = True
    qualifying = 0
    for seed, split in splits.items():
        rows = [row for row in preds if row["seed"] == seed]
        if len(rows) != 64 or set(split) != set(si) or set(row["subject_id"] for row in rows) != set(si):
            checks["split_assignment_and_prior"] = False
            continue
        labels = {row["subject_id"]: int(row["label"]) for row in rows}
        if Counter(labels.values()) != Counter({0:29,1:35}):
            checks["split_assignment_and_prior"] = False
        for fold in range(5):
            test = [row for row in rows if int(row["fold"]) == fold]
            train_ids = [sid for sid, k in split.items() if k != fold]
            prior = sum(labels[sid] for sid in train_ids)/len(train_ids)
            if not test or not all(split[row["subject_id"]] == fold and
                abs(float(row["p_PD_train_prior"])-prior) < 1e-12 and
                0 < float(row["p_PD_model"]) < 1 for row in test):
                checks["split_assignment_and_prior"] = False
        model = scored(rows, "p_PD_model")
        baseline = scored(rows, "p_PD_train_prior")
        reported = metrics["repetitions"][seed]
        improvement = baseline["macro_log_loss"]-model["macro_log_loss"]
        gate = model["balanced_accuracy"] >= .55 and improvement >= .02
        qualifying += int(gate)
        for key in ("macro_log_loss", "balanced_accuracy"):
            if abs(model[key]-reported["model"][key]) > 1e-12 or abs(baseline[key]-reported["train_prior"][key]) > 1e-12:
                checks["independent_metric_recompute"] = False
        if abs(improvement-reported["macro_log_loss_improvement"]) > 1e-12 or gate != reported["frozen_repetition_gate"]:
            checks["independent_metric_recompute"] = False
    checks["frozen_gate_recompute"] = qualifying == metrics["qualifying_repetitions"] == 4 and metrics["gate_pass"] == (qualifying >= 4)
    output = {"run_id": "EXP032-VERIFY-001", "scope": "saved Si source audit and saved model outputs only; no refit or source reread",
              "checks": checks, "pass": all(checks.values()), "qualifying_repetitions": qualifying}
    OUT.write_text(json.dumps(output, indent=2)+"\n")
    print(json.dumps(output, indent=2))
    if not output["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
