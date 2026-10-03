"""EXP033-MODEL-001: one predeclared Si-to-Ga source holdout."""

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent / "STAT-PSYMOE-EXP031-20261002-001"
MODEL_SOURCE = PARENT / "derived" / "fit_source_holdouts.py"
STATE = ROOT / "MODEL_STATE.json"
OPT = ROOT / "OPTIMIZATION.json"
PRED = ROOT / "PREDICTIONS.csv"
METRICS = ROOT / "METRICS.json"


def reuse_model():
    spec = importlib.util.spec_from_file_location("exp031_fixed_statistics", MODEL_SOURCE)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    return model


def read_rows(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    if any(path.exists() for path in (STATE, OPT, PRED, METRICS)):
        raise FileExistsError("Preserve EXP033-MODEL-001 outputs")
    model = reuse_model()
    audit = read_rows(PARENT / "SOURCE_AUDIT.csv")
    features = read_rows(PARENT / "FORCE_FEATURES.csv")
    relevant_audit = {r["subject_id"]: r for r in audit if r["study"] in ("Si", "Ga")}
    relevant_features = sorted((r for r in features if r["study"] in ("Si", "Ga")), key=lambda r: r["subject_id"])
    if len(relevant_audit) != 111 or len(relevant_features) != 111 or len({r["subject_id"] for r in relevant_features}) != 111:
        raise ValueError("STOP_INPUT: key cardinality")
    if set(relevant_audit) != {r["subject_id"] for r in relevant_features}:
        raise ValueError("STOP_INPUT: audit alignment")
    if any(r["status"] != "READABLE_NUMERIC" for r in relevant_audit.values()):
        raise ValueError("STOP_INPUT: source eligibility")
    if set(relevant_features[0]) != {"subject_id", "study", "label"} | set(model.NAMES):
        raise ValueError("STOP_INPUT: predictor allowlist")
    ids = np.array([r["subject_id"] for r in relevant_features])
    study = np.array([r["study"] for r in relevant_features])
    y = np.array([int(r["label"]) for r in relevant_features], dtype=np.int64)
    X = np.array([[float(r[name]) for name in model.NAMES] for r in relevant_features], dtype=float)
    train = study == "Si"
    test = study == "Ga"
    if not np.isfinite(X).all() or np.bincount(y[train], minlength=2).tolist() != [29, 35] or np.bincount(y[test], minlength=2).tolist() != [18, 29]:
        raise ValueError("STOP_INPUT: values or groups")
    prep = model.preprocess_fit(X[train])
    Xt = model.preprocess_apply(X[train], prep)
    Xg = model.preprocess_apply(X[test], prep)
    theta, info = model.fit(Xt, y[train], lam=.1)
    OPT.write_text(json.dumps({"run_id": "EXP033-MODEL-001", "fit": info}, indent=2)+"\n")
    if not info["converged"]:
        raise RuntimeError("STOP_ENGINEERING: Si model did not converge")
    probs = model.sigmoid(Xg @ theta[:-1] + theta[-1])
    prior = float(y[train].mean())
    baseline = model.score(y[test], np.full(int(test.sum()), prior))
    fitted = model.score(y[test], probs)
    improvement = float(baseline["macro_log_loss"]-fitted["macro_log_loss"])
    gate = bool(fitted["balanced_accuracy"] >= .55 and improvement >= .02)
    state = {"run_id": "EXP033-MODEL-001", "training_study": "Si", "model_source": str(MODEL_SOURCE),
             "feature_names": model.NAMES, "lambda": .1, "train_pd_prior": prior,
             "preprocessing": {"median": prep[0].tolist(), "mean": prep[1].tolist(), "std": prep[2].tolist()},
             "weights": theta[:-1].tolist(), "intercept": float(theta[-1])}
    metrics = {"run_id": "EXP033-MODEL-001", "train_study": "Si", "holdout_study": "Ga",
               "train_n": int(train.sum()), "holdout_n": int(test.sum()),
               "train_counts_HC_PD": np.bincount(y[train], minlength=2).tolist(),
               "holdout_counts_HC_PD": np.bincount(y[test], minlength=2).tolist(),
               "prior": baseline, "model": fitted, "macro_log_loss_improvement": improvement,
               "gate_pass": gate,
               "independence_note": "Different original studies; cross-study individual overlap not verified"}
    pred_rows = [{"subject_id": str(sid), "study": "Ga", "label": int(label),
                  "p_PD_model": float(prob), "p_PD_si_prior": prior}
                 for sid, label, prob in zip(ids[test], y[test], probs)]
    with PRED.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pred_rows[0]))
        writer.writeheader()
        writer.writerows(pred_rows)
    STATE.write_text(json.dumps(state, indent=2)+"\n")
    METRICS.write_text(json.dumps(metrics, indent=2)+"\n")
    print(json.dumps({"prior_loss": baseline["macro_log_loss"], "model_loss": fitted["macro_log_loss"],
                      "loss_improvement": improvement, "model_bacc": fitted["balanced_accuracy"],
                      "gate_pass": gate, "confusion": fitted["confusion_rows_true_HC_PD"]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
