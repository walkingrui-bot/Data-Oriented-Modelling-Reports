"""EXP026-MODEL-001: locked person-level statistical baselines; one test evaluation."""

import csv
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "SPLIT_MANIFEST.csv"
FEATURES = ROOT / "FEATURES.csv"
SOURCE = ROOT / "SOURCE_SUMMARY.json"
SELECTION = ROOT / "MODEL_SELECTION.csv"
PREDICTIONS = ROOT / "PREDICTIONS.csv"
METRICS = ROOT / "METRICS.json"
OPTIMIZATION = ROOT / "OPTIMIZATION.json"
Q_NAMES = [f"q{i:02d}" for i in range(1, 31)]
ONE_WRIST = [f"{sensor}_{stat}" for sensor in ("acc", "gyro") for stat in ("mean", "std", "p95p05", "jerk_rms", "band3to7_ratio")]
MOTION_NAMES = [f"{wrist}_{name}" for wrist in ("left", "right") for name in ONE_WRIST] + [f"absdiff_{name}" for name in ONE_WRIST]
ARMS = {"M1_questionnaire": Q_NAMES, "M2_relaxed_bilateral": MOTION_NAMES, "M3_combined": Q_NAMES + MOTION_NAMES}
LAMBDAS = (0.01, 0.1, 1.0, 10.0)
MAX_STEPS = 5000
TOL = 1e-6


def load():
    if json.loads(SOURCE.read_text())["source_gate"] != "PASS":
        raise ValueError("Frozen source gate did not pass")
    with SPLIT.open(newline="") as f:
        manifest = {r["subject_id"]: r for r in csv.DictReader(f)}
    with FEATURES.open(newline="") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 469 or len(manifest) != 469 or len({r["subject_id"] for r in rows}) != 469:
        raise ValueError("Expected 469 unique feature persons")
    rows.sort(key=lambda r: r["subject_id"])
    for row in rows:
        m = manifest[row["subject_id"]]
        if row["label"] != m["label"] or row["split"] != m["split"]:
            raise ValueError("Feature/split label mismatch")
    ids = [r["subject_id"] for r in rows]
    y = np.array([int(r["label"]) for r in rows], dtype=np.int64)
    split = np.array([r["split"] for r in rows])
    if set(y) != {0,1,2} or Counter(split) != {"train":280, "validation":92, "test":97}:
        raise ValueError("Split distribution changed")
    return rows, ids, y, split


def matrix(rows, names):
    return np.array([[float(row[name]) if row[name] != "" else np.nan for name in names] for row in rows], dtype=np.float64)


def preprocess_fit(x):
    all_missing = np.all(np.isnan(x), axis=0)
    if np.any(all_missing):
        raise ValueError("Feature all missing in training: " + str(np.flatnonzero(all_missing).tolist()))
    med = np.nanmedian(x, axis=0)
    filled = np.where(np.isnan(x), med, x)
    mask = np.isnan(x).astype(np.float64)
    augmented = np.concatenate([filled, mask], axis=1)
    mean = augmented.mean(axis=0)
    std = augmented.std(axis=0)
    std[std < 1e-12] = 1.0
    return med, mean, std


def preprocess_apply(x, state):
    med, mean, std = state
    filled = np.where(np.isnan(x), med, x)
    augmented = np.concatenate([filled, np.isnan(x).astype(np.float64)], axis=1)
    out = (augmented-mean)/std
    if not np.isfinite(out).all():
        raise ValueError("Nonfinite preprocessed features")
    return out


def objective(theta, X, y, weights, lam):
    n, p = X.shape
    W = theta[:p*3].reshape(p,3)
    b = theta[p*3:]
    z = X @ W + b
    z -= z.max(axis=1, keepdims=True)
    ez = np.exp(z)
    prob = ez / ez.sum(axis=1, keepdims=True)
    selected = np.maximum(prob[np.arange(n), y], 1e-300)
    loss = float(np.dot(weights, -np.log(selected))/n + 0.5*lam*np.sum(W*W))
    err = prob.copy()
    err[np.arange(n), y] -= 1.0
    err *= weights[:, None]/n
    gw = X.T @ err + lam*W
    gb = err.sum(axis=0)
    grad = np.concatenate([gw.ravel(), gb])
    return loss, grad


def fit(X, y, lam):
    n, p = X.shape
    counts = np.bincount(y, minlength=3)
    weights = n / (3.0*counts[y])
    theta = np.zeros(p*3+3, dtype=np.float64)
    info = {"lambda":lam, "iterations":0, "converged":False, "gradient_inf":None, "loss":None}
    for step in range(MAX_STEPS+1):
        loss, grad = objective(theta, X, y, weights, lam)
        g_inf = float(np.max(np.abs(grad)))
        if g_inf < TOL:
            info.update({"iterations":step, "converged":True, "gradient_inf":g_inf, "loss":loss})
            break
        if step == MAX_STEPS:
            info.update({"iterations":step, "converged":False, "gradient_inf":g_inf, "loss":loss})
            break
        step_size = 1.0
        g_sq = float(np.dot(grad,grad))
        for _ in range(35):
            candidate = theta-step_size*grad
            new_loss, _ = objective(candidate, X, y, weights, lam)
            if new_loss <= loss-1e-4*step_size*g_sq:
                theta = candidate
                break
            step_size *= 0.5
        else:
            info.update({"iterations":step, "converged":False, "gradient_inf":g_inf, "loss":loss, "line_search_failed":True})
            break
    return theta, info


def probability(X, theta):
    p = X.shape[1]
    z = X @ theta[:p*3].reshape(p,3)+theta[p*3:]
    z -= z.max(axis=1, keepdims=True)
    ez = np.exp(z)
    return ez/ez.sum(axis=1, keepdims=True)


def scores(y, p):
    predicted = p.argmax(axis=1)
    recalls = [float(np.mean(predicted[y==k]==k)) for k in range(3)]
    class_loss = [float(np.mean(-np.log(np.maximum(p[y==k,k],1e-300)))) for k in range(3)]
    cm = [[int(np.sum((y==true)&(predicted==pred))) for pred in range(3)] for true in range(3)]
    return {"macro_log_loss":float(np.mean(class_loss)), "balanced_accuracy":float(np.mean(recalls)), "recall_HC_PD_DD":recalls, "class_log_loss_HC_PD_DD":class_loss, "confusion_rows_true_HC_PD_DD":cm, "n":len(y)}


def main():
    if any(p.exists() for p in (SELECTION, PREDICTIONS, METRICS, OPTIMIZATION)):
        raise FileExistsError("Preserve existing model run outputs")
    rows, ids, y, split = load()
    train = split=="train"
    val = split=="validation"
    test = split=="test"
    trainval = train|val
    selection_rows = []
    validation_predictions = {}
    selected = {}
    optimization = {"run_id":"EXP026-MODEL-001", "optimizer":"full_batch_softmax_gradient_backtracking", "max_steps":MAX_STEPS, "tolerance_gradient_inf":TOL, "fits":{}}
    # Complete every arm's validation selection before computing any test prediction.
    for arm, names in ARMS.items():
        raw = matrix(rows, names)
        state = preprocess_fit(raw[train])
        Xt, Xv = preprocess_apply(raw[train],state), preprocess_apply(raw[val],state)
        arm_candidates = []
        for lam in LAMBDAS:
            theta, info = fit(Xt,y[train],lam)
            optimization["fits"][f"{arm}_validation_lambda_{lam}"] = info
            p_val = probability(Xv,theta)
            metric = scores(y[val],p_val)
            rec = {"arm":arm,"lambda":lam,"converged":info["converged"],"steps":info["iterations"],"validation_macro_log_loss":metric["macro_log_loss"],"validation_balanced_accuracy":metric["balanced_accuracy"]}
            selection_rows.append(rec)
            arm_candidates.append((rec,p_val,metric))
        eligible = [item for item in arm_candidates if item[0]["converged"]]
        if not eligible:
            raise RuntimeError(f"No converged candidate for {arm}")
        rec,p_val,metric = min(eligible, key=lambda item:(item[0]["validation_macro_log_loss"],-item[0]["lambda"]))
        selected[arm] = {"lambda":rec["lambda"],"validation":metric}
        validation_predictions[arm] = p_val
        print("selected",arm,rec["lambda"],"val_loss",rec["validation_macro_log_loss"],"val_bacc",rec["validation_balanced_accuracy"],flush=True)
    # M0 validation uses train prior; test uses train+validation prior per Amendment 001.
    prior_train = np.bincount(y[train],minlength=3)/int(train.sum())
    p0_val = np.tile(prior_train,(int(val.sum()),1))
    m0_val = scores(y[val],p0_val)
    test_predictions = {}
    for arm,names in ARMS.items():
        raw = matrix(rows,names)
        state = preprocess_fit(raw[trainval])
        Xtv,Xtest = preprocess_apply(raw[trainval],state),preprocess_apply(raw[test],state)
        theta,info = fit(Xtv,y[trainval],selected[arm]["lambda"])
        optimization["fits"][f"{arm}_final"] = info
        if not info["converged"]:
            raise RuntimeError(f"Final fit did not converge: {arm}")
        test_predictions[arm]=probability(Xtest,theta)
        selected[arm]["test"]=scores(y[test],test_predictions[arm])
    prior_trainval=np.bincount(y[trainval],minlength=3)/int(trainval.sum())
    p0_test=np.tile(prior_trainval,(int(test.sum()),1))
    m0_test=scores(y[test],p0_test)
    v1,v3=selected["M1_questionnaire"]["validation"],selected["M3_combined"]["validation"]
    t1,t3=selected["M1_questionnaire"]["test"],selected["M3_combined"]["test"]
    improvement={"validation_macro_log_loss":v1["macro_log_loss"]-v3["macro_log_loss"],"validation_balanced_accuracy":v3["balanced_accuracy"]-v1["balanced_accuracy"],"test_macro_log_loss":t1["macro_log_loss"]-t3["macro_log_loss"],"test_balanced_accuracy":t3["balanced_accuracy"]-t1["balanced_accuracy"]}
    gate = improvement["validation_macro_log_loss"]>=0.02 and improvement["validation_balanced_accuracy"]>=0.03 and improvement["test_macro_log_loss"]>0 and improvement["test_balanced_accuracy"]>0
    output={"run_id":"EXP026-MODEL-001","status":"COMPLETE","science_status":"OBSERVED_ADDED_VALUE_IN_INTERNAL_SPLIT" if gate else "NO_QUALIFIED_ADDED_VALUE_IN_INTERNAL_SPLIT","thresholds":{"validation_loss_improvement_min":0.02,"validation_balanced_accuracy_improvement_min":0.03,"test_loss_improvement_strictly_positive":True,"test_balanced_accuracy_improvement_strictly_positive":True},"split_counts":dict(Counter(split)),"M0_prior":{"validation":m0_val,"test":m0_test},"arms":selected,"M3_minus_M1_improvement":improvement,"gate_pass":bool(gate),"external_validation":False,"test_used_once":True}
    with SELECTION.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(selection_rows[0]))
        writer.writeheader(); writer.writerows(selection_rows)
    pred_rows=[]
    for arm,p in [("M0_prior",p0_val)]+list(validation_predictions.items()):
        for sid,yi,pi in zip(np.array(ids)[val],y[val],p):
            pred_rows.append({"split":"validation","subject_id":sid,"label":int(yi),"arm":arm,"p_HC":float(pi[0]),"p_PD":float(pi[1]),"p_DD":float(pi[2]),"prediction":int(np.argmax(pi))})
    for arm,p in [("M0_prior",p0_test)]+list(test_predictions.items()):
        for sid,yi,pi in zip(np.array(ids)[test],y[test],p):
            pred_rows.append({"split":"test","subject_id":sid,"label":int(yi),"arm":arm,"p_HC":float(pi[0]),"p_PD":float(pi[1]),"p_DD":float(pi[2]),"prediction":int(np.argmax(pi))})
    with PREDICTIONS.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(pred_rows[0]))
        writer.writeheader(); writer.writerows(pred_rows)
    OPTIMIZATION.write_text(json.dumps(optimization,indent=2)+"\n")
    METRICS.write_text(json.dumps(output,indent=2)+"\n")
    print(json.dumps({"gate_pass":gate,"M3_minus_M1_improvement":improvement,"selected_lambda":{arm:selected[arm]["lambda"] for arm in selected}},indent=2),flush=True)


if __name__=="__main__":
    main()
