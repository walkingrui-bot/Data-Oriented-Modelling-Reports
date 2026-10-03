"""EXP031-SOURCE-001: original usual-walk force signals to one derived person table."""

import csv
import io
import json
import math
import threading
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path

import numpy as np


ROOT=Path(__file__).resolve().parents[1]
FEATURES=ROOT/"FORCE_FEATURES.csv"
AUDIT=ROOT/"SOURCE_AUDIT.csv"
SUMMARY=ROOT/"SOURCE_SUMMARY.json"
REQUEST_CAP=180
BYTE_CAP=250*1024*1024
FILE_CAP=2*1024*1024
lock=threading.Lock();requests=0;bytes_read=0
NAMES=[f"{side}_{stat}" for side in ("left","right") for stat in ("mean","std","p95p05","contact_fraction")]+["mean_asymmetry_abs","left_right_corr","total_dominant_hz","total_band_ratio"]


def fetch(url):
    global requests,bytes_read
    errors=[]
    for attempt in (1,2):
        with lock:
            if requests>=REQUEST_CAP:raise RuntimeError("REQUEST_BUDGET_EXCEEDED")
            requests+=1
        try:
            req=urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0 EXP031 person-level force source"})
            with urllib.request.urlopen(req,timeout=40) as r:
                body=r.read(FILE_CAP+1);status=r.status
            if len(body)>FILE_CAP or status!=200:raise ValueError(f"FILE_CAP_OR_HTTP_{status}_{len(body)}")
            with lock:
                bytes_read+=len(body)
                if bytes_read>BYTE_CAP:raise RuntimeError("BYTE_BUDGET_EXCEEDED")
            return body,attempt,errors
        except Exception as exc:
            errors.append(f"{type(exc).__name__}:{str(exc)[:100]}")
            if attempt==2 or "BUDGET_EXCEEDED" in str(exc):raise RuntimeError("|".join(errors)) from exc
    raise AssertionError("unreachable")


def extract(body):
    arr=np.loadtxt(io.BytesIO(body),dtype=np.float64)
    if arr.ndim!=2 or arr.shape[1]!=19 or arr.shape[0]<5000 or not np.isfinite(arr).all():
        raise ValueError(f"NUMERIC_SHAPE_OR_FINITE:{arr.shape}")
    dt=np.diff(arr[:,0])
    if not np.all(dt>0):raise ValueError("TIME_NOT_INCREASING")
    dt_med=float(np.median(dt))
    if not 0.009<=dt_med<=0.011:raise ValueError(f"TIME_INTERVAL:{dt_med}")
    left,right=arr[:,17],arr[:,18]
    total=left+right
    positive=total[total>0]
    if len(positive)<5000 or not np.isfinite(positive).all():raise ValueError("NO_POSITIVE_WALKING_FORCE")
    scale=float(np.median(positive))
    if scale<=0:raise ValueError("NONPOSITIVE_SCALE")
    l,r=left/scale,right/scale
    out={}
    for side,v in (("left",l),("right",r)):
        out[f"{side}_mean"]=float(v.mean())
        out[f"{side}_std"]=float(v.std())
        out[f"{side}_p95p05"]=float(np.quantile(v,.95)-np.quantile(v,.05))
        out[f"{side}_contact_fraction"]=float(np.mean(v>0.1))
    out["mean_asymmetry_abs"]=float(abs(l.mean()-r.mean()))
    l0=l-l.mean();r0=r-r.mean()
    denom=float(np.linalg.norm(l0)*np.linalg.norm(r0))
    out["left_right_corr"]=float(np.dot(l0,r0)/denom) if denom>0 else 0.0
    signal=l+r-(l+r).mean()
    hz=np.fft.rfftfreq(len(signal),1/100)
    power=np.abs(np.fft.rfft(signal))**2
    low=(hz>=.4)&(hz<=3);wide=(hz>=.4)&(hz<=10)
    if not np.any(low) or float(power[wide].sum())<=0:raise ValueError("NO_GAIT_BAND_POWER")
    out["total_dominant_hz"]=float(hz[low][np.argmax(power[low])])
    out["total_band_ratio"]=float(power[low].sum()/power[wide].sum())
    if set(out)!=set(NAMES) or not all(math.isfinite(v) for v in out.values()):raise ValueError("FEATURE_SCHEMA_OR_NONFINITE")
    return out,arr.shape[0],dt_med


def one(row):
    sid=row["subject_id"]
    feat={"subject_id":sid,"study":row["study"],"label":1 if row["group"]=="PD" else 0,**{name:"" for name in NAMES}}
    audit={"subject_id":sid,"study":row["study"],"group":row["group"],"url":row["usual_file_url"],"status":"","bytes":0,"rows":"","columns":"","dt_median":"","retry_count":0,"retry_errors":"","error":""}
    try:
        body,attempts,errors=fetch(row["usual_file_url"])
        audit["bytes"]=len(body);audit["retry_count"]=attempts-1;audit["retry_errors"]="|".join(errors)
        values,n,dt=extract(body)
        feat.update(values);audit["status"]="READABLE_NUMERIC";audit["rows"]=n;audit["columns"]=19;audit["dt_median"]=dt
    except Exception as exc:
        audit["status"]="SOURCE_OR_NUMERIC_FAIL";audit["error"]=f"{type(exc).__name__}:{str(exc)[:180]}"
    return feat,audit


def main():
    if any(p.exists() for p in (FEATURES,AUDIT,SUMMARY)):raise FileExistsError("Preserve EXP031-SOURCE-001 outputs")
    with (ROOT/"COHORT_AUDIT.csv").open(newline="") as f:
        people=[r for r in csv.DictReader(f) if r["eligible"]=="True"]
    if len(people)!=165 or len({r["subject_id"] for r in people})!=165:raise ValueError("Cohort gate not 165 unique")
    audits=[]
    feature_fields=["subject_id","study","label"]+NAMES
    audit_fields=["subject_id","study","group","url","status","bytes","rows","columns","dt_median","retry_count","retry_errors","error"]
    with FEATURES.open("w",newline="") as ff,AUDIT.open("w",newline="") as fa:
        fw=csv.DictWriter(ff,fieldnames=feature_fields);aw=csv.DictWriter(fa,fieldnames=audit_fields)
        fw.writeheader();aw.writeheader()
        with ThreadPoolExecutor(max_workers=6) as pool:
            futures=[pool.submit(one,row) for row in people]
            for future in as_completed(futures):
                feat,audit=future.result();fw.writerow(feat);aw.writerow(audit);ff.flush();fa.flush();audits.append(audit)
                if len(audits)%25==0:print("persons",len(audits),"requests",requests,"bytes",bytes_read,flush=True)
    counts=Counter((r["study"],r["group"]) for r in audits if r["status"]=="READABLE_NUMERIC")
    denominators=Counter((r["study"],r["group"]) for r in audits)
    gate=all(counts[k]/denominators[k]>=.9 for k in denominators) and requests<=REQUEST_CAP and bytes_read<=BYTE_CAP
    summary={"run_id":"EXP031-SOURCE-001","people":len(audits),"requests":requests,"bytes_read":bytes_read,"readable_numeric":sum(r["status"]=="READABLE_NUMERIC" for r in audits),"numeric_by_study_group":{f"{s}_{g}":counts[(s,g)] for s in ("Ga","Ju","Si") for g in ("PD","HC")},"denominator_by_study_group":{f"{s}_{g}":denominators[(s,g)] for s in ("Ga","Ju","Si") for g in ("PD","HC")},"failed_ids":[r["subject_id"] for r in audits if r["status"]!="READABLE_NUMERIC"],"retries":sum(int(r["retry_count"]) for r in audits),"source_gate":"PASS" if gate else "STOP_NUMERIC_SOURCE","original_force_files_saved":False}
    SUMMARY.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2),flush=True)
    if not gate:raise SystemExit(2)


if __name__=="__main__":main()
