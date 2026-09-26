import re, math, hashlib, json, zipfile
from pathlib import Path
from collections import Counter, defaultdict
import numpy as np
import pandas as pd

BASE=Path('/mnt/data')
CORP=BASE/'LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014_language_corpus.txt'
text=CORP.read_text(errors='ignore').lower()
tokens=re.findall(r"[a-z]+(?:'[a-z]+)?|\d+(?:\.\d+)?|[^\w\s]",text)
N=len(tokens)

# ---------- vocabulary and empirical predictive states ----------
V=128
cnt=Counter(tokens)
vocab=[w for w,_ in cnt.most_common(V-1)]
wid={w:i for i,w in enumerate(vocab)}
OTHER=V-1
ids=np.array([wid.get(w,OTHER) for w in tokens],dtype=np.int16)
label=vocab+['<OTHER>']

MAXL=4
# counts[(L, context_tuple)] -> vector next counts
counts=[None]+[defaultdict(Counter) for _ in range(MAXL)]
ctxfreq=[None]+[Counter() for _ in range(MAXL)]
for t in range(1,N):
    nxt=int(ids[t])
    for L in range(1,MAXL+1):
        if t-L<0: break
        c=tuple(map(int,ids[t-L:t]))
        counts[L][c][nxt]+=1
        ctxfreq[L][c]+=1

mincount={1:8,2:5,3:3,4:2}
alpha=.05
# global backoff
ug=np.bincount(ids,minlength=V).astype(float)+alpha
ug/=ug.sum()

def q_for_pos(t):
    # predictive state before token t using longest supported suffix
    for L in range(MAXL,0,-1):
        if t-L<0: continue
        c=tuple(map(int,ids[t-L:t]))
        n=ctxfreq[L].get(c,0)
        if n>=mincount[L]:
            v=np.full(V,alpha,dtype=float)
            for k,x in counts[L][c].items(): v[k]+=x
            v/=v.sum()
            return v,L,c,n
    return ug.copy(),0,(),N

# Build states for all usable positions. Use sqrt-probability (Hellinger) before PCA.
positions=np.arange(MAXL,N-1)
Q=np.empty((len(positions),V),dtype=np.float32)
usedL=np.empty(len(positions),dtype=np.int8)
contexts=[]
weights=np.empty(len(positions),dtype=np.float32)
for ii,t in enumerate(positions):
    q,L,c,n=q_for_pos(int(t)); Q[ii]=np.sqrt(q); usedL[ii]=L; contexts.append(c); weights[ii]=min(n,50)

# weighted PCA to common predictive-state coordinates
w=weights.astype(float); w/=w.sum(); mu=(Q*w[:,None]).sum(0); X=Q-mu
cov=(X*w[:,None]).T@X
ev,E=np.linalg.eigh(cov); order=np.argsort(ev)[::-1]; E=E[:,order]
d=10; B=E[:,:d]
Z=(Q-mu)@B  # state before token at positions[ii]
pos_to_i={int(t):i for i,t in enumerate(positions)}

def zpos(t):
    i=pos_to_i.get(int(t)); return None if i is None else Z[i]

def split_key(t):
    # context identity split, deterministic. Keeps repeated same suffix together.
    i=pos_to_i.get(int(t))
    if i is None: return 1
    c=contexts[i]
    h=hashlib.blake2b(repr(c).encode(),digest_size=4).digest()
    return int.from_bytes(h,'little')%5

# ---------- affine helpers ----------
def fit_affine(X,Y,W=None,lam=1.0):
    X=np.asarray(X,float); Y=np.asarray(Y,float)
    if W is None: W=np.ones(len(X))
    W=np.asarray(W,float); sw=np.sqrt(W/np.mean(W))
    Phi=np.hstack([X,np.ones((len(X),1))])
    Pw=Phi*sw[:,None]; Yw=Y*sw[:,None]
    reg=np.eye(d+1)*lam; reg[-1,-1]=lam*.1
    return np.linalg.solve(Pw.T@Pw+reg,Pw.T@Yw)  # (d+1,d), y=[x,1]@C

def apply(C,X):
    X=np.asarray(X,float)
    return np.hstack([X,np.ones((len(X),1))])@C

def compose(C2,C1):
    # y=[x,1]@C1 then C2; return homogeneous affine H (d+1,d+1) representation convenience
    H1=np.eye(d+1); H1[:d,:d]=C1[:d,:]; H1[d,:d]=C1[d,:]
    H2=np.eye(d+1); H2[:d,:d]=C2[:d,:]; H2[d,:d]=C2[d,:]
    H=H1@H2  # row homogeneous: [x,1] H1 H2
    return H[:,:d]

def chain_apply(Cs,x):
    y=np.asarray(x,float)[None,:]
    for C in Cs: y=apply(C,y)
    return y[0]

def wmse(P,Y,W):
    return float(np.average(np.sum((np.asarray(P)-np.asarray(Y))**2,axis=1),weights=np.asarray(W,float)))

# ---------- base lexical operators ----------
# transitions before token t -> before token t+1
bytok_train=defaultdict(list); bytok_test=defaultdict(list)
for t in range(MAXL,N-2):
    x=zpos(t); y=zpos(t+1)
    if x is None or y is None: continue
    a=int(ids[t]); rec=(x,y,1.0,t)
    (bytok_test if split_key(t)==0 else bytok_train)[a].append(rec)

ops={}; lexrows=[]
for a,tr in bytok_train.items():
    te=bytok_test.get(a,[])
    if len(tr)<40 or len(te)<10: continue
    Xtr=np.vstack([r[0] for r in tr]); Ytr=np.vstack([r[1] for r in tr]); W=np.ones(len(tr))
    C=fit_affine(Xtr,Ytr,W,lam=2.0); ops[a]=C
    Xte=np.vstack([r[0] for r in te]); Yte=np.vstack([r[1] for r in te]); Wt=np.ones(len(te))
    reset=np.mean(Ytr,0); shift=np.mean(Ytr-Xtr,0)
    lexrows.append(dict(token=label[a],token_id=a,n_train=len(tr),n_test=len(te),
                        mse_identity=wmse(Xte,Yte,Wt),mse_shift=wmse(Xte+shift,Yte,Wt),
                        mse_reset=wmse(np.repeat(reset[None,:],len(te),0),Yte,Wt),
                        mse_operator=wmse(apply(C,Xte),Yte,Wt)))
lexdf=pd.DataFrame(lexrows)
lexdf.to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_lexical.csv',index=False)

# ---------- exact bigram macro-operators vs lexical composition ----------
pair_occ=defaultdict(list)
for t in range(MAXL,N-3):
    a,b=int(ids[t]),int(ids[t+1])
    if a not in ops or b not in ops: continue
    x=zpos(t); y=zpos(t+2)
    if x is None or y is None: continue
    pair_occ[(a,b)].append((x,y,t))

pairrows=[]; residual_flat=[]; residual_w=[]; synthetic_flat=[]
for (a,b),occ in pair_occ.items():
    tr=[r for r in occ if split_key(r[2])!=0]; te=[r for r in occ if split_key(r[2])==0]
    if len(tr)<60 or len(te)<15: continue
    Xtr=np.vstack([r[0] for r in tr]); Ytr=np.vstack([r[1] for r in tr])
    Xte=np.vstack([r[0] for r in te]); Yte=np.vstack([r[1] for r in te])
    D=fit_affine(Xtr,Ytr,lam=2.0)
    C=compose(ops[b],ops[a])
    pred_comp=apply(C,Xte); pred_direct=apply(D,Xte)
    err_comp=wmse(pred_comp,Yte,np.ones(len(te))); err_direct=wmse(pred_direct,Yte,np.ones(len(te)))
    # synthetic composition-only target on same train X, fit direct map, measures finite-sample estimation residual
    Ys=apply(C,Xtr); Ds=fit_affine(Xtr,Ys,lam=2.0)
    normD=np.linalg.norm(D)+1e-12
    resid=np.linalg.norm(D-C)/normD
    sres=np.linalg.norm(Ds-C)/(np.linalg.norm(C)+1e-12)
    pairrows.append(dict(w1=label[a],w2=label[b],n_train=len(tr),n_test=len(te),
                         mse_composed=err_comp,mse_direct=err_direct,
                         direct_gain=(err_comp-err_direct)/(err_comp+1e-12),
                         operator_residual_ratio=resid,synthetic_residual_ratio=sres))
    residual_flat.append((D-C).reshape(-1)); residual_w.append(len(occ)); synthetic_flat.append((Ds-C).reshape(-1))
pairdf=pd.DataFrame(pairrows).sort_values('n_train',ascending=False)
pairdf.to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_phrases.csv',index=False)

# residual spectrum helper
def spectrum(M,W=None):
    M=np.asarray(M,float)
    if len(M)==0: return dict(stable_rank=np.nan,participation_rank=np.nan,top3=np.nan,d95=np.nan,singular=[])
    if W is None: W=np.ones(len(M))
    W=np.asarray(W,float); W/=W.sum(); m=(M*W[:,None]).sum(0); A=(M-m)*np.sqrt(W[:,None])
    s=np.linalg.svd(A,compute_uv=False); e=s*s; tot=e.sum()+1e-30
    stable=float(tot/(s[0]**2+1e-30)); participation=float(tot*tot/(np.sum(e*e)+1e-30)); cum=np.cumsum(e)/tot
    return dict(stable_rank=stable,participation_rank=participation,top3=float(cum[min(2,len(cum)-1)]),d95=int(np.searchsorted(cum,.95)+1),singular=s.tolist())
realres=spectrum(residual_flat,residual_w); synres=spectrum(synthetic_flat,residual_w)

# ---------- relation/construction-level residual corrections ----------
# Fixed 5-token windows beginning at relation markers. Sequential lexical composition predicts post-state.
# Fit class-specific affine correction G_r(predicted_post) -> actual_post. Compare generic G_all and identity.
classes={
    'condition':['if','when','unless','otherwise'],
    'contrast':['but','however','although'],
    'alternative':['or'],
    'conjunction':['and'],
    'negation':['not'],
    'modality':['must','may','can'],
    'relative_complement':['that','which'],
}
tokclass={w:k for k,ws in classes.items() for w in ws}
H=5
relation_occ=defaultdict(list)
all_rel=[]
for t in range(MAXL,N-H-1):
    w0=tokens[t]
    cls=tokclass.get(w0)
    if cls is None: continue
    seq=list(map(int,ids[t:t+H]))
    if any(a not in ops for a in seq): continue
    x=zpos(t); y=zpos(t+H)
    if x is None or y is None: continue
    pred=chain_apply([ops[a] for a in seq],x)
    rec=(pred,y,t,w0,tuple(tokens[t:t+H]))
    relation_occ[cls].append(rec); all_rel.append((cls,)+rec)

# Generic correction trained across all relation occurrences, split by same context split.
all_tr=[r for r in all_rel if split_key(r[3])!=0]  # r=(cls,pred,y,t,...)
all_te=[r for r in all_rel if split_key(r[3])==0]
if len(all_tr)>50:
    GX=np.vstack([r[1] for r in all_tr]); GY=np.vstack([r[2] for r in all_tr]); Ggeneric=fit_affine(GX,GY,lam=3.0)
else: Ggeneric=None

relrows=[]; class_corr_flat=[]; class_w=[]
Iaff=np.zeros((d+1,d)); Iaff[:d,:d]=np.eye(d)
for cls,occ in relation_occ.items():
    tr=[r for r in occ if split_key(r[2])!=0]; te=[r for r in occ if split_key(r[2])==0]
    if len(tr)<40 or len(te)<10: continue
    Xtr=np.vstack([r[0] for r in tr]); Ytr=np.vstack([r[1] for r in tr])
    Xte=np.vstack([r[0] for r in te]); Yte=np.vstack([r[1] for r in te])
    G=fit_affine(Xtr,Ytr,lam=3.0)
    ebase=wmse(Xte,Yte,np.ones(len(te)))
    eclass=wmse(apply(G,Xte),Yte,np.ones(len(te)))
    egeneric=wmse(apply(Ggeneric,Xte),Yte,np.ones(len(te))) if Ggeneric is not None else np.nan
    relrows.append(dict(relation=cls,n_train=len(tr),n_test=len(te),
                        mse_lexical_composition=ebase,mse_generic_correction=egeneric,mse_class_correction=eclass,
                        class_gain_vs_lexical=(ebase-eclass)/(ebase+1e-12),
                        class_gain_vs_generic=(egeneric-eclass)/(egeneric+1e-12) if np.isfinite(egeneric) else np.nan))
    class_corr_flat.append((G-Iaff).reshape(-1)); class_w.append(len(occ))
reldf=pd.DataFrame(relrows)
reldf.to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_relations.csv',index=False)
relspec=spectrum(class_corr_flat,class_w)

# Label-shuffle control: preserve predicted/actual pairs, permute class labels on train/test; fit pseudo class corrections.
rng=np.random.default_rng(1701)
shuffle_gains=[]
usable_classes=list(reldf.relation) if len(reldf) else []
for rep in range(50):
    # pool records from usable classes, shuffle class membership labels keeping sizes approximately same
    pool=[]
    for cls in usable_classes:
        for r in relation_occ[cls]: pool.append([cls,*r])
    labs=[x[0] for x in pool]; rng.shuffle(labs)
    grouped=defaultdict(list)
    for lab,r in zip(labs,pool): grouped[lab].append(tuple(r[1:]))
    for cls in usable_classes:
        occ=grouped[cls]; tr=[r for r in occ if split_key(r[2])!=0]; te=[r for r in occ if split_key(r[2])==0]
        if len(tr)<30 or len(te)<8: continue
        Xtr=np.vstack([r[0] for r in tr]); Ytr=np.vstack([r[1] for r in tr]); Xte=np.vstack([r[0] for r in te]); Yte=np.vstack([r[1] for r in te])
        G=fit_affine(Xtr,Ytr,lam=3.0)
        eclass=wmse(apply(G,Xte),Yte,np.ones(len(te))); egeneric=wmse(apply(Ggeneric,Xte),Yte,np.ones(len(te)))
        shuffle_gains.append((egeneric-eclass)/(egeneric+1e-12))

# ---------- hierarchy summary ----------
lex_w=lexdf.n_test.values if len(lexdf) else np.array([1])
def wavg(df,col,wcol='n_test'):
    if len(df)==0:return float('nan')
    return float(np.average(df[col],weights=df[wcol]))
summary={
    'tokens':N,'vocab_states':V,'state_dim':d,'lexical_operators':len(ops),
    'lexical_mse_operator':wavg(lexdf,'mse_operator'),'lexical_mse_reset':wavg(lexdf,'mse_reset'),
    'phrase_operators_tested':len(pairdf),'phrase_mse_composed':wavg(pairdf,'mse_composed'),'phrase_mse_direct':wavg(pairdf,'mse_direct'),
    'phrase_direct_gain':wavg(pairdf,'direct_gain'),
    'phrase_operator_residual_ratio':float(np.average(pairdf.operator_residual_ratio,weights=pairdf.n_train)) if len(pairdf) else np.nan,
    'phrase_synthetic_residual_ratio':float(np.average(pairdf.synthetic_residual_ratio,weights=pairdf.n_train)) if len(pairdf) else np.nan,
    'phrase_residual_stable_rank':realres['stable_rank'],'phrase_residual_top3':realres['top3'],'phrase_residual_d95':realres['d95'],
    'synthetic_residual_stable_rank':synres['stable_rank'],'synthetic_residual_top3':synres['top3'],'synthetic_residual_d95':synres['d95'],
    'relation_classes_tested':len(reldf),'relation_mse_lexical':wavg(reldf,'mse_lexical_composition'),
    'relation_mse_generic':wavg(reldf,'mse_generic_correction'),'relation_mse_class':wavg(reldf,'mse_class_correction'),
    'relation_class_gain_vs_lexical':wavg(reldf,'class_gain_vs_lexical'),'relation_class_gain_vs_generic':wavg(reldf,'class_gain_vs_generic'),
    'relation_shuffle_gain_vs_generic_mean':float(np.mean(shuffle_gains)) if shuffle_gains else np.nan,
    'relation_shuffle_gain_vs_generic_p95':float(np.quantile(shuffle_gains,.95)) if shuffle_gains else np.nan,
    'relation_correction_stable_rank':relspec['stable_rank'],'relation_correction_top3':relspec['top3'],'relation_correction_d95':relspec['d95'],
}
pd.DataFrame([summary]).to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_summary.csv',index=False)
# spectra
pd.DataFrame({'mode':np.arange(1,len(realres['singular'])+1),'phrase_residual_singular':realres['singular']}).to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_residual_spectrum.csv',index=False)
pd.DataFrame({'mode':np.arange(1,len(relspec['singular'])+1),'relation_correction_singular':relspec['singular']}).to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_spectrum.csv',index=False)
print(pd.DataFrame([summary]).T.to_string(header=False))
print('\nRELATIONS\n',reldf.to_string(index=False))
print('\nTop phrases direct gain\n',pairdf.sort_values('direct_gain',ascending=False).head(20).to_string(index=False))

# ---------- conservative additive residual test across horizons ----------
add_rows=[]; add_shuffle=[]
for HH in [2,3,4,5,6,8]:
    occs=defaultdict(list)
    for t in range(MAXL,N-HH-1):
        cls=tokclass.get(tokens[t])
        if cls is None: continue
        seq=list(map(int,ids[t:t+HH]))
        if any(a not in ops for a in seq): continue
        x=zpos(t); y=zpos(t+HH)
        if x is None or y is None: continue
        pred=chain_apply([ops[a] for a in seq],x)
        occs[cls].append((pred,y,t,tokens[t]))
    # global train residual
    gtr=[]
    for cls,os in occs.items():
        gtr += [r for r in os if split_key(r[2])!=0]
    if len(gtr)<100: continue
    gres=np.mean(np.vstack([r[1]-r[0] for r in gtr]),axis=0)
    usable=[]
    for cls,os in occs.items():
        tr=[r for r in os if split_key(r[2])!=0]; te=[r for r in os if split_key(r[2])==0]
        if len(tr)<30 or len(te)<8: continue
        cres=np.mean(np.vstack([r[1]-r[0] for r in tr]),axis=0)
        Xte=np.vstack([r[0] for r in te]); Yte=np.vstack([r[1] for r in te])
        e0=wmse(Xte,Yte,np.ones(len(te)))
        eg=wmse(Xte+gres,Yte,np.ones(len(te)))
        ec=wmse(Xte+cres,Yte,np.ones(len(te)))
        add_rows.append(dict(horizon=HH,relation=cls,n_train=len(tr),n_test=len(te),mse_lexical=e0,mse_global_residual=eg,mse_class_residual=ec,
                             gain_class_vs_lexical=(e0-ec)/(e0+1e-12),gain_class_vs_global=(eg-ec)/(eg+1e-12)))
        usable.append(cls)
    # marker-specific version
    # shuffle labels among usable-class records for calibration
    pool=[]
    for cls in usable:
        for r in occs[cls]: pool.append([cls,*r])
    if pool:
        origlabs=[x[0] for x in pool]
        for rep in range(30):
            labs=origlabs.copy(); rng.shuffle(labs)
            grouped=defaultdict(list)
            for lab,r in zip(labs,pool): grouped[lab].append(tuple(r[1:]))
            gains=[]
            for cls in usable:
                os=grouped[cls]; tr=[r for r in os if split_key(r[2])!=0]; te=[r for r in os if split_key(r[2])==0]
                if len(tr)<20 or len(te)<6: continue
                cres=np.mean(np.vstack([r[1]-r[0] for r in tr]),axis=0)
                Xte=np.vstack([r[0] for r in te]); Yte=np.vstack([r[1] for r in te])
                eg=wmse(Xte+gres,Yte,np.ones(len(te))); ec=wmse(Xte+cres,Yte,np.ones(len(te)))
                gains.append((eg-ec)/(eg+1e-12))
            if gains: add_shuffle.append(dict(horizon=HH,rep=rep,mean_gain=float(np.mean(gains))))
adddf=pd.DataFrame(add_rows); adddf.to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_additive.csv',index=False)
shdf=pd.DataFrame(add_shuffle); shdf.to_csv(BASE/'LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_additive_shuffle.csv',index=False)
print('\nADDITIVE BY HORIZON')
for HH,g in adddf.groupby('horizon'):
    wg=g.n_test
    print(HH, 'nclasses',len(g),'gain_vs_lex',np.average(g.gain_class_vs_lexical,weights=wg),'gain_vs_global',np.average(g.gain_class_vs_global,weights=wg),
          'shuffle_mean', shdf[shdf.horizon==HH].mean_gain.mean() if len(shdf) else np.nan,
          'shuffle_p95', shdf[shdf.horizon==HH].mean_gain.quantile(.95) if len(shdf) else np.nan)
print(adddf.to_string(index=False))
