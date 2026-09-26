#!/usr/bin/env python3
from pathlib import Path
from collections import Counter, defaultdict
import hashlib, importlib.util, math, re
import numpy as np
import pandas as pd

OUT=Path(__file__).resolve().parent
CORPUS=OUT/'LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014_language_corpus.txt'
V=64
ALPHA=0.1

spec=importlib.util.spec_from_file_location('exp14',str(OUT/'LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014.py'))
exp14=importlib.util.module_from_spec(spec); spec.loader.exec_module(exp14)
text=CORPUS.read_text(encoding='utf-8')
arr, chars=exp14.encode_language(text)
arr=np.asarray(arr,dtype=np.int64)
def sym(a): return chars[int(a)] if int(a)<len(chars) else '<UNK>'

def bucket(c,mod=5):
    s='|'.join(map(str,c)).encode('utf-8')
    return int.from_bytes(hashlib.sha256(s).digest()[:4],'little')%mod

def build_counts(a,maxL=5):
    ccb={}; ncb={}
    for L in range(1,maxL+1):
        cc=Counter(); nc=defaultdict(Counter)
        for i in range(len(a)-L):
            c=tuple(map(int,a[i:i+L])); y=int(a[i+L])
            cc[c]+=1; nc[c][y]+=1
        ccb[L]=cc; ncb[L]=nc
    return ccb,ncb

def q_from(counter,V=64,alpha=.1):
    v=np.full(V,alpha,dtype=float)
    for y,n in counter.items(): v[int(y)]+=n
    return v/v.sum()

def apply_op(C,z):
    return np.r_[z,1.0]@C

MIN={1:50,2:20,3:10,4:5,5:5}

def pooled_operator_experiment(a,d=10,lam=2.0,min_train=100,min_test=20):
    ccb,ncb=build_counts(a,5)
    def q(c): return q_from(ncb[len(c)][c],V,ALPHA)
    trans=[]; states=set()
    for L in range(1,5):
        for child,n in ccb[L+1].items():
            parent=child[:-1]
            if n>=MIN[L+1] and ccb[L][parent]>=MIN[L]:
                trans.append((parent,int(child[-1]),child,n,L))
                states.add(parent); states.add(child)
    sk=list(states)
    X=np.vstack([q(c) for c in sk])
    sw=np.array([ccb[len(c)][c] for c in sk],float); sw/=sw.sum()
    mu=(sw[:,None]*X).sum(0); Xc=X-mu
    cov=(Xc*sw[:,None]).T@Xc
    ev,E=np.linalg.eigh(cov); order=np.argsort(ev)[::-1]; ev=ev[order]; E=E[:,order]
    B=E[:,:d]
    z={c:(x-mu)@B for c,x in zip(sk,X)}
    train=defaultdict(list); test=defaultdict(list)
    for p,tok,ch,n,L in trans:
        e=(z[p],z[ch],n,p,ch,L)
        (test if bucket(p)==0 else train)[tok].append(e)
    rows=[]; ops={}; stats={}
    for tok,tr in train.items():
        te=test.get(tok,[])
        if len(tr)<min_train or len(te)<min_test: continue
        Xtr=np.vstack([e[0] for e in tr]); Ytr=np.vstack([e[1] for e in tr]); W=np.array([e[2] for e in tr],float)
        Xte=np.vstack([e[0] for e in te]); Yte=np.vstack([e[1] for e in te]); Wt=np.array([e[2] for e in te],float)
        shift=np.average(Ytr-Xtr,axis=0,weights=W)
        reset=np.average(Ytr,axis=0,weights=W)
        Phi=np.hstack([Xtr,np.ones((len(Xtr),1))]); Pte=np.hstack([Xte,np.ones((len(Xte),1))])
        wr=np.sqrt(W/W.mean()); reg=np.eye(d+1)*lam; reg[-1,-1]=lam*.1
        Pw=Phi*wr[:,None]; Yw=Ytr*wr[:,None]
        C=np.linalg.solve(Pw.T@Pw+reg,Pw.T@Yw)
        def mse(P): return np.average(np.sum((P-Yte)**2,axis=1),weights=Wt)
        rows.append(dict(token=sym(tok),id=tok,n_train=len(tr),n_test=len(te),train_weight=W.sum(),test_weight=Wt.sum(),
                         mse_identity=mse(Xte),mse_fixed_shift=mse(Xte+shift),
                         mse_token_reset=mse(np.repeat(reset[None,:],len(te),0)),mse_state_operator=mse(Pte@C)))
        ops[tok]=C; stats[tok]=(shift,reset)
    df=pd.DataFrame(rows)
    # Held-out two-step chains: both parent contexts are in the held-out hash bucket.
    chains=[]
    for L in [1,2,3]:
        for full,n in ccb[L+2].items():
            if n<MIN[L+2]: continue
            c=full[:L]; ca=full[:L+1]; ta=int(full[L]); tb=int(full[L+1])
            if bucket(c)!=0 or bucket(ca)!=0: continue
            if c not in z or ca not in z or full not in z or ta not in ops or tb not in ops: continue
            z0,z1,z2=z[c],z[ca],z[full]
            da,ra=stats[ta]; db,rb=stats[tb]
            chains.append(dict(weight=n,L=L,a=sym(ta),b=sym(tb),
                err_sequential=float(np.sum((apply_op(ops[tb],apply_op(ops[ta],z0))-z2)**2)),
                err_actual_intermediate=float(np.sum((apply_op(ops[tb],z1)-z2)**2)),
                err_fixed_shift=float(np.sum((z0+da+db-z2)**2)),
                err_last_token_reset=float(np.sum((rb-z2)**2)),
                err_reversed=float(np.sum((apply_op(ops[ta],apply_op(ops[tb],z0))-z2)**2))))
    chain_df=pd.DataFrame(chains)
    # Operator-basis SVD across token-specific affine maps.
    ids=list(ops)
    wt=np.array([float(df.loc[df.id==i,'train_weight'].iloc[0]) for i in ids]); wt/=wt.sum()
    M=np.vstack([ops[i].reshape(-1) for i in ids])
    mean=(wt[:,None]*M).sum(0); XM=M-mean
    _,s,vt=np.linalg.svd(XM*np.sqrt(wt)[:,None],full_matrices=False)
    energy=s*s; frac=energy/energy.sum()
    basis_summary=[]
    for K in [0,1,2,3,4,5,6,8,10,12,16,20,24,30,34]:
        if K>len(ids)-1: continue
        Mr=np.repeat(mean[None,:],len(ids),0) if K==0 else mean+(XM@vt[:K].T)@vt[:K]
        es=ws=0.0
        for j,tok in enumerate(ids):
            te=test[tok]
            Xte=np.vstack([e[0] for e in te]); Yte=np.vstack([e[1] for e in te]); Wt=np.array([e[2] for e in te],float)
            P=np.hstack([Xte,np.ones((len(Xte),1))])@Mr[j].reshape(ops[tok].shape)
            es+=(np.sum((P-Yte)**2,axis=1)*Wt).sum(); ws+=Wt.sum()
        basis_summary.append(dict(k=K,mse=es/ws))
    basis_df=pd.DataFrame(basis_summary)
    met=dict(operator_stable_rank=float(energy.sum()/energy.max()),operator_participation_rank=float(energy.sum()**2/(energy@energy)),
             operator_top3=float(frac[:3].sum()),operator_top6=float(frac[:6].sum()),operator_top10=float(frac[:10].sum()),
             operator_d95=int(np.searchsorted(np.cumsum(frac),.95)+1))
    scores=XM@vt.T
    mode_rows=[]
    for j,tok in enumerate(ids):
        r={'token':sym(tok),'id':tok,'weight':wt[j]}
        for k in range(min(10,scores.shape[1])): r[f'mode_{k+1}']=scores[j,k]
        mode_rows.append(r)
    return df,chain_df,basis_df,pd.DataFrame(mode_rows),met,(ccb,ncb,z)

def aggregate_one_step(df):
    w=df.test_weight.to_numpy(float)
    return {c:float(np.average(df[c],weights=w)) for c in ['mse_identity','mse_fixed_shift','mse_token_reset','mse_state_operator']}

def aggregate_chains(df):
    w=df.weight.to_numpy(float)
    return {c:float(np.average(df[c],weights=w)) for c in ['err_sequential','err_actual_intermediate','err_fixed_shift','err_last_token_reset','err_reversed']}

def empirical_P(a):
    C=np.full((V,V),.1,float); np.add.at(C,(a[:-1],a[1:]),1.0)
    P=C/C.sum(1,keepdims=True); pi=np.bincount(a,minlength=V).astype(float); pi/=pi.sum()
    return P,pi

def gen_markov(a,seed=901):
    P,pi=empirical_P(a); rng=np.random.default_rng(seed); cdf=np.cumsum(P,axis=1)
    x=np.empty(len(a),dtype=np.int64); x[0]=rng.choice(V,p=pi)
    for t in range(1,len(x)): x[t]=np.searchsorted(cdf[x[t-1]],rng.random())
    return x

def same_final_order_effect(a,min_full=5):
    # Compare [a,b,z] and [b,a,z], so the last symbol is identical and only earlier order changes.
    L=3; cc=Counter(); nc=defaultdict(Counter)
    for i in range(len(a)-L):
        c=tuple(map(int,a[i:i+L])); y=int(a[i+L]); cc[c]+=1; nc[c][y]+=1
    def q(c): return q_from(nc[c],V,.1)
    seen=set(); rows=[]
    for full,n in cc.items():
        if n<min_full: continue
        x,y,z=full
        if x==y: continue
        rev=(y,x,z)
        if cc.get(rev,0)<min_full: continue
        key=(min(x,y),max(x,y),z)
        if key in seen: continue
        seen.add(key)
        p1,p2=q(full),q(rev); m=.5*(p1+p2)
        js=.5*((p1*np.log((p1+1e-15)/(m+1e-15))).sum()+(p2*np.log((p2+1e-15)/(m+1e-15))).sum())
        rows.append(dict(first=sym(x),second=sym(y),same_final=sym(z),count_forward=n,count_reverse=cc[rev],weight=min(n,cc[rev]),js=float(js)))
    return pd.DataFrame(rows)

# Main character-level operator experiment.
one,chains,basis,modes,opmet,aux=pooled_operator_experiment(arr)
one.to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_one_step.csv',index=False)
chains.to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_composition.csv',index=False)
basis.to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_basis.csv',index=False)
modes.to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_modes.csv',index=False)

# First-order Markov control.
markov=gen_markov(arr)
mark_one,mark_chains,_,_,_,_=pooled_operator_experiment(markov)
order_lang=same_final_order_effect(arr); order_markov=same_final_order_effect(markov)
order_lang.assign(world='language').to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_order_language.csv',index=False)
order_markov.assign(world='markov').to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_order_markov.csv',index=False)

# Word-level secondary replication (technical-English corpus; top-128 predictive vocabulary).
word_tokens=re.findall(r"[A-Za-z]+(?:'[A-Za-z]+)?|\d+(?:\.\d+)?|[^\w\s]",text.lower())
wc=Counter(word_tokens); M=128
vocab=[w for w,_ in wc.most_common(M-1)]; wid={w:i for i,w in enumerate(vocab)}; OTHER=M-1
pcount=Counter(); pn=defaultdict(Counter); bcount=Counter(); bn=defaultdict(Counter)
for i in range(len(word_tokens)-2):
    p=(word_tokens[i],); b=(word_tokens[i],word_tokens[i+1])
    pcount[p]+=1; pn[p][wid.get(word_tokens[i+1],OTHER)]+=1
    bcount[b]+=1; bn[b][wid.get(word_tokens[i+2],OTHER)]+=1
pairs=defaultdict(list)
for b,n in bcount.items():
    if n>=3 and pcount[(b[0],)]>=20: pairs[b[1]].append(((b[0],),b,n))
parents=[p for p,n in pcount.items() if n>=20]; children=[b for b,n in bcount.items() if n>=3 and pcount[(b[0],)]>=20]
def qw(counter): return q_from(counter,M,.1)
SX=[]; SW=[]; keys=[]
for p in parents: SX.append(qw(pn[p])); SW.append(pcount[p]); keys.append(('p',p))
for b in children: SX.append(qw(bn[b])); SW.append(bcount[b]); keys.append(('b',b))
SX=np.vstack(SX); SW=np.asarray(SW,float); SW/=SW.sum(); smu=(SW[:,None]*SX).sum(0); SC=SX-smu
cov=(SC*SW[:,None]).T@SC; ev,E=np.linalg.eigh(cov); E=E[:,np.argsort(ev)[::-1]]; d=6; B=E[:,:d]
z={k:(x-smu)@B for k,x in zip(keys,SX)}
word_train=defaultdict(list); word_test=defaultdict(list)
for tok,lst in pairs.items():
    for p,b,n in lst:
        e=(z[('p',p)],z[('b',b)],n,p,b)
        (word_test if bucket(p)==0 else word_train)[tok].append(e)
word_rows=[]
for tok,tr in word_train.items():
    te=word_test.get(tok,[])
    if len(tr)<20 or len(te)<5: continue
    Xtr=np.vstack([e[0] for e in tr]); Ytr=np.vstack([e[1] for e in tr]); W=np.array([e[2] for e in tr],float)
    Xte=np.vstack([e[0] for e in te]); Yte=np.vstack([e[1] for e in te]); Wt=np.array([e[2] for e in te],float)
    shift=np.average(Ytr-Xtr,axis=0,weights=W); reset=np.average(Ytr,axis=0,weights=W)
    Phi=np.hstack([Xtr,np.ones((len(Xtr),1))]); Pte=np.hstack([Xte,np.ones((len(Xte),1))]); wr=np.sqrt(W/W.mean())
    reg=np.eye(d+1); reg[-1,-1]=.1; Pw=Phi*wr[:,None]; Yw=Ytr*wr[:,None]
    C=np.linalg.solve(Pw.T@Pw+reg,Pw.T@Yw)
    def mse(P): return np.average(np.sum((P-Yte)**2,axis=1),weights=Wt)
    word_rows.append(dict(token=tok,n_train=len(tr),n_test=len(te),train_weight=W.sum(),test_weight=Wt.sum(),
                          mse_identity=mse(Xte),mse_fixed_shift=mse(Xte+shift),mse_token_reset=mse(np.repeat(reset[None,:],len(te),0)),mse_state_operator=mse(Pte@C)))
word_df=pd.DataFrame(word_rows); word_df.to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_word_level.csv',index=False)

# Summary table.
A=aggregate_one_step(one); Mctrl=aggregate_one_step(mark_one); Csum=aggregate_chains(chains)
wordagg=aggregate_one_step(word_df) if len(word_df) else {}
summary={
    'char_tokens_tested':len(one),'heldout_two_step_chains':len(chains),'heldout_chain_weight':float(chains.weight.sum()),
    **{f'language_{k}':v for k,v in A.items()},
    **{f'markov_{k}':v for k,v in Mctrl.items()},
    **{f'composition_{k}':v for k,v in Csum.items()},
    'language_same_final_order_pairs':len(order_lang),'language_same_final_order_js':float(np.average(order_lang.js,weights=order_lang.weight)),
    'markov_same_final_order_pairs':len(order_markov),'markov_same_final_order_js':float(np.average(order_markov.js,weights=order_markov.weight)),
    **opmet,
    'word_tokens_tested':len(word_df),
    **{f'word_{k}':v for k,v in wordagg.items()},
}
pd.DataFrame([summary]).to_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_summary.csv',index=False)
print(pd.DataFrame([summary]).T.to_string(header=False))
