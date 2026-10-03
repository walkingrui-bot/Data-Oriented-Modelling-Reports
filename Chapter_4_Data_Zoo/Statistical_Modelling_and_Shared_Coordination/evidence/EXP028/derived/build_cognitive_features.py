"""EXP028-SOURCE-001: only new cognitive-task features, streaming official originals."""

import csv
import json
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
PARENT=ROOT.parent/"STAT-PSYMOE-EXP026-20261002-001"
sys.path.insert(0,str(PARENT/"derived"))
import build_features as source

FEATURES=ROOT/"COGNITIVE_FEATURES.csv"
AUDIT=ROOT/"SOURCE_AUDIT.csv"
SUMMARY=ROOT/"SOURCE_SUMMARY.json"
source.REQUEST_CAP=1200
source.BYTE_CAP=180*1024*1024


def one_person(subject_id,label):
    feat={"subject_id":subject_id,**{name:"" for name in source.MOTION_NAMES}}
    audit={"subject_id":subject_id,"label":label,"observation_status":"","left_status":"","right_status":"","left_rows":"","right_rows":"","retry_count":0,"retry_errors":"","error":""}
    try:
        body,attempts,errors=source.fetch(f"movement/observation_{subject_id}.json")
        audit["retry_count"]+=attempts-1;audit["retry_errors"]+="|".join(errors)
        obs=json.loads(body)
        if obs.get("subject_id")!=subject_id or obs.get("sampling_rate")!=100:
            raise ValueError("SCHEMA_ERROR:identity_or_sampling_rate")
        sessions=[s for s in obs.get("session",[]) if s.get("record_name")=="RelaxedTask"]
        if len(sessions)!=1:raise ValueError("SCHEMA_ERROR:task_session_count")
        session=sessions[0];n=session.get("rows")
        if not isinstance(n,int) or n<1000 or n>4096:raise ValueError("SCHEMA_ERROR:row_count")
        records={r.get("device_location"):r for r in session.get("records",[])}
        if set(records)!={"LeftWrist","RightWrist"}:raise ValueError("SCHEMA_ERROR:bilateral_records")
        for wrist in ("Left","Right"):
            r=records[wrist+"Wrist"]
            if r.get("file_name")!=f"timeseries/{subject_id}_RelaxedTask_{wrist}Wrist.txt" or r.get("channels")!=source.CHANNELS:
                raise ValueError("SCHEMA_ERROR:reference_or_channels")
        audit["observation_status"]="OK"
    except Exception as exc:
        audit["observation_status"]="FAIL";audit["error"]+=f"OBSERVATION:{type(exc).__name__}:{str(exc)[:130]}|"
        return feat,audit
    wrists={}
    for wrist in ("Left","Right"):
        try:
            blob,attempts,errors=source.fetch(f"movement/timeseries/{subject_id}_RelaxedTask_{wrist}Wrist.txt")
            audit["retry_count"]+=attempts-1;audit["retry_errors"]+="|".join(errors)
            wrists[wrist.lower()]=source.wrist_features(blob,n,100)
            audit[wrist.lower()+"_status"]="OK";audit[wrist.lower()+"_rows"]=n
        except Exception as exc:
            audit[wrist.lower()+"_status"]="FAIL";audit["error"]+=f"{wrist.upper()}:{type(exc).__name__}:{str(exc)[:130]}|"
    for wrist in ("left","right"):
        if wrist in wrists:
            feat.update({f"{wrist}_{name}":value for name,value in wrists[wrist].items()})
    if len(wrists)==2:
        feat.update({f"absdiff_{name}":abs(wrists["left"][name]-wrists["right"][name]) for name in source.ONE_WRIST})
    return feat,audit


def main():
    if any(p.exists() for p in (FEATURES,AUDIT,SUMMARY)):raise FileExistsError("Preserve EXP028-SOURCE-001 outputs")
    with (PARENT/"SPLIT_MANIFEST.csv").open(newline="") as f:
        people=[r for r in csv.DictReader(f) if r["split"]!="test"]
    if len(people)!=372 or len({r["subject_id"] for r in people})!=372 or Counter(r["label"] for r in people)!={"0":62,"1":220,"2":90}:
        raise ValueError("Expected 372 development people")
    fields=["subject_id"]+source.MOTION_NAMES
    audit_fields=["subject_id","label","observation_status","left_status","right_status","left_rows","right_rows","retry_count","retry_errors","error"]
    audits=[]
    with FEATURES.open("w",newline="") as ff,AUDIT.open("w",newline="") as fa:
        fw=csv.DictWriter(ff,fieldnames=fields);aw=csv.DictWriter(fa,fieldnames=audit_fields)
        fw.writeheader();aw.writeheader()
        with ThreadPoolExecutor(max_workers=10) as pool:
            futures=[pool.submit(one_person,r["subject_id"],r["label"]) for r in people]
            for future in as_completed(futures):
                feat,audit=future.result();fw.writerow(feat);aw.writerow(audit);ff.flush();fa.flush();audits.append(audit)
                if len(audits)%50==0:print("persons",len(audits),"requests",source.requests,"bytes",source.bytes_read,flush=True)
    missing=[r for r in audits if r["left_status"]!="OK" or r["right_status"]!="OK"]
    missing_by_class=Counter(r["label"] for r in missing)
    schema=[r["subject_id"] for r in audits if "SCHEMA_ERROR" in r["error"]]
    gate=len(missing)<=18 and missing_by_class["0"]<=6 and missing_by_class["1"]<=22 and missing_by_class["2"]<=9 and not schema and source.requests<=1200 and source.bytes_read<=180*1024*1024
    summary={"run_id":"EXP028-SOURCE-001","development_people":len(audits),"original_test_used":False,"requests_in_script":source.requests,"preflight_observation_requests":1,"bytes_in_script":source.bytes_read,"observation_ok":sum(r["observation_status"]=="OK" for r in audits),"left_ok":sum(r["left_status"]=="OK" for r in audits),"right_ok":sum(r["right_status"]=="OK" for r in audits),"bilateral_missing_people":len(missing),"bilateral_missing_by_class":dict(missing_by_class),"schema_error_ids":schema,"retries":sum(int(r["retry_count"]) for r in audits),"source_gate":"PASS" if gate else "STOP_SOURCE","original_responses_saved":False}
    SUMMARY.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    if not gate:raise SystemExit(2)


if __name__=="__main__":main()
