"""EXP026-VERIFY-001: audit only this study's saved predictions and source counts."""

import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "LOCAL_VALIDATION.json"


def table(name):
    with (ROOT/name).open(newline="") as f:
        return list(csv.DictReader(f))


def scored(rows):
    losses=[]; recalls=[]
    for k in range(3):
        subset=[r for r in rows if int(r["label"])==k]
        assert subset
        losses.append(sum(-math.log(max(float(r[["p_HC","p_PD","p_DD"][k]]),1e-300)) for r in subset)/len(subset))
        recalls.append(sum(int(r["prediction"])==k for r in subset)/len(subset))
    return sum(losses)/3,sum(recalls)/3


def main():
    if OUT.exists():
        raise FileExistsError(OUT)
    split=table("SPLIT_MANIFEST.csv")
    features=table("FEATURES.csv")
    source=table("SOURCE_AUDIT.csv")
    selection=table("MODEL_SELECTION.csv")
    predictions=table("PREDICTIONS.csv")
    summary=json.loads((ROOT/"SOURCE_SUMMARY.json").read_text())
    metrics=json.loads((ROOT/"METRICS.json").read_text())
    opt=json.loads((ROOT/"OPTIMIZATION.json").read_text())
    sm={r["subject_id"]:r for r in split}
    checks={}
    checks["469_unique_split_and_feature_ids"]=len(sm)==len(split)==len(features)==469 and {r["subject_id"] for r in features}==set(sm)
    checks["label_split_alignment"]=all(r["label"]==sm[r["subject_id"]]["label"] and r["split"]==sm[r["subject_id"]]["split"] for r in features)
    allowed={"subject_id","label","split"}|{f"q{i:02d}" for i in range(1,31)}|{f"{w}_{s}_{stat}" for w in ("left","right","absdiff") for s in ("acc","gyro") for stat in ("mean","std","p95p05","jerk_rms","band3to7_ratio")}
    checks["feature_fields_only_allowlist"]=set(features[0])==allowed
    checks["all_original_sources_readable"]=len(source)==469 and all(all(r[k]=="OK" for k in ("questionnaire_status","observation_status","left_status","right_status")) for r in source) and summary["source_gate"]=="PASS"
    checks["source_budget"]=summary["requests"]<=2000 and summary["bytes_read"]<=250*1024*1024
    checks["15_fits_converged"]=len(opt["fits"])==15 and all(v["converged"] for v in opt["fits"].values())
    checks["12_validation_candidates"]=len(selection)==12
    grouped=defaultdict(list)
    for r in predictions:
        grouped[(r["split"],r["arm"])].append(r)
    checks["prediction_rows_and_probabilities"]=len(predictions)==4*(92+97) and len({(r["split"],r["arm"],r["subject_id"]) for r in predictions})==len(predictions) and all(abs(sum(float(r[k]) for k in ("p_HC","p_PD","p_DD"))-1)<1e-9 for r in predictions)
    checks["prediction_labels_match_split"]=all(r["label"]==sm[r["subject_id"]]["label"] and r["split"]==sm[r["subject_id"]]["split"] for r in predictions)
    correct=True
    for (split_name,arm),rows in grouped.items():
        expected=metrics["M0_prior"][split_name] if arm=="M0_prior" else metrics["arms"][arm][split_name]
        loss,bacc=scored(rows)
        if abs(loss-expected["macro_log_loss"])>1e-12 or abs(bacc-expected["balanced_accuracy"])>1e-12:
            correct=False
    checks["metrics_recomputed_from_saved_predictions"]=correct and len(grouped)==8
    delta=metrics["M3_minus_M1_improvement"]
    checks["frozen_gate_recomputed"]=metrics["gate_pass"]==(delta["validation_macro_log_loss"]>=0.02 and delta["validation_balanced_accuracy"]>=0.03 and delta["test_macro_log_loss"]>0 and delta["test_balanced_accuracy"]>0)
    result={"run_id":"EXP026-VERIFY-001","checks":checks,"passed":sum(checks.values()),"total":len(checks),"all_passed":all(checks.values()),"scope":"Only EXP026 saved outputs; no source fetch or model refit"}
    OUT.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
    if not result["all_passed"]:
        raise SystemExit(2)


if __name__=="__main__":
    main()
