from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
import re, hashlib, json
import numpy as np, pandas as pd
OUT=Path('/mnt/data/LANGUAGE-DYNAMICAL-SURROGATE-021'); OUT.mkdir(exist_ok=True)
rng=np.random.default_rng(20260929)
# corpus
parts=[]
for p in sorted(Path('/usr/local/go/doc').glob('*.html')):
    soup=BeautifulSoup(p.read_text(errors='ignore'),'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    parts.append(re.sub(r'\s+',' ',soup.get_text(' ')).strip())
corpus='\n'.join(parts)
pat=re.compile(r"[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|[^\s]")
toks=pat.findall(corpus); C=Counter(toks); V=128
vocab=[x for x,_ in C.most_common(V-1)]+['<UNK>']; m={x:i for i,x in enumerate(vocab)}
ids=np.array([m.get(x,V-1) for x in toks],np.int16); N=len(ids)
# predictive contexts
thr={1:50,2:20,3:10,4:5}; nxt={L:defaultdict(Counter) for L in thr}; freq={L:Counter() for L in thr}
for t in range(N):
    y=int(ids[t])
    for L in thr:
        if t>=L:
            c=tuple(map(int,ids[t-L:t])); nxt[L][c][y]+=1; freq[L][c]+=1
q={}; wctx={}
for L,k in thr.items():
    for c,n in freq[L].items():
        if n>=k:
            a=np.zeros(V); 
            for y,z in nxt[L][c].items(): a[y]=z
            q[c]=a/a.sum(); wctx[c]=n
ctx=list(q); ci={c:i for i,c in enumerate(ctx)}; Q=np.vstack([q[c] for c in ctx]); H=np.sqrt(Q); W=np.array([wctx[c] for c in ctx],float)
def bucket(c): return int.from_bytes(hashlib.blake2b(repr(c).encode(),digest_size=8).digest(),'little')%100
buc=np.array([bucket(c) for c in ctx]); train=buc<80
mu=np.average(H[train],axis=0,weights=W[train]); X=(H[train]-mu)*np.sqrt(W[train,None]); _,S,Vt=np.linalg.svd(X,full_matrices=False)
Dmax=64; comp=Vt[:Dmax]; Z=(H-mu)@comp.T; e=S*S; ec=np.cumsum(e/e.sum())
# position contexts
pc=[None]*(N+1)
for t in range(1,N+1):
    for L in (4,3,2,1):
        if t>=L:
            c=tuple(map(int,ids[t-L:t]))
            if c in q: pc[t]=c; break
# unique weighted transitions
TC=Counter()
for t in range(1,N-1):
    if pc[t] is not None and pc[t+1] is not None: TC[(pc[t],int(ids[t]),pc[t+1])]+=1
tr=np.array([(ci[a],b,ci[c],ww,bucket(a)) for (a,b,c),ww in TC.items()],dtype=np.int64)
fit=tr[:,4]<70; val=(tr[:,4]>=70)&(tr[:,4]<80); test=tr[:,4]>=80
# exact same support rule
stats=[]
for a in range(V):
    stats.append((a,((tr[:,1]==a)&fit).sum(),((tr[:,1]==a)&val).sum(),((tr[:,1]==a)&test).sum(),tr[(tr[:,1]==a)&(tr[:,4]<80),3].sum()))
supported={a for a,nf,nv,nt,ww in stats if nf>=12 and nv>=3 and nt>=5}; main=np.array([a in supported for a in tr[:,1]])

def fit_aff(X,Y,w,alpha):
    xa=np.c_[X,np.ones(len(X))]; sw=np.sqrt(w)[:,None]; xw=xa*sw; yw=Y*sw
    G=xw.T@xw; scale=np.trace(G[:-1,:-1])/max(1,X.shape[1]); P=np.eye(G.shape[0]); P[-1,-1]=0
    B=np.linalg.solve(G+alpha*max(scale,1e-12)*P,xw.T@yw); return B[:-1].T,B[-1]
def decode(z,D):
    h=mu+z@comp[:D]; h=np.clip(h,0,None); qq=h*h; return qq/np.clip(qq.sum(1,keepdims=True),1e-15,None)
def js(p,r):
    p=np.clip(p,1e-15,1); r=np.clip(r,1e-15,1); z=.5*(p+r)
    return .5*np.sum(p*np.log2(p/z),1)+.5*np.sum(r*np.log2(r/z),1)
def wmse(y,p,w): return np.average(np.mean((y-p)**2,1),weights=w)
def wr2(y,p,w):
    ym=np.average(y,axis=0,weights=w); return 1-(w[:,None]*(y-p)**2).sum()/(w[:,None]*(y-ym)**2).sum()

Ds=[6,10,12,16,24]; rs=[1,2,3,4,6,8,10,12,16,24]
rows=[]; mov=[]; fitted={}
for D in Ds:
    mt=(tr[:,4]<80)&main; Xs=Z[tr[mt,0],:D]; Ys=Z[tr[mt,2],:D]; wt=tr[mt,3].astype(float); delta=Ys-Xs
    _,sd,Vtd=np.linalg.svd(delta*np.sqrt(wt[:,None]),full_matrices=False); de=sd*sd; cum=np.cumsum(de/de.sum()); Rmax=min(24,D); basis=Vtd[:Rmax]
    mov.append(dict(D=D,stable_rank=float(de.sum()/de.max()),participation_rank=float(de.sum()**2/(de@de)),d95=int(np.searchsorted(cum,.95)+1),top2=float(cum[1]),top3=float(cum[2]),top6=float(cum[min(5,len(cum)-1)]),top10=float(cum[min(9,len(cum)-1)])))
    # choose alpha by fitting Rmax coeffs once per token per alpha
    aval=[]
    for alpha in [0.01,0.1,1.0]:
        PP=[]; YY=[]; WW=[]
        for a in supported:
            mf=(tr[:,1]==a)&fit; mv=(tr[:,1]==a)&val
            xf=Z[tr[mf,0],:D]; yf=Z[tr[mf,2],:D]; wf=tr[mf,3].astype(float); ct=(yf-xf)@basis.T
            A,b=fit_aff(xf,ct,wf,alpha); xv=Z[tr[mv,0],:D]; cp=xv@A.T+b; PP.append(xv+cp@basis); YY.append(Z[tr[mv,2],:D]); WW.append(tr[mv,3].astype(float))
        aval.append((wmse(np.vstack(YY),np.vstack(PP),np.concatenate(WW)),alpha))
    alpha=min(aval)[1]
    # final fits max coeff dimension
    model={}; fixed={}
    for a in supported:
        mm=(tr[:,1]==a)&(tr[:,4]<80); xa=Z[tr[mm,0],:D]; ya=Z[tr[mm,2],:D]; wa=tr[mm,3].astype(float); ct=(ya-xa)@basis.T
        model[a]=fit_aff(xa,ct,wa,alpha); fixed[a]=np.average(ct,axis=0,weights=wa)
    fitted[D]=(basis,model,alpha)
    idx=np.where(test&main)[0]; xt=Z[tr[idx,0],:D]; yt=Z[tr[idx,2],:D]; w=tr[idx,3].astype(float); qtrue=Q[tr[idx,2]]
    # compute max coefficient predictions once
    cp=np.empty((len(idx),Rmax)); cf=np.empty_like(cp)
    for j,ridx in enumerate(idx):
        a=int(tr[ridx,1]); A,b=model[a]; cp[j]=xt[j]@A.T+b; cf[j]=fixed[a]
    for r in rs:
        if r>Rmax: continue
        pred=xt+cp[:,:r]@basis[:r]; predf=xt+cf[:,:r]@basis[:r]
        qp=decode(pred,D); qf=decode(predf,D); qfloor=decode(yt,D)
        rows.append(dict(D=D,r=r,alpha=alpha,movement_energy=float(cum[r-1]),mse_state_dep=wmse(yt,pred,w),mse_fixed_control=wmse(yt,predf,w),r2_state_dep=wr2(yt,pred,w),js_state_dep_bits=float(np.average(js(qtrue,qp),weights=w)),js_fixed_control_bits=float(np.average(js(qtrue,qf),weights=w)),js_projection_floor_bits=float(np.average(js(qtrue,qfloor),weights=w)),top1_teacher_match=float(np.average(qtrue.argmax(1)==qp.argmax(1),weights=w))))

movdf=pd.DataFrame(mov); df=pd.DataFrame(rows); movdf.to_csv(OUT/'movement_spectrum_lowD.csv',index=False); df.to_csv(OUT/'factorized_control_surrogate_lowD.csv',index=False)
# Pareto per D: smallest r with 95% of within-D JS gain
prs=[]
for D in Ds:
    s=df[df.D==D].sort_values('r').copy(); j1=s.iloc[0].js_state_dep_bits; jb=s.js_state_dep_bits.min(); s['gain']=(j1-s.js_state_dep_bits)/(j1-jb) if j1>jb else 0
    c=s[s.gain>=.95]; row=(c.iloc[0] if len(c) else s.loc[s.js_state_dep_bits.idxmin()]).to_dict(); row['params']=len(supported)*int(row['r'])*(D+1); prs.append(row)
pd.DataFrame(prs).to_csv(OUT/'factorized_control_pareto_lowD.csv',index=False)
# choose compact model: lowest parameter Pareto point within absolute 0.02 JS bits of best Pareto (transparent tolerance)
pdf=pd.DataFrame(prs); jbest=pdf.js_state_dep_bits.min(); cand=pdf[pdf.js_state_dep_bits<=jbest+0.02]; sel=cand.sort_values(['params','js_state_dep_bits']).iloc[0]; Dsel=int(sel.D); rsel=int(sel.r)
# movement selected model multistep starts: start held-out, valid 8 future states/actions
pos=[]
for t in range(4,N-10):
    if pc[t] is None or bucket(pc[t])<80: continue
    ok=True
    for h in range(9):
        if pc[t+h] is None: ok=False; break
        if h<8 and int(ids[t+h]) not in supported: ok=False; break
    if ok: pos.append(t)
if len(pos)>5000: pos=list(rng.choice(pos,5000,False))
basis,model,alpha=fitted[Dsel]; roll=[]
for h in range(1,9):
    pp=[]; yy=[]
    for t in pos:
        z=Z[ci[pc[t]],:Dsel].copy()
        for j in range(h):
            a=int(ids[t+j]); A,b=model[a]; cc=z@A.T+b; z=z+cc[:rsel]@basis[:rsel]
        pp.append(z); yy.append(Z[ci[pc[t+h]],:Dsel])
    pp=np.vstack(pp); yy=np.vstack(yy); qt=Q[[ci[pc[t+h]] for t in pos]]; qp=decode(pp,Dsel)
    roll.append(dict(D=Dsel,r=rsel,horizon=h,n=len(pos),mse=wmse(yy,pp,np.ones(len(pp))),r2=wr2(yy,pp,np.ones(len(pp))),js_bits=float(js(qt,qp).mean()),top1_teacher_match=float((qt.argmax(1)==qp.argmax(1)).mean())))
rolldf=pd.DataFrame(roll); rolldf.to_csv(OUT/'factorized_control_multistep_lowD.csv',index=False)
summary={'corpus_chars':len(corpus),'tokens':N,'contexts':len(ctx),'unique_transitions':len(tr),'supported_actions':len(supported),'state_pca_top3':float(ec[2]),'state_pca_top10':float(ec[9]),'movement':movdf.to_dict('records'),'pareto':pdf.to_dict('records'),'selected_D':Dsel,'selected_r':rsel,'selected_row':sel.to_dict(),'rollout':rolldf.to_dict('records')}
with open(OUT/'factorized_summary_lowD.json','w') as f: json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))
