#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, urllib.request
from pathlib import Path
import pandas as pd
import bedrock_bio as bb

RELEASE="26.06"
NAMESPACE="open_targets"
DATASOURCES=[
"gwas_credible_sets","gene_burden","eva","genomics_england","gene2phenotype",
"uniprot_literature","uniprot_variants","orphanet","clingen","cancer_gene_census",
"intogen","cancer_biomarkers","crispr_screen","crispr","reactome","europepmc",
"expression_atlas","impc"]
TERMINAL_URL="https://raw.githubusercontent.com/vi-c-ky/Human-genetic-evidence-associated-with-drug-approval/main/data/final_dataset.csv"

def cols(meta):
    out=[]
    for c in meta.get("columns",[]):
        if isinstance(c,dict): out.append(c.get("name"))
        else: out.append(str(c))
    return {x for x in out if x}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--cache-dir",type=Path,default=Path("data/cache"))
    args=ap.parse_args(); args.cache_dir.mkdir(parents=True,exist_ok=True)
    assoc_name=f"{NAMESPACE}.association_by_datasource_direct"
    meta=bb.describe_table(assoc_name); available=cols(meta)
    wanted=[c for c in ["targetId","diseaseId","aggregationValue","associationScore","evidenceCount","timeseries","currentNovelty","release"] if c in available]
    rel=bb.load_table(assoc_name)
    if "release" in available:
        rel=rel.filter(f"release = '{RELEASE}'")
    if "aggregationValue" in available:
        quoted=",".join("'"+x.replace("'","''")+"'" for x in DATASOURCES)
        rel=rel.filter(f"aggregationValue IN ({quoted})")
    df=rel.select(", ".join(wanted)).df()
    df.to_parquet(args.cache_dir/"association_by_datasource_direct_26.06.parquet",index=False)

    disease_name=f"{NAMESPACE}.disease"
    dm=bb.describe_table(disease_name); dc=cols(dm)
    dcols=[c for c in ["id","obsoleteTerms","obsoleteXRefs","dbXRefs","name"] if c in dc]
    disease=bb.load_table(disease_name).select(", ".join(dcols)).df()
    disease.to_parquet(args.cache_dir/"disease_26.06.parquet",index=False)

    with urllib.request.urlopen(TERMINAL_URL) as r:
        terminal=pd.read_csv(r)
    terminal.to_parquet(args.cache_dir/"terminal_cohort_26278.parquet",index=False)

    info={"release":RELEASE,"association_rows":len(df),"disease_rows":len(disease),"terminal_rows":len(terminal),"datasources":sorted(df["aggregationValue"].dropna().unique().tolist()) if "aggregationValue" in df else []}
    (args.cache_dir/"cache_manifest.json").write_text(json.dumps(info,indent=2))
    print(json.dumps(info,indent=2))
if __name__=="__main__": main()
