#!/usr/bin/env python3
"""
RELATIONAL-ARITY-005 reproduction skeleton.

Input:
  Local copies of the exact Universal Dependencies test .conllu blobs listed in
  source_manifest.csv. External corpus text is intentionally not bundled.

Computes:
  explicit predicate-local arity, role frequencies, sentence-complexity
  quartiles, sentence-level correlations, and abstract/realization covariance
  geometry.

The executed artifact tables in this evidence package are the authoritative
outputs from the 2026-09-27 run.
"""
import re, math, json
from pathlib import Path
import numpy as np
import pandas as pd

ROLES = ["nsubj","csubj","obj","iobj","ccomp","xcomp","obl"]

def base_rel(x): return x.split(":")[0]

def parse_conllu(path):
    sents=[]; cur=[]
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            if cur: sents.append(cur); cur=[]
            continue
        if line.startswith("#"): continue
        f=line.split("\t")
        if len(f)<8 or "-" in f[0] or "." in f[0]: continue
        try: idx,head=int(f[0]),int(f[6])
        except ValueError: continue
        cur.append(dict(id=idx,upos=f[3],head=head,deprel=f[7]))
    if cur: sents.append(cur)
    return sents

def predicate_vectors(sent):
    children={}
    for t in sent: children.setdefault(t["head"],[]).append(t)
    out=[]
    for t in sent:
        ch=children.get(t["id"],[])
        has_cop=any(base_rel(x["deprel"])=="cop" for x in ch)
        has_part=any(base_rel(x["deprel"]) in ROLES for x in ch)
        is_pred=(t["upos"]=="VERB" or
                 (t["upos"] in {"ADJ","NOUN","PROPN"} and has_cop) or
                 (t["upos"]=="AUX" and has_part))
        if not is_pred: continue
        counts=np.zeros(len(ROLES),dtype=float)
        offsets=np.zeros(len(ROLES),dtype=float)
        for x in ch:
            r=base_rel(x["deprel"])
            if r in ROLES:
                j=ROLES.index(r); counts[j]+=1
                offsets[j]+=(x["id"]-t["id"])/max(1,len(sent))
        mean_offsets=np.divide(offsets,counts,out=np.zeros_like(offsets),where=counts>0)
        out.append((counts,np.concatenate([counts,mean_offsets])))
    return out

if __name__ == "__main__":
    print("Use source_manifest.csv to obtain the exact blobs, then apply the functions above.")
