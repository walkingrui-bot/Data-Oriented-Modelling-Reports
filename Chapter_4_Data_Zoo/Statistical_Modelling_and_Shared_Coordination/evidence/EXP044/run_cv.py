"""EXP044 frozen repeated person-level CV for M0/M1/M2."""

import csv
import json
import warnings
from pathlib import Path

import numpy as np
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import LogisticRegression

HERE = Path(__file__).resolve().parent
SEEDS = list(range(202610020, 202610025))


def score(y, p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    positive = y == 1
    negative = y == 0
    return {
        "macro_log_loss": float(-0.5 * (np.log(p[positive]).mean() + np.log(1 - p[negative]).mean())),
        "balanced_accuracy": float(0.5 * (((p[positive] >= 0.5).mean()) + ((p[negative] < 0.5).mean()))),
        "overall_log_loss": float(-(y * np.log(p) + (1 - y) * np.log(1 - p)).mean()),
    }


def fitted_probabilities(x_train, y_train, x_test):
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std == 0] = 1.0
    train = (x_train - mean) / std
    test = (x_test - mean) / std
    model = LogisticRegression(C=1.0, penalty="l2", solver="lbfgs", max_iter=1000, tol=1e-8, fit_intercept=True, class_weight=None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", ConvergenceWarning)
        model.fit(train, y_train)
    issue = [str(w.message) for w in caught if issubclass(w.category, ConvergenceWarning)]
    n_iter = int(model.n_iter_[0])
    if issue or n_iter >= 1000:
        raise RuntimeError(f"logistic not converged: {n_iter}, {issue}")
    return model.predict_proba(test)[:, 1], {"n_iter": n_iter, "coef": model.coef_[0].tolist(), "intercept": float(model.intercept_[0]), "train_mean": mean.tolist(), "train_std": std.tolist(), "converged": True}


def main():
    paths = [HERE / name for name in ("SPLITS.json", "OPTIMIZATION.json", "PREDICTIONS.csv", "METRICS.json")]
    if any(path.exists() for path in paths):
        raise FileExistsError("EXP044-CV-001 output exists; preserve attempt")
    source = json.loads((HERE / "SOURCE_GATE.json").read_text())
    assert source["gate"] == "ANALYSIS_SOURCE_READY" and source["speed_complete_people"] == 40
    rows = list(csv.DictReader((HERE / "ANALYSIS_TABLE.csv").open(newline="")))
    ids = np.array([r["participant_id"] for r in rows])
    y = np.array([int(r["y_fell_last_month"]) for r in rows])
    x = np.array([[float(r["log_clinical_speed"]), float(r["bilateral_accel_asym"])] for r in rows])
    assert len(rows) == 40 and len(set(ids)) == 40 and np.bincount(y, minlength=2).tolist() == [30, 10] and np.isfinite(x).all()
    splits = {"run_id": "EXP044-CV-001", "unit": "unique PD participant", "repeated_same_people": True, "seeds": {}}
    for seed in SEEDS:
        fold = np.full(len(y), -1, dtype=int)
        rng = np.random.default_rng(seed)
        for klass in (0, 1):
            indices = np.flatnonzero(y == klass)
            rng.shuffle(indices)
            for pos, index in enumerate(indices):
                fold[index] = pos % 5
        assert all(np.bincount(y[fold == k], minlength=2).tolist() == [6, 2] for k in range(5))
        splits["seeds"][str(seed)] = {str(ident): int(k) for ident, k in zip(ids, fold)}
    paths[0].write_text(json.dumps(splits, indent=2) + "\n")
    opt = {"run_id": "EXP044-CV-001", "sklearn_model": "LogisticRegression(C=1.0, penalty=l2, solver=lbfgs, max_iter=1000, tol=1e-8, class_weight=None)", "fits": {}}
    metrics = {"run_id": "EXP044-CV-001", "development_only": True, "same_40_people_repeated": True, "repetitions": {}}
    predictions = []
    for seed in SEEDS:
        fold = np.array([splits["seeds"][str(seed)][str(ident)] for ident in ids])
        p = {name: np.full(len(y), np.nan) for name in ("M0", "M1", "M2")}
        for k in range(5):
            train = fold != k
            test = fold == k
            p["M0"][test] = y[train].mean()
            for name, columns in (("M1", [0]), ("M2", [0, 1])):
                try:
                    prob, info = fitted_probabilities(x[train][:, columns], y[train], x[test][:, columns])
                except Exception as exc:
                    opt["failure"] = {"seed": seed, "fold": k, "model": name, "error": repr(exc)}
                    paths[1].write_text(json.dumps(opt, indent=2) + "\n")
                    raise
                p[name][test] = prob
                opt["fits"][f"{seed}_fold{k}_{name}"] = info
                paths[1].write_text(json.dumps(opt, indent=2) + "\n")
        assert all(np.isfinite(p[name]).all() for name in p)
        scored = {name: score(y, p[name]) for name in ("M0", "M1", "M2")}
        loss_gain_vs_speed = scored["M1"]["macro_log_loss"] - scored["M2"]["macro_log_loss"]
        bacc_gain_vs_speed = scored["M2"]["balanced_accuracy"] - scored["M1"]["balanced_accuracy"]
        loss_gain_vs_prior = scored["M0"]["macro_log_loss"] - scored["M2"]["macro_log_loss"]
        pass_gate = loss_gain_vs_speed >= 0.02 and bacc_gain_vs_speed >= 0.05 and loss_gain_vs_prior >= 0.02
        metrics["repetitions"][str(seed)] = {"scores": scored, "M2_minus_M1_macro_log_loss_improvement": float(loss_gain_vs_speed), "M2_minus_M1_balanced_accuracy_gain": float(bacc_gain_vs_speed), "M2_minus_M0_macro_log_loss_improvement": float(loss_gain_vs_prior), "frozen_repetition_gate": bool(pass_gate)}
        for idx, ident in enumerate(ids):
            predictions.append({"seed": seed, "participant_id": str(ident), "fold": int(fold[idx]), "y_fell_last_month": int(y[idx]), "p_M0": float(p["M0"][idx]), "p_M1": float(p["M1"][idx]), "p_M2": float(p["M2"][idx])})
        print(seed, scored, "gate", pass_gate, flush=True)
    passes = sum(row["frozen_repetition_gate"] for row in metrics["repetitions"].values())
    metrics["qualifying_repetitions"] = passes
    metrics["gate_pass"] = passes >= 4
    with paths[2].open("x", newline="") as out:
        writer = csv.DictWriter(out, fieldnames=list(predictions[0]))
        writer.writeheader()
        writer.writerows(predictions)
    paths[3].write_text(json.dumps(metrics, indent=2) + "\n")
    print("OVERALL_GATE", metrics["gate_pass"], "qualifying", passes, flush=True)


if __name__ == "__main__":
    main()
