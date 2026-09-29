from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
import re, hashlib, json
import numpy as np, pandas as pd
OUT=Path('/mnt/data/LANGUAGE-DYNAMICAL-SURROGATE-021'); OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(20260929)
# same stripped technical-language corpus
parts=[]
for p in sorted(Path('/usr/local/go/doc').glob('*.html')):
    soup=BeautifulSoup(p.read_text(errors='ignore'),'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    parts.append(re.sub(r'\s+',' ',soup.get_text(' ')).strip())
text='\n'.join(parts)
C=Counter(text); V=64; vocab=[x for x,_ in C.most_common(V-1)]+['<UNK>']; m={x:i for i,x in enumerate(vocab)}
ids=np.array([m.get(ch,V-1) for ch in text],np.int16); N=len(ids); coverage=float(np.mean(ids!=(V-1)))
# predictive contexts 1..5
thr={1:50,2:20,3:10,4:5,5:5}; nxt={L:defaultdict(Counter) for L in thr}; fr={L:Counter() for L in thr}
for t in range(N):
    y=int(ids[t])
    for L in thr:
        if t>=L:
            c=tuple(map(int,ids[t-L:t])); nxt[L][c][y]+=1; fr[L][c]+=1
q={}; qw={}
for L,k in thr.items():
    for c,n in fr[L].items():
        if n>=k:
            a=np.zeros(V)
            for y,z in nxt[L][c].items(): a[y]=z
            q[c]=a/a.sum(); qw[c]=n
ctx=list(q); ci={c:i for i,c in enumerate(ctx)}; Q=np.vstack([q[c] for c in ctx]); H=np.sqrt(Q); W=np.array([qw[c] for c in ctx],float)
def bucket(c): return int.from_bytes(hashlib.blake2b(repr(c).encode(),digest_size=8).digest(),'little')%100
buc=np.array([bucket(c) for c in ctx]); train=buc<80; mu=np.average(H[train],axis=0,weights=W[train]); XX=(H[train]-mu)*np.sqrt(W[train,None]); _,S,Vt=np.linalg.svd(XX,full_matrices=False); comp=Vt; e=S*S; ec=np.cumsum(e/e.sum())
Dmax=32; Z=(H-mu)@comp[:Dmax].T
# state before positions
pc=[None]*(N+1)
for t in range(1,N+1):
    for L in (5,4,3,2,1):
        if t>=L:
            c=tuple(map(int,ids[t-L:t]))
            if c in q: pc[t]=c; break
TC=Counter()
for t in range(1,N-1):
    if pc[t] is not None and pc[t+1] is not None: TC[(pc[t],int(ids[t]),pc[t+1])]+=1
tr=np.array([(ci[a],b,ci[c],ww,bucket(a)) for (a,b,c),ww in TC.items()],dtype=np.int64)
fit=tr[:,4]<70; val=(tr[:,4]>=70)&(tr[:,4]<80); test=tr[:,4]>=80
# support
sup=set()
for a in range(V):
    nf=((tr[:,1]==a)&fit).sum(); nv=((tr[:,1]==a)&val).sum(); nt=((tr[:,1]==a)&test).sum()
    if nf>=15 and nv>=3 and nt>=5: sup.add(a)
main=np.array([a in sup for a in tr[:,1]])

def fit_aff(X,Y,w,alpha):
    xa=np.c_[X,np.ones(len(X))]; sw=np.sqrt(w)[:,None]; xw=xa*sw; yw=Y*sw; G=xw.T@xw; sc=np.trace(G[:-1,:-1])/max(1,X.shape[1]); P=np.eye(G.shape[0]); P[-1,-1]=0; B=np.linalg.solve(G+alpha*max(sc,1e-12)*P,xw.T@yw); return B[:-1].T,B[-1]
def decode(z,D):
    h=mu+z@comp[:D]; h=np.clip(h,0,None); a=h*h; return a/np.clip(a.sum(1,keepdims=True),1e-15,None)
def js(p,r):
    p=np.clip(p,1e-15,1); r=np.clip(r,1e-15,1); z=.5*(p+r); return .5*np.sum(p*np.log2(p/z),1)+.5*np.sum(r*np.log2(r/z),1)
def wmse(y,p,w): return np.average(np.mean((y-p)**2,1),weights=w)
def wr2(y,p,w):
    ym=np.average(y,axis=0,weights=w); return 1-(w[:,None]*(y-p)**2).sum()/(w[:,None]*(y-ym)**2).sum()

rows=[]; models={}
for D in [2,3,4,6,8,10,12,16,24,32]:
    av=[]
    for alpha in [1e-4,1e-3,1e-2,.1,1.0]:
        pp=[]; yy=[]; ww=[]
        for a in sup:
            mf=(tr[:,1]==a)&fit; mv=(tr[:,1]==a)&val
            X=Z[tr[mf,0],:D]; Y=Z[tr[mf,2],:D]; w=tr[mf,3].astype(float); A,b=fit_aff(X,Y,w,alpha); xv=Z[tr[mv,0],:D]; pp.append(xv@A.T+b); yy.append(Z[tr[mv,2],:D]); ww.append(tr[mv,3].astype(float))
        av.append((wmse(np.vstack(yy),np.vstack(pp),np.concatenate(ww)),alpha))
    alpha=min(av)[1]; model={}; reset={}
    for a in sup:
        mm=(tr[:,1]==a)&(tr[:,4]<80); X=Z[tr[mm,0],:D]; Y=Z[tr[mm,2],:D]; w=tr[mm,3].astype(float); model[a]=fit_aff(X,Y,w,alpha); reset[a]=np.average(Y,axis=0,weights=w)
    models[D]=model; idx=np.where(test&main)[0]; X=Z[tr[idx,0],:D]; Y=Z[tr[idx,2],:D]; w=tr[idx,3].astype(float); P=np.empty_like(Y); R=np.empty_like(Y)
    for j,ridx in enumerate(idx): a=int(tr[ridx,1]); A,b=model[a]; P[j]=X[j]@A.T+b; R[j]=reset[a]
    qt=Q[tr[idx,2]]; qp=decode(P,D); qf=decode(Y,D)
    rows.append(dict(D=D,alpha=alpha,pca_energy=float(ec[D-1]),mse=wmse(Y,P,w),mse_reset=wmse(Y,R,w),r2=wr2(Y,P,w),js_bits=float(np.average(js(qt,qp),weights=w)),projection_floor_js=float(np.average(js(qt,qf),weights=w)),top1=float(np.average(qt.argmax(1)==qp.argmax(1),weights=w))))
df=pd.DataFrame(rows); df.to_csv(OUT/'char_dimension_performance.csv',index=False)
# select smallest D within .015 JS bits of best
jb=df.js_bits.min(); sel=df[df.js_bits<=jb+.015].sort_values('D').iloc[0]; Dsel=int(sel.D); model=models[Dsel]
# movement spectrum in selected state
mt=(tr[:,4]<80)&main; dlt=Z[tr[mt,2],:Dsel]-Z[tr[mt,0],:Dsel]; ww=tr[mt,3].astype(float); _,sd,Vtd=np.linalg.svd(dlt*np.sqrt(ww[:,None]),full_matrices=False); de=sd*sd; cum=np.cumsum(de/de.sum()); mov={'D':Dsel,'stable_rank':float(de.sum()/de.max()),'participation_rank':float(de.sum()**2/(de@de)),'d95':int(np.searchsorted(cum,.95)+1),'top2':float(cum[min(1,Dsel-1)]),'top3':float(cum[min(2,Dsel-1)]),'top6':float(cum[min(5,Dsel-1)])}
# multistep conditional rollouts 1..16
pos=[]
for t in range(5,N-18):
    if pc[t] is None or bucket(pc[t])<80: continue
    ok=True
    for h in range(17):
        if pc[t+h] is None: ok=False; break
        if h<16 and int(ids[t+h]) not in sup: ok=False; break
    if ok: pos.append(t)
if len(pos)>5000: pos=list(rng.choice(pos,5000,False))
roll=[]
for h in [1,2,4,8,12,16]:
    pp=[]; yy=[]
    for t in pos:
        z=Z[ci[pc[t]],:Dsel].copy()
        for j in range(h): a=int(ids[t+j]); A,b=model[a]; z=z@A.T+b
        pp.append(z); yy.append(Z[ci[pc[t+h]],:Dsel])
    pp=np.vstack(pp); yy=np.vstack(yy); qt=Q[[ci[pc[t+h]] for t in pos]]; qp=decode(pp,Dsel); roll.append(dict(horizon=h,n=len(pos),mse=wmse(yy,pp,np.ones(len(pp))),r2=wr2(yy,pp,np.ones(len(pp))),js_bits=float(js(qt,qp).mean()),top1=float((qt.argmax(1)==qp.argmax(1)).mean())))
pd.DataFrame(roll).to_csv(OUT/'char_multistep_rollout.csv',index=False)
# closed-loop generation from heldout 5-char contexts
starts=[c for c in ctx if len(c)==5 and bucket(c)>=80 and qw[c]>=10 and all(x!=V-1 for x in c)]; starts=sorted(starts,key=lambda c:qw[c],reverse=True)[:10]
def qz(z): return decode(z[None,:],Dsel)[0]
def sample(q,temp=.85):
    lp=np.log(np.clip(q,1e-15,1))/temp; lp-=lp.max(); p=np.exp(lp); p/=p.sum(); return int(rng.choice(V,p=p))
gens=[]
for c in starts[:5]:
    for rep in range(2):
        z=Z[ci[c],:Dsel].copy(); seq=list(c)
        for j in range(300):
            qq=qz(z); a=sample(qq)
            if a not in model:
                a=next(int(x) for x in np.argsort(qq)[::-1] if int(x) in model)
            seq.append(a); A,b=model[a]; z=z@A.T+b
        s=''.join(vocab[x] if x!=V-1 else '�' for x in seq)
        gens.append(dict(start=''.join(vocab[x] for x in c),sample=rep,text=s))
pd.DataFrame(gens).to_csv(OUT/'char_closed_loop_samples.csv',index=False)
summary={'chars':N,'char_vocab_coverage':coverage,'contexts':len(ctx),'unique_transitions':len(tr),'supported_actions':len(sup),'selected_D':Dsel,'selected':sel.to_dict(),'movement':mov,'rollout':roll,'samples':gens[:4]}
with open(OUT/'char_summary.json','w') as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))
