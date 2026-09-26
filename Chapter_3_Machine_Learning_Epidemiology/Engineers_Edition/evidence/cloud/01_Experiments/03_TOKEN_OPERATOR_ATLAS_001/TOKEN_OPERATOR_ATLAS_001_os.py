#!/usr/bin/env python3
import argparse, json, numpy as np
from pathlib import Path

BASE=Path(__file__).resolve().parent
R=np.load(BASE/"TOKEN_OPERATOR_ATLAS_001_runtime.npz")
with open(BASE/"TOKEN_OPERATOR_ATLAS_001_manifest.json","r",encoding="utf-8") as f:
    MAN=json.load(f)

TOKENS=[str(x) for x in R["token_names"]]
EMB={t:R["token_embeddings"][i].astype(float) for i,t in enumerate(TOKENS)}
W_ih=R["W_ih"]; W_hh=R["W_hh"]; b_ih=R["b_ih"]; b_hh=R["b_hh"]
H=R["state_h"]
SID=R["state_id"]; SQ=R["state_q"]; ST=R["state_t"]
SP=R["state_phase"]; SN=R["state_natural_token"]

def sigm(x): return 1.0/(1.0+np.exp(-x))

def apply(token,h):
    e=EMB[token]
    gi=W_ih@e+b_ih
    gh=W_hh@h+b_hh
    ir,iz,inn=np.split(gi,3)
    hr,hz,hn=np.split(gh,3)
    r=sigm(ir+hr); z=sigm(iz+hz)
    n=np.tanh(inn+r*hn)
    return (1-z)*n+z*h

def get_state(args):
    if args.state_id is not None:
        i=int(args.state_id)
        if i<0 or i>=len(H): raise SystemExit("state-id out of range")
        return H[i].astype(float),i
    if args.h is not None:
        vals=np.array([float(x) for x in args.h.split(",")],dtype=float)
        if len(vals)!=10: raise SystemExit("--h requires 10 comma-separated numbers")
        return vals,None
    raise SystemExit("provide --state-id or --h")

def state_meta(i):
    if i is None: return {}
    return {"state_id":int(i),"q":int(SQ[i]),"t":int(ST[i]),
            "phase":str(SP[i]),"natural_token":str(SN[i])}

def out(x):
    print(json.dumps(x,ensure_ascii=False,indent=2))

def main():
    ap=argparse.ArgumentParser(description="Token Operator OS")
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("list")

    p=sub.add_parser("state"); p.add_argument("--state-id",type=int,required=True)

    p=sub.add_parser("card"); p.add_argument("token",choices=TOKENS)

    for name in ["apply","compare","compose","order"]:
        p=sub.add_parser(name)
        if name=="apply": p.add_argument("token",choices=TOKENS)
        elif name in ["compare","order"]:
            p.add_argument("token_a",choices=TOKENS); p.add_argument("token_b",choices=TOKENS)
        else:
            p.add_argument("sequence",help="comma-separated tokens, e.g. A,0,xor,B")
        p.add_argument("--state-id",type=int)
        p.add_argument("--h")

    args=ap.parse_args()

    if args.cmd=="list":
        out({"tokens":TOKENS,"n_states":len(H)})
    elif args.cmd=="state":
        i=args.state_id
        out({**state_meta(i),"h":H[i].tolist()})
    elif args.cmd=="card":
        c=next(c for c in MAN["cards"] if c["token"]==args.token)
        out(c)
    elif args.cmd=="apply":
        h,i=get_state(args); y=apply(args.token,h)
        out({**state_meta(i),"token":args.token,"h_in":h.tolist(),"h_out":y.tolist(),
             "delta":(y-h).tolist(),"delta_norm":float(np.linalg.norm(y-h))})
    elif args.cmd=="compare":
        h,i=get_state(args); ya=apply(args.token_a,h); yb=apply(args.token_b,h)
        out({**state_meta(i),"token_a":args.token_a,"token_b":args.token_b,
             "output_distance":float(np.linalg.norm(ya-yb)),
             "delta_difference":(ya-yb).tolist()})
    elif args.cmd=="compose":
        h,i=get_state(args); seq=[x.strip() for x in args.sequence.split(",") if x.strip()]
        bad=[x for x in seq if x not in EMB]
        if bad: raise SystemExit("unknown token(s): "+",".join(bad))
        cur=h.copy(); trace=[]
        for tok in seq:
            nxt=apply(tok,cur); trace.append({"token":tok,"delta_norm":float(np.linalg.norm(nxt-cur))})
            cur=nxt
        out({**state_meta(i),"sequence":seq,"h_in":h.tolist(),"h_out":cur.tolist(),
             "total_state_change":float(np.linalg.norm(cur-h)),"trace":trace})
    elif args.cmd=="order":
        h,i=get_state(args)
        hab=apply(args.token_b,apply(args.token_a,h))
        hba=apply(args.token_a,apply(args.token_b,h))
        out({**state_meta(i),"order_ab":[args.token_a,args.token_b],
             "order_ba":[args.token_b,args.token_a],
             "state_distance":float(np.linalg.norm(hab-hba)),
             "h_ab":hab.tolist(),"h_ba":hba.tolist()})
if __name__=="__main__": main()
