"""EXP027-VERIFY-001: only saved fold and OOF output accounting."""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/"STAT-PSYMOE-EXP026-20261002-001"
OUT=ROOT/"LOCAL_VALIDATION.json"


def rows(name,root=ROOT):
    with (root/name).open(newline="") as f:return list(csv.DictReader(f))


def score(data):
    losses=[];recall=[]
    for k in range(3):
        subset=[r for r in data if int(r["label"])==k]
        losses.append(sum(-math.log(max(float(r[["p_HC","p_PD","p_DD"][k]]),1e-300)) for r in subset)/len(subset))
        recall.append(sum(int(r["prediction"])==k for r in subset)/len(subset))
    return sum(losses)/3,sum(recall)/3


def main():
    if OUT.exists():raise FileExistsError(OUT)
    manifest=rows("SPLIT_MANIFEST.csv",PARENT)
    folds=rows("FOLD_MANIFEST.csv")
    fold_metrics=rows("FOLD_METRICS.csv")
    repeats=rows("REPEAT_METRICS.csv")
    pred=rows("OOF_PREDICTIONS.csv")
    opt=json.loads((ROOT/"OPTIMIZATION.json").read_text())
    dev={r["subject_id"] for r in manifest if r["split"]!="test"}
    test={r["subject_id"] for r in manifest if r["split"]=="test"}
    chk={}
    chk["original_test_excluded"]=len(dev)==372 and len(test)==97 and not any(r["subject_id"] in test for r in folds+pred)
    chk["fold_entries"]=len(folds)==1860 and all(Counter(r["subject_id"] for r in folds if int(r["repeat"])==i)==Counter(dev) for i in range(1,6))
    chk["oof_entries"]=len(pred)==3720 and len({(r["repeat"],r["subject_id"],r["arm"]) for r in pred})==3720 and all(abs(sum(float(r[k]) for k in ("p_HC","p_PD","p_DD"))-1)<1e-9 for r in pred)
    chk["50_fits"]=len(opt["fits"])==50 and all(v["converged"] for v in opt["fits"].values())
    grouped=defaultdict(list)
    for r in pred:grouped[(int(r["repeat"]),r["arm"])].append(r)
    checked=True
    for r in repeats:
        repeat=int(r["repeat"])
        a=score(grouped[(repeat,"M1_questionnaire")]);b=score(grouped[(repeat,"M3_combined")])
        expected=(float(r["m1_macro_log_loss"]),float(r["m1_balanced_accuracy"]),float(r["m3_macro_log_loss"]),float(r["m3_balanced_accuracy"]))
        actual=(a[0],a[1],b[0],b[1])
        checked &= all(abs(x-y)<1e-12 for x,y in zip(expected,actual))
    chk["repeat_metrics_recomputed"]=len(repeats)==5 and checked
    qualified=sum(float(r["loss_improvement"])>=0.02 and float(r["balanced_accuracy_improvement"])>=0.03 for r in repeats)
    chk["frozen_gate_recomputed"]=qualified==3 and all(float(r["loss_improvement"])>=0 and float(r["balanced_accuracy_improvement"])>=0 for r in repeats)
    result={"run_id":"EXP027-VERIFY-001","checks":chk,"passed":sum(chk.values()),"total":len(chk),"all_passed":all(chk.values()),"qualified_repeats":qualified,"scope":"EXP027 outputs and EXP026 split IDs only; no refit/test"}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if not result["all_passed"]:raise SystemExit(2)


if __name__=="__main__":main()
