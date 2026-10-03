"""EXP028-VERIFY-001: read-only source, fold, and saved-probability checks."""

import csv
import json
import math
from collections import Counter,defaultdict
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/"STAT-PSYMOE-EXP026-20261002-001"
CV=ROOT.parent/"STAT-PSYMOE-EXP027-20261002-001"
OUT=ROOT/"LOCAL_VALIDATION.json"


def table(root,name):
    with (root/name).open(newline="") as f:return list(csv.DictReader(f))


def score(data):
    losses=[];recalls=[]
    for k in range(3):
        group=[r for r in data if int(r["label"])==k]
        losses.append(sum(-math.log(max(float(r[["p_HC","p_PD","p_DD"][k]]),1e-300)) for r in group)/len(group))
        recalls.append(sum(int(r["prediction"])==k for r in group)/len(group))
    return sum(losses)/3,sum(recalls)/3


def main():
    if OUT.exists():raise FileExistsError(OUT)
    split=table(PARENT,"SPLIT_MANIFEST.csv")
    dev={r["subject_id"] for r in split if r["split"]!="test"};test={r["subject_id"] for r in split if r["split"]=="test"}
    features=table(ROOT,"COGNITIVE_FEATURES.csv")
    audit=table(ROOT,"SOURCE_AUDIT.csv")
    summary=json.loads((ROOT/"SOURCE_SUMMARY.json").read_text())
    folds=table(CV,"FOLD_MANIFEST.csv")
    pred=table(ROOT,"OOF_PREDICTIONS.csv")
    repeat=table(ROOT,"REPEAT_METRICS.csv")
    opt=json.loads((ROOT/"OPTIMIZATION.json").read_text())
    chk={}
    chk["372_new_unique_features_no_test"]=len(features)==len(audit)==len(dev)==372 and {r["subject_id"] for r in features}==dev and not ({r["subject_id"] for r in features}&test)
    chk["source_gate_and_budget"]=summary["source_gate"]=="PASS" and summary["requests_in_script"]+summary["preflight_observation_requests"]<=1200 and summary["bytes_in_script"]<=180*1024*1024 and all(r["observation_status"]==r["left_status"]==r["right_status"]=="OK" for r in audit)
    chk["25_fits_converged"]=len(opt["fits"])==25 and all(v["converged"] for v in opt["fits"].values())
    fold_map={(int(r["repeat"]),r["subject_id"]):int(r["fold"]) for r in folds}
    chk["1860_oof_unique_and_same_folds"]=len(pred)==1860 and len({(r["repeat"],r["subject_id"]) for r in pred})==1860 and all(r["subject_id"] in dev and int(r["fold"])==fold_map[(int(r["repeat"]),r["subject_id"])] for r in pred)
    chk["probabilities_sum_to_one"]=all(abs(sum(float(r[k]) for k in ("p_HC","p_PD","p_DD"))-1)<1e-9 for r in pred)
    by_repeat=defaultdict(list)
    for r in pred:by_repeat[int(r["repeat"])].append(r)
    chk["m4_repeat_metrics_recomputed"]=len(repeat)==5 and all(abs(score(by_repeat[int(r["repeat"])])[0]-float(r["m4_loss"]))<1e-12 and abs(score(by_repeat[int(r["repeat"])])[1]-float(r["m4_bacc"]))<1e-12 for r in repeat)
    qualified=sum(float(r["m4_vs_m1_loss_improvement"])>=.02 and float(r["m4_vs_m1_bacc_improvement"])>=.03 for r in repeat)
    chk["frozen_gate_recomputed"]=qualified==5 and all(float(r["m4_vs_m1_loss_improvement"])>=0 and float(r["m4_vs_m1_bacc_improvement"])>=0 for r in repeat)
    result={"run_id":"EXP028-VERIFY-001","checks":chk,"passed":sum(chk.values()),"total":len(chk),"all_passed":all(chk.values()),"qualified_repeats":qualified,"scope":"EXP028 outputs plus direct EXP026/027 references; no refit or test"}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if not result["all_passed"]:raise SystemExit(2)


if __name__=="__main__":main()
