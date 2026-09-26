#!/usr/bin/env python3
"""
TOOL-CALL-004 — Semantic Tool Selection OS

Diagnose WHY a model prefers one hard-admissible tool over another.

Input JSON:
{
  "case_id": "...",
  "candidates": [
    {
      "id": "tool_A",
      "full": 3.2,
      "name_neutral": 2.8,
      "description_neutral": 1.0,
      "schema_neutral": 2.9,
      "name_only": 0.5,             # optional
      "description_only": 2.2,      # optional
      "schema_only": -0.1           # optional
    }, ...
  ],
  "correct_id": "tool_A"            # optional; include for incident analysis
}

Commands:
  diagnose incident.json
  batch incidents.jsonl
"""
import argparse, json
from pathlib import Path
import numpy as np

VIEWS=["full","name_neutral","description_neutral","schema_neutral"]

def winner(cands, field):
    vals=[float(c.get(field,float("-inf"))) for c in cands]
    order=np.argsort(vals)[::-1]
    return int(order[0]), int(order[1]), vals

def margin(vals,a,b): return float(vals[a]-vals[b])

def diagnose(x):
    c=x["candidates"]
    views={}
    for v in VIEWS:
        i,j,vals=winner(c,v)
        views[v]={
            "winner":c[i]["id"],"runner_up":c[j]["id"],
            "margin":margin(vals,i,j)
        }
    full_i,full_j,full_vals=winner(c,"full")
    selected=c[full_i]["id"]
    runner=c[full_j]["id"]

    channel_effect={}
    for neutral,channel in [
        ("name_neutral","name"),
        ("description_neutral","description"),
        ("schema_neutral","schema")
    ]:
        vals=[float(z.get(neutral,float("-inf"))) for z in c]
        # effect of neutralizing this channel on selected-vs-runner margin
        m_full=full_vals[full_i]-full_vals[full_j]
        m_neut=vals[full_i]-vals[full_j]
        channel_effect[channel]=float(m_full-m_neut)

    winners={v:d["winner"] for v,d in views.items()}
    unique=set(winners.values())
    flags=[]
    if len(unique)>1: flags.append("EVIDENCE_VIEW_DISAGREEMENT")
    if winners["name_neutral"]!=selected: flags.append("NAME_CAPTURE_RISK")
    if winners["description_neutral"]!=selected: flags.append("DESCRIPTION_CAPTURE_RISK")
    if winners["schema_neutral"]!=selected: flags.append("SCHEMA_CAPTURE_RISK")

    result={
      "case_id":x.get("case_id"),
      "selected":selected,
      "runner_up":runner,
      "views":views,
      "channel_effect_on_selected_margin":channel_effect,
      "flags":flags
    }

    correct=x.get("correct_id")
    if correct is not None:
        ids=[z["id"] for z in c]
        if correct not in ids:
            raise ValueError("correct_id not in candidates")
        ci=ids.index(correct)
        wi=full_i
        wrong=(wi!=ci)
        result["correct_id"]=correct
        result["wrong"]=wrong
        if wrong:
            base=float(full_vals[ci]-full_vals[wi])
            rescues={}
            for neutral,channel in [
                ("name_neutral","name"),
                ("description_neutral","description"),
                ("schema_neutral","schema")
            ]:
                vals=[float(z.get(neutral,float("-inf"))) for z in c]
                new=float(vals[ci]-vals[wi])
                rescues[channel]={
                    "margin_shift":new-base,
                    "new_correct_minus_selected_margin":new,
                    "flips_correct":new>0
                }
            best=max(rescues,key=lambda k:rescues[k]["margin_shift"])
            result["incident_root_channel"]=best
            result["channel_rescue"]=rescues

    # Optional channel-only evidence conflict.
    if all(all(k in z for k in ["name_only","description_only","schema_only"]) for z in c):
        ch={}
        for field in ["name_only","description_only","schema_only"]:
            vals=[float(z[field]) for z in c]
            ch[field]={
              "winner":c[int(np.argmax(vals))]["id"],
              "selected_minus_runner":float(vals[full_i]-vals[full_j])
            }
        signs=[np.sign(ch[k]["selected_minus_runner"]) for k in ch]
        result["channel_only"]=ch
        result["evidence_conflict"]=len(set(signs))>1
        pos=sum(max(ch[k]["selected_minus_runner"],0) for k in ch)
        neg=sum(max(-ch[k]["selected_minus_runner"],0) for k in ch)
        result["evidence_conflict_index"]=float(2*min(pos,neg)/(pos+neg+1e-30))

    # Portable repair plan: never assume one universal hidden axis across architectures.
    plan=[]
    if "NAME_CAPTURE_RISK" in flags:
        plan.append("Re-score with opaque/delexicalized tool IDs; map opaque ID to canonical executable name only after semantic selection.")
    if "SCHEMA_CAPTURE_RISK" in flags:
        plan.append("Separate binding compatibility from semantic tool choice; parameter-name overlap must not be allowed to choose the operator by itself.")
    if "DESCRIPTION_CAPTURE_RISK" in flags:
        plan.append("Audit candidate descriptions for overlap/ambiguity; use contrastive, discriminative descriptions and explicit negative distinctions.")
    if len(unique)>1:
        plan.append("HOLD_CONFLICT: do not execute consequential tools until multi-view disagreement is resolved.")
    if not plan:
        plan.append("No single evidence-view instability detected; inspect pairwise margin/radius and run internal Failure Axis Guard if the selected tool is known wrong.")
    result["repair_plan"]=plan
    return result

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("diagnose");p.add_argument("json")
    p=sp.add_parser("batch");p.add_argument("jsonl")
    a=ap.parse_args()
    if a.cmd=="diagnose":
        print(json.dumps(diagnose(json.loads(Path(a.json).read_text())),indent=2))
    else:
        for line in Path(a.jsonl).read_text().splitlines():
            if line.strip(): print(json.dumps(diagnose(json.loads(line))))
if __name__=="__main__":main()
