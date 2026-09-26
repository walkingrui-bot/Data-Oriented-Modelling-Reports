#!/usr/bin/env python3
"""
TOOL-CALL-002 — Partial Operator Validator

Deterministically checks whether a proposed tool action is inside the currently
admissible executable set. It does not judge semantic usefulness; it checks the
hard execution domain.

Usage:
  python TOOL_CALL_002_partial_operator_guard.py cases
  python TOOL_CALL_002_partial_operator_guard.py validate \
      --case BFCL_simple_python_0 \
      --proposal '{"mode":"CALL","calls":[{"name":"calculate_triangle_area","arguments":{"base":10,"height":5}}]}'
"""
import argparse,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
CONTRACTS=json.loads((HERE/"TOOL_CALL_002_guard_contracts.json").read_text())

def typ_ok(v,t):
    if t=="number": return isinstance(v,(int,float)) and not isinstance(v,bool)
    if t=="string": return isinstance(v,str)
    if t=="array": return isinstance(v,list)
    if t=="boolean": return isinstance(v,bool)
    return True

def validate(case,proposal):
    c=CONTRACTS[case]
    mode=proposal.get("mode")
    calls=proposal.get("calls",[])
    problems=[]
    if mode not in c["allowed_modes"]:
        problems.append({"gate":"MODE","error":f"{mode} not in allowed modes {c['allowed_modes']}"})

    if mode in ("ABSTAIN","ASK","WAIT"):
        if calls:
            problems.append({"gate":"CARDINALITY","error":f"{mode} must not execute calls"})
        return {"admissible":not problems,"problems":problems}

    if c.get("expected_cardinality") is not None and len(calls)!=c["expected_cardinality"]:
        problems.append({"gate":"CALL_SET_CARDINALITY",
                         "error":f"expected {c['expected_cardinality']} calls, got {len(calls)}"})

    reg=c["registry"]
    for i,call in enumerate(calls):
        name=call.get("name")
        args=call.get("arguments",{})
        if name not in reg:
            problems.append({"gate":"REGISTRY","call":i,"error":f"unregistered tool {name}"})
            continue
        sch=reg[name]
        missing=[k for k in sch["required"] if k not in args]
        if missing:
            problems.append({"gate":"BINDING_COMPLETE","call":i,"error":f"missing required arguments: {missing}"})
        allowed=set(sch["required"])|set(sch["optional"])
        extra=[k for k in args if k not in allowed]
        if extra:
            problems.append({"gate":"SCHEMA","call":i,"error":f"unexpected arguments: {extra}"})
        for k,t in {**sch["required"],**sch["optional"]}.items():
            if k in args and not typ_ok(args[k],t):
                problems.append({"gate":"TYPE","call":i,"error":f"{k} expected {t}, got {type(args[k]).__name__}"})
    return {"admissible":not problems,"problems":problems}

def main():
    ap=argparse.ArgumentParser()
    sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("cases")
    p=sp.add_parser("validate")
    p.add_argument("--case",required=True,choices=list(CONTRACTS))
    p.add_argument("--proposal",required=True)
    args=ap.parse_args()
    if args.cmd=="cases":
        print(json.dumps(list(CONTRACTS),indent=2));return
    proposal=json.loads(args.proposal)
    result=validate(args.case,proposal)
    print(json.dumps({"case":args.case,"proposal":proposal,**result},indent=2))

if __name__=="__main__":
    main()
