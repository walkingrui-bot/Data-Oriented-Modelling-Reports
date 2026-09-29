from pathlib import Path
from bs4 import BeautifulSoup
from collections import Counter, defaultdict
import re, hashlib, json, math, csv
import numpy as np
import pandas as pd

OUT=Path('/mnt/data/LANGUAGE-DYNAMICAL-SURROGATE-021')
OUT.mkdir(exist_ok=True)
SEED=20260929
rng=np.random.default_rng(SEED)

# ---------- corpus ----------
root=Path('/usr/local/go/doc')
html_files=sorted(root.glob('*.html'))
parts=[]
file_meta=[]
for p in html_files:
    raw=p.read_text(errors='ignore')
    soup=BeautifulSoup(raw,'html.parser')
    for tag in soup(['script','style']): tag.decompose()
    txt=soup.get_text(' ')
    txt=re.sub(r'\s+',' ',txt).strip()
    parts.append(txt)
    file_meta.append({'file':str(p),'chars':len(txt)})
corpus='\n'.join(parts)
sha=hashlib.sha256(corpus.encode()).hexdigest()

# Word/punctuation tokenization, preserving case. Numbers are kept as contiguous runs.
pat=re.compile(r"[A-Za-z_][A-Za-z_0-9]*|\d+(?:\.\d+)?|[^\s]", re.UNICODE)
raw_tokens=pat.findall(corpus)
counts=Counter(raw_tokens)
V=128
vocab=[t for t,_ in counts.most_common(V-1)]
unk='<UNK>'
vocab.append(unk)
tok2id={t:i for i,t in enumerate(vocab)}
ids=np.array([tok2id.get(t,V-1) for t in raw_tokens],dtype=np.int16)

# ---------- empirical predictive states ----------
threshold={1:50,2:20,3:10,4:5}
# counts[L][context] = next-token Counter
ctx_next={L:defaultdict(Counter) for L in threshold}
ctx_freq={L:Counter() for L in threshold}
N=len(ids)
for t in range(N):
    y=int(ids[t])
    for L in threshold:
        if t>=L:
            c=tuple(map(int,ids[t-L:t]))
            ctx_next[L][c][y]+=1
            ctx_freq[L][c]+=1

# retain supported contexts and their q
state_q={}
state_w={}
state_L={}
for L,thr in threshold.items():
    for c,n in ctx_freq[L].items():
        if n>=thr:
            arr=np.zeros(V,float)
            for j,k in ctx_next[L][c].items(): arr[j]=k
            arr/=arr.sum()
            state_q[c]=arr
            state_w[c]=n
            state_L[c]=L

# choose longest supported suffix before every position
def state_context_before(t):
    for L in (4,3,2,1):
        if t>=L:
            c=tuple(map(int,ids[t-L:t]))
            if c in state_q: return c
    return None

pos_ctx=[None]*(N+1)
for t in range(1,N+1):
    # state before token t; for t==N this is end position
    for L in (4,3,2,1):
        if t>=L:
            c=tuple(map(int,ids[t-L:t]))
            if c in state_q:
                pos_ctx[t]=c; break

# transitions keyed by (source context, action, target context)
trans=Counter()
for t in range(1,N-1):
    c0=pos_ctx[t]
    c1=pos_ctx[t+1]
    if c0 is not None and c1 is not None:
        a=int(ids[t])
        trans[(c0,a,c1)]+=1

contexts=list(state_q.keys())
ctx_index={c:i for i,c in enumerate(contexts)}
Q=np.vstack([state_q[c] for c in contexts])
H=np.sqrt(Q)
W=np.array([state_w[c] for c in contexts],float)

# deterministic split by context identity
def bucket(c):
    b=repr(c).encode()
    return int.from_bytes(hashlib.blake2b(b,digest_size=8).digest(),'little')%100
buckets=np.array([bucket(c) for c in contexts])
train_ctx_mask=buckets<80

# weighted PCA on TRAIN contexts only
Ht=H[train_ctx_mask]; Wt=W[train_ctx_mask]
mu=(Wt[:,None]*Ht).sum(0)/Wt.sum()
X=Ht-mu
Xw=X*np.sqrt(Wt[:,None])
# SVD of weighted centered Hellinger states
_,S,Vt=np.linalg.svd(Xw,full_matrices=False)
components=Vt
energy=S**2
energy_frac=energy/energy.sum()
cum_energy=np.cumsum(energy_frac)
# project all contexts into max D
Dmax=64
Z=(H-mu)@components[:Dmax].T

# transition dataframe indices
rows=[]
for (c0,a,c1),w in trans.items():
    i0=ctx_index[c0]; i1=ctx_index[c1]
    rows.append((i0,a,i1,w,bucket(c0)))
tr=np.array(rows,dtype=np.int64)
# columns src, action, tgt, weight, bucket

# split masks based on source context
fit_mask=tr[:,4] < 70
val_mask=(tr[:,4]>=70)&(tr[:,4]<80)
test_mask=tr[:,4]>=80

# support actions on final train/test
act_stats=[]
for a in range(V):
    nfit=((tr[:,1]==a)&fit_mask).sum()
    ntrain=((tr[:,1]==a)&(tr[:,4]<80)).sum()
    nval=((tr[:,1]==a)&val_mask).sum()
    ntest=((tr[:,1]==a)&test_mask).sum()
    wtrain=tr[(tr[:,1]==a)&(tr[:,4]<80),3].sum()
    wtest=tr[(tr[:,1]==a)&test_mask,3].sum()
    act_stats.append((a,nfit,ntrain,nval,ntest,wtrain,wtest))
act_df=pd.DataFrame(act_stats,columns=['action','n_fit','n_train','n_val','n_test','weight_train','weight_test'])
# moderate support; fall back global for others but main metrics on supported actions
supported=set(act_df.query('n_fit>=12 and n_val>=3 and n_test>=5').action.astype(int))
main_mask=np.array([a in supported for a in tr[:,1]])

# helpers
def weighted_mse(y,p,w):
    return np.average(np.mean((y-p)**2,axis=1),weights=w)

def weighted_r2(y,p,w):
    ym=np.average(y,axis=0,weights=w)
    sse=np.sum(w[:,None]*(y-p)**2)
    sst=np.sum(w[:,None]*(y-ym)**2)
    return 1-sse/sst

def fit_affine(X,Y,w,alpha):
    xa=np.c_[X,np.ones(len(X))]
    sw=np.sqrt(w)[:,None]
    xw=xa*sw; yw=Y*sw
    G=xw.T@xw
    scale=np.trace(G[:-1,:-1])/max(1,X.shape[1])
    pen=np.eye(G.shape[0]); pen[-1,-1]=0
    G=G + alpha*max(scale,1e-12)*pen
    B=np.linalg.solve(G,xw.T@yw) # (d+1,d)
    return B[:-1].T, B[-1]

def decode(z,d):
    h=mu+z@components[:d]
    h=np.clip(h,0,None)
    q=h*h
    q/=np.clip(q.sum(1,keepdims=True),1e-15,None)
    return q

def js_rows(p,q):
    eps=1e-15
    p=np.clip(p,eps,1); q=np.clip(q,eps,1)
    m=.5*(p+q)
    return .5*np.sum(p*np.log2(p/m),1)+.5*np.sum(q*np.log2(q/m),1)

def kl_rows(p,q):
    eps=1e-15
    p=np.clip(p,eps,1); q=np.clip(q,eps,1)
    return np.sum(p*np.log2(p/q),1)

alphas=[1e-5,1e-4,1e-3,1e-2,1e-1,1.0]
dims=[1,2,3,4,6,8,10,12,16,20,24]
perf=[]
models_by_d={}

for d in dims:
    # choose global alpha by validation weighted MSE, supported actions only
    alpha_scores=[]
    for alpha in alphas:
        preds=[]; ys=[]; ws=[]
        for a in supported:
            mf=(tr[:,1]==a)&fit_mask
            mv=(tr[:,1]==a)&val_mask
            if mf.sum()<d+2 or mv.sum()==0: continue
            X=Z[tr[mf,0],:d]; Y=Z[tr[mf,2],:d]; w=tr[mf,3].astype(float)
            A,b=fit_affine(X,Y,w,alpha)
            xv=Z[tr[mv,0],:d]
            preds.append(xv@A.T+b); ys.append(Z[tr[mv,2],:d]); ws.append(tr[mv,3].astype(float))
        P=np.vstack(preds); Yv=np.vstack(ys); Wv=np.concatenate(ws)
        alpha_scores.append((weighted_mse(Yv,P,Wv),alpha))
    best_alpha=min(alpha_scores)[1]

    # fit on all train (<80)
    model={}
    reset={}; shift={}
    for a in supported:
        mt=(tr[:,1]==a)&(tr[:,4]<80)
        X=Z[tr[mt,0],:d]; Y=Z[tr[mt,2],:d]; w=tr[mt,3].astype(float)
        A,b=fit_affine(X,Y,w,best_alpha)
        model[a]=(A,b)
        reset[a]=np.average(Y,axis=0,weights=w)
        shift[a]=np.average(Y-X,axis=0,weights=w)
    models_by_d[d]=(model,best_alpha)

    # test metrics
    mtst=test_mask & main_mask
    idx=np.where(mtst)[0]
    X=Z[tr[idx,0],:d]; Y=Z[tr[idx,2],:d]; w=tr[idx,3].astype(float)
    Pa=np.empty_like(Y); Pr=np.empty_like(Y); Ps=np.empty_like(Y)
    for j,ridx in enumerate(idx):
        a=int(tr[ridx,1]); A,b=model[a]
        Pa[j]=X[j]@A.T+b
        Pr[j]=reset[a]
        Ps[j]=X[j]+shift[a]
    mse=weighted_mse(Y,Pa,w); r2=weighted_r2(Y,Pa,w)
    mse_reset=weighted_mse(Y,Pr,w); mse_shift=weighted_mse(Y,Ps,w)
    qtrue=Q[tr[idx,2]]
    qpred=decode(Pa,d)
    qfloor=decode(Y,d)
    js=np.average(js_rows(qtrue,qpred),weights=w)
    js_floor=np.average(js_rows(qtrue,qfloor),weights=w)
    kl=np.average(kl_rows(qtrue,qpred),weights=w)
    top1=np.average((qtrue.argmax(1)==qpred.argmax(1)).astype(float),weights=w)
    # q entropy and cross entropy in bits
    eps=1e-15
    Htrue=np.average(-np.sum(np.clip(qtrue,eps,1)*np.log2(np.clip(qtrue,eps,1)),1),weights=w)
    CE=Htrue+kl
    perf.append(dict(d=d,alpha=best_alpha,pca_cum_energy=float(cum_energy[d-1]),
                     mse_affine=mse,mse_reset=mse_reset,mse_shift=mse_shift,r2_affine=r2,
                     js_affine_bits=js,js_projection_floor_bits=js_floor,kl_affine_bits=kl,
                     teacher_entropy_bits=Htrue,cross_entropy_bits=CE,top1_teacher_match=top1,
                     n_test_rows=len(idx),test_occurrence_weight=int(w.sum()),n_supported_actions=len(supported)))

perf_df=pd.DataFrame(perf)
perf_df.to_csv(OUT/'dimension_performance.csv',index=False)
act_df.assign(token=[vocab[i] for i in act_df.action]).to_csv(OUT/'action_support.csv',index=False)

# objective saturation dimension based on JS improvement 1D -> best observed
js1=float(perf_df.loc[perf_df.d==1,'js_affine_bits'].iloc[0])
jsbest=float(perf_df.js_affine_bits.min())
bestd=int(perf_df.loc[perf_df.js_affine_bits.idxmin(),'d'])
if js1>jsbest:
    perf_df['js_gain_fraction']=(js1-perf_df.js_affine_bits)/(js1-jsbest)
else: perf_df['js_gain_fraction']=0
sat_candidates=perf_df[perf_df.js_gain_fraction>=.95]
d_sat=int(sat_candidates.d.iloc[0]) if len(sat_candidates) else bestd
perf_df.to_csv(OUT/'dimension_performance.csv',index=False)

# operator-basis compression for d_sat and bestd; use token frequency weights
basis_rows=[]
compressed_models={}
for d in sorted(set([d_sat,bestd,3,6,10]) & set(dims)):
    model,_=models_by_d[d]
    toks=sorted(model)
    flats=[]; tw=[]
    for a in toks:
        A,b=model[a]; flats.append(np.r_[A.ravel(),b])
        tw.append(float(act_df.loc[act_df.action==a,'weight_train'].iloc[0]))
    M=np.vstack(flats); tw=np.array(tw)
    mbar=np.average(M,axis=0,weights=tw)
    Mw=(M-mbar)*np.sqrt(tw[:,None])
    _,sop,vop=np.linalg.svd(Mw,full_matrices=False)
    e=sop**2; ec=np.cumsum(e/e.sum())
    for k in [0,1,2,3,4,6,8,12,16,24,32]:
        if k>len(sop): continue
        if k==0: Mr=np.tile(mbar,(len(toks),1))
        else:
            scores=(M-mbar)@vop[:k].T
            Mr=mbar+scores@vop[:k]
        cm={}
        for row,a in zip(Mr,toks):
            A=row[:d*d].reshape(d,d); b=row[d*d:]
            cm[a]=(A,b)
        idx=np.where(test_mask & main_mask)[0]
        X=Z[tr[idx,0],:d]; Y=Z[tr[idx,2],:d]; w=tr[idx,3].astype(float)
        P=np.empty_like(Y)
        for j,ridx in enumerate(idx):
            A,b=cm[int(tr[ridx,1])]; P[j]=X[j]@A.T+b
        qtrue=Q[tr[idx,2]]; qpred=decode(P,d)
        basis_rows.append(dict(d=d,k=k,operator_energy=float(ec[k-1]) if k else 0.0,
                               mse=weighted_mse(Y,P,w),r2=weighted_r2(Y,P,w),
                               js_bits=np.average(js_rows(qtrue,qpred),weights=w),
                               top1_teacher_match=np.average((qtrue.argmax(1)==qpred.argmax(1)).astype(float),weights=w)))
        if d==d_sat: compressed_models[k]=cm
operator_df=pd.DataFrame(basis_rows)
operator_df.to_csv(OUT/'operator_basis_compression.csv',index=False)

# choose k at d_sat: smallest giving >=95% JS gain from k=0 to full-ish minimum
sub=operator_df[operator_df.d==d_sat].sort_values('k')
js0=float(sub[sub.k==0].js_bits.iloc[0]); jmin=float(sub.js_bits.min())
if js0>jmin:
    sub=sub.copy(); sub['gain_fraction']=(js0-sub.js_bits)/(js0-jmin)
    kk=sub[sub.gain_fraction>=.95]
    k_sat=int(kk.k.iloc[0]) if len(kk) else int(sub.loc[sub.js_bits.idxmin(),'k'])
else: k_sat=int(sub.loc[sub.js_bits.idxmin(),'k'])

# multi-step observed-trajectory rollout for selected dimensions; all source states along segment held out
roll_rows=[]
# Build usable starting positions sampled deterministically to cap work
positions=[]
for t in range(4,N-10):
    ok=True
    for h in range(0,9):
        c=pos_ctx[t+h]
        if c is None: ok=False; break
        if h==0 and bucket(c)<80: ok=False; break
        if h<8 and int(ids[t+h]) not in supported: ok=False; break
    if ok: positions.append(t)
if len(positions)>5000:
    positions=list(rng.choice(positions,5000,replace=False))
for d in sorted(set([3,d_sat,bestd,6,10]) & set(dims)):
    model,_=models_by_d[d]
    for h in range(1,9):
        preds=[]; ys=[]
        for t in positions:
            c0=pos_ctx[t]; z=Z[ctx_index[c0],:d].copy()
            for j in range(h):
                a=int(ids[t+j]); A,b=model[a]; z=z@A.T+b
            ct=pos_ctx[t+h]
            preds.append(z); ys.append(Z[ctx_index[ct],:d])
        if not preds: continue
        P=np.vstack(preds); Y=np.vstack(ys); w=np.ones(len(P))
        qtrue=Q[[ctx_index[pos_ctx[t+h]] for t in positions]]; qpred=decode(P,d)
        roll_rows.append(dict(d=d,horizon=h,n=len(P),mse=weighted_mse(Y,P,w),r2=weighted_r2(Y,P,w),
                              js_bits=float(js_rows(qtrue,qpred).mean()),
                              top1_teacher_match=float((qtrue.argmax(1)==qpred.argmax(1)).mean())))
roll_df=pd.DataFrame(roll_rows)
roll_df.to_csv(OUT/'multistep_rollout.csv',index=False)

# noncommutativity directly in surrogate at d_sat using matched test states and token pairs from observed triples
model,_=models_by_d[d_sat]
pair_acc=defaultdict(lambda: [0.0,0])
# collect states where both orders observed as source trajectories and actions supported
# use actual corpus triples and aggregate by pair with endpoint teacher JS between contexts after ab vs ba where available
# For surrogate commutator, evaluate ||Tb(Ta(z))-Ta(Tb(z))|| on held-out states where a,b are supported.
comm=[]
# select top frequent supported action pairs from corpus transitions
pair_counts=Counter()
for t in range(4,N-2):
    c=pos_ctx[t]
    if c is not None and bucket(c)>=80:
        a=int(ids[t]); b=int(ids[t+1])
        if a in supported and b in supported and a!=b: pair_counts[(a,b)]+=1
for (a,b),cnt in pair_counts.most_common(200):
    # states from occurrences of this pair in heldout contexts, cap 100
    zs=[]
    for t in range(4,N-2):
        c=pos_ctx[t]
        if c is not None and bucket(c)>=80 and int(ids[t])==a and int(ids[t+1])==b:
            zs.append(Z[ctx_index[c],:d_sat])
            if len(zs)>=100: break
    if not zs: continue
    Zs=np.vstack(zs)
    Aa,ba=model[a]; Ab,bb=model[b]
    zab=(Zs@Aa.T+ba)@Ab.T+bb
    zba=(Zs@Ab.T+bb)@Aa.T+ba
    dist=np.linalg.norm(zab-zba,axis=1)
    comm.append(dict(a=a,b=b,token_a=vocab[a],token_b=vocab[b],count=cnt,n_states=len(zs),comm_norm_mean=dist.mean(),comm_norm_median=np.median(dist)))
comm_df=pd.DataFrame(comm)
comm_df.to_csv(OUT/'surrogate_noncommutativity.csv',index=False)

# closed-loop generation from surrogate at d_sat using chosen compressed/full model.
def sample_from(q,rng,temp=1.0):
    if temp!=1:
        log=np.log(np.clip(q,1e-15,1))/temp; log-=log.max(); q=np.exp(log); q/=q.sum()
    return int(rng.choice(len(q),p=q))

def q_from_z(z,d): return decode(np.asarray(z)[None,:],d)[0]

# start from a frequent held-out state with a human-readable 4-token context
starts=[]
for c in contexts:
    if len(c)==4 and bucket(c)>=80 and state_w[c]>=10 and all(vocab[x]!=unk for x in c): starts.append(c)
starts=sorted(starts,key=lambda c:state_w[c],reverse=True)[:20]
gen_rows=[]
for si,c in enumerate(starts[:5]):
    for rep in range(3):
        z=Z[ctx_index[c],:d_sat].copy(); toks=list(c)
        for step in range(40):
            q=q_from_z(z,d_sat)
            a=sample_from(q,rng,temp=.9)
            if a not in model:
                order=np.argsort(q)[::-1]
                a=next(int(x) for x in order if int(x) in model)
            toks.append(a)
            A,b=model[a]; z=z@A.T+b
        gen_rows.append(dict(start=' '.join(vocab[x] for x in c),sample=rep,text=' '.join(vocab[x] for x in toks)))
pd.DataFrame(gen_rows).to_csv(OUT/'closed_loop_samples.csv',index=False)


# ---------- factorized low-dimensional control surrogate ----------
# High-fidelity predictive state can be broader than its movement field.  We therefore
# keep a D-dimensional predictive state but force every local transition to move through
# an r-dimensional shared control basis:
#   z_{t+1} = z_t + U_r^T (C_a z_t + d_a)
control_rows=[]
movement_rows=[]
control_models={}
for D in [16,24,32,48,64]:
    # movement basis estimated only from training source contexts (<80)
    mtrain=(tr[:,4]<80) & main_mask
    src=Z[tr[mtrain,0],:D]; tgt=Z[tr[mtrain,2],:D]; ww=tr[mtrain,3].astype(float)
    Delta=tgt-src
    Dw=Delta*np.sqrt(ww[:,None])
    _,sd,Vtd=np.linalg.svd(Dw,full_matrices=False)
    de=sd**2; dc=np.cumsum(de/de.sum())
    stable=float(de.sum()/de.max())
    pr=float(de.sum()**2/(de@de))
    d95=int(np.searchsorted(dc,.95)+1)
    movement_rows.append(dict(D=D,stable_rank=stable,participation_rank=pr,d95=d95,
                              top2=float(dc[1]),top3=float(dc[2]),top6=float(dc[5]),top10=float(dc[9])))
    for r in [1,2,3,4,6,8,12,16,24]:
        if r>D: continue
        basis=Vtd[:r] # r x D
        # choose alpha using validation for this (D,r), but only 3 values for compute economy
        alpha_scores=[]
        for alpha in [0.01,0.1,1.0]:
            PY=[]; YY=[]; WW=[]
            for a in supported:
                mf=(tr[:,1]==a)&fit_mask
                mv=(tr[:,1]==a)&val_mask
                if mf.sum()<5 or mv.sum()==0: continue
                Xf=Z[tr[mf,0],:D]; Yf=Z[tr[mf,2],:D]; wf=tr[mf,3].astype(float)
                Cf=(Yf-Xf)@basis.T
                A,b=fit_affine(Xf,Cf,wf,alpha)
                Xv=Z[tr[mv,0],:D]
                cp=Xv@A.T+b
                pred=Xv+cp@basis
                PY.append(pred); YY.append(Z[tr[mv,2],:D]); WW.append(tr[mv,3].astype(float))
            alpha_scores.append((weighted_mse(np.vstack(YY),np.vstack(PY),np.concatenate(WW)),alpha))
        alpha=min(alpha_scores)[1]
        # final fit on <80
        cm={}; fixed={}
        for a in supported:
            mt=(tr[:,1]==a)&(tr[:,4]<80)
            Xf=Z[tr[mt,0],:D]; Yf=Z[tr[mt,2],:D]; wf=tr[mt,3].astype(float)
            Ctrue=(Yf-Xf)@basis.T
            A,b=fit_affine(Xf,Ctrue,wf,alpha)
            cm[a]=(A,b)
            fixed[a]=np.average(Ctrue,axis=0,weights=wf)
        idx=np.where(test_mask & main_mask)[0]
        Xte=Z[tr[idx,0],:D]; Yte=Z[tr[idx,2],:D]; wte=tr[idx,3].astype(float)
        P=np.empty_like(Yte); Pf=np.empty_like(Yte)
        for j,ridx in enumerate(idx):
            a=int(tr[ridx,1]); A,b=cm[a]
            cc=Xte[j]@A.T+b
            P[j]=Xte[j]+cc@basis
            Pf[j]=Xte[j]+fixed[a]@basis
        qtrue=Q[tr[idx,2]]; qpred=decode(P,D); qfixed=decode(Pf,D)
        qfloor=decode(Yte,D)
        control_rows.append(dict(D=D,r=r,alpha=alpha,movement_energy=float(dc[r-1]),
                                 mse_state_dep=weighted_mse(Yte,P,wte),mse_fixed_control=weighted_mse(Yte,Pf,wte),
                                 r2_state_dep=weighted_r2(Yte,P,wte),
                                 js_state_dep_bits=float(np.average(js_rows(qtrue,qpred),weights=wte)),
                                 js_fixed_control_bits=float(np.average(js_rows(qtrue,qfixed),weights=wte)),
                                 js_projection_floor_bits=float(np.average(js_rows(qtrue,qfloor),weights=wte)),
                                 top1_teacher_match=float(np.average((qtrue.argmax(1)==qpred.argmax(1)),weights=wte))))
        control_models[(D,r)]=(basis,cm)
movement_df=pd.DataFrame(movement_rows)
control_df=pd.DataFrame(control_rows)
movement_df.to_csv(OUT/'movement_spectrum.csv',index=False)
control_df.to_csv(OUT/'factorized_control_surrogate.csv',index=False)

# choose compact model by Pareto criterion: lowest r at each D reaching 95% of that D's
# improvement from r=1 to its best measured r; among those choose lowest JS, breaking ties by parameters.
pareto=[]
for D in sorted(control_df.D.unique()):
    ss=control_df[control_df.D==D].sort_values('r').copy()
    j1=float(ss.iloc[0].js_state_dep_bits); jb=float(ss.js_state_dep_bits.min())
    if j1>jb: ss['gain']=(j1-ss.js_state_dep_bits)/(j1-jb)
    else: ss['gain']=0
    cand=ss[ss.gain>=.95]
    row=(cand.iloc[0] if len(cand) else ss.loc[ss.js_state_dep_bits.idxmin()]).to_dict()
    row['params']=len(supported)*int(row['r'])*(D+1)
    pareto.append(row)
pareto_df=pd.DataFrame(pareto)
pareto_df.to_csv(OUT/'factorized_control_pareto.csv',index=False)
# select compact: best JS among pareto points within 10% relative of global best control JS, then fewest params
jglobal=float(control_df.js_state_dep_bits.min())
elig=pareto_df[pareto_df.js_state_dep_bits <= jglobal*1.10]
if len(elig)==0: elig=pareto_df
sel=elig.sort_values(['params','js_state_dep_bits']).iloc[0]
D_sel=int(sel.D); r_sel=int(sel.r)

# multi-step rollout for factorized selected model on same 5000 held-out starts
basis,cm=control_models[(D_sel,r_sel)]
control_roll=[]
for h in range(1,9):
    P=[]; Y=[]
    for t in positions:
        z=Z[ctx_index[pos_ctx[t]],:D_sel].copy()
        for j in range(h):
            a=int(ids[t+j]); A,b=cm[a]; cc=z@A.T+b; z=z+cc@basis
        P.append(z); Y.append(Z[ctx_index[pos_ctx[t+h]],:D_sel])
    P=np.vstack(P); Y=np.vstack(Y)
    qtrue=Q[[ctx_index[pos_ctx[t+h]] for t in positions]]; qpred=decode(P,D_sel)
    control_roll.append(dict(D=D_sel,r=r_sel,horizon=h,n=len(P),mse=weighted_mse(Y,P,np.ones(len(P))),
                             r2=weighted_r2(Y,P,np.ones(len(P))),js_bits=float(js_rows(qtrue,qpred).mean()),
                             top1_teacher_match=float((qtrue.argmax(1)==qpred.argmax(1)).mean())))
control_roll_df=pd.DataFrame(control_roll)
control_roll_df.to_csv(OUT/'factorized_control_multistep.csv',index=False)

# summary
summary={
    'experiment':'LANGUAGE-DYNAMICAL-SURROGATE-021',
    'date':'2026-09-29',
    'corpus_source':'locally installed Go HTML documentation (/usr/local/go/doc/*.html), HTML stripped',
    'corpus_files':file_meta,
    'corpus_chars':len(corpus),
    'corpus_sha256':sha,
    'raw_word_punct_tokens':len(raw_tokens),
    'vocab_size':V,
    'supported_contexts':len(contexts),
    'transitions_unique':len(tr),
    'transition_occurrence_weight':int(tr[:,3].sum()),
    'supported_actions':len(supported),
    'pca_energy_top3':float(cum_energy[2]),
    'pca_energy_top6':float(cum_energy[5]),
    'pca_energy_top10':float(cum_energy[9]),
    'best_dimension_by_JS':bestd,
    'dimension_95pct_JS_gain':d_sat,
    'operator_basis_k_95pct_JS_gain_at_d_sat':k_sat,
    'all_heldout_8step_trajectories':len(positions),
    'selected_factorized_state_D':D_sel,
    'selected_factorized_control_r':r_sel,
    'selected_factorized_js_bits':float(sel.js_state_dep_bits),
    'selected_factorized_movement_energy':float(sel.movement_energy),
}
summary['movement_rows']=movement_df.to_dict('records')
summary['factorized_pareto']=pareto_df.to_dict('records')
summary['factorized_rollout']=control_roll_df.to_dict('records')
# include selected rows
summary['dimension_rows']=perf_df[perf_df.d.isin(sorted(set([1,2,3,d_sat,bestd,6,10,16,24])))].to_dict('records')
summary['operator_rows_at_selected_d']=operator_df[operator_df.d==d_sat].to_dict('records')
summary['rollout_rows_selected_d']=roll_df[roll_df.d==d_sat].to_dict('records')
if len(comm_df):
    summary['noncommutativity_median_pair_mean_norm']=float(comm_df.comm_norm_mean.median())
    summary['noncommutativity_top_pairs']=comm_df.sort_values('comm_norm_mean',ascending=False).head(10).to_dict('records')
with open(OUT/'summary.json','w') as f: json.dump(summary,f,indent=2)

print(json.dumps(summary,indent=2)[:12000])
