#!/usr/bin/env python3
"""TOOL-CALL-003 Action Readiness OS: DECIDE / CALIBRATE / TRACE."""
import argparse,json
import numpy as np
from pathlib import Path

def readj(p): return json.loads(Path(p).read_text())

def evaluate(x,th=None):
    acts=[a for a in x["actions"] if a.get("admissible",True)]
    if len(acts)<2: raise ValueError("Need >=2 admissible actions including a no-op/CONTINUE alternative")
    acts=sorted(acts,key=lambda a:a["score"],reverse=True)
    w,r=acts[0],acts[1]
    g=np.asarray(w["gradient"],float)-np.asarray(r["gradient"],float)
    margin=float(w["score"]-r["score"])
    radius=float(margin/(np.linalg.norm(g)+1e-30))
    tau=0.0 if th is None else float(th.get("radius_min_by_kind",{}).get(w["kind"],th.get("global_radius_min",0)))
    robust=radius>=tau
    mapping={"CALL":"EXECUTE","CALL_SET":"EXECUTE_SET","ASK":"ASK","WAIT":"WAIT",
             "ABSTAIN":"ABSTAIN","CONTINUE":"CONTINUE"}
    return {"state_id":x.get("state_id"),"winner":w["name"],"winner_kind":w["kind"],
            "runner_up":r["name"],"runner_kind":r["kind"],"readiness_margin":margin,
            "stability_radius":radius,"radius_threshold":tau,"robust":robust,
            "operation":mapping.get(w["kind"],w["kind"]) if robust else "HOLD_UNSTABLE",
            "hard_call_domain":x.get("hard_call_domain"),
            "nearest_boundary_gradient":g.tolist()}

def calibrate(xs):
    rs=[evaluate(x) for x in xs]; by={}
    for r in rs: by.setdefault(r["winner_kind"],[]).append(r["stability_radius"])
    allv=[r["stability_radius"] for r in rs]
    return {"global_radius_min":float(np.quantile(allv,.01)),
            "radius_min_by_kind":{k:float(np.quantile(v,.01)) for k,v in by.items() if len(v)>=2},
            "rule":"Start from clean p01. Recalibrate per model/task/tool registry; tighten for consequential actions."}

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("decide");p.add_argument("telemetry");p.add_argument("--thresholds")
    p=sp.add_parser("calibrate");p.add_argument("jsonl");p.add_argument("--out",required=True)
    p=sp.add_parser("trace");p.add_argument("jsonl");p.add_argument("--thresholds")
    a=ap.parse_args()
    if a.cmd=="calibrate":
        xs=[json.loads(s) for s in Path(a.jsonl).read_text().splitlines() if s.strip()]
        th=calibrate(xs);Path(a.out).write_text(json.dumps(th,indent=2));print(json.dumps(th,indent=2));return
    th=readj(a.thresholds) if a.thresholds else None
    if a.cmd=="decide":
        print(json.dumps(evaluate(readj(a.telemetry),th),indent=2));return
    xs=[json.loads(s) for s in Path(a.jsonl).read_text().splitlines() if s.strip()]
    rs=[evaluate(x,th) for x in xs];events=[];ready_seen=False
    for i,r in enumerate(rs):
        ready=r["operation"] in ("EXECUTE","EXECUTE_SET")
        if ready: ready_seen=True
        if ready_seen and not ready and r.get("hard_call_domain") is True:
            events.append({"step":i,"event":"TOOL_OVERTHINKING_EXIT"})
        if i>0 and ready and rs[i-1]["operation"] not in ("EXECUTE","EXECUTE_SET"):
            events.append({"step":i,"event":"CALL_REENTRY"})
    print(json.dumps({"trace":rs,"events":events},indent=2))
if __name__=="__main__":main()
