#!/usr/bin/env python3
import os, json, random, csv
from pathlib import Path
from collections import Counter
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.linear_model import RidgeClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import StratifiedKFold

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
SEED=20261006
DIGITS=["1","2","3","4","5","6"]
KS=[2,3,4,5,6]
N=120
DEPTHS=[0,6,12,18,24]
OUT=Path("probe_only_results"); OUT.mkdir(exist_ok=True)
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(min(4,os.cpu_count() or 2))

def seqs_balanced(k):
    rng=np.random.default_rng(SEED+k)
    cols=[]
    base=np.array(DIGITS*(N//len(DIGITS)),dtype=object)
    for j in range(k):
        c=base.copy(); rng.shuffle(c); cols.append(c)
    return np.stack(cols,axis=1).tolist()

def prompt(tok,seq):
    u="Copy the sequence exactly. Return only the sequence with spaces between items. Sequence: "+" ".join(seq)
    return tok.apply_chat_template([{"role":"user","content":u}],tokenize=False,add_generation_prompt=True)

def cvacc(X,y):
    y=np.asarray(y)
    sk=StratifiedKFold(n_splits=5,shuffle=True,random_state=SEED)
    vals=[]
    for tr,te in sk.split(X,y):
        m=make_pipeline(StandardScaler(),RidgeClassifier(alpha=10.0))
        m.fit(X[tr],y[tr]); vals.append(np.mean(m.predict(X[te])==y[te]))
    return float(np.mean(vals))

def block(X,y):
    y=np.asarray(y); mus=[]
    for d in DIGITS:
        mus.append(X[y==d].mean(0))
    M=np.stack(mus); return M-M.mean(0,keepdims=True)

def basis(B):
    _,s,vt=np.linalg.svd(B,full_matrices=False)
    e=s*s
    r=max(1,int(np.searchsorted(np.cumsum(e)/e.sum(),0.90)+1))
    return vt[:r].T, s

def overlap(Q1,Q2):
    r=min(Q1.shape[1],Q2.shape[1])
    return float(np.linalg.norm(Q1.T@Q2,"fro")**2/r)

def prank(blocks):
    M=np.concatenate([b/(np.linalg.norm(b)+1e-12) for b in blocks],axis=0)
    s=np.linalg.svd(M,compute_uv=False); e=s*s
    return float((e.sum()**2)/(np.sum(e*e)+1e-12)), int(np.searchsorted(np.cumsum(e)/e.sum(),.95)+1)

print("loading",MODEL,flush=True)
tok=AutoTokenizer.from_pretrained(MODEL,use_fast=True)
if tok.pad_token_id is None: tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(MODEL,torch_dtype=torch.float32,low_cpu_mem_usage=True)
model.eval(); print("loaded",flush=True)

digit_ids={d:tok(d,add_special_tokens=False)["input_ids"][0] for d in DIGITS}
rows=[]; rank_rows=[]; overlap_rows=[]; basis_store={}

for k in KS:
    S=seqs_balanced(k)
    Hparts=[]; Lparts=[]
    for b0 in range(0,N,30):
        sub=S[b0:b0+30]
        texts=[prompt(tok,s) for s in sub]
        enc=tok(texts,return_tensors="pt",padding=True,add_special_tokens=False)
        lens=enc.attention_mask.sum(1)-1
        with torch.inference_mode():
            o=model(**enc,output_hidden_states=True,use_cache=False,return_dict=True)
        hs=[]
        for dep in DEPTHS:
            hs.append(o.hidden_states[dep][torch.arange(len(sub)),lens,:].float().cpu().numpy())
        Hparts.append(np.stack(hs,1))
        Lparts.append(o.logits[torch.arange(len(sub)),lens,:].float().cpu().numpy())
    H=np.concatenate(Hparts); logits=np.concatenate(Lparts)
    next_pred=np.argmax(logits[:,[digit_ids[d] for d in DIGITS]],axis=1)
    next_acc=float(np.mean(np.array(DIGITS,dtype=object)[next_pred]==np.array([s[0] for s in S],dtype=object)))
    print("k",k,"next_acc",next_acc,flush=True)

    for di,dep in enumerate(DEPTHS):
        Bs=[]; Qs=[]
        for off in range(k):
            y=np.array([s[off] for s in S],dtype=object)
            a=cvacc(H[:,di,:],y)
            B=block(H[:,di,:],y); Q,_=basis(B)
            Bs.append(B); Qs.append(Q)
            basis_store[(k,dep,off)]=Q
            rows.append({"k":k,"depth":dep,"future_offset":off+1,"probe_acc":a,"chance":1/6,"next_token_acc":next_acc})
        er,r95=prank(Bs)
        rank_rows.append({"k":k,"depth":dep,"future_items":k,"effective_rank":er,"rank95":r95})
        ovs=[]
        for a in range(k):
            for b in range(a+1,k):
                v=overlap(Qs[a],Qs[b]); ovs.append(v)
                overlap_rows.append({"k":k,"depth":dep,"slot_a":a+1,"slot_b":b+1,"overlap":v})
        print(" depth",dep,"rank",er,"mean_overlap",float(np.mean(ovs)) if ovs else None,flush=True)

cross=[]
for dep in DEPTHS:
    for ka,kb in zip(KS[:-1],KS[1:]):
        m=min(ka,kb)
        vals=[overlap(basis_store[(ka,dep,s)],basis_store[(kb,dep,s)]) for s in range(m)]
        cross.append({"depth":dep,"k_a":ka,"k_b":kb,"shared_offset_overlap":float(np.mean(vals))})

with open(OUT/"probe.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
with open(OUT/"rank.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rank_rows[0].keys()); w.writeheader(); w.writerows(rank_rows)
with open(OUT/"overlap.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=overlap_rows[0].keys()); w.writeheader(); w.writerows(overlap_rows)
with open(OUT/"cross_length.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cross[0].keys()); w.writeheader(); w.writerows(cross)

summary={}
for k in KS:
    q=[r for r in rows if r["k"]==k and r["depth"]==24]
    rr=[r for r in rank_rows if r["k"]==k and r["depth"]==24][0]
    oo=[r["overlap"] for r in overlap_rows if r["k"]==k and r["depth"]==24]
    summary[str(k)]={
        "next_token_acc":q[0]["next_token_acc"],
        "layer24_probe_by_offset":[r["probe_acc"] for r in q],
        "layer24_effective_rank":rr["effective_rank"],
        "layer24_rank95":rr["rank95"],
        "layer24_mean_pairwise_slot_overlap":float(np.mean(oo)) if oo else None
    }
with open(OUT/"summary.json","w") as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2),flush=True)
