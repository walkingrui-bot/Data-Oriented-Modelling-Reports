#!/usr/bin/env python3
"""Reproduction script for RESPONSE-REGIME-004B1.

Download the seven pinned files listed in SOURCE_MANIFEST.json into --raw-dir,
then run this script. It verifies Git blob SHA identities and recomputes the
transition geometry and leave-one-style-out target retrieval.
"""
import argparse, hashlib, json, math, re
from collections import Counter
from pathlib import Path
import numpy as np

FILES = {
 'naive':'test/naive_source.txt', 'syntactic':'test/syntactic_source.txt',
 'morphological':'test/morphological_source.txt', 'lexical':'test/lexical_source.txt',
 'semantic':'test/semantic_source.txt', 'missing':'test/missing_source.txt',
 'sql':'test/patients_test.sql'}
BLOBS = {
 'naive':'901e481c69ae97a9a0747ab33f996dc5aa0c69e7',
 'syntactic':'606b5f7b29f92fc8d600fab7ac6792220d556904',
 'morphological':'f3bf0fd2bf05e648d83a55ac70d673160f24b990',
 'lexical':'94ef608904e42bc5300c3344c59de7f35df4dcb5',
 'semantic':'49caa4cae431f439a392c2d9cd100de2d40ee469',
 'missing':'c9041b4d44f3fc4b311cf87fd66237b23488a123',
 'sql':'cb33a787182deb62d39d9eec0ba7e7eb22371beb'}
STYLES=['naive','syntactic','morphological','lexical','semantic','missing']

def git_blob_sha(raw: bytes):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()

def read_data(root):
    out={}
    for k,rel in FILES.items():
        p=root/Path(rel).name
        raw=p.read_bytes()
        got=git_blob_sha(raw)
        if got != BLOBS[k]: raise ValueError(f'{p}: blob {got} != expected {BLOBS[k]}')
        out[k]=[x.strip() for x in raw.decode('utf-8').splitlines() if x.strip()]
    if any(len(out[k])!=57 for k in FILES): raise ValueError('Expected 57 aligned rows in each file')
    return out

def tok_nl(s): return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+|[?.,:;]",s.lower())
def tok_sql(s):
    z=re.findall(r'<>|>=|<=|=|>|<|[a-z_]+|\d+|[(),.;]',s.lower())
    return ['table' if t=='patients' else t for t in z]

def vocab(groups,k,tokenizer):
    c=Counter(t for arr in groups for s in arr for t in tokenizer(s))
    top=sorted(c.items(),key=lambda x:(-x[1],x[0]))[:k]
    return ['<BOS>','<EOS>','<UNK>']+[x[0] for x in top]

def geom(rows,V,tokenizer):
    ind={t:i for i,t in enumerate(V)}; d=len(V)
    C=np.zeros((d,d),float); cur=np.zeros(d); nxt=np.zeros(d); T=0
    for s in rows:
        ts=['<BOS>']+[t if t in ind else '<UNK>' for t in tokenizer(s)]+['<EOS>']
        for a,b in zip(ts,ts[1:]):
            i,j=ind[a],ind[b]; C[i,j]+=1; cur[i]+=1; nxt[j]+=1; T+=1
    pg=nxt/T; M=np.zeros((d,d))
    for i in range(d):
        if cur[i]:
            v=C[i]/cur[i]-pg; M += (cur[i]/T)*np.outer(v,v)
    ev,U=np.linalg.eigh(M); order=np.argsort(ev)[::-1]; ev=ev[order]; U=U[:,order]
    tr=float(ev.sum())
    return {'stable_rank':tr/ev[0], 'participation_rank':tr*tr/float((ev*ev).sum()), 'top3':float(ev[:3].sum()/tr), 'U3':U[:,:3]}

def overlap(a,b): return float(np.linalg.norm(a['U3'].T@b['U3'],'fro')**2/3)

def norm_text(s): return ' '+re.sub(r'\s+',' ',re.sub(r'[^a-z0-9]+',' ',s.lower()).strip())+' '
def fnv1a(s):
    h=2166136261
    for ch in s:
        h ^= ord(ch); h=(h*16777619)&0xffffffff
    return h

def ngram_counts(s,D=4096):
    s=norm_text(s); c=Counter()
    for n in (3,4,5):
        for i in range(len(s)-n+1): c[fnv1a(s[i:i+n])%D]+=1
    return c

def build_vectors(data,D=4096):
    docs=[ngram_counts(s,D) for st in STYLES for s in data[st]]
    df=Counter(k for g in docs for k in g)
    idf=np.array([math.log((len(docs)+1)/(df.get(k,0)+1))+1 for k in range(D)])
    V={}; off=0
    for st in STYLES:
        V[st]=[]
        for s in data[st]:
            g=ngram_counts(s,D); x=np.zeros(D)
            for k,c in g.items(): x[k]=(1+math.log(c))*idf[k]
            n=np.linalg.norm(x); V[st].append(x/n if n else x)
    return V

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--raw-dir',type=Path,required=True); ap.add_argument('--out',type=Path,default=Path('recomputed.json')); a=ap.parse_args()
    data=read_data(a.raw_dir)
    Vocab=vocab([data[s] for s in STYLES],64,tok_nl)
    G={s:geom(data[s],Vocab,tok_nl) for s in STYLES}
    sqlG=geom(data['sql'],vocab([data['sql']],64,tok_sql),tok_sql)
    X=build_vectors(data)
    loo={}
    for hold in STYLES:
        prot=[]
        for i in range(57):
            p=sum((X[s][i] for s in STYLES if s!=hold),np.zeros(4096)); n=np.linalg.norm(p); prot.append(p/n if n else p)
        sims=np.stack([X[hold][i]@np.stack(prot).T for i in range(57)])
        ranks=[]
        for i in range(57): ranks.append(int(np.flatnonzero(np.argsort(-sims[i])==i)[0])+1)
        loo[hold]={'top1':sum(r==1 for r in ranks)/57,'mrr':sum(1/r for r in ranks)/57}
    out={'geometry':{s:{'stable_rank':G[s]['stable_rank'],'participation_rank':G[s]['participation_rank'],'top3':G[s]['top3'],'overlap_with_naive':overlap(G['naive'],G[s])} for s in STYLES},'sql_geometry':{k:sqlG[k] for k in ('stable_rank','participation_rank','top3')},'leave_one_style_out':loo}
    a.out.write_text(json.dumps(out,indent=2),encoding='utf-8')
if __name__=='__main__': main()
