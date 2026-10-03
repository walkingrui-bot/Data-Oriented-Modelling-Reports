"""EXP028-MODEL-001: fixed cognitive-task model on EXP027 folds, M1 reused by path."""

import csv
import json
import sys
from collections import Counter,defaultdict
from pathlib import Path

import numpy as np


ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/"STAT-PSYMOE-EXP026-20261002-001"
CV=ROOT.parent/"STAT-PSYMOE-EXP027-20261002-001"
sys.path.insert(0,str(PARENT/"derived"))
import fit_baselines as base

FOLD_METRICS=ROOT/"FOLD_METRICS.csv"
REPEAT_METRICS=ROOT/"REPEAT_METRICS.csv"
PRED=ROOT/"OOF_PREDICTIONS.csv"
OPT=ROOT/"OPTIMIZATION.json"
LAM=0.1


def load():
    if json.loads((ROOT/"SOURCE_SUMMARY.json").read_text())["source_gate"]!="PASS":raise ValueError("Source gate did not pass")
    with (PARENT/"SPLIT_MANIFEST.csv").open(newline="") as f:manifest={r["subject_id"]:r for r in csv.DictReader(f)}
    with (ROOT/"COGNITIVE_FEATURES.csv").open(newline="") as f:new={r["subject_id"]:r for r in csv.DictReader(f)}
    original={}
    with (PARENT/"FEATURES.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            if manifest[r["subject_id"]]["split"]!="test":original[r["subject_id"]]=r
    ids=sorted(r["subject_id"] for r in manifest.values() if r["split"]!="test")
    if len(ids)!=372 or set(ids)!=set(new)==set(original):raise ValueError("Development identity mismatch")
    y=np.array([int(manifest[sid]["label"]) for sid in ids],dtype=np.int64)
    if Counter(y)!={0:62,1:220,2:90}:raise ValueError("Development label counts changed")
    names=base.Q_NAMES+base.MOTION_NAMES
    rows=[]
    for sid in ids:
        if original[sid]["label"]!=manifest[sid]["label"]:raise ValueError("Old feature label mismatch")
        rows.append({**{name:original[sid][name] for name in base.Q_NAMES},**{name:new[sid][name] for name in base.MOTION_NAMES}})
    X=base.matrix(rows,names)
    with (CV/"FOLD_MANIFEST.csv").open(newline="") as f:fold_rows=list(csv.DictReader(f))
    folds={(int(r["repeat"]),r["subject_id"]):int(r["fold"]) for r in fold_rows}
    if len(folds)!=1860 or len(fold_rows)!=1860:raise ValueError("EXP027 fold manifest changed")
    reference=defaultdict(dict)
    with (CV/"OOF_PREDICTIONS.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            key=(int(r["repeat"]),r["arm"])
            reference[key][r["subject_id"]]=np.array([float(r[k]) for k in ("p_HC","p_PD","p_DD")])
    for repeat in range(1,6):
        for arm in ("M1_questionnaire","M3_combined"):
            if set(reference[(repeat,arm)])!=set(ids):raise ValueError("Old OOF reference mismatch")
    return ids,y,X,folds,reference


def main():
    if any(p.exists() for p in (FOLD_METRICS,REPEAT_METRICS,PRED,OPT)):raise FileExistsError("Preserve EXP028-MODEL-001 outputs")
    ids,y,X,assign,ref=load()
    opt={"run_id":"EXP028-MODEL-001","lambda":LAM,"old_test_used":False,"M1_M3_reference_path":str(CV/"OOF_PREDICTIONS.csv"),"new_feature_path":str(ROOT/"COGNITIVE_FEATURES.csv"),"fits":{}}
    fold_fields=["repeat","fold","n","m1_loss","m4_loss","m4_vs_m1_loss_improvement","m1_bacc","m4_bacc","m4_vs_m1_bacc_improvement","m3_loss","m4_vs_m3_loss_improvement","m3_bacc","m4_vs_m3_bacc_improvement"]
    repeat_fields=["repeat","n_unique_people","m1_loss","m4_loss","m4_vs_m1_loss_improvement","m1_bacc","m4_bacc","m4_vs_m1_bacc_improvement","m3_loss","m4_vs_m3_loss_improvement","m3_bacc","m4_vs_m3_bacc_improvement"]
    pred_fields=["repeat","fold","subject_id","label","p_HC","p_PD","p_DD","prediction"]
    results=[]
    with FOLD_METRICS.open("w",newline="") as ff,REPEAT_METRICS.open("w",newline="") as fr,PRED.open("w",newline="") as fp:
        fw=csv.DictWriter(ff,fieldnames=fold_fields);rw=csv.DictWriter(fr,fieldnames=repeat_fields);pw=csv.DictWriter(fp,fieldnames=pred_fields)
        fw.writeheader();rw.writeheader();pw.writeheader()
        for repeat in range(1,6):
            folds=np.array([assign[(repeat,sid)] for sid in ids],dtype=np.int64)
            oof=np.full((len(ids),3),np.nan)
            old={arm:np.vstack([ref[(repeat,arm)][sid] for sid in ids]) for arm in ("M1_questionnaire","M3_combined")}
            for fold in range(5):
                tr=folds!=fold;va=folds==fold
                state=base.preprocess_fit(X[tr])
                Xt=base.preprocess_apply(X[tr],state);Xv=base.preprocess_apply(X[va],state)
                theta,info=base.fit(Xt,y[tr],LAM)
                opt["fits"][f"repeat_{repeat}_fold_{fold}"]=info
                if not info["converged"]:
                    OPT.write_text(json.dumps(opt,indent=2)+"\n")
                    raise RuntimeError(f"STOP_ENGINEERING: nonconverged repeat {repeat} fold {fold}")
                p=base.probability(Xv,theta);oof[va]=p
                for sid,yi,pi in zip(np.array(ids)[va],y[va],p):
                    pw.writerow({"repeat":repeat,"fold":fold,"subject_id":sid,"label":int(yi),"p_HC":float(pi[0]),"p_PD":float(pi[1]),"p_DD":float(pi[2]),"prediction":int(np.argmax(pi))})
                a=base.scores(y[va],old["M1_questionnaire"][va]);b=base.scores(y[va],p);c=base.scores(y[va],old["M3_combined"][va])
                fw.writerow({"repeat":repeat,"fold":fold,"n":int(va.sum()),"m1_loss":a["macro_log_loss"],"m4_loss":b["macro_log_loss"],"m4_vs_m1_loss_improvement":a["macro_log_loss"]-b["macro_log_loss"],"m1_bacc":a["balanced_accuracy"],"m4_bacc":b["balanced_accuracy"],"m4_vs_m1_bacc_improvement":b["balanced_accuracy"]-a["balanced_accuracy"],"m3_loss":c["macro_log_loss"],"m4_vs_m3_loss_improvement":c["macro_log_loss"]-b["macro_log_loss"],"m3_bacc":c["balanced_accuracy"],"m4_vs_m3_bacc_improvement":b["balanced_accuracy"]-c["balanced_accuracy"]})
                fp.flush();ff.flush()
            if not np.isfinite(oof).all():raise ValueError("OOF incomplete")
            a=base.scores(y,old["M1_questionnaire"]);b=base.scores(y,oof);c=base.scores(y,old["M3_combined"])
            result={"repeat":repeat,"n_unique_people":len(ids),"m1_loss":a["macro_log_loss"],"m4_loss":b["macro_log_loss"],"m4_vs_m1_loss_improvement":a["macro_log_loss"]-b["macro_log_loss"],"m1_bacc":a["balanced_accuracy"],"m4_bacc":b["balanced_accuracy"],"m4_vs_m1_bacc_improvement":b["balanced_accuracy"]-a["balanced_accuracy"],"m3_loss":c["macro_log_loss"],"m4_vs_m3_loss_improvement":c["macro_log_loss"]-b["macro_log_loss"],"m3_bacc":c["balanced_accuracy"],"m4_vs_m3_bacc_improvement":b["balanced_accuracy"]-c["balanced_accuracy"]}
            rw.writerow(result);fr.flush();results.append(result)
            print("repeat",repeat,"M4vsM1_loss",result["m4_vs_m1_loss_improvement"],"M4vsM1_bacc",result["m4_vs_m1_bacc_improvement"],"M4vsM3_bacc",result["m4_vs_m3_bacc_improvement"],flush=True)
    OPT.write_text(json.dumps(opt,indent=2)+"\n")
    qualified=sum(r["m4_vs_m1_loss_improvement"]>=.02 and r["m4_vs_m1_bacc_improvement"]>=.03 for r in results)
    nonnegative=all(r["m4_vs_m1_loss_improvement"]>=0 and r["m4_vs_m1_bacc_improvement"]>=0 for r in results)
    print(json.dumps({"fits":len(opt["fits"]),"qualified_repeats":qualified,"all_nonnegative":nonnegative,"gate_pass":qualified>=4 and nonnegative},indent=2),flush=True)


if __name__=="__main__":main()
