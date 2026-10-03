"""EXP033-VERIFY-002: saved-state and independent-score audit without refit."""

import csv
import json
import math
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent / "STAT-PSYMOE-EXP031-20261002-001"
OUT = ROOT / "LOCAL_VALIDATION.json"


def rows_of(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def score(rows, key):
    losses = []
    recalls = []
    cm = []
    for label in (0, 1):
        subset = [r for r in rows if int(r["label"]) == label]
        ps = [float(r[key]) for r in subset]
        losses.append(sum(-math.log(p if label else 1-p) for p in ps)/len(ps))
        pred = [int(p >= .5) for p in ps]
        recalls.append(sum(p == label for p in pred)/len(pred))
        cm.append([sum(p == k for p in pred) for k in (0, 1)])
    return {"macro_log_loss": sum(losses)/2, "balanced_accuracy": sum(recalls)/2,
            "confusion_rows_true_HC_PD": cm}


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    state = json.loads((ROOT / "MODEL_STATE.json").read_text())
    opt = json.loads((ROOT / "OPTIMIZATION.json").read_text())
    metrics = json.loads((ROOT / "METRICS.json").read_text())
    rows = rows_of(ROOT / "PREDICTIONS.csv")
    audit = {r["subject_id"]: r for r in rows_of(PARENT / "SOURCE_AUDIT.csv") if r["study"] == "Ga"}
    features = {r["subject_id"]: r for r in rows_of(PARENT / "FORCE_FEATURES.csv") if r["study"] == "Ga"}
    checks = {}
    checks["holdout_keys_and_source_qualified"] = (len(rows) == len(audit) == len(features) == 47
        and len({r["subject_id"] for r in rows}) == 47
        and {r["subject_id"] for r in rows} == set(audit) == set(features)
        and all(r["status"] == "READABLE_NUMERIC" for r in audit.values()))
    checks["one_converged_fit"] = opt["fit"]["converged"] and metrics["train_n"] == 64 and metrics["holdout_n"] == 47
    names = state["feature_names"]
    med = np.array(state["preprocessing"]["median"])
    mean = np.array(state["preprocessing"]["mean"])
    std = np.array(state["preprocessing"]["std"])
    weights = np.array(state["weights"])
    checks["saved_state_shape"] = len(names) == len(med) == 12 and len(weights) == len(mean) == len(std) == 24
    checks["prediction_reconstruction"] = True
    for row in rows:
        sid = row["subject_id"]
        x = np.array([float(features[sid][name]) for name in names])
        aug = np.concatenate((np.where(np.isnan(x), med, x), np.isnan(x).astype(float)))
        z = float(((aug-mean)/std) @ weights + state["intercept"])
        p = 1/(1+math.exp(-max(-40, min(40, z))))
        if abs(p-float(row["p_PD_model"])) > 1e-12 or abs(float(row["p_PD_si_prior"])-state["train_pd_prior"]) > 1e-12:
            checks["prediction_reconstruction"] = False
    fitted = score(rows, "p_PD_model")
    prior = score(rows, "p_PD_si_prior")
    checks["independent_metric_recompute"] = all(
        abs(fitted[key]-metrics["model"][key]) < 1e-12 and abs(prior[key]-metrics["prior"][key]) < 1e-12
        for key in ("macro_log_loss", "balanced_accuracy")) and fitted["confusion_rows_true_HC_PD"] == metrics["model"]["confusion_rows_true_HC_PD"]
    gain = prior["macro_log_loss"]-fitted["macro_log_loss"]
    checks["frozen_gate_recompute"] = (abs(gain-metrics["macro_log_loss_improvement"]) < 1e-12
        and metrics["gate_pass"] == (fitted["balanced_accuracy"] >= .55 and gain >= .02))
    result = {"run_id": "EXP033-VERIFY-002", "scope": "saved state and Ga predictions only; no fit or source reread",
              "checks": checks, "pass": all(checks.values())}
    OUT.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(result, indent=2))
    if not result["pass"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
