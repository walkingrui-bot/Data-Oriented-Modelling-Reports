import os, json, math, random, itertools
from pathlib import Path
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from sklearn.linear_model import RidgeClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
SEED = 20261006
DIGITS = ["1","2","3","4","5","6"]
KS = [2,3,4,5,6]
TASKS = ["copy","reverse"]
N_DEFAULT = 36
BATCH = 12
DEPTHS = list(range(0,25,2))
OUTDIR = Path("scratch/neural_blueprint_slots_qwen05b/results")
OUTDIR.mkdir(parents=True, exist_ok=True)

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.set_num_threads(min(4, os.cpu_count() or 2))

def balanced_sequences(k, n, seed):
    allp = list(itertools.permutations(DIGITS, k))
    if len(allp) <= n:
        return [list(x) for x in allp]
    rng = random.Random(seed + k)
    best, best_score = None, -1
    for _ in range(400):
        cand = rng.sample(allp, n)
        counts = []
        for pos in range(k):
            c = Counter(x[pos] for x in cand)
            counts.extend([c[d] for d in DIGITS])
        score = min(counts)
        if score > best_score:
            best_score, best = score, cand
        if best_score >= max(3, n//len(DIGITS)-1):
            break
    return [list(x) for x in best]

def user_text(task, seq):
    s = " ".join(seq)
    if task == "reverse":
        return f"Reverse the sequence. Return only the sequence with spaces between items. Sequence: {s}"
    return f"Copy the sequence exactly. Return only the sequence with spaces between items. Sequence: {s}"

def target_for(task, seq):
    return list(reversed(seq)) if task == "reverse" else list(seq)

def chat_prompt(tok, task, seq):
    return tok.apply_chat_template(
        [{"role":"user","content":user_text(task, seq)}],
        tokenize=False,
        add_generation_prompt=True
    )

def source_positions(tok, prompt_text, task, seq):
    u = user_text(task, seq)
    base = prompt_text.find(u)
    if base < 0:
        raise RuntimeError("user text not found inside chat template")
    seq_marker = "Sequence: "
    local = u.index(seq_marker) + len(seq_marker)
    starts, cursor = [], local
    for d in seq:
        j = u.find(d, cursor)
        if j < 0:
            raise RuntimeError("digit span not found")
        starts.append(base + j)
        cursor = j + len(d)
    enc = tok(prompt_text, add_special_tokens=False, return_offsets_mapping=True)
    offs = enc["offset_mapping"]
    pos = []
    for st in starts:
        hit = None
        for i,(a,b) in enumerate(offs):
            if a <= st < b:
                hit = i
                break
        if hit is None:
            raise RuntimeError(f"no token for char {st}")
        pos.append(hit)
    return pos

def cv_ridge_acc(X, y):
    y = np.asarray(y)
    counts = Counter(y.tolist())
    if len(counts) < 2 or min(counts.values()) < 3:
        return float("nan")
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=SEED)
    vals = []
    for tr,te in skf.split(X,y):
        clf = make_pipeline(StandardScaler(), RidgeClassifier(alpha=10.0))
        clf.fit(X[tr], y[tr])
        vals.append(float((clf.predict(X[te]) == y[te]).mean()))
    return float(np.mean(vals))

def coding_basis(X, y, max_rank=5):
    classes = sorted(set(y))
    mus = []
    yy = np.asarray(y)
    for c in classes:
        idx = np.where(yy == c)[0]
        mus.append(X[idx].mean(axis=0))
    M = np.stack(mus,axis=0)
    M = M - M.mean(axis=0,keepdims=True)
    if np.linalg.norm(M) < 1e-12:
        return np.zeros((X.shape[1],0),dtype=np.float32), np.array([])
    _,S,Vt = np.linalg.svd(M,full_matrices=False)
    cum = np.cumsum(S*S)/np.sum(S*S)
    r = int(np.searchsorted(cum,0.90)+1)
    r = min(r,max_rank,Vt.shape[0])
    return Vt[:r].T.astype(np.float32), S

def proj_overlap(Q1,Q2):
    if Q1.shape[1] == 0 or Q2.shape[1] == 0:
        return float("nan")
    r = min(Q1.shape[1],Q2.shape[1])
    return float(np.linalg.norm(Q1.T@Q2,ord="fro")**2 / r)

def participation_rank_from_blocks(blocks):
    mats = []
    for B in blocks:
        n = np.linalg.norm(B)
        if n > 1e-12:
            mats.append(B/n)
    if not mats:
        return float("nan"), float("nan"), 0
    M = np.concatenate(mats,axis=0)
    S = np.linalg.svd(M,compute_uv=False)
    e = S*S
    er = float((e.sum()**2)/(np.sum(e*e)+1e-12))
    cum = np.cumsum(e)/e.sum()
    r95 = int(np.searchsorted(cum,0.95)+1)
    return er,float(r95),len(mats)

def centered_centroid_block(X,y):
    classes = sorted(set(y))
    mus = []
    yy = np.asarray(y)
    for c in classes:
        idx = np.where(yy == c)[0]
        mus.append(X[idx].mean(axis=0))
    M = np.stack(mus)
    return (M-M.mean(axis=0,keepdims=True)).astype(np.float32)

print("loading",MODEL_ID,flush=True)
tok = AutoTokenizer.from_pretrained(MODEL_ID, use_fast=True)
tok.padding_side = "right"
if tok.pad_token_id is None:
    tok.pad_token = tok.eos_token
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
    attn_implementation="eager",
)
model.eval()
print("loaded",flush=True)

first_ids = {}
for d in DIGITS:
    a = tok(d,add_special_tokens=False)["input_ids"]
    if len(a) != 1:
        raise RuntimeError(f"digit not single-token: {d}: {a}")
    first_ids[d] = a[0]
space_tokenization = tok(" ",add_special_tokens=False)["input_ids"]
with open(OUTDIR/"token_ids.json","w") as f:
    json.dump({"digit":first_ids,"space_tokenization":space_tokenization},f,indent=2)

sequences = {k:balanced_sequences(k, 30 if k==2 else N_DEFAULT, SEED) for k in KS}
print({k:len(v) for k,v in sequences.items()},flush=True)

tf_rows, probe_rows, erank_rows = [], [], []
basis_store = {}

for task in TASKS:
    for k in KS:
        seqs = sequences[k]
        targets = [target_for(task,s) for s in seqs]
        for stage in range(k):
            all_h, all_logits = [], []
            for b0 in range(0,len(seqs),BATCH):
                sub = seqs[b0:b0+BATCH]
                texts = []
                for s in sub:
                    pref = target_for(task,s)[:stage]
                    ans = " ".join(pref)
                    if stage > 0:
                        ans += " "
                    texts.append(chat_prompt(tok,task,s) + ans)
                enc = tok(texts,return_tensors="pt",padding=True,add_special_tokens=False)
                lens = enc["attention_mask"].sum(dim=1)-1
                with torch.inference_mode():
                    out = model(**enc,output_hidden_states=True,use_cache=False,return_dict=True)
                H = []
                for dep in DEPTHS:
                    hs = out.hidden_states[dep]
                    gather = hs[torch.arange(hs.shape[0]),lens,:].float().cpu().numpy()
                    H.append(gather)
                all_h.append(np.stack(H,axis=1))
                all_logits.append(out.logits[torch.arange(out.logits.shape[0]),lens,:].float().cpu().numpy())
                del out
            H = np.concatenate(all_h,axis=0)
            logits = np.concatenate(all_logits,axis=0)

            next_labels = [t[stage] for t in targets]
            candidate_ids = first_ids
            cand = np.array([candidate_ids[d] for d in DIGITS],dtype=int)
            targ = np.array([candidate_ids[d] for d in next_labels],dtype=int)
            full_top1 = np.argmax(logits,axis=1)
            restricted_idx = np.argmax(logits[:,cand],axis=1)
            restricted_pred = np.array(DIGITS,dtype=object)[restricted_idx]
            restricted_acc = float(np.mean(restricted_pred == np.array(next_labels,dtype=object)))
            full_acc = float(np.mean(full_top1 == targ))
            margins = []
            for i,d in enumerate(next_labels):
                tid = candidate_ids[d]
                wrong = [candidate_ids[x] for x in DIGITS if x != d]
                margins.append(float(logits[i,tid]-np.max(logits[i,wrong])))
            tf_rows.append({
                "task":task,"k":k,"stage":stage,"n":len(seqs),
                "full_vocab_top1":full_acc,
                "restricted_digit_acc":restricted_acc,
                "digit_margin_mean":float(np.mean(margins)),
                "digit_margin_median":float(np.median(margins)),
            })

            for off in range(1,k-stage+1):
                y = np.array([t[stage+off-1] for t in targets])
                for di,dep in enumerate(DEPTHS):
                    X = H[:,di,:]
                    acc = cv_ridge_acc(X,y)
                    probe_rows.append({
                        "task":task,"k":k,"stage":stage,"depth":dep,
                        "future_offset":off,"accuracy":acc,
                        "chance":1/len(DIGITS),"n":len(y)
                    })
                    if dep in [6,12,18,24]:
                        Q,_ = coding_basis(X,y,max_rank=5)
                        basis_store[(task,k,stage,dep,off)] = Q

            for di,dep in enumerate(DEPTHS):
                blocks = []
                for off in range(1,k-stage+1):
                    y = np.array([t[stage+off-1] for t in targets])
                    blocks.append(centered_centroid_block(H[:,di,:],y))
                er,r95,nb = participation_rank_from_blocks(blocks)
                erank_rows.append({
                    "task":task,"k":k,"stage":stage,"depth":dep,
                    "remaining_items":k-stage,"effective_rank":er,
                    "rank95":r95,"blocks":nb,
                    "effective_rank_per_item":er/max(1,k-stage)
                })
            print("done",task,k,stage,"restricted",restricted_acc,flush=True)

pd.DataFrame(tf_rows).to_csv(OUTDIR/"teacher_forced.csv",index=False)
pd.DataFrame(probe_rows).to_csv(OUTDIR/"probe_accuracy.csv",index=False)
pd.DataFrame(erank_rows).to_csv(OUTDIR/"effective_rank.csv",index=False)

ov_rows = []
for task in TASKS:
    for k in KS:
        for dep in [6,12,18,24]:
            for s in range(k-1):
                q1 = basis_store.get((task,k,s,dep,1))
                q2 = basis_store.get((task,k,s+1,dep,1))
                if q1 is not None and q2 is not None:
                    ov_rows.append({"task":task,"k":k,"depth":dep,"kind":"next_slot_across_stage",
                                    "stage":s,"a_offset":1,"b_offset":1,"overlap":proj_overlap(q1,q2)})
                qa = basis_store.get((task,k,s,dep,2))
                qb = basis_store.get((task,k,s+1,dep,1))
                if qa is not None and qb is not None:
                    ov_rows.append({"task":task,"k":k,"depth":dep,"kind":"future_to_next_shift",
                                    "stage":s,"a_offset":2,"b_offset":1,"overlap":proj_overlap(qa,qb)})
            for s in range(k):
                q1 = basis_store.get((task,k,s,dep,1))
                q2 = basis_store.get((task,k,s,dep,2))
                if q1 is not None and q2 is not None:
                    ov_rows.append({"task":task,"k":k,"depth":dep,"kind":"offset1_vs_offset2_same_stage",
                                    "stage":s,"a_offset":1,"b_offset":2,"overlap":proj_overlap(q1,q2)})
pd.DataFrame(ov_rows).to_csv(OUTDIR/"subspace_overlap.csv",index=False)

tfdf = pd.DataFrame(tf_rows)
k5s0 = tfdf[(tfdf.k==5)&(tfdf.stage==0)]
rev = float(k5s0[k5s0.task=="reverse"].restricted_digit_acc.mean())
cpy = float(k5s0[k5s0.task=="copy"].restricted_digit_acc.mean())
primary = "reverse" if rev >= 0.70 else "copy"
if cpy > rev + 0.15 and rev < 0.8:
    primary = "copy"
print("primary task",primary,"reverse",rev,"copy",cpy,flush=True)

attn_rows = []
attn_examples = sequences[5][:8]
for stage in range(5):
    for ei,seq in enumerate(attn_examples):
        targ = target_for(primary,seq)
        pref = " ".join(targ[:stage])
        if stage > 0:
            pref += " "
        ptxt = chat_prompt(tok,primary,seq)
        full = ptxt + pref
        spos = source_positions(tok,ptxt,primary,seq)
        enc = tok(full,return_tensors="pt",add_special_tokens=False)
        qpos = int(enc["attention_mask"].sum().item()-1)
        correct_source = (4-stage) if primary=="reverse" else stage
        with torch.inference_mode():
            out = model(**enc,output_attentions=True,use_cache=False,return_dict=True)
        for li,A in enumerate(out.attentions):
            v = A[0,:,qpos,spos].float().cpu().numpy()
            cm = v[:,correct_source]
            sm = v.sum(axis=1)
            sel = cm/(sm+1e-12)
            hits = (v.argmax(axis=1)==correct_source)
            attn_rows.append({
                "task":primary,"example":ei,"stage":stage,"layer":li,
                "correct_source_index":correct_source,
                "mean_correct_mass":float(cm.mean()),
                "mean_source_mass":float(sm.mean()),
                "mean_selectivity_within_source":float(sel.mean()),
                "head_hit_rate":float(hits.mean()),
                "max_head_selectivity":float(sel.max()),
            })
        del out
pd.DataFrame(attn_rows).to_csv(OUTDIR/"attention_pointer.csv",index=False)

patch_rows = []
patch_examples = sequences[5][:5]
patch_layers = [-1,3,7,11,15,19,23]

def run_logits(text):
    enc = tok(text,return_tensors="pt",add_special_tokens=False)
    with torch.inference_mode():
        out = model(**enc,use_cache=False,return_dict=True)
    qpos = int(enc["attention_mask"].sum().item()-1)
    return out.logits[0,qpos,:].float().cpu().numpy(), enc

for ei,seq in enumerate(patch_examples):
    src_index = 4 if primary=="reverse" else 0
    orig = seq[src_index]
    unused = [d for d in DIGITS if d not in seq]
    if not unused:
        continue
    new = unused[0]
    rec_prompt = chat_prompt(tok,primary,seq)
    rec_spos = source_positions(tok,rec_prompt,primary,seq)
    base_logits,rec_enc = run_logits(rec_prompt)
    orig_id,new_id = first_ids[orig],first_ids[new]
    base_margin = float(base_logits[new_id]-base_logits[orig_id])

    donor_seq = list(seq)
    donor_seq[src_index] = new
    donor_prompt = chat_prompt(tok,primary,donor_seq)
    donor_spos = source_positions(tok,donor_prompt,primary,donor_seq)
    donor_enc = tok(donor_prompt,return_tensors="pt",add_special_tokens=False)
    with torch.inference_mode():
        donor_out = model(**donor_enc,output_hidden_states=True,use_cache=False,return_dict=True)
    donor_h = [h.detach().clone() for h in donor_out.hidden_states]
    del donor_out

    dist_index = 0 if src_index != 0 else 4
    donor2_seq = list(seq)
    donor2_seq[dist_index] = new
    donor2_prompt = chat_prompt(tok,primary,donor2_seq)
    donor2_spos = source_positions(tok,donor2_prompt,primary,donor2_seq)
    donor2_enc = tok(donor2_prompt,return_tensors="pt",add_special_tokens=False)
    with torch.inference_mode():
        donor2_out = model(**donor2_enc,output_hidden_states=True,use_cache=False,return_dict=True)
    donor2_h = [h.detach().clone() for h in donor2_out.hidden_states]
    del donor2_out

    for ptype,sp_idx,dh,dspos in [
        ("target_source",src_index,donor_h,donor_spos),
        ("distractor_source",dist_index,donor2_h,donor2_spos)
    ]:
        for layer in patch_layers:
            handles = []
            if layer == -1:
                def make_emb_hook(srcpos, donorvec):
                    def hook(module, inp, out):
                        z = out.clone()
                        z[:,srcpos,:] = donorvec.to(z.dtype)
                        return z
                    return hook
                handles.append(model.model.embed_tokens.register_forward_hook(
                    make_emb_hook(rec_spos[sp_idx], dh[0][0,dspos[sp_idx],:])
                ))
            else:
                def make_layer_hook(srcpos, donorvec):
                    def hook(module, inp, out):
                        if isinstance(out, tuple):
                            z = out[0].clone()
                            z[:,srcpos,:] = donorvec.to(z.dtype)
                            return (z,)+out[1:]
                        z = out.clone()
                        z[:,srcpos,:] = donorvec.to(z.dtype)
                        return z
                    return hook
                handles.append(model.model.layers[layer].register_forward_hook(
                    make_layer_hook(rec_spos[sp_idx], dh[layer+1][0,dspos[sp_idx],:])
                ))
            with torch.inference_mode():
                out = model(**rec_enc,use_cache=False,return_dict=True)
            qpos = int(rec_enc["attention_mask"].sum().item()-1)
            lg = out.logits[0,qpos,:].float().cpu().numpy()
            for h in handles:
                h.remove()
            margin = float(lg[new_id]-lg[orig_id])
            patch_rows.append({
                "task":primary,"example":ei,"patch_type":ptype,"patch_layer":layer,
                "source_index":sp_idx,"orig":orig,"new":new,
                "baseline_new_minus_orig":base_margin,
                "patched_new_minus_orig":margin,
                "delta_margin":margin-base_margin
            })
            del out
pd.DataFrame(patch_rows).to_csv(OUTDIR/"patching.csv",index=False)

probe_df = pd.DataFrame(probe_rows)
er_df = pd.DataFrame(erank_rows)
ov_df = pd.DataFrame(ov_rows)
att_df = pd.DataFrame(attn_rows)
pat_df = pd.DataFrame(patch_rows)

sub = probe_df[(probe_df.task==primary)&(probe_df.k==5)&(probe_df.stage==0)]
best_depth = int(sub.groupby("depth").accuracy.mean().idxmax())
best_probe = sub[sub.depth==best_depth].sort_values("future_offset")
best_er = er_df[(er_df.task==primary)&(er_df.stage==0)&(er_df.depth==best_depth)].sort_values("k")
near_depth = min([6,12,18,24],key=lambda x:abs(x-best_depth))
ov_best = ov_df[(ov_df.task==primary)&(ov_df.depth==near_depth)]
ov_summary = ov_best.groupby("kind").overlap.mean().to_dict() if len(ov_best) else {}

att_group = att_df.groupby("layer").agg(
    selectivity=("mean_selectivity_within_source","mean"),
    hit=("head_hit_rate","mean"),
    source_mass=("mean_source_mass","mean")
).reset_index()
att_idx = int(att_group.selectivity.idxmax())
best_att_row = att_group.loc[att_idx].to_dict()

pat_summary = pat_df.groupby(["patch_type","patch_layer"]).delta_margin.mean().reset_index()
target_pat = pat_summary[pat_summary.patch_type=="target_source"]
dist_pat = pat_summary[pat_summary.patch_type=="distractor_source"]
target_peak = target_pat.loc[target_pat.delta_margin.abs().idxmax()].to_dict() if len(target_pat) else {}
dist_peak = dist_pat.loc[dist_pat.delta_margin.abs().idxmax()].to_dict() if len(dist_pat) else {}

summary = {
    "model":{
        "id":MODEL_ID,"parameters_reported":"0.49B","layers":24,
        "hidden_size":896,"attention_heads":14,"kv_heads":2
    },
    "task_accuracy_k5_stage0":{
        "reverse_restricted":rev,"copy_restricted":cpy,"primary_task":primary
    },
    "best_blueprint_depth":best_depth,
    "future_probe_at_best_depth":best_probe[["future_offset","accuracy"]].to_dict(orient="records"),
    "stage0_effective_rank_at_best_depth":best_er[["k","remaining_items","effective_rank","rank95","effective_rank_per_item"]].to_dict(orient="records"),
    "subspace_overlap_near_best_depth":ov_summary,
    "attention_best_layer":best_att_row,
    "patch_target_peak":target_peak,
    "patch_distractor_peak":dist_peak,
}
with open(OUTDIR/"summary.json","w") as f:
    json.dump(summary,f,indent=2)

import matplotlib.pyplot as plt
plt.figure(figsize=(7,4))
for k in KS:
    q = probe_df[(probe_df.task==primary)&(probe_df.k==k)&(probe_df.stage==0)&(probe_df.depth==best_depth)]
    plt.plot(q.future_offset,q.accuracy,marker="o",label=f"k={k}")
plt.axhline(1/len(DIGITS),linestyle="--")
plt.xlabel("Future offset from current output position")
plt.ylabel("Cross-validated linear probe accuracy")
plt.title(f"{primary}: future-item decodability at depth {best_depth}")
plt.legend(ncol=2)
plt.tight_layout()
plt.savefig(OUTDIR/"probe_future_slots.png",dpi=160)
plt.close()

plt.figure(figsize=(7,4))
for task in TASKS:
    q = er_df[(er_df.task==task)&(er_df.stage==0)&(er_df.depth==best_depth)]
    plt.plot(q.k,q.effective_rank,marker="o",label=task)
plt.xlabel("Sequence length")
plt.ylabel("Effective rank of concatenated future-item codes")
plt.title(f"Blueprint coding rank at depth {best_depth}")
plt.legend()
plt.tight_layout()
plt.savefig(OUTDIR/"effective_rank_vs_length.png",dpi=160)
plt.close()

plt.figure(figsize=(7,4))
plt.plot(att_group.layer,att_group.selectivity,marker="o")
plt.axhline(1/5,linestyle="--")
plt.xlabel("Transformer layer")
plt.ylabel("Attention selectivity for currently due source item")
plt.title(f"{primary}: source-pointer selectivity")
plt.tight_layout()
plt.savefig(OUTDIR/"attention_pointer.png",dpi=160)
plt.close()

plt.figure(figsize=(7,4))
for typ,g in pat_summary.groupby("patch_type"):
    plt.plot(g.patch_layer,g.delta_margin,marker="o",label=typ)
plt.axhline(0,linestyle="--")
plt.xlabel("Patch layer (-1 = embedding)")
plt.ylabel("Change in donor-vs-original next-token margin")
plt.title(f"{primary}: causal source-token patching")
plt.legend()
plt.tight_layout()
plt.savefig(OUTDIR/"patching_by_layer.png",dpi=160)
plt.close()

with open(OUTDIR/"README_RESULTS.md","w") as f:
    f.write("# Neural Blueprint Slot Probe — Qwen2.5-0.5B-Instruct\\n\\n")
    f.write("Controlled copy/reverse sequence experiments. Result files separate behavior, linear decodability, coding rank, attention pointer, and causal patching evidence.\\n\\n")
    f.write("Primary task: **%s**. Best sampled residual depth for simultaneous future-item decoding at K=5 stage 0: **%d**.\\n\\n"%(primary,best_depth))
    f.write("See summary.json for aggregate results and CSV files for row-level derived measurements.\\n")
print(json.dumps(summary,indent=2),flush=True)
