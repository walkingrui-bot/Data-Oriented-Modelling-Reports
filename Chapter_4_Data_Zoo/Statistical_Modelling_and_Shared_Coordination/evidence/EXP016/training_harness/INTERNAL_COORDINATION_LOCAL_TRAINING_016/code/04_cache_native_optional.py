#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
import bedrock_bio as bb
from native_pipeline_harness import registry, PIPELINE_FIELDS, RELEASE

def columns(meta):
    out=[]
    for c in meta.get("columns",[]):out.append(c.get("name") if isinstance(c,dict) else str(c))
    return {x for x in out if x}

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--passport",required=True);ap.add_argument("--out-dir",type=Path,default=Path("data/native"));ap.add_argument("--limit",type=int,default=0);args=ap.parse_args()
    p=next((x for x in registry() if x.passport_id==args.passport),None)
    if p is None: raise SystemExit("Unknown passport")
    name=f"open_targets.{p.native_table}";meta=bb.describe_table(name);avail=columns(meta);wanted=[c for c in PIPELINE_FIELDS[p.datasource_id] if c in avail]
    if "release" in avail and "release" not in wanted:wanted.append("release")
    rel=bb.load_table(name)
    if "release" in avail:rel=rel.filter(f"release = '{RELEASE}'")
    if wanted:rel=rel.select(", ".join(wanted))
    if args.limit>0:rel=rel.limit(args.limit)
    df=rel.df();args.out_dir.mkdir(parents=True,exist_ok=True);out=args.out_dir/f"{p.passport_id}_{p.datasource_id}_26.06.parquet";df.to_parquet(out,index=False)
    print(json.dumps({"passport":p.passport_id,"table":name,"rows":len(df),"columns":list(df.columns),"path":str(out)},indent=2))
if __name__=="__main__":main()
