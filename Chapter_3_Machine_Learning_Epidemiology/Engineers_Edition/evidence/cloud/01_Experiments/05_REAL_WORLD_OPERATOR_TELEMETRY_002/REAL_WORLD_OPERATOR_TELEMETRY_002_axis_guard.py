#!/usr/bin/env python3
"""
REAL-WORLD-OPERATOR-TELEMETRY-002
One-click failure-axis locator + intervention/guard planner for HuggingFace causal LMs.

Commands
--------
cases
locate --model MODEL --case CASE_ID [--device auto] [--out report.json]
trace --report report.json
guard-plan --report report.json
self-test

The locator has two modes:
1) paired-causal: clean/failure prompts differ. Uses Δh · ∇h(score), SVD, then activation patch rescue.
2) gradient-source: no clean contrast. Uses source-span behavior gradients, SVD, then negative-axis intervention.

This is a diagnostic tool. Production safety should still enforce deterministic tool registry,
structured data flow, least privilege and approval boundaries.
"""
import argparse, json, math, os, hashlib, difflib
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
CASES_PATH=HERE/"REAL_WORLD_OPERATOR_TELEMETRY_002_cases.json"

def load_cases():
    with open(CASES_PATH,"r",encoding="utf-8") as f:
        return {c["case_id"]:c for c in json.load(f)}

def jprint(x):
    print(json.dumps(x,ensure_ascii=False,indent=2))

def render_messages(tokenizer,messages):
    if hasattr(tokenizer,"apply_chat_template"):
        try:
            return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True)
        except Exception:
            pass
    parts=[]
    for m in messages:
        parts.append(f"{m['role'].upper()}:\n{m['content']}")
    parts.append("ASSISTANT:\n")
    return "\n\n".join(parts)

def find_subseq(seq,sub):
    if not sub: return []
    for i in range(len(seq)-len(sub)+1):
        if seq[i:i+len(sub)]==sub:
            return list(range(i,i+len(sub)))
    return []

def token_span(tokenizer,prompt_ids,substring):
    if not substring: return []
    sub=tokenizer.encode(substring,add_special_tokens=False)
    hit=find_subseq(prompt_ids,sub)
    if hit: return hit
    # fallback: whitespace-prefixed encoding
    sub=tokenizer.encode(" "+substring,add_special_tokens=False)
    return find_subseq(prompt_ids,sub)

def get_blocks(model):
    paths=[
        ("model.layers", lambda m:m.model.layers),
        ("transformer.h", lambda m:m.transformer.h),
        ("gpt_neox.layers", lambda m:m.gpt_neox.layers),
        ("model.decoder.layers", lambda m:m.model.decoder.layers),
    ]
    for name,fn in paths:
        try:
            blocks=fn(model)
            if blocks is not None and len(blocks)>0:
                return name,list(blocks)
        except Exception:
            pass
    raise RuntimeError("Cannot locate transformer blocks. Add architecture adapter in get_blocks().")

def output_tensor(out):
    if isinstance(out,tuple): return out[0]
    return out

def replace_output(out,new):
    if isinstance(out,tuple): return (new,)+tuple(out[1:])
    return new

class HFBackend:
    def __init__(self,model_name,device="auto",dtype="auto"):
        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM
        self.torch=torch
        self.tokenizer=AutoTokenizer.from_pretrained(model_name,use_fast=True,trust_remote_code=True)
        kwargs={"trust_remote_code":True}
        if device=="auto":
            kwargs["device_map"]="auto"
        if dtype=="auto":
            kwargs["torch_dtype"]="auto"
        self.model=AutoModelForCausalLM.from_pretrained(model_name,**kwargs)
        self.model.eval()
        self.block_path,self.blocks=get_blocks(self.model)
        # Keep only embeddings differentiable. This lets residual grads flow without storing parameter grads.
        for p in self.model.parameters(): p.requires_grad_(False)
        emb=self.model.get_input_embeddings()
        emb.weight.requires_grad_(True)
        self.device=next(self.model.parameters()).device
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id=self.tokenizer.eos_token_id

    def encode_messages(self,messages):
        text=render_messages(self.tokenizer,messages)
        ids=self.tokenizer.encode(text,add_special_tokens=True)
        return text,ids

    def prompt_states(self,prompt_ids):
        torch=self.torch
        captures={}
        handles=[]
        for li,b in enumerate(self.blocks):
            def hook(mod,inp,out,li=li):
                captures[li]=output_tensor(out).detach()
            handles.append(b.register_forward_hook(hook))
        x=torch.tensor([prompt_ids],device=self.device)
        with torch.no_grad():
            self.model(input_ids=x,use_cache=False)
        for h in handles:h.remove()
        return {li:t[0,:len(prompt_ids)].float().cpu().numpy() for li,t in captures.items()}

    def score_grad(self,prompt_ids,continuation):
        torch=self.torch
        cand=self.tokenizer.encode(continuation,add_special_tokens=False)
        if not cand: raise ValueError("empty continuation")
        full=prompt_ids+cand
        captures={}
        handles=[]
        for li,b in enumerate(self.blocks):
            def hook(mod,inp,out,li=li):
                h=output_tensor(out)
                h.retain_grad()
                captures[li]=h
            handles.append(b.register_forward_hook(hook))
        self.model.zero_grad(set_to_none=True)
        x=torch.tensor([full],device=self.device)
        out=self.model(input_ids=x,use_cache=False)
        logp=torch.log_softmax(out.logits[0],dim=-1)
        p=len(prompt_ids)
        positions=torch.arange(p-1,p-1+len(cand),device=self.device)
        targets=torch.tensor(cand,device=self.device)
        score=logp[positions,targets].sum()
        score.backward()
        result={}
        for li,h in captures.items():
            result[li]={
                "state":h.detach()[0,:p].float().cpu().numpy(),
                "grad":h.grad.detach()[0,:p].float().cpu().numpy()
            }
        for hd in handles:hd.remove()
        return float(score.detach().cpu()),result

    def margin_grad(self,prompt_ids,target,safe):
        st,rt=self.score_grad(prompt_ids,target)
        ss,rs=self.score_grad(prompt_ids,safe)
        layers={}
        for li in rt:
            layers[li]={
                "state":rt[li]["state"],
                "grad_target":rt[li]["grad"],
                "grad_safe":rs[li]["grad"],
                "grad_margin":rt[li]["grad"]-rs[li]["grad"]
            }
        return st-ss,st,ss,layers

    def score_margin_only(self,prompt_ids,target,safe,patch=None):
        torch=self.torch
        def one(cont):
            cand=self.tokenizer.encode(cont,add_special_tokens=False)
            full=prompt_ids+cand
            handles=[]
            if patch:
                li=patch["layer"]; positions=patch["positions"]; axis=patch["axis"]
                amps=patch["amps"]
                b=self.blocks[li]
                axis_t=torch.tensor(axis,device=self.device,dtype=next(self.model.parameters()).dtype)
                def phook(mod,inp,out):
                    h=output_tensor(out)
                    h2=h.clone()
                    for pos,amp in zip(positions,amps):
                        if pos<h2.shape[1]:
                            h2[:,pos,:]=h2[:,pos,:]-float(amp)*axis_t
                    return replace_output(out,h2)
                handles.append(b.register_forward_hook(phook))
            x=torch.tensor([full],device=self.device)
            with torch.no_grad():
                o=self.model(input_ids=x,use_cache=False)
                lp=torch.log_softmax(o.logits[0],dim=-1)
                p=len(prompt_ids)
                positions=torch.arange(p-1,p-1+len(cand),device=self.device)
                targets=torch.tensor(cand,device=self.device)
                score=lp[positions,targets].sum()
            for h in handles:h.remove()
            return float(score.cpu())
        return one(target)-one(safe)

def align_tokens(tok,clean_ids,fail_ids):
    a=tok.convert_ids_to_tokens(clean_ids)
    b=tok.convert_ids_to_tokens(fail_ids)
    sm=difflib.SequenceMatcher(a=a,b=b,autojunk=False)
    pairs=[]
    for block in sm.get_matching_blocks():
        for k in range(block.size):
            pairs.append((block.a+k,block.b+k))
    return pairs,a,b

def svd_axis(vectors):
    V=np.asarray(vectors,dtype=float)
    if V.ndim==1: V=V[None,:]
    if len(V)==0: return None,0.0
    _,s,vt=np.linalg.svd(V,full_matrices=False)
    concentration=float(s[0]**2/np.sum(s*s)) if np.sum(s*s)>0 else 0
    return vt[0],concentration

def angle_deg(a,b):
    na=np.linalg.norm(a); nb=np.linalg.norm(b)
    if na==0 or nb==0:return None
    c=np.clip(abs(float(np.dot(a,b)/(na*nb))),0,1)
    return float(np.degrees(np.arccos(c)))

def paired_locate(backend,case,clean_ids,fail_ids,out_dir,topk=4):
    clean_states=backend.prompt_states(clean_ids)
    failure_margin,st,ss,grads=backend.margin_grad(fail_ids,case["failure_target"],case["safe_target"])
    clean_margin=backend.score_margin_only(clean_ids,case["failure_target"],case["safe_target"])
    pairs,clean_tokens,fail_tokens=align_tokens(backend.tokenizer,clean_ids,fail_ids)
    src=token_span(backend.tokenizer,fail_ids,case.get("untrusted_span",""))
    trusted=token_span(backend.tokenizer,fail_ids,case.get("trusted_span",""))
    layer_reports=[]
    for li in sorted(grads):
        rows=[]
        gmat=grads[li]["grad_margin"]
        for ci,fi in pairs:
            dh=grads[li]["state"][fi]-clean_states[li][ci]
            g=gmat[fi]
            c=float(np.dot(dh,g))
            al=float(abs(c)/(np.linalg.norm(dh)*np.linalg.norm(g)+1e-30))
            rows.append((ci,fi,c,al,dh,g))
        if not rows: continue
        total=float(sum(abs(r[2]) for r in rows))
        top=sorted(rows,key=lambda r:abs(r[2]),reverse=True)[:topk]
        vecs=[]
        for r in top:
            g=r[5]
            if np.linalg.norm(g)>0:
                vecs.append(np.sign(r[2])*math.sqrt(abs(r[2])+1e-30)*g/np.linalg.norm(g))
        axis,conc=svd_axis(vecs)
        if axis is None: continue
        positions=[]; amps=[]
        for r in top:
            fi=r[1]; dh=r[4]
            positions.append(fi)
            amps.append(float(np.dot(dh,axis)))
        patched=backend.score_margin_only(fail_ids,case["failure_target"],case["safe_target"],
                                          patch={"layer":li,"positions":positions,"amps":amps,"axis":axis})
        denom=failure_margin-clean_margin
        rescue=float((failure_margin-patched)/(denom+1e-30)) if abs(denom)>1e-9 else float(failure_margin-patched)
        sg=float(sum(np.linalg.norm(gmat[i]) for i in src)) if src else 0.0
        tg=float(sum(np.linalg.norm(gmat[i]) for i in trusted)) if trusted else 0.0
        auth=float(sg/(tg+1e-30)) if trusted else None
        gt=grads[li]["grad_target"][-1]; gs=grads[li]["grad_safe"][-1]
        gra=angle_deg(gt,gs)
        layer_reports.append({
            "layer":li,"paired_total_abs_contribution":total,
            "axis_concentration":conc,"patched_margin":patched,
            "rescue_fraction":rescue,"source_authority_ratio":auth,
            "goal_gradient_angle_deg":gra,
            "top_positions":[{"clean_index":r[0],"failure_index":r[1],
                              "token":fail_tokens[r[1]],"contribution":r[2],
                              "alignment":r[3],"axis_load":float(np.dot(r[4],axis))}
                             for r in top],
            "_axis":axis
        })
    best=max(layer_reports,key=lambda x:(x["rescue_fraction"],x["paired_total_abs_contribution"]))
    axis_path=Path(out_dir)/f"{case['case_id']}_FCA_layer{best['layer']}.npy"
    np.save(axis_path,best["_axis"])
    # earliest meaningful downstream divergence
    threshold=.10*max(abs(x["contribution"]) for x in best["top_positions"])
    onset=sorted([x for x in best["top_positions"] if abs(x["contribution"])>=threshold],
                 key=lambda x:x["failure_index"])[0]
    for lr in layer_reports: lr.pop("_axis",None)
    return {
        "mode":"paired-causal",
        "failure_margin":failure_margin,"clean_margin":clean_margin,
        "target_logprob":st,"safe_logprob":ss,
        "selected_layer":best["layer"],"axis_file":str(axis_path.name),
        "axis_concentration":best["axis_concentration"],
        "patch_rescue_fraction":best["rescue_fraction"],
        "injection_onset":onset,
        "source_authority_ratio":best["source_authority_ratio"],
        "goal_gradient_angle_deg":best["goal_gradient_angle_deg"],
        "layer_ranking":sorted(layer_reports,key=lambda x:x["rescue_fraction"],reverse=True)[:12]
    }

def gradient_locate(backend,case,fail_ids,out_dir):
    margin,st,ss,grads=backend.margin_grad(fail_ids,case["failure_target"],case["safe_target"])
    src=token_span(backend.tokenizer,fail_ids,case.get("untrusted_span",""))
    if not src: src=list(range(len(fail_ids)))
    reports=[]
    for li in sorted(grads):
        gm=grads[li]["grad_margin"]
        vecs=[gm[i] for i in src if np.linalg.norm(gm[i])>0]
        axis,conc=svd_axis(vecs)
        if axis is None: continue
        energy=float(sum(np.linalg.norm(gm[i])**2 for i in src))
        # negative-axis intervention, grid search relative to median source hidden norm
        h=grads[li]["state"]
        scale=float(np.median([np.linalg.norm(h[i]) for i in src])) if src else 1.0
        best_margin=margin; best_alpha=0.0
        for frac in [0.01,0.03,0.10,0.30,0.60]:
            alpha=frac*scale
            amps=[]
            for i in src:
                sign=np.sign(np.dot(gm[i],axis)) or 1.0
                amps.append(alpha*sign)
            patched=backend.score_margin_only(fail_ids,case["failure_target"],case["safe_target"],
                                              patch={"layer":li,"positions":src,"amps":amps,"axis":axis})
            if patched<best_margin:
                best_margin=patched; best_alpha=alpha
        reduction=float(margin-best_margin)
        reports.append({"layer":li,"source_grad_energy":energy,"axis_concentration":conc,
                        "best_patch_alpha":best_alpha,"patched_margin":best_margin,
                        "margin_reduction":reduction,"_axis":axis})
    best=max(reports,key=lambda x:(x["margin_reduction"],x["source_grad_energy"]))
    axis_path=Path(out_dir)/f"{case['case_id']}_FCA_layer{best['layer']}.npy"
    np.save(axis_path,best["_axis"])
    for r in reports:r.pop("_axis",None)
    return {
        "mode":"gradient-source","failure_margin":margin,
        "target_logprob":st,"safe_logprob":ss,
        "selected_layer":best["layer"],"axis_file":axis_path.name,
        "axis_concentration":best["axis_concentration"],
        "best_patch_alpha":best["best_patch_alpha"],
        "patch_margin_reduction":best["margin_reduction"],
        "source_token_indices":src,
        "layer_ranking":sorted(reports,key=lambda x:x["margin_reduction"],reverse=True)[:12]
    }

def guard_plan(case,report=None):
    cls=case["failure_class"]
    if cls=="indirect_prompt_injection":
        plan=[
            {"order":1,"action":"SOURCE_TAG","do":"Mark retrieved/tool/web text UNTRUSTED_DATA. Never place it in system/developer authority."},
            {"order":2,"action":"STRUCTURE","do":"Extract only schema fields needed by the task. Do not pass free-form external text to privileged action planning when avoidable."},
            {"order":3,"action":"INTENT_GATE","do":"A tool output may provide data but may not authorize a new side-effect tool. Compare every proposed write action with explicit user intent."},
            {"order":4,"action":"REGISTRY+LEAST_PRIVILEGE","do":"Allow only task-scoped tools/arguments; default write/physical/financial actions to denied."},
            {"order":5,"action":"AXIS_MONITOR","do":"Calibrate clean p99 thresholds for source_authority_ratio / failure-axis load. If exceeded, freeze side-effect tools and reroute."},
            {"order":6,"action":"APPROVAL","do":"Require explicit human approval before consequential side effects."},
            {"order":7,"action":"AXIS_PATCH_EXPERIMENTAL","do":"For diagnosis only: subtract the validated failure-axis component at the localized layer/token and verify behavior rescue. Do not use as the sole production barrier."},
        ]
    elif cls=="nonexistent_tool_hallucination":
        plan=[
            {"order":1,"action":"REGISTRY_ENUM","do":"Tool name must be selected from the runtime registry enum; unknown names are rejected before execution."},
            {"order":2,"action":"NO_TOOL_PATH","do":"Provide a first-class abstain/no-tool result. If registry is empty or capability match fails, route there deterministically."},
            {"order":3,"action":"SCHEMA_CONSTRAINT","do":"Constrain tool calls to structured tool schemas; do not parse arbitrary free-text tool names into executable calls."},
            {"order":4,"action":"TOOL_GUARD","do":"Validate tool name, arguments, identity, permissions and scope immediately before side effect."},
            {"order":5,"action":"AXIS_MONITOR","do":"Monitor the localized hallucinated-tool axis. If the requested nonexistent tool span dominates the valid-registry control signal, force abstention."},
            {"order":6,"action":"REGRESSION","do":"Continuously replay NTA/DT benchmark cases after model/prompt/tool-registry changes."},
        ]
    else:
        plan=[]
    if report:
        plan.insert(0,{"order":0,"action":"LOCALIZED_EVIDENCE",
                       "do":f"Use FCA at layer {report.get('selected_layer')} from {report.get('axis_file')}; patch result is evidence for this model/case only."})
    return plan

def self_test():
    p=HERE/"REAL_WORLD_OPERATOR_TELEMETRY_002_axis_locator_selftest.json"
    with open(p,"r") as f:r=json.load(f)
    jprint(r)

def main():
    ap=argparse.ArgumentParser(description="Failure Axis Guard OS")
    sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("cases")
    p=sp.add_parser("locate")
    p.add_argument("--model",required=True)
    p.add_argument("--case",required=True)
    p.add_argument("--device",default="auto")
    p.add_argument("--dtype",default="auto")
    p.add_argument("--out",default="failure_axis_report.json")
    p=sp.add_parser("trace"); p.add_argument("--report",required=True)
    p=sp.add_parser("guard-plan"); p.add_argument("--report"); p.add_argument("--case",required=True)
    sp.add_parser("self-test")
    args=ap.parse_args()
    cases=load_cases()
    if args.cmd=="cases":
        jprint([{"case_id":c["case_id"],"failure_class":c["failure_class"],"source":c["source"]} for c in cases.values()])
        return
    if args.cmd=="self-test":
        self_test(); return
    if args.cmd=="trace":
        with open(args.report,"r") as f:r=json.load(f)
        jprint(r); return
    if args.cmd=="guard-plan":
        report=None
        if args.report:
            with open(args.report,"r") as f: report=json.load(f)
        jprint(guard_plan(cases[args.case],report)); return
    case=cases[args.case]
    out=Path(args.out).resolve(); out.parent.mkdir(parents=True,exist_ok=True)
    backend=HFBackend(args.model,args.device,args.dtype)
    _,clean_ids=backend.encode_messages(case["messages_clean"])
    _,fail_ids=backend.encode_messages(case["messages_failure"])
    if clean_ids!=fail_ids:
        loc=paired_locate(backend,case,clean_ids,fail_ids,out.parent)
    else:
        loc=gradient_locate(backend,case,fail_ids,out.parent)
    report={
        "case_id":case["case_id"],"failure_class":case["failure_class"],
        "model":args.model,"block_path":backend.block_path,
        "localization":loc,
        "guard_plan":guard_plan(case,loc)
    }
    with open(out,"w",encoding="utf-8") as f: json.dump(report,f,ensure_ascii=False,indent=2)
    jprint(report)

if __name__=="__main__":
    main()
