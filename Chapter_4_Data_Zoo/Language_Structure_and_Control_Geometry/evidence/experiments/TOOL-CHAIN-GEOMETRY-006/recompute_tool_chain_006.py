"""Recompute TOOL-CHAIN-GEOMETRY-006 from BFCL V4 source files.

Place these BFCL files in ./raw before running:
  data_overall.csv
  claude_opus_4_5_multi_turn_base_score.json
  xlam_2_70b_multi_turn_base_score.json
  glm_4_6_multi_turn_base_score.json

The .json files are JSONL: first line summary, subsequent lines failed episodes.
"""
from pathlib import Path
import json, re
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parent
RAW = ROOT / "raw"
OUT = ROOT / "recomputed"
OUT.mkdir(exist_ok=True)

def pct(x):
    if pd.isna(x): return np.nan
    s = str(x).strip()
    if s == "N/A" or not s: return np.nan
    return float(s.rstrip("%"))

df = pd.read_csv(RAW / "data_overall.csv")
for c in ["Non-Live AST Acc","Multi Turn Acc","Web Search Acc","Memory Acc",
          "Multi Turn Base","Multi Turn Miss Func","Multi Turn Miss Param","Multi Turn Long Context"]:
    df[c+"_num"] = df[c].map(pct)
df["Agentic mean"] = (df["Web Search Acc_num"] + df["Memory Acc_num"])/2

cors = {
    "single_turn_nonlive_vs_multiturn": spearmanr(df["Non-Live AST Acc_num"], df["Multi Turn Acc_num"], nan_policy="omit").statistic,
    "single_turn_nonlive_vs_agentic_mean": spearmanr(df["Non-Live AST Acc_num"], df["Agentic mean"], nan_policy="omit").statistic,
    "multiturn_vs_agentic_mean": spearmanr(df["Multi Turn Acc_num"], df["Agentic mean"], nan_policy="omit").statistic,
    "web_vs_memory": spearmanr(df["Web Search Acc_num"], df["Memory Acc_num"], nan_policy="omit").statistic,
}

for name, col in [("miss_function","Multi Turn Miss Func_num"),("miss_parameter","Multi Turn Miss Param_num"),("long_context","Multi Turn Long Context_num")]:
    df[name+"_drop"] = df["Multi Turn Base_num"] - df[col]

subset = df[df["Multi Turn Base_num"] >= 20]
perturb = {}
for name in ["miss_function_drop","miss_parameter_drop","long_context_drop"]:
    x = subset[name].dropna()
    perturb[name] = {"n":len(x), "mean":float(x.mean()), "median":float(x.median()), "q25":float(x.quantile(.25)), "q75":float(x.quantile(.75))}

def family(s):
    return re.sub(r" \((?:FC(?: thinking)?|Prompt(?: \+ Thinking)?)\)$", "", s)
df["family"] = df["Model"].map(family)
pairs=[]
for fam,g in df.groupby("family"):
    fc=g[g["Model"].str.contains(r"\(FC(?: thinking)?\)$",regex=True)]
    pr=g[g["Model"].str.contains(r"\(Prompt(?: \+ Thinking)?\)$",regex=True)]
    if len(fc)==1 and len(pr)==1:
        pairs.append({"family":fam,"multi_turn_fc_minus_prompt_pp":float(fc.iloc[0]["Multi Turn Acc_num"]-pr.iloc[0]["Multi Turn Acc_num"])})
pairs=pd.DataFrame(pairs)
pairs.to_csv(OUT/"paired_fc_vs_prompt_multiturn.csv",index=False)

raw_files = {
    "Claude Opus 4.5 FC":"claude_opus_4_5_multi_turn_base_score.json",
    "xLAM-2-70B FC":"xlam_2_70b_multi_turn_base_score.json",
    "GLM-4.6 FC thinking":"glm_4_6_multi_turn_base_score.json",
}
err_rows=[]
for model,fn in raw_files.items():
    lines=(RAW/fn).read_text().splitlines()
    summary=json.loads(lines[0])
    counts={}
    for line in lines[1:]:
        rec=json.loads(line)
        et=rec.get("error",{}).get("error_type","UNKNOWN")
        counts[et]=counts.get(et,0)+1
    err_rows.append({"model":model,"accuracy":summary["accuracy"],"correct_count":summary["correct_count"],"total_count":summary["total_count"],**counts})
pd.DataFrame(err_rows).to_csv(OUT/"base_error_type_counts.csv",index=False)

summary={
  "n_configurations":int(len(df)),
  "spearman":{k:round(float(v),3) for k,v in cors.items()},
  "perturbation_base_ge20":perturb,
  "fc_prompt_n":int(len(pairs)),
  "fc_prompt_mean_pp":float(pairs["multi_turn_fc_minus_prompt_pp"].mean()),
  "fc_prompt_median_pp":float(pairs["multi_turn_fc_minus_prompt_pp"].median()),
}
(OUT/"summary.json").write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
