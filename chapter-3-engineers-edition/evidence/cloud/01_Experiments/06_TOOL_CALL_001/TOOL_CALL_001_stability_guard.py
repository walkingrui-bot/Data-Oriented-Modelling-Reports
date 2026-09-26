#!/usr/bin/env python3
"""
TOOL-CALL-001 — Tool Stability Guard

Works on exported tool-choice telemetry. No model-specific code is required.

Expected NPZ fields:
  action_names: [A] strings
  logits:       [N,A]
  logit_grads:  [N,A,D]  gradient of each action logit wrt chosen hidden state
Optional:
  registries:   object array/list of valid action-name lists per sample
  sample_ids:   [N]

Commands:
  inspect telemetry.npz
  calibrate clean.npz --out thresholds.json
  check run.npz --thresholds thresholds.json
"""
import argparse, json, numpy as np
from pathlib import Path

def load(path):
    r=np.load(path,allow_pickle=True)
    out={k:r[k] for k in r.files}
    out["action_names"]=[str(x) for x in out["action_names"]]
    return out

def sample_metrics(d):
    names=d["action_names"]; logits=d["logits"]; grads=d["logit_grads"]
    regs=d.get("registries",None)
    rows=[]
    for i in range(len(logits)):
        z=logits[i]
        order=np.argsort(z)
        w=int(order[-1]); r=int(order[-2])
        margin=float(z[w]-z[r])
        g=grads[i,w]-grads[i,r]
        radius=margin/(np.linalg.norm(g)+1e-30)

        valid=set(names if regs is None else list(regs[i]))
        valid_idx=[j for j,n in enumerate(names) if n in valid]
        invalid_idx=[j for j,n in enumerate(names) if n not in valid]
        if valid_idx:
            bestv=max(valid_idx,key=lambda j:z[j])
            zv=float(z[bestv])
        else:
            bestv=None; zv=float("-inf")
        if invalid_idx:
            besti=max(invalid_idx,key=lambda j:z[j])
            zi=float(z[besti])
        else:
            besti=None; zi=float("-inf")

        if bestv is not None and besti is not None:
            rm=zv-zi
            rg=grads[i,bestv]-grads[i,besti]
            reg_radius=float(rm/(np.linalg.norm(rg)+1e-30))
        elif bestv is None and besti is not None:
            rm=float("-inf"); reg_radius=float("-inf")
        else:
            rm=float("inf"); reg_radius=float("inf")

        rows.append({
            "sample":int(i),
            "winner":names[w],
            "runner_up":names[r],
            "selection_margin":margin,
            "tool_stability_radius":float(radius),
            "winner_is_registered":bool(names[w] in valid),
            "registry_margin":float(rm),
            "registry_escape_radius":float(reg_radius),
        })
    return rows

def finite(x):
    return [v for v in x if np.isfinite(v)]

def calibrate(rows):
    stab=np.array(finite([r["tool_stability_radius"] for r in rows]))
    reg=np.array(finite([r["registry_escape_radius"] for r in rows]))
    return {
      "tool_stability_radius_p01":float(np.quantile(stab,.01)) if len(stab) else None,
      "tool_stability_radius_p05":float(np.quantile(stab,.05)) if len(stab) else None,
      "registry_escape_radius_p01":float(np.quantile(reg,.01)) if len(reg) else None,
      "registry_escape_radius_p05":float(np.quantile(reg,.05)) if len(reg) else None,
      "rule":"Flag below clean p01 as critical; p01–p05 as warning. Recalibrate per model/tool registry."
    }

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    p=sp.add_parser("inspect"); p.add_argument("npz")
    p=sp.add_parser("calibrate"); p.add_argument("npz"); p.add_argument("--out",required=True)
    p=sp.add_parser("check"); p.add_argument("npz"); p.add_argument("--thresholds",required=True)
    args=ap.parse_args()
    d=load(args.npz); rows=sample_metrics(d)

    if args.cmd=="inspect":
        print(json.dumps(rows,indent=2)); return
    if args.cmd=="calibrate":
        th=calibrate(rows)
        Path(args.out).write_text(json.dumps(th,indent=2))
        print(json.dumps(th,indent=2)); return
    th=json.loads(Path(args.thresholds).read_text())
    for r in rows:
        sr=r["tool_stability_radius"]; rr=r["registry_escape_radius"]
        if not r["winner_is_registered"]:
            status="BLOCK_UNREGISTERED"
        elif np.isfinite(rr) and rr < th["registry_escape_radius_p01"]:
            status="CRITICAL_REGISTRY_BOUNDARY"
        elif sr < th["tool_stability_radius_p01"]:
            status="CRITICAL_TOOL_BOUNDARY"
        elif sr < th["tool_stability_radius_p05"]:
            status="WARN_TOOL_BOUNDARY"
        else:
            status="OK"
        r["status"]=status
    print(json.dumps(rows,indent=2))

if __name__=="__main__":
    main()
