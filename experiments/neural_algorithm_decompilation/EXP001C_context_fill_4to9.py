#!/usr/bin/env python3
import os, json, math, random, csv, re
from collections import defaultdict

import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

SEED = 20261006
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)

MODEL_ID = os.environ.get("MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")
NS = [2, 4, 6]
WORLDS = int(os.environ.get("WORLDS", "16"))
OUTDIR = os.environ.get("OUTDIR", "outputs")
os.makedirs(OUTDIR, exist_ok=True)

torch.set_grad_enabled(False)
torch.set_num_threads(max(1, min(4, os.cpu_count() or 2)))

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
if tokenizer.pad_token_id is None:
    tokenizer.pad_token = tokenizer.eos_token

model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
)
model.eval()

keys_all = list("ABCDEF")

templates = [
    "Temporary table:\n{bindings}\nReturn the values for keys in this exact order: {order}.\nReply only with the digits separated by single spaces.",
    "Read this short lookup table exactly:\n{bindings}\nRequested key order: {order}.\nOutput only the corresponding digits, separated by one space.",
    "Store these bindings for this reply:\n{bindings}\nGive the values in this order: {order}.\nDigits only; use spaces between digits.",
    "Use the following temporary bindings:\n{bindings}\nAnswer the key sequence {order}.\nReturn only digits separated by spaces.",
]

def make_user_prompt(keys, values, order, template_idx):
    bindings = "\n".join(f"{k} = {values[k]}" for k in keys)
    return templates[template_idx % len(templates)].format(
        bindings=bindings, order=" ".join(order)
    )

def chat_prompt(user_text):
    return tokenizer.apply_chat_template(
        [{"role":"user","content":user_text}],
        tokenize=False,
        add_generation_prompt=True,
    )

def build_item(keys, order, edit_slot, template_idx):
    values = {k: 4 for k in keys}
    if edit_slot is not None:
        values[order[edit_slot]] = 9
    user = make_user_prompt(keys, values, order, template_idx)
    cp = chat_prompt(user)
    answer_digits = [str(values[k]) for k in order]
    answer = " ".join(answer_digits)

    prompt_ids = tokenizer(cp, add_special_tokens=False)["input_ids"]
    ans_enc = tokenizer(answer, add_special_tokens=False, return_offsets_mapping=True)
    answer_ids = ans_enc["input_ids"]
    offsets = ans_enc["offset_mapping"]
    full_ids = prompt_ids + answer_ids + [tokenizer.eos_token_id]

    digit_char_positions = []
    cursor = 0
    for j, d in enumerate(answer_digits):
        pos = answer.find(d, cursor)
        digit_char_positions.append(pos)
        cursor = pos + 1

    digit_token_indices = []
    for pos in digit_char_positions:
        hit = None
        for ti, (a,b) in enumerate(offsets):
            if a <= pos < b:
                hit = ti
                break
        digit_token_indices.append(hit)

    return {
        "user": user,
        "chat_prompt": cp,
        "answer": answer,
        "answer_digits": answer_digits,
        "prompt_ids": prompt_ids,
        "answer_ids": answer_ids,
        "full_ids": full_ids,
        "digit_token_indices": digit_token_indices,
    }

def pad_batch(items):
    maxlen = max(len(x["full_ids"]) for x in items)
    B = len(items)
    ids = torch.full((B,maxlen), tokenizer.pad_token_id, dtype=torch.long)
    mask = torch.zeros((B,maxlen), dtype=torch.long)
    for i,x in enumerate(items):
        seq = torch.tensor(x["full_ids"], dtype=torch.long)
        ids[i,:len(seq)] = seq
        mask[i,:len(seq)] = 1
    return ids, mask

def score_and_hidden(items):
    ids, mask = pad_batch(items)
    out = model(
        input_ids=ids,
        attention_mask=mask,
        output_hidden_states=True,
        use_cache=False,
        return_dict=True,
    )
    hs = out.hidden_states
    logits = out.logits

    # [B, layers+1, D] at final prompt token
    H = []
    for b,x in enumerate(items):
        p = len(x["prompt_ids"]) - 1
        H.append(torch.stack([h[b,p].cpu() for h in hs], dim=0))
    H = torch.stack(H, dim=0).numpy()

    rows = []
    for b,x in enumerate(items):
        plen = len(x["prompt_ids"])
        answer_ids = x["answer_ids"]
        # teacher-forced answer token accuracy
        correct = 0
        total = 0
        nll = 0.0
        for ai,tok in enumerate(answer_ids):
            pred_pos = plen + ai - 1
            lp = torch.log_softmax(logits[b,pred_pos], dim=-1)
            nll -= float(lp[tok].item())
            correct += int(int(torch.argmax(logits[b,pred_pos]).item()) == int(tok))
            total += 1
        rows.append({
            "answer_nll": nll / max(total,1),
            "answer_token_acc": correct / max(total,1),
        })
    return H, logits.cpu(), rows

def target_margin(logits, item, batch_index, edit_slot):
    if edit_slot is None:
        return None
    ti = item["digit_token_indices"][edit_slot]
    if ti is None:
        return None
    # Build wrong answer differing only at the edited output digit.
    wrong_digits = item["answer_digits"].copy()
    wrong_digits[edit_slot] = "4"
    wrong_answer = " ".join(wrong_digits)
    wrong_enc = tokenizer(wrong_answer, add_special_tokens=False, return_offsets_mapping=True)
    if len(wrong_enc["input_ids"]) != len(item["answer_ids"]):
        return None
    wrong_offsets = wrong_enc["offset_mapping"]
    char_pos = wrong_answer.find("0", 0)
    # locate edited slot char robustly
    cursor = 0
    positions = []
    for d in wrong_digits:
        p = wrong_answer.find(d, cursor)
        positions.append(p); cursor=p+1
    pos = positions[edit_slot]
    wrong_ti = None
    for wi,(a,b) in enumerate(wrong_offsets):
        if a <= pos < b:
            wrong_ti = wi; break
    if wrong_ti is None or wrong_ti != ti:
        return None
    correct_tok = item["answer_ids"][ti]
    wrong_tok = wrong_enc["input_ids"][wrong_ti]
    pred_pos = len(item["prompt_ids"]) + ti - 1
    return float(logits[batch_index,pred_pos,correct_tok] - logits[batch_index,pred_pos,wrong_tok])

records = []
# Store deltas indexed by (n, layer, world, perm, slot)
deltas = {}
orders = {}
sample_generations = []

for n in NS:
    keys = keys_all[:n]
    for w in range(WORLDS):
        rng = random.Random(SEED + 1000*n + w)
        p1 = keys.copy(); rng.shuffle(p1)
        shift = rng.randint(1,n-1)
        p2 = p1[shift:] + p1[:shift]
        for pi,order in enumerate([p1,p2]):
            orders[(n,w,pi)] = order
            items = [build_item(keys, order, None, w+pi)]
            meta = [None]
            for s in range(n):
                items.append(build_item(keys, order, s, w+pi))
                meta.append(s)
            H, logits, scores = score_and_hidden(items)
            baseH = H[0]
            for bi,s in enumerate(meta):
                margin = target_margin(logits, items[bi], bi, s)
                records.append({
                    "n":n, "world":w, "perm":pi, "edit_slot":-1 if s is None else s,
                    "answer":items[bi]["answer"],
                    "answer_nll":scores[bi]["answer_nll"],
                    "answer_token_acc":scores[bi]["answer_token_acc"],
                    "target_margin_9_vs_4":margin,
                })
                if s is not None:
                    for layer in range(H.shape[1]):
                        deltas[(n,layer,w,pi,s)] = H[bi,layer] - baseH[layer]

        # Greedy behavior only for one world per n, two variants.
        if w == 0:
            order = p1
            for s in [None, min(1,n-1)]:
                it = build_item(keys, order, s, w)
                inp = torch.tensor([it["prompt_ids"]], dtype=torch.long)
                gen = model.generate(
                    input_ids=inp,
                    max_new_tokens=18,
                    do_sample=False,
                    pad_token_id=tokenizer.pad_token_id,
                    eos_token_id=tokenizer.eos_token_id,
                )
                txt = tokenizer.decode(gen[0, inp.shape[1]:], skip_special_tokens=True)
                sample_generations.append({
                    "n":n, "edit_slot":-1 if s is None else s,
                    "order":" ".join(order),
                    "expected":it["answer"],
                    "generated":txt.strip(),
                })

def cosine(a,b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12: return np.nan
    return float(np.dot(a,b)/(na*nb))

def layer_analysis(n, layer):
    # prototypes and split-half nearest-centroid slot decoding
    X=[]; y=[]; world_ids=[]
    for w in range(WORLDS):
        for pi in [0,1]:
            for s in range(n):
                d=deltas[(n,layer,w,pi,s)]
                norm=np.linalg.norm(d)
                if norm>1e-12:
                    X.append(d/norm); y.append(s); world_ids.append(w)
    X=np.asarray(X); y=np.asarray(y); world_ids=np.asarray(world_ids)
    if len(X) == 0:
        return {
            "n":n, "layer":layer,
            "slot_decode_acc":None,
            "effective_rank_pr":0.0,
            "rank90":0,
            "same_key_cos":None,
            "same_slot_cos":None,
            "slot_minus_key_cos":None,
            "mean_delta_norm":0.0,
            "sv":[],
        }

    prot=[]
    for s in range(n):
        m=X[y==s].mean(0)
        if np.linalg.norm(m)>1e-12: m=m/np.linalg.norm(m)
        prot.append(m)
    P=np.stack(prot)
    sv=np.linalg.svd(P,compute_uv=False)
    energy=sv**2
    if energy.sum()>0:
        p=energy/energy.sum()
        pr=1.0/np.sum(p**2)
        cum=np.cumsum(p)
        rank90=int(np.searchsorted(cum,0.90)+1)
    else:
        pr=np.nan; rank90=0

    accs=[]
    for parity in [0,1]:
        tr=(world_ids%2)==parity
        te=~tr
        train_prot=[]
        for s in range(n):
            m=X[tr & (y==s)].mean(0)
            if np.linalg.norm(m)>1e-12: m=m/np.linalg.norm(m)
            train_prot.append(m)
        TP=np.stack(train_prot)
        pred=np.argmax(X[te]@TP.T,axis=1)
        accs.append(float(np.mean(pred==y[te])))
    slot_decode=float(np.mean(accs))

    same_key=[]; same_slot=[]
    for w in range(WORLDS):
        o1=orders[(n,w,0)]; o2=orders[(n,w,1)]
        for key in o1:
            s1=o1.index(key); s2=o2.index(key)
            same_key.append(cosine(deltas[(n,layer,w,0,s1)], deltas[(n,layer,w,1,s2)]))
        for s in range(n):
            same_slot.append(cosine(deltas[(n,layer,w,0,s)], deltas[(n,layer,w,1,s)]))
    same_key=np.asarray(same_key,dtype=float)
    same_slot=np.asarray(same_slot,dtype=float)

    norms=[np.linalg.norm(deltas[(n,layer,w,pi,s)])
           for w in range(WORLDS) for pi in [0,1] for s in range(n)]

    return {
        "n":n, "layer":layer,
        "slot_decode_acc":slot_decode,
        "effective_rank_pr":float(pr),
        "rank90":rank90,
        "same_key_cos":float(np.nanmean(same_key)),
        "same_slot_cos":float(np.nanmean(same_slot)),
        "slot_minus_key_cos":float(np.nanmean(same_slot)-np.nanmean(same_key)),
        "mean_delta_norm":float(np.mean(norms)),
        "sv":sv.tolist(),
    }

n_layers = max(k[1] for k in deltas.keys()) + 1
analysis=[]
for n in NS:
    for layer in range(n_layers):
        analysis.append(layer_analysis(n,layer))

# Cross-n alignment of slot prototypes for shared slot indices.
cross_n=[]
def prototype(n,layer,s):
    arr=[]
    for w in range(WORLDS):
        for pi in [0,1]:
            d=deltas[(n,layer,w,pi,s)]
            z=np.linalg.norm(d)
            if z>1e-12: arr.append(d/z)
    m=np.mean(arr,axis=0)
    return m/(np.linalg.norm(m)+1e-12)

for layer in range(n_layers):
    for a,b in [(2,4),(4,6),(2,6)]:
        vals=[]
        for s in range(min(a,b)):
            vals.append(cosine(prototype(a,layer,s), prototype(b,layer,s)))
        cross_n.append({
            "layer":layer,"n_a":a,"n_b":b,
            "shared_slot_proto_cos":float(np.nanmean(vals))
        })

# Summary layer per n: prioritize slot decodability, then slot-over-key.
summary={}
for n in NS:
    rows=[r for r in analysis if r["n"]==n]
    valid=[r for r in rows if r["slot_decode_acc"] is not None and r["slot_minus_key_cos"] is not None]
    best=max(valid,key=lambda r:(r["slot_decode_acc"],r["slot_minus_key_cos"]))
    summary[str(n)]=best

# Behavior aggregate on edited variants only
edited=[r for r in records if r["edit_slot"]>=0]
behavior={}
for n in NS:
    rr=[r for r in edited if r["n"]==n]
    margins=[r["target_margin_9_vs_4"] for r in rr if r["target_margin_9_vs_4"] is not None]
    behavior[str(n)]={
        "mean_answer_token_acc":float(np.mean([r["answer_token_acc"] for r in rr])),
        "mean_answer_nll":float(np.mean([r["answer_nll"] for r in rr])),
        "margin_available":len(margins),
        "mean_target_margin_9_vs_4":float(np.mean(margins)) if margins else None,
        "fraction_positive_target_margin":float(np.mean(np.asarray(margins)>0)) if margins else None,
    }

with open(os.path.join(OUTDIR,"sample_generations.json"),"w") as f:
    json.dump(sample_generations,f,indent=2)
with open(os.path.join(OUTDIR,"behavior_records.json"),"w") as f:
    json.dump(records,f,indent=2)
with open(os.path.join(OUTDIR,"layer_analysis.json"),"w") as f:
    json.dump(analysis,f,indent=2)
with open(os.path.join(OUTDIR,"cross_n_alignment.json"),"w") as f:
    json.dump(cross_n,f,indent=2)
with open(os.path.join(OUTDIR,"summary.json"),"w") as f:
    json.dump({
        "model":MODEL_ID,
        "seed":SEED,
        "worlds":WORLDS,
        "n_values":NS,
        "hidden_states":n_layers,
        "behavior":behavior,
        "best_layers":summary,
        "sample_generations":sample_generations,
        "operational_definition":{
            "slot":"A reproducible context-edit direction at the final prompt state indexed by requested output position.",
            "fixed_vs_variable":"Whether effective rank/rank90 of slot prototypes saturates or grows as requested output length n increases.",
            "fill_rule":"Whether identical 4->9 source edits align more strongly by source-key identity or by requested output slot after changing the request permutation."
        }
    },f,indent=2)

# CSV for easy inspection
with open(os.path.join(OUTDIR,"layer_analysis.csv"),"w",newline="") as f:
    fields=["n","layer","slot_decode_acc","effective_rank_pr","rank90","same_key_cos","same_slot_cos","slot_minus_key_cos","mean_delta_norm"]
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for r in analysis:
        w.writerow({k:r[k] for k in fields})

print(json.dumps({
    "model":MODEL_ID,
    "behavior":behavior,
    "best_layers":summary,
    "sample_generations":sample_generations,
}, indent=2))
