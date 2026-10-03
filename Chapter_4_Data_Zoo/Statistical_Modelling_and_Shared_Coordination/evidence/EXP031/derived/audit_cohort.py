"""EXP031-COHORT-001: official subject-level usual-walk support across Ga/Ju/Si."""

import csv
import html
import io
import json
import re
import urllib.request
from collections import Counter
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
BASE="https://physionet.org/files/gaitpdb/1.0.0/"
OUT=ROOT/"COHORT_AUDIT.csv"
DIAG=ROOT/"COHORT_DIAGNOSTICS.json"


def fetch(name,cap):
    req=urllib.request.Request(BASE+name,headers={"User-Agent":"Mozilla/5.0 EXP031 cohort audit"})
    with urllib.request.urlopen(req,timeout=30) as r:
        blob=r.read(cap+1)
        if r.status!=200 or len(blob)>cap:raise ValueError(f"source status/cap {name}")
    return blob.decode("utf-8","replace")


def main():
    if OUT.exists() or DIAG.exists():raise FileExistsError("Preserve EXP031-COHORT-001 outputs")
    page=html.unescape(fetch("",1_000_000))
    fmt=fetch("format.txt",100_000)
    demo=fetch("demographics.txt",200_000)
    if not all(x in fmt for x in ("A walk number of 01", "usual, normal walk", "Co or Pt", "Ga, Ju or Si", "100 Hz", "Column     19")):
        raise ValueError("Format semantics not as frozen")
    files={html.unescape(x) for x in re.findall(r'href="([^"]+)"',page)}
    all_rows=list(csv.DictReader(io.StringIO(demo),delimiter="\t"))
    def substantive(row):
        return any(str(cell).strip() for value in row.values() for cell in (value if isinstance(value,list) else [value]) if cell is not None)
    blank_rows=sum(not substantive(row) for row in all_rows)
    rows=[row for row in all_rows if substantive(row)]
    ids=Counter(r.get("ID","") for r in rows)
    fields=["subject_id","study","group","demographic_group","usual_file_url","file_present","id_unique","group_prefix_match","study_prefix_match","eligible","reason"]
    output=[]
    for row in rows:
        sid=row.get("ID","")
        study=row.get("Study","")
        group=row.get("Group","")
        path=sid+"_01.txt"
        file_ok=path in files
        pattern=bool(re.fullmatch(r"(?:Ga|Ju|Si)(?:Pt|Co)\d{2}",sid))
        group_ok=pattern and group==("1" if sid[2:4]=="Pt" else "2")
        study_ok=pattern and sid[:2]==study
        eligible=ids[sid]==1 and file_ok and group_ok and study_ok
        reason="ELIGIBLE" if eligible else "DUPLICATE_ID" if ids[sid]!=1 else "NO_EXACT_01_FILE" if not file_ok else "GROUP_PREFIX_MISMATCH" if not group_ok else "STUDY_PREFIX_MISMATCH"
        output.append({"subject_id":sid,"study":study,"group":"PD" if group=="1" else "HC" if group=="2" else "UNKNOWN","demographic_group":group,"usual_file_url":BASE+path if file_ok else "","file_present":file_ok,"id_unique":ids[sid]==1,"group_prefix_match":group_ok,"study_prefix_match":study_ok,"eligible":eligible,"reason":reason})
    with OUT.open("w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(output)
    counts=Counter((r["study"],r["group"]) for r in output if r["eligible"])
    totals=Counter(r["group"] for r in output if r["eligible"])
    gate=totals["PD"]>=80 and totals["HC"]>=60 and all(counts[(study,"PD")]>=20 and counts[(study,"HC")]>=15 for study in ("Ga","Ju","Si")) and len({r["subject_id"] for r in output if r["eligible"]})==sum(r["eligible"] for r in output)
    diagnostics={"run_id":"EXP031-COHORT-003","official_listing_url":BASE,"format_url":BASE+"format.txt","demographics_url":BASE+"demographics.txt","requests":3,"demographic_rows":len(rows),"blank_non_subject_rows_skipped":blank_rows,"eligible_people":sum(r["eligible"] for r in output),"eligible_totals":dict(totals),"eligible_by_study_group":{f"{s}_{g}":counts[(s,g)] for s in ("Ga","Ju","Si") for g in ("PD","HC")},"ineligible_subjects":[{"id":r["subject_id"],"reason":r["reason"]} for r in output if not r["eligible"]],"source_gate":"PASS" if gate else "STOP_SUPPORT","raw_force_files_read":False,"original_source_files_saved":False}
    DIAG.write_text(json.dumps(diagnostics,indent=2)+"\n")
    print(json.dumps(diagnostics,indent=2),flush=True)


if __name__=="__main__":main()
