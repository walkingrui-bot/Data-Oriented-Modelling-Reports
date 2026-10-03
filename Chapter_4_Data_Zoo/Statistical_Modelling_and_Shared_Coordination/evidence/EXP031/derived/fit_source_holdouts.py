"""EXP031-MODEL-001: fixed binary logistic vs train prior, three study holdouts."""

import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np


ROOT=Path(__file__).resolve().parents[1]
FEATURES=ROOT/"FORCE_FEATURES.csv"
SOURCE=ROOT/"SOURCE_SUMMARY.json"
OPT=ROOT/"OPTIMIZATION.json"
METRICS=ROOT/"METRICS.json"
PRED=ROOT/"PREDICTIONS.csv"
NAMES=[f"{side}_{stat}" for side in ("left","right") for stat in ("mean","std","p95p05","contact_fraction")]+["mean_asymmetry_abs","left_right_corr","total_dominant_hz","total_band_ratio"]
LAM=.1;MAX_STEPS=5000;TOL=1e-6


def preprocess_fit(x):
    if np.any(np.all(np.isnan(x),axis=0)):raise ValueError("Entire feature missing in train")
    med=np.nanmedian(x,axis=0)
    aug=np.concatenate([np.where(np.isnan(x),med,x),np.isnan(x).astype(float)],axis=1)
    mean=aug.mean(axis=0);std=aug.std(axis=0);std[std<1e-12]=1
    return med,mean,std


def preprocess_apply(x,state):
    med,mean,std=state
    aug=np.concatenate([np.where(np.isnan(x),med,x),np.isnan(x).astype(float)],axis=1)
    out=(aug-mean)/std
    if not np.isfinite(out).all():raise ValueError("Nonfinite processed features")
    return out


def sigmoid(z):return 1/(1+np.exp(-np.clip(z,-40,40)))


def objective(theta,X,y,weights,lam):
    w=theta[:-1];b=theta[-1];z=X@w+b
    p=sigmoid(z)
    loss=float(np.mean(weights*(np.logaddexp(0,z)-y*z))+.5*lam*np.dot(w,w))
    err=weights*(p-y)/len(y)
    grad=np.r_[X.T@err+lam*w,err.sum()]
    return loss,grad


def fit(X,y,lam=LAM):
    n,p=X.shape
    counts=np.bincount(y,minlength=2)
    if np.any(counts==0):raise ValueError("Both classes needed in train")
    weights=n/(2*counts[y])
    theta=np.zeros(p+1)
    info={"lambda":lam,"iterations":0,"converged":False,"gradient_inf":None,"loss":None}
    for step in range(MAX_STEPS+1):
        loss,grad=objective(theta,X,y,weights,lam)
        g_inf=float(np.max(np.abs(grad)))
        if g_inf<TOL:
            info.update({"iterations":step,"converged":True,"gradient_inf":g_inf,"loss":loss});break
        if step==MAX_STEPS:
            info.update({"iterations":step,"gradient_inf":g_inf,"loss":loss});break
        step_size=1.;g_sq=float(np.dot(grad,grad))
        for _ in range(35):
            candidate=theta-step_size*grad
            new_loss,_=objective(candidate,X,y,weights,lam)
            if new_loss<=loss-1e-4*step_size*g_sq:
                theta=candidate;break
            step_size*=.5
        else:
            info.update({"iterations":step,"gradient_inf":g_inf,"loss":loss,"line_search_failed":True});break
    return theta,info


def score(y,p):
    pred=(p>=.5).astype(int)
    recalls=[float(np.mean(pred[y==k]==k)) for k in (0,1)]
    losses=[float(np.mean(-(y[y==k]*np.log(np.maximum(p[y==k],1e-300))+(1-y[y==k])*np.log(np.maximum(1-p[y==k],1e-300))))) for k in (0,1)]
    cm=[[int(np.sum((y==t)&(pred==a))) for a in (0,1)] for t in (0,1)]
    return {"macro_log_loss":float(np.mean(losses)),"balanced_accuracy":float(np.mean(recalls)),"recall_HC_PD":recalls,"confusion_rows_true_HC_PD":cm,"n":len(y)}


def main():
    if any(p.exists() for p in (OPT,METRICS,PRED)):raise FileExistsError("Preserve EXP031-MODEL-001 outputs")
    summary=json.loads(SOURCE.read_text())
    if summary["source_gate"]!="PASS":raise ValueError("Numeric source gate not passed")
    with FEATURES.open(newline="") as f:rows=list(csv.DictReader(f))
    if len(rows)!=165 or len({r["subject_id"] for r in rows})!=165:raise ValueError("Expected 165 people")
    rows.sort(key=lambda r:r["subject_id"])
    if set(rows[0])!={"subject_id","study","label"}|set(NAMES):raise ValueError("Feature allowlist changed")
    ids=np.array([r["subject_id"] for r in rows]);study=np.array([r["study"] for r in rows]);y=np.array([int(r["label"]) for r in rows],dtype=np.int64)
    X=np.array([[float(r[name]) if r[name]!="" else np.nan for name in NAMES] for r in rows],dtype=float)
    opt={"run_id":"EXP031-MODEL-001","lambda":LAM,"fits":{}}
    metrics={"run_id":"EXP031-MODEL-001","status":"COMPLETE","independence_note":"study-held-out stress; cross-study person overlap not established","holdouts":{},"gate_pass":False}
    pred_rows=[]
    for holdout in ("Ga","Ju","Si"):
        train=study!=holdout;test=study==holdout
        state=preprocess_fit(X[train])
        Xt=preprocess_apply(X[train],state);Xtest=preprocess_apply(X[test],state)
        theta,info=fit(Xt,y[train]);opt["fits"][holdout]=info
        if not info["converged"]:
            OPT.write_text(json.dumps(opt,indent=2)+"\n")
            raise RuntimeError(f"STOP_ENGINEERING: {holdout} fit did not converge")
        p=sigmoid(Xtest@theta[:-1]+theta[-1])
        prior=float(y[train].mean());p0=np.full(int(test.sum()),prior)
        model=score(y[test],p);baseline=score(y[test],p0)
        improvement={"macro_log_loss":baseline["macro_log_loss"]-model["macro_log_loss"],"balanced_accuracy":model["balanced_accuracy"]-baseline["balanced_accuracy"]}
        metrics["holdouts"][holdout]={"train_n":int(train.sum()),"test_n":int(test.sum()),"train_counts_HC_PD":np.bincount(y[train],minlength=2).tolist(),"test_counts_HC_PD":np.bincount(y[test],minlength=2).tolist(),"prior":baseline,"logistic":model,"improvement":improvement,"frozen_study_gate":bool(model["balanced_accuracy"]>=.55 and improvement["macro_log_loss"]>=.02)}
        for sid,yi,prob in zip(ids[test],y[test],p):
            pred_rows.append({"subject_id":sid,"study":holdout,"label":int(yi),"p_PD_model":float(prob),"p_PD_prior":prior,"prediction_model":int(prob>=.5),"prediction_prior":int(prior>=.5)})
    metrics["gate_pass"]=all(r["frozen_study_gate"] for r in metrics["holdouts"].values())
    with PRED.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=list(pred_rows[0]));writer.writeheader();writer.writerows(pred_rows)
    OPT.write_text(json.dumps(opt,indent=2)+"\n")
    METRICS.write_text(json.dumps(metrics,indent=2)+"\n")
    print(json.dumps({s:{"prior_loss":r["prior"]["macro_log_loss"],"model_loss":r["logistic"]["macro_log_loss"],"model_bacc":r["logistic"]["balanced_accuracy"],"gate":r["frozen_study_gate"]} for s,r in metrics["holdouts"].items()},indent=2),flush=True)
    print("OVERALL_GATE",metrics["gate_pass"],flush=True)


if __name__=="__main__":main()
