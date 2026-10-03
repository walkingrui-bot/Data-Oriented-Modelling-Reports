"""EXP032-MODEL-001: frozen five-repeat person-fold development comparison."""

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT.parent / "STAT-PSYMOE-EXP031-20261002-001"
MODEL_SOURCE = PARENT / "derived" / "fit_source_holdouts.py"
SPLITS = ROOT / "SPLITS.json"
OPT = ROOT / "OPTIMIZATION.json"
PRED = ROOT / "PREDICTIONS.csv"
METRICS = ROOT / "METRICS.json"
SEEDS = list(range(202610020, 202610025))


def reuse_parent_model():
    spec = importlib.util.spec_from_file_location("exp031_fixed_statistics", MODEL_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rows_of(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def main():
    if any(path.exists() for path in (SPLITS, OPT, PRED, METRICS)):
        raise FileExistsError("Preserve EXP032-MODEL-001 outputs")
    model = reuse_parent_model()
    source = json.loads((PARENT / "SOURCE_SUMMARY.json").read_text())
    audit = rows_of(PARENT / "SOURCE_AUDIT.csv")
    features = rows_of(PARENT / "FORCE_FEATURES.csv")
    s_audit = {row["subject_id"]: row for row in audit if row["study"] == "Si"}
    s_features = sorted((row for row in features if row["study"] == "Si"), key=lambda row: row["subject_id"])
    if len(s_audit) != 64 or len(s_features) != 64 or len({row["subject_id"] for row in s_features}) != 64:
        raise ValueError("STOP_INPUT: Si person support")
    if set(s_audit) != {row["subject_id"] for row in s_features}:
        raise ValueError("STOP_INPUT: Si audit alignment")
    if not all(row["status"] == "READABLE_NUMERIC" for row in s_audit.values()):
        raise ValueError("STOP_INPUT: Si numerical source")
    if source["numeric_by_study_group"]["Si_PD"] != 35 or source["numeric_by_study_group"]["Si_HC"] != 29:
        raise ValueError("STOP_INPUT: Si group support")
    if set(s_features[0]) != {"subject_id", "study", "label"} | set(model.NAMES):
        raise ValueError("STOP_INPUT: feature allowlist")
    ids = np.array([row["subject_id"] for row in s_features])
    y = np.array([int(row["label"]) for row in s_features], dtype=np.int64)
    X = np.array([[float(row[name]) for name in model.NAMES] for row in s_features], dtype=float)
    if not np.isfinite(X).all() or np.bincount(y, minlength=2).tolist() != [29, 35]:
        raise ValueError("STOP_INPUT: feature values or classes")

    all_splits = {}
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        fold = np.full(len(y), -1, dtype=int)
        for klass in (0, 1):
            indices = np.flatnonzero(y == klass)
            rng.shuffle(indices)
            for pos, index in enumerate(indices):
                fold[index] = pos % 5
        if np.any(fold < 0) or any(np.bincount(y[fold == k], minlength=2).min() < 1 for k in range(5)):
            raise ValueError("STOP_INPUT: stratification")
        all_splits[str(seed)] = {str(sid): int(k) for sid, k in zip(ids, fold)}
    SPLITS.write_text(json.dumps({"run_id": "EXP032-MODEL-001", "unit": "Si study subject",
                                  "repetitions": all_splits}, indent=2) + "\n")

    optimization = {"run_id": "EXP032-MODEL-001", "parent_model_source": str(MODEL_SOURCE),
                    "lambda": 0.1, "fits": {}}
    metrics = {"run_id": "EXP032-MODEL-001", "independence_note": "Five partitions of the same 64 Si people; development only",
               "repetitions": {}, "gate_pass": False}
    prediction_rows = []
    for seed in SEEDS:
        fold = np.array([all_splits[str(seed)][str(sid)] for sid in ids])
        p_model = np.full(len(y), np.nan)
        p_prior = np.full(len(y), np.nan)
        for k in range(5):
            train = fold != k
            test = fold == k
            state = model.preprocess_fit(X[train])
            Xt = model.preprocess_apply(X[train], state)
            Xtest = model.preprocess_apply(X[test], state)
            theta, info = model.fit(Xt, y[train], lam=0.1)
            optimization["fits"][f"{seed}_fold{k}"] = info
            if not info["converged"]:
                OPT.write_text(json.dumps(optimization, indent=2) + "\n")
                raise RuntimeError(f"STOP_ENGINEERING: {seed} fold {k} did not converge")
            p_model[test] = model.sigmoid(Xtest @ theta[:-1] + theta[-1])
            p_prior[test] = float(y[train].mean())
        if not np.isfinite(p_model).all() or not np.isfinite(p_prior).all():
            raise ValueError("Incomplete OOF prediction")
        fitted = model.score(y, p_model)
        prior = model.score(y, p_prior)
        improvement = float(prior["macro_log_loss"] - fitted["macro_log_loss"])
        gate = bool(fitted["balanced_accuracy"] >= .55 and improvement >= .02)
        metrics["repetitions"][str(seed)] = {"model": fitted, "train_prior": prior,
                                                "macro_log_loss_improvement": improvement,
                                                "frozen_repetition_gate": gate}
        for sid, yi, fidx, p1, p0 in zip(ids, y, fold, p_model, p_prior):
            prediction_rows.append({"seed": seed, "subject_id": str(sid), "fold": int(fidx),
                                    "label": int(yi), "p_PD_model": float(p1), "p_PD_train_prior": float(p0)})
    metrics["gate_pass"] = sum(v["frozen_repetition_gate"] for v in metrics["repetitions"].values()) >= 4
    metrics["qualifying_repetitions"] = sum(v["frozen_repetition_gate"] for v in metrics["repetitions"].values())
    with PRED.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(prediction_rows[0]))
        writer.writeheader()
        writer.writerows(prediction_rows)
    OPT.write_text(json.dumps(optimization, indent=2) + "\n")
    METRICS.write_text(json.dumps(metrics, indent=2) + "\n")
    print(json.dumps({seed: {"model_loss": row["model"]["macro_log_loss"],
                             "prior_loss": row["train_prior"]["macro_log_loss"],
                             "model_bacc": row["model"]["balanced_accuracy"],
                             "gate": row["frozen_repetition_gate"]}
                      for seed, row in metrics["repetitions"].items()}, indent=2), flush=True)
    print("OVERALL_GATE", metrics["gate_pass"], flush=True)


if __name__ == "__main__":
    main()
