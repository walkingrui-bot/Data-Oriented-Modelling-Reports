#!/usr/bin/env python3
import os, json, random, csv
from pathlib import Path
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

MODEL="Qwen/Qwen2.5-0.5B-Instruct"
SEED=20261006
NS=[2,4,6]
WORLDS=8
DIGITS=list("123456")
REPL="9"
OUT=Path("factorial_fill_results"); OUT.mkdir(exist_ok=True)
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)
torch.set_num_threads(min(4,os.cpu_count() or 2))

tok=AutoTokenizer.from_pretrained(MODEL,use_fast=True)
if tok.pad_token_id is None: tok.pad_token=tok.eos_token
model=AutoModelForCausalLM.from_pretrained(MODEL,torch_dtype=torch.float32,low_cpu_mem_usage=True)
model.eval()

keys_all=list("ABCDEF")

def chat(user):
    return tok.apply_chat_template([{"role":"user","content":user}],tokenize=False,add_generation_prompt=True)

def make_prompt(keys, values, order):
    rows="\n".join(f"{k} = {values[k]}" for k in keys)
    user=f"""Temporary lookup table:
{rows}
Return the values for these keys in exactly this order: {' '.join(order)}.
Reply only with the values separated by single spaces."""
    return chat(user)

def forward(prompts):
    enc=tok(prompts,return_tensors="pt",padding=True,add_special_tokens=False)
    lens=enc.attention_mask.sum(1)-1
    with torch.inference_mode():
        out=model(**enc,output_hidden_states=True,use_cache=False,return_dict=True)
    H=[]
    for h in out.hidden_states:
        H.append(h[torch.arange(len(prompts)),lens,:].float().cpu().numpy())
    H=np.stack(H,axis=1) # B,L,D
    logits=out.logits[torch.arange(len(prompts)),lens,:].float().cpu().numpy()
    return H,logits

digit_id={d:tok(d,add_special_tokens=False)["input_ids"][0] for d in DIGITS+[REPL]}
records=[]; behavior=[]

for n in NS:
    keys=keys_all[:n]
    for w in range(WORLDS):
        rng=random.Random(SEED+100*n+w)
        vals_digits=rng.sample(DIGITS,n)
        values=dict(zip(keys,vals_digits))
        start=rng.randrange(n)
        base_order=keys[start:]+keys[:start]
        orders=[base_order[s:]+base_order[:s] for s in range(n)]
        for pi,order in enumerate(orders):
            prompts=[make_prompt(keys,values,order)]
            edits=[]
            for source in keys:
                ev=dict(values); ev[source]=REPL
                prompts.append(make_prompt(keys,ev,order))
                edits.append(source)
            H,logits=forward(prompts)
            base=H[0]
            # baseline and edited first-output behavior, restricted digit candidates
            cand=np.array([digit_id[d] for d in DIGITS+[REPL]])
            base_expected=values[order[0]]
            base_pred=(DIGITS+[REPL])[int(np.argmax(logits[0,cand]))]
            behavior.append({"n":n,"world":w,"perm":pi,"edit_source":"BASE",
                             "expected_first":base_expected,"pred_first":base_pred,
                             "correct":int(base_pred==base_expected)})
            for bi,source in enumerate(edits, start=1):
                slot=order.index(source)
                expected = REPL if slot==0 else values[order[0]]
                pred=(DIGITS+[REPL])[int(np.argmax(logits[bi,cand]))]
                behavior.append({"n":n,"world":w,"perm":pi,"edit_source":source,
                                 "slot":slot,"expected_first":expected,"pred_first":pred,
                                 "correct":int(pred==expected)})
                for layer in range(H.shape[1]):
                    d=H[bi,layer]-base[layer]
                    records.append({"n":n,"world":w,"perm":pi,"source":source,"slot":slot,
                                    "layer":layer,"delta":d})
        print("done",n,w,flush=True)

# balanced within-world two-way ANOVA on vector deltas after removing grand mean
rows=[]
for n in NS:
  keys=keys_all[:n]
  for layer in range(25):
    world_stats=[]
    for w in range(WORLDS):
      rr=[r for r in records if r["n"]==n and r["layer"]==layer and r["world"]==w]
      X=np.stack([r["delta"] for r in rr]) # n*n,D
      src=np.array([r["source"] for r in rr])
      slot=np.array([r["slot"] for r in rr])
      grand=X.mean(0)
      total=float(np.sum((X-grand)**2))
      if total < 1e-20:
        world_stats.append((0,0,0,0))
        continue
      ss_src=0.0
      for s in keys:
        m=X[src==s].mean(0); ss_src += n*float(np.sum((m-grand)**2))
      ss_slot=0.0
      for q in range(n):
        m=X[slot==q].mean(0); ss_slot += n*float(np.sum((m-grand)**2))
      ss_res=max(0.0,total-ss_src-ss_slot)
      world_stats.append((total,ss_src,ss_slot,ss_res))
    A=np.array(world_stats,float)
    sums=A.sum(0)
    rows.append({
      "n":n,"layer":layer,
      "ss_total":sums[0],"ss_source":sums[1],"ss_slot":sums[2],"ss_residual":sums[3],
      "source_share":sums[1]/sums[0] if sums[0]>0 else None,
      "slot_share":sums[2]/sums[0] if sums[0]>0 else None,
      "residual_share":sums[3]/sums[0] if sums[0]>0 else None,
      "slot_minus_source_share":(sums[2]-sums[1])/sums[0] if sums[0]>0 else None
    })

# within-world cosine controls
def cos(a,b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    return np.nan if na<1e-12 or nb<1e-12 else float(np.dot(a,b)/(na*nb))
cosrows=[]
for n in NS:
  for layer in range(1,25):
    sk=[]; sl=[]
    for w in range(WORLDS):
      rr=[r for r in records if r["n"]==n and r["layer"]==layer and r["world"]==w]
      # same source across all pairs of slots
      for source in keys_all[:n]:
        z=[r["delta"] for r in rr if r["source"]==source]
        for i in range(len(z)):
          for j in range(i+1,len(z)): sk.append(cos(z[i],z[j]))
      # same slot across different sources
      for q in range(n):
        z=[r["delta"] for r in rr if r["slot"]==q]
        for i in range(len(z)):
          for j in range(i+1,len(z)): sl.append(cos(z[i],z[j]))
    cosrows.append({"n":n,"layer":layer,"same_source_cos":float(np.nanmean(sk)),
                    "same_slot_cos":float(np.nanmean(sl)),
                    "slot_minus_source_cos":float(np.nanmean(sl)-np.nanmean(sk))})

with open(OUT/"anova.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
with open(OUT/"cosine.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cosrows[0].keys()); w.writeheader(); w.writerows(cosrows)
with open(OUT/"behavior.csv","w",newline="") as f:
    fields=sorted(set().union(*[r.keys() for r in behavior]))
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(behavior)

summary={}
for n in NS:
    a=[r for r in rows if r["n"]==n]
    valid=[r for r in a if r["slot_share"] is not None]
    peak=max(valid,key=lambda r:r["slot_minus_source_share"])
    late=[r for r in valid if r["layer"]>=16]
    summary[str(n)]={
      "peak_slot_relative_layer":peak["layer"],
      "peak_source_share":peak["source_share"],
      "peak_slot_share":peak["slot_share"],
      "peak_slot_minus_source_share":peak["slot_minus_source_share"],
      "layer16_24":[{k:r[k] for k in ["layer","source_share","slot_share","residual_share","slot_minus_source_share"]} for r in late],
      "restricted_first_token_accuracy":float(np.mean([r["correct"] for r in behavior if r["n"]==n]))
    }
with open(OUT/"summary.json","w") as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2),flush=True)
