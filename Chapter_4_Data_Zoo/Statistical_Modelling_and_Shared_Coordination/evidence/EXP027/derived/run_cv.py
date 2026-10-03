"""EXP027-CV-001: five frozen person-level 5-fold development diagnostics."""

import csv
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np


ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/"STAT-PSYMOE-EXP026-20261002-001"
sys.path.insert(0,str(PARENT/"derived"))
import fit_baselines as base

FOLDS=ROOT/"FOLD_MANIFEST.csv"
FOLD_METRICS=ROOT/"FOLD_METRICS.csv"
REPEAT_METRICS=ROOT/"REPEAT_METRICS.csv"
PRED=ROOT/"OOF_PREDICTIONS.csv"
OPT=ROOT/"OPTIMIZATION.json"
LAM=0.1
SEEDS=range(20261003,20261008)
ARMS={"M1_questionnaire":base.Q_NAMES,"M3_combined":base.Q_NAMES+base.MOTION_NAMES}


def read_development():
    with (PARENT/"SPLIT_MANIFEST.csv").open(newline="") as f:
        manifest={r["subject_id"]:r for r in csv.DictReader(f)}
    rows=[]
    with (PARENT/"FEATURES.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            m=manifest[r["subject_id"]]
            if r["split"]!=m["split"] or r["label"]!=m["label"]:
                raise ValueError("EXP026 feature/split mismatch")
            if m["split"]!="test":
                rows.append(r)
    rows.sort(key=lambda r:r["subject_id"])
    if len(rows)!=372 or len({r["subject_id"] for r in rows})!=372 or Counter(r["label"] for r in rows)!={"0":62,"1":220,"2":90}:
        raise ValueError("Expected exact EXP026 372-person development cohort")
    return rows


def assign_folds(rows):
    by_label=defaultdict(list)
    for r in rows:
        by_label[int(r["label"])].append(r["subject_id"])
    entries=[]
    for repeat,seed in enumerate(SEEDS,1):
        rng=random.Random(seed)
        for label in sorted(by_label):
            ids=sorted(by_label[label]);rng.shuffle(ids)
            for ix,sid in enumerate(ids):
                entries.append({"repeat":repeat,"seed":seed,"subject_id":sid,"label":label,"fold":ix%5})
    entries.sort(key=lambda r:(r["repeat"],r["subject_id"]))
    if len(entries)!=1860 or any(Counter(r["subject_id"] for r in entries if r["repeat"]==repeat)!=Counter(r["subject_id"] for r in rows) for repeat in range(1,6)):
        raise ValueError("Repeated fold identity check failed")
    return entries


def main():
    if any(p.exists() for p in (FOLDS,FOLD_METRICS,REPEAT_METRICS,PRED,OPT)):
        raise FileExistsError("Preserve EXP027-CV-001 original outputs")
    start=time.monotonic()
    rows=read_development()
    ids=[r["subject_id"] for r in rows]
    y=np.array([int(r["label"]) for r in rows],dtype=np.int64)
    mats={arm:base.matrix(rows,names) for arm,names in ARMS.items()}
    entries=assign_folds(rows)
    with FOLDS.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["repeat","seed","subject_id","label","fold"])
        writer.writeheader();writer.writerows(entries)
    opt={"run_id":"EXP027-CV-001","parent_feature_path":str(PARENT/"FEATURES.csv"),"original_test_used":False,"lambda":LAM,"seeds":list(SEEDS),"fits":{}}
    fold_fields=["repeat","fold","n","m1_macro_log_loss","m3_macro_log_loss","loss_improvement","m1_balanced_accuracy","m3_balanced_accuracy","balanced_accuracy_improvement"]
    repeat_fields=["repeat","seed","n_unique_people","m1_macro_log_loss","m3_macro_log_loss","loss_improvement","m1_balanced_accuracy","m3_balanced_accuracy","balanced_accuracy_improvement","folds_both_positive"]
    pred_fields=["repeat","fold","subject_id","label","arm","p_HC","p_PD","p_DD","prediction"]
    result=[]
    with FOLD_METRICS.open("w",newline="") as ff,REPEAT_METRICS.open("w",newline="") as fr,PRED.open("w",newline="") as fp:
        fw=csv.DictWriter(ff,fieldnames=fold_fields);rw=csv.DictWriter(fr,fieldnames=repeat_fields);pw=csv.DictWriter(fp,fieldnames=pred_fields)
        fw.writeheader();rw.writeheader();pw.writeheader()
        for repeat,seed in enumerate(SEEDS,1):
            assignment={r["subject_id"]:r["fold"] for r in entries if r["repeat"]==repeat}
            folds=np.array([assignment[sid] for sid in ids],dtype=np.int64)
            oof={arm:np.full((len(rows),3),np.nan,dtype=np.float64) for arm in ARMS}
            fold_rows=[]
            for fold in range(5):
                tr=folds!=fold;va=folds==fold
                local={}
                for arm in ARMS:
                    raw=mats[arm]
                    state=base.preprocess_fit(raw[tr])
                    Xt=base.preprocess_apply(raw[tr],state)
                    Xv=base.preprocess_apply(raw[va],state)
                    theta,info=base.fit(Xt,y[tr],LAM)
                    opt["fits"][f"repeat_{repeat}_fold_{fold}_{arm}"]=info
                    if not info["converged"]:
                        OPT.write_text(json.dumps(opt,indent=2)+"\n")
                        raise RuntimeError(f"STOP_ENGINEERING: fit did not converge, repeat {repeat}, fold {fold}, {arm}")
                    p=base.probability(Xv,theta)
                    oof[arm][va]=p
                    local[arm]=base.scores(y[va],p)
                    for sid,yi,pi in zip(np.array(ids)[va],y[va],p):
                        pw.writerow({"repeat":repeat,"fold":fold,"subject_id":sid,"label":int(yi),"arm":arm,"p_HC":float(pi[0]),"p_PD":float(pi[1]),"p_DD":float(pi[2]),"prediction":int(np.argmax(pi))})
                a,b=local["M1_questionnaire"],local["M3_combined"]
                fold_row={"repeat":repeat,"fold":fold,"n":int(va.sum()),"m1_macro_log_loss":a["macro_log_loss"],"m3_macro_log_loss":b["macro_log_loss"],"loss_improvement":a["macro_log_loss"]-b["macro_log_loss"],"m1_balanced_accuracy":a["balanced_accuracy"],"m3_balanced_accuracy":b["balanced_accuracy"],"balanced_accuracy_improvement":b["balanced_accuracy"]-a["balanced_accuracy"]}
                fw.writerow(fold_row);ff.flush();fp.flush();fold_rows.append(fold_row)
                if time.monotonic()-start>600:
                    OPT.write_text(json.dumps(opt,indent=2)+"\n")
                    raise TimeoutError("STOP_BUDGET: EXP027 exceeded ten minutes")
            if not all(np.isfinite(p).all() for p in oof.values()):
                raise ValueError("Incomplete out-of-fold coverage")
            a=base.scores(y,oof["M1_questionnaire"]);b=base.scores(y,oof["M3_combined"])
            repeat_row={"repeat":repeat,"seed":seed,"n_unique_people":len(rows),"m1_macro_log_loss":a["macro_log_loss"],"m3_macro_log_loss":b["macro_log_loss"],"loss_improvement":a["macro_log_loss"]-b["macro_log_loss"],"m1_balanced_accuracy":a["balanced_accuracy"],"m3_balanced_accuracy":b["balanced_accuracy"],"balanced_accuracy_improvement":b["balanced_accuracy"]-a["balanced_accuracy"],"folds_both_positive":sum(x["loss_improvement"]>0 and x["balanced_accuracy_improvement"]>0 for x in fold_rows)}
            rw.writerow(repeat_row);fr.flush();result.append(repeat_row)
            print("repeat",repeat,"loss_improvement",repeat_row["loss_improvement"],"bacc_improvement",repeat_row["balanced_accuracy_improvement"],flush=True)
    OPT.write_text(json.dumps(opt,indent=2)+"\n")
    qualified=sum(r["loss_improvement"]>=0.02 and r["balanced_accuracy_improvement"]>=0.03 for r in result)
    nonnegative=all(r["loss_improvement"]>=0 and r["balanced_accuracy_improvement"]>=0 for r in result)
    print(json.dumps({"fits":len(opt["fits"]),"qualified_repeats":qualified,"all_nonnegative":nonnegative,"gate_pass":qualified>=4 and nonnegative},indent=2),flush=True)


if __name__=="__main__":
    main()
