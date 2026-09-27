#!/usr/bin/env python3
"""Reproduce NATLANG-COMPAT-004B from pinned FLORES-200 dev files.

This script downloads exact source files from the pinned Git commit unless
--data-dir already contains them. It recreates the main surface/script-neutral
pair-class measurements, same-language script-swap controls, data geometry,
and low-dimensional neighborhood preservation.

External corpus text is not shipped in the evidence ZIP. See source_manifest.csv.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, math, re, unicodedata
from pathlib import Path
from urllib.request import urlopen
import numpy as np

REPO = "common-parallel-corpora/common-parallel-corpora"
COMMIT = "dbc2cd91df89c52dffe899efe7ea4dff63e172fc"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{COMMIT}/data/common-parallel-corpora/flores-200-dev/"
N = 997
DH, DS, D = 24, 8, 32
FILES = [
    ("ace","Arab","ace_Arab.dev"),("ace","Latn","ace_Latn.dev"),
    ("arb","Arab","arb_Arab.dev"),("arb","Latn","arb_Latn.dev"),
    ("bjn","Arab","bjn_Arab.dev"),("bjn","Latn","bjn_Latn.dev"),
    ("kas","Arab","kas_Arab.dev"),("kas","Deva","kas_Deva.dev"),
    ("knc","Arab","knc_Arab.dev"),("knc","Latn","knc_Latn.dev"),
    ("min","Arab","min_Arab.dev"),("min","Latn","min_Latn.dev"),
    ("taq","Latn","taq_Latn.dev"),("taq","Tfng","taq_Tfng.dev"),
    ("zho","Hans","zho_Hans.dev"),("zho","Hant","zho_Hant.dev"),
    ("hin","Deva","hin_Deva.dev"),("tzm","Tfng","tzm_Tfng.dev"),
    ("yue","Hant","yue_Hant.dev"),
]
SAME = [
    ("ace_Arab.dev","ace_Latn.dev"),("arb_Arab.dev","arb_Latn.dev"),
    ("bjn_Arab.dev","bjn_Latn.dev"),("kas_Arab.dev","kas_Deva.dev"),
    ("knc_Arab.dev","knc_Latn.dev"),("min_Arab.dev","min_Latn.dev"),
    ("taq_Latn.dev","taq_Tfng.dev"),("zho_Hans.dev","zho_Hant.dev"),
]


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def load_sources(data_dir: Path, manifest_path: Path):
    data_dir.mkdir(parents=True, exist_ok=True)
    expected = {}
    with manifest_path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f): expected[r["file"]] = r["git_blob_sha"]
    texts, meta = {}, {}
    for lang, script, fn in FILES:
        p = data_dir / fn
        if not p.exists():
            print("download", fn)
            p.write_bytes(urlopen(RAW_BASE + fn, timeout=60).read())
        b = p.read_bytes()
        got = git_blob_sha1(b)
        if fn in expected and got != expected[fn]:
            raise RuntimeError(f"Git blob mismatch for {fn}: {got} != {expected[fn]}")
        lines = b.decode("utf-8").splitlines()
        if len(lines) != N: raise RuntimeError(f"{fn}: expected {N} rows, got {len(lines)}")
        texts[fn] = lines
        meta[fn] = {"lang":lang,"script":script}
    return texts, meta


def fnv1a(s: str) -> int:
    h=2166136261
    for ch in s:
        h ^= ord(ch); h = (h * 16777619) & 0xffffffff
    return h


def char_class(ch: str) -> str:
    cat = unicodedata.category(ch)
    if cat.startswith("L"): return "L"
    if cat.startswith("N"): return "N"
    if cat.startswith("M"): return "M"
    if ch.isspace(): return "_"
    if ch in ".!?。！？": return "."
    if ch in ",，、؛،": return ","
    if cat.startswith("P"): return "P"
    if cat.startswith("S"): return "S"
    return "O"


def feature(s: str, neutral=False) -> np.ndarray:
    s0 = unicodedata.normalize("NFKC", s).lower()
    cp = list(s0)
    seq = [char_class(c) for c in cp] if neutral else cp
    v = np.zeros(D, np.float64)
    for n in (3,4,5):
        for i in range(len(seq)-n+1):
            h = fnv1a("".join(seq[i:i+n])); v[h % DH] += -1.0 if (h & 0x80000000) else 1.0
    z = np.linalg.norm(v[:DH]); v[:DH] /= (z if z else 1.0)
    L=max(1,len(cp)); words=s.strip().split(); lens=np.array([len(w) for w in words], float)
    wm=float(lens.mean()) if len(lens) else 0.0; ws=float(lens.std()) if len(lens) else 0.0
    digit=sum(c.isdigit() for c in cp); punct=sum(unicodedata.category(c).startswith("P") for c in cp)
    space=sum(c.isspace() for c in cp); mark=sum(unicodedata.category(c).startswith("M") for c in cp)
    vals=[math.log1p(L),math.log1p(len(words)),digit/L,punct/L,space/L,mark/L,math.log1p(wm),math.log1p(ws)]
    v[DH:] = vals
    return v


def split(seed=20260927):
    rng=np.random.default_rng(seed); idx=np.arange(N); rng.shuffle(idx); return idx[:800], idx[800:]


def standardize(X, train):
    mu=X[train].mean(0); sd=X[train].std(0); sd[sd<1e-8]=1.0; return (X-mu)/sd


def ridge_map(X,Y,train,lam=10.0, perm=False):
    Xt=X[train]; yt=train.copy()
    if perm: yt=np.roll(yt,-137)
    Yt=Y[yt]
    return np.linalg.solve(Xt.T@Xt + lam*np.eye(D), Xt.T@Yt)


def retrieval(X,Y,test,B=None):
    Q=X[test] if B is None else X[test]@B; T=Y[test]
    Q=Q/np.maximum(np.linalg.norm(Q,axis=1,keepdims=True),1e-12); T=T/np.maximum(np.linalg.norm(T,axis=1,keepdims=True),1e-12)
    S=Q@T.T; order=np.argsort(-S,axis=1); truth=np.arange(len(test)); ranks=np.array([np.where(order[i]==i)[0][0]+1 for i in truth])
    return {"top1":float(np.mean(ranks==1)),"mrr":float(np.mean(1/ranks))}


def geometry(X):
    C=np.cov(X,rowvar=False,bias=True); e=np.linalg.eigvalsh(C)[::-1]; e=np.maximum(e,0); tr=e.sum();
    stable=tr/max(e[0],1e-12); participation=tr*tr/max(np.sum(e*e),1e-12); p95=int(np.searchsorted(np.cumsum(e),.95*tr)+1)
    return {"stable_rank":float(stable),"participation_rank":float(participation),"pca95":p95,"top3_energy":float(e[:3].sum()/tr)}


def knn_retention(X, kdim, n=220, k=10):
    X=X[:n]; _,_,Vt=np.linalg.svd(X-X.mean(0),full_matrices=False); P=(X-X.mean(0))@Vt[:kdim].T
    def neigh(A):
        d=((A[:,None,:]-A[None,:,:])**2).sum(-1); np.fill_diagonal(d,np.inf); return np.argsort(d,axis=1)[:,:k]
    A,B=neigh(X),neigh(P); return float(np.mean([len(set(A[i])&set(B[i]))/k for i in range(n)]))


def run_space(F, meta, train, test):
    Z={f:standardize(x,train) for f,x in F.items()}; pairs=[]
    files=list(F)
    same_script=[]; far=[]
    for i,a in enumerate(files):
        for b in files[i+1:]:
            if meta[a]["lang"]==meta[b]["lang"]: typ="SAME_LANG_DIFF_SCRIPT"
            elif meta[a]["script"]==meta[b]["script"]: typ="DIFF_LANG_SAME_SCRIPT"; same_script.append((a,b))
            else: typ="DIFF_LANG_DIFF_SCRIPT"; far.append((a,b))
            if typ!="DIFF_LANG_DIFF_SCRIPT": pairs.append((a,b,typ))
    for k in range(len(same_script)):
        a,b=far[(k*17+3)%len(far)]; pairs.append((a,b,"DIFF_LANG_DIFF_SCRIPT"))
    rows=[]
    for a,b,t in pairs:
        da=(retrieval(Z[a],Z[b],test)["top1"]+retrieval(Z[b],Z[a],test)["top1"])/2
        mab=ridge_map(Z[a],Z[b],train); mba=ridge_map(Z[b],Z[a],train)
        ma=(retrieval(Z[a],Z[b],test,mab)["top1"]+retrieval(Z[b],Z[a],test,mba)["top1"])/2
        rows.append({"a":a,"b":b,"type":t,"direct":da,"mapped":ma,"gain":ma-da})
    return Z,rows


def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-dir",type=Path,default=Path("flores_cache")); ap.add_argument("--out",type=Path,default=Path("reproduced_004b"));
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    here=Path(__file__).resolve().parent; texts,meta=load_sources(args.data_dir,here/"source_manifest.csv")
    train,test=split(); FS={f:np.stack([feature(s,False) for s in lines]) for f,lines in texts.items()}; FN={f:np.stack([feature(s,True) for s in lines]) for f,lines in texts.items()}
    Zs,srows=run_space(FS,meta,train,test); Zn,nrows=run_space(FN,meta,train,test)
    def save_rows(name,rows):
        with (args.out/name).open("w",newline="",encoding="utf-8") as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    save_rows("pairwise_surface_results.csv",srows); save_rows("pairwise_script_neutral_results.csv",nrows)
    # same-language controls
    same=[]
    for a,b in SAME:
        da=(retrieval(Zs[a],Zs[b],test)["top1"]+retrieval(Zs[b],Zs[a],test)["top1"])/2
        ma=(retrieval(Zs[a],Zs[b],test,ridge_map(Zs[a],Zs[b],train))["top1"]+retrieval(Zs[b],Zs[a],test,ridge_map(Zs[b],Zs[a],train))["top1"])/2
        pa=(retrieval(Zs[a],Zs[b],test,ridge_map(Zs[a],Zs[b],train,perm=True))["top1"]+retrieval(Zs[b],Zs[a],test,ridge_map(Zs[b],Zs[a],train,perm=True))["top1"])/2
        same.append({"language":meta[a]["lang"],"a":a,"b":b,"direct":da,"mapped":ma,"gain":ma-da,"permuted":pa})
    save_rows("same_language_script_swap_results.csv",same)
    # geometry diagnostics
    grows=[]
    for f in [x for p in SAME for x in p]:
        g=geometry(Zs[f][train]); g.update({"variant":f,"knn4":knn_retention(Zs[f][train],4),"knn8":knn_retention(Zs[f][train],8)}); grows.append(g)
    save_rows("surface_geometry_primary_variants.csv",grows)
    summary={}
    for lab,rows in [("surface",srows),("script_neutral",nrows)]:
        summary[lab]={}
        for t in ("SAME_LANG_DIFF_SCRIPT","DIFF_LANG_SAME_SCRIPT","DIFF_LANG_DIFF_SCRIPT"):
            a=[r for r in rows if r["type"]==t]; summary[lab][t]={"n":len(a),"direct":float(np.mean([r["direct"] for r in a])),"mapped":float(np.mean([r["mapped"] for r in a])),"gain":float(np.mean([r["gain"] for r in a]))}
    (args.out/"summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
