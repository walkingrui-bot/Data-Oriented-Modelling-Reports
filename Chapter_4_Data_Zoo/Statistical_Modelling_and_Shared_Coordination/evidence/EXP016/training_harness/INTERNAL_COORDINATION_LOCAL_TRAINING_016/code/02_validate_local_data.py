#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

DATASOURCES=["gwas_credible_sets","gene_burden","eva","genomics_england","gene2phenotype","uniprot_literature","uniprot_variants","orphanet","clingen","cancer_gene_census","intogen","cancer_biomarkers","crispr_screen","crispr","reactome","europepmc","expression_atlas","impc"]

def flatten_vals(v):
    if v is None: return []
    if isinstance(v,(list,tuple)): return list(v)
    try:
        if pd.isna(v): return []
    except Exception: pass
    return [v]

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--cache-dir",type=Path,default=Path("data/cache"));args=ap.parse_args()
    a=pd.read_parquet(args.cache_dir/"association_by_datasource_direct_26.06.parquet")
    d=pd.read_parquet(args.cache_dir/"disease_26.06.parquet")
    t=pd.read_parquet(args.cache_dir/"terminal_cohort_26278.parquet")
    present=set(a["aggregationValue"].dropna().astype(str))
    missing=[x for x in DATASOURCES if x not in present]
    bridge={}
    if "id" in d:
        for row in d.itertuples(index=False):
            cur=str(getattr(row,"id"));bridge[cur]=cur
            for f in ["obsoleteTerms","obsoleteXRefs","dbXRefs"]:
                if hasattr(row,f):
                    for v in flatten_vals(getattr(row,f)):
                        bridge[str(v)]=cur
    mapped=t["efo_id_norm"].astype(str).map(bridge) if "efo_id_norm" in t else pd.Series([],dtype=object)
    report={"association_rows":len(a),"terminal_rows":len(t),"datasources_present":len(present & set(DATASOURCES)),"missing_datasources":missing,"terminal_disease_mapping_rate":float(mapped.notna().mean()) if len(mapped) else None}
    print(json.dumps(report,indent=2))
    if missing:
        raise SystemExit("Missing expected datasources: "+", ".join(missing))
if __name__=="__main__":main()
