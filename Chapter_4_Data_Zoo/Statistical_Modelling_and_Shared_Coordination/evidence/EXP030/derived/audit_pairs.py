"""EXP030-SOURCE-001: official GaitPDB directory and format-based Ga dual-task pairs."""

import csv
import html
import io
import json
import re
import urllib.request
from collections import Counter,defaultdict
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
BASE="https://physionet.org/files/gaitpdb/1.0.0/"
OUT=ROOT/"PAIR_AUDIT.csv"
DIAG=ROOT/"SOURCE_DIAGNOSTICS.json"


def fetch(name,cap):
    u=BASE+name
    req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0 EXP030 paired source audit"})
    with urllib.request.urlopen(req,timeout=30) as r:
        body=r.read(cap+1);status=r.status
    if len(body)>cap or status!=200:raise ValueError(f"Source cap/status: {u} {len(body)} {status}")
    return body


def main():
    if OUT.exists() or DIAG.exists():raise FileExistsError("Preserve EXP030-SOURCE-001 output")
    listing=html.unescape(fetch("",1_000_000).decode("utf-8","replace"))
    fmt=fetch("format.txt",100_000).decode("utf-8","replace")
    demographics=fetch("demographics.txt",200_000).decode("utf-8","replace")
    if "A walk number of 10" not in fmt or "serial-7 subtraction" not in fmt or "A walk number of 01" not in fmt or "100 Hz" not in fmt or "Column     19" not in fmt:
        raise ValueError("Official format semantics changed")
    files=set(html.unescape(x) for x in re.findall(r'href="([^"]+)"',listing))
    ga_files={x for x in files if re.fullmatch(r"Ga(?:Co|Pt)\d{2}_\d{2}\.txt",x)}
    meta={}
    for row in csv.DictReader(io.StringIO(demographics),delimiter="\t"):
        sid=row.get("ID","")
        if sid.startswith("Ga"):
            meta[sid]=row
    if not meta:raise ValueError("No Ga demographics")
    ids=sorted(set(re.match(r"(Ga(?:Co|Pt)\d{2})_",x).group(1) for x in ga_files)|set(meta))
    fields=["subject_id","study","group","demographic_group","demographic_row_present","usual_01_present","dual_10_present","paired_official_tasks","usual_01_url","dual_10_url","reason"]
    output=[]
    for sid in ids:
        group="PD" if sid[2:4]=="Pt" else "HC"
        dm=meta.get(sid,{})
        normal=f"{sid}_01.txt";dual=f"{sid}_10.txt"
        has_normal=normal in ga_files;has_dual=dual in ga_files
        dm_group=dm.get("Group","")
        group_match=dm_group==("1" if group=="PD" else "2")
        paired=has_normal and has_dual and group_match
        reason="ELIGIBLE_PAIR" if paired else "NO_OFFICIAL_DEMOGRAPHIC_GROUP" if not group_match else "NO_NORMAL_01" if not has_normal else "NO_DUAL_10"
        output.append({"subject_id":sid,"study":"Ga","group":group,"demographic_group":dm_group,"demographic_row_present":bool(dm),"usual_01_present":has_normal,"dual_10_present":has_dual,"paired_official_tasks":paired,"usual_01_url":BASE+normal if has_normal else "","dual_10_url":BASE+dual if has_dual else "","reason":reason})
    with OUT.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(output)
    pairs=Counter(r["group"] for r in output if r["paired_official_tasks"])
    diag={"run_id":"EXP030-SOURCE-001","official_listing_url":BASE,"official_format_url":BASE+"format.txt","official_demographics_url":BASE+"demographics.txt","script_requests":3,"earlier_manual_preflight_requests":3,"raw_source_files_saved":False,"ga_file_count":len(ga_files),"ga_distinct_subjects":len(output),"ga_demographic_subjects":len(meta),"paired_by_group":dict(pairs),"paired_total":sum(pairs.values()),"frozen_min_each_group":20,"gate_support_possible":pairs["PD"]>=20 and pairs["HC"]>=20,"numeric_qa_status":"NOT_RUN_IF_SUPPORT_GATE_IMPOSSIBLE","note":"Official format.txt defines Ga, Co/Pt, walk 01 usual, walk 10 serial-7 dual; index file existence and demographics group were required. No raw force files fetched because sample support was evaluated first."}
    DIAG.write_text(json.dumps(diag,indent=2)+"\n")
    print(json.dumps(diag,indent=2),flush=True)


if __name__=="__main__":main()
