import numpy as np, pandas as pd, os
from scipy.stats import skew, kurtosis, spearmanr
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score, brier_score_loss, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
import matplotlib.pyplot as plt

OUT='/mnt/data/causal_geometry_006'; os.makedirs(OUT,exist_ok=True)
rng=np.random.default_rng(260927)

# ---------- generators ----------
def gen(fam,n,seed,heldout=False):
    rg=np.random.default_rng(seed); E=rg.choice([-1.,1.],size=n)
    # parameter ranges: heldout uses stronger/different ranges, not seen in calibration
    if heldout:
        a=rg.uniform(.55,1.35); noise=rg.uniform(.55,1.05)
    else:
        a=rg.uniform(.65,1.25); noise=rg.uniform(.45,.95)
    if fam=='REV':
        X=rg.normal(size=n); Y=a*X+noise*rg.normal(size=n); E=rg.choice([-1.,1.],size=n)
    elif fam=='ANM':
        X=rg.normal(size=n); b=rg.uniform(.45,.9) if heldout else rg.uniform(.25,.7)
        Y=a*X+b*np.tanh(1.4*X)+noise*rg.normal(size=n)
    elif fam=='HET':
        X=rg.normal(size=n); h=rg.uniform(.45,.8) if heldout else rg.uniform(.25,.65)
        Y=a*X+noise*np.exp(h*np.tanh(X))*rg.normal(size=n)
    elif fam=='NG':
        X=rg.laplace(size=n)/np.sqrt(2); N=rg.laplace(size=n)/np.sqrt(2)
        Y=a*X+noise*N
    elif fam=='ENV':
        shift=rg.uniform(.8,1.4) if heldout else rg.uniform(.5,1.1)
        X=shift*E+rg.normal(size=n); Y=a*X+noise*rg.normal(size=n)
    elif fam=='PNL':
        X=rg.normal(size=n); Z=a*X+noise*rg.normal(size=n); c=rg.uniform(.45,.75) if heldout else rg.uniform(.25,.6)
        Y=Z+c*np.tanh(1.3*Z)
    elif fam=='MIX':
        shift=rg.uniform(.55,1.15); h=rg.uniform(.25,.65); b=rg.uniform(.2,.65)
        X=shift*E+rg.normal(size=n)
        eps=rg.laplace(size=n)/np.sqrt(2)
        Y=a*X+b*np.tanh(X)+noise*np.exp(h*np.tanh(X))*eps
    else: raise ValueError(fam)
    # standardize for geometry comparability
    X=(X-X.mean())/(X.std()+1e-12); Y=(Y-Y.mean())/(Y.std()+1e-12)
    return X,Y,E

# ---------- geometry ----------
def polyfit_resid(x,y,deg=3):
    X=np.column_stack([x**k for k in range(1,deg+1)])
    X=np.column_stack([np.ones(len(x)),X])
    coef=np.linalg.lstsq(X,y,rcond=None)[0]; pred=X@coef; return y-pred,coef,np.mean((y-pred)**2)

def binned_stats(x,r,bins=8):
    qs=np.quantile(x,np.linspace(0,1,bins+1)); qs=np.unique(qs)
    if len(qs)<4: return 0.,0.
    idx=np.digitize(x,qs[1:-1],right=True); means=[]; sds=[]; ns=[]
    for b in range(len(qs)-1):
        z=r[idx==b]
        if len(z)>=8: means.append(z.mean()); sds.append(z.std()+1e-12); ns.append(len(z))
    if len(means)<3: return 0.,0.
    means=np.array(means); sds=np.array(sds); ns=np.array(ns); w=ns/ns.sum()
    eta_mean=float(np.sum(w*(means-np.sum(w*means))**2)/(np.var(r)+1e-12))
    fibre_cv=float(np.std(sds)/(np.mean(sds)+1e-12))
    return eta_mean,fibre_cv

def env_stability(x,y,E):
    coefs=[]; vars_=[]
    for ev in (-1.,1.):
        m=E==ev
        r,c,mse=polyfit_resid(x[m],y[m],3); coefs.append(c); vars_.append(np.var(r))
    coefs=np.array(coefs)
    cvar=float(np.linalg.norm(coefs[0]-coefs[1])/(np.linalg.norm(coefs.mean(0))+1e-8))
    vcv=float(np.std(vars_)/(np.mean(vars_)+1e-12))
    return cvar,vcv

def dir_features(x,y,E):
    r3,c3,mse3=polyfit_resid(x,y,3); r1,c1,mse1=polyfit_resid(x,y,1)
    eta,fibre=binned_stats(x,r3)
    rho_abs=abs(spearmanr(x,np.abs(r3)).statistic); rho_sq=abs(spearmanr(x,r3*r3).statistic)
    # residual shape and nonlinear advantage
    shp=abs(skew(r3)); kur=abs(kurtosis(r3,fisher=True))
    gain=max(0.,(mse1-mse3)/(mse1+1e-12))
    envc,envv=env_stability(x,y,E)
    return np.array([eta,fibre,rho_abs,rho_sq,shp,kur,gain,envc,envv,mse3],float)

def feature_pack(a,b,E):
    fab=dir_features(a,b,E); fba=dir_features(b,a,E)
    gap=fab-fba
    sym=np.concatenate([np.minimum(fab,fba),np.maximum(fab,fba),np.abs(gap)])
    # direction-free marginal geometry: sorted skew/kurt and environment shifts
    marg=[]
    for z in (a,b):
        marg += [abs(skew(z)),abs(kurtosis(z,fisher=True)), abs(z[E==1].mean()-z[E==-1].mean()), abs(z[E==1].std()-z[E==-1].std())]
    m1=np.array(marg[:4]); m2=np.array(marg[4:])
    sym=np.concatenate([sym,np.minimum(m1,m2),np.maximum(m1,m2)])
    return gap,sym,fab,fba

FAMS=['REV','ANM','HET','NG','ENV','PNL']
# base datasets, paired orientations; group prevents leakage
rows=[]; gid=0
for split,heldout,per in [('cal',False,95),('external',True,45)]:
    for fam in FAMS:
        for j in range(per):
            n=int(rng.choice([300,500,800,1200]))
            X,Y,E=gen(fam,n,int(rng.integers(1e9)),heldout)
            gap,sym,fxy,fyx=feature_pack(X,Y,E)
            for rev in [0,1]:
                g=gap if rev==0 else -gap
                label=1 if rev==0 else 0 # left variable is cause
                rec={'split':split,'family':fam,'group':gid,'left_is_cause':label,'n':n}
                for k,v in enumerate(g): rec[f'g{k}']=v
                for k,v in enumerate(sym): rec[f's{k}']=v
                rows.append(rec)
            gid+=1
# unseen mixtures only external
for j in range(90):
    n=int(rng.choice([300,500,800,1200])); X,Y,E=gen('MIX',n,int(rng.integers(1e9)),True)
    gap,sym,_,_=feature_pack(X,Y,E)
    for rev in [0,1]:
        g=gap if rev==0 else -gap; label=1 if rev==0 else 0
        rec={'split':'external','family':'MIX','group':gid,'left_is_cause':label,'n':n}
        for k,v in enumerate(g): rec[f'g{k}']=v
        for k,v in enumerate(sym): rec[f's{k}']=v
        rows.append(rec)
    gid+=1
D=pd.DataFrame(rows); D.to_csv(f'{OUT}/cg006_practical_features.csv',index=False)
gcols=[c for c in D if c.startswith('g') and c[1:].isdigit()]; scols=[c for c in D if c.startswith('s') and c[1:].isdigit()]
cal=D[D.split=='cal'].copy(); ext=D[D.split=='external'].copy()
# calibration train/validation by groups
GSS=GroupShuffleSplit(n_splits=1,test_size=.28,random_state=11)
itr,iva=next(GSS.split(cal,groups=cal.group)); tr=cal.iloc[itr].copy(); va=cal.iloc[iva].copy()
# router on one orientation per group only; symmetric features make orientation irrelevant
trr=tr.drop_duplicates('group'); var=va.drop_duplicates('group')
router=RandomForestClassifier(n_estimators=500,min_samples_leaf=4,max_features=.65,class_weight='balanced',random_state=3)
router.fit(trr[scols],trr.family)
# experts: transparent regularized logistic per regime on directional geometry gaps
experts={}
for fam in FAMS[1:]:
    z=tr[tr.family==fam]
    model=make_pipeline(StandardScaler(),LogisticRegression(C=.7,max_iter=3000))
    model.fit(z[gcols],z.left_is_cause); experts[fam]=model
# unified baselines
uni_lin=make_pipeline(StandardScaler(),LogisticRegression(C=.7,max_iter=3000)).fit(tr[tr.family!='REV'][gcols],tr[tr.family!='REV'].left_is_cause)
uni_rf=ExtraTreesClassifier(n_estimators=600,min_samples_leaf=3,max_features=.8,random_state=5).fit(tr[tr.family!='REV'][gcols+scols],tr[tr.family!='REV'].left_is_cause)
classes=list(router.classes_)

def predict_atlas(df):
    rp=router.predict_proba(df[scols]); cmap={c:i for i,c in enumerate(classes)}
    p=np.zeros(len(df)); mass=np.zeros(len(df))
    for fam,mod in experts.items():
        w=rp[:,cmap[fam]] if fam in cmap else 0
        pf=mod.predict_proba(df[gcols])[:,1]
        p+=w*pf; mass+=w
    # condition on non-reversible mechanism mass, but retain rev probability for abstention
    p=np.where(mass>1e-8,p/mass,.5)
    revp=rp[:,cmap['REV']]
    return p,revp,rp

def evalset(name,df):
    active=df.family!='REV'; y=df.left_is_cause.values
    pa,pr,_=predict_atlas(df); pl=uni_lin.predict_proba(df[gcols])[:,1]; prf=uni_rf.predict_proba(df[gcols+scols])[:,1]
    out=[]
    for method,p in [('unified_linear',pl),('unified_nonlinear',prf),('soft_geometry_atlas',pa)]:
        out.append({'set':name,'method':method,'accuracy_nonreversible':accuracy_score(y[active],p[active]>=.5),
                    'brier_nonreversible':brier_score_loss(y[active],p[active]),'n_nonrev':int(active.sum())})
    # selective triage: only answer if causal probability strong and reversible probability low
    ans=(np.abs(pa-.5)>=.30)&(pr<.40)
    useful=ans & active
    out.append({'set':name,'method':'atlas_selective_p80','accuracy_nonreversible':accuracy_score(y[useful],pa[useful]>=.5) if useful.sum() else np.nan,
                'brier_nonreversible':brier_score_loss(y[useful],pa[useful]) if useful.sum() else np.nan,
                'n_nonrev':int(useful.sum()),'coverage_nonrev':float(useful.sum()/active.sum()),
                'abstain_REV':float((~ans[df.family=='REV']).mean()) if (df.family=='REV').any() else np.nan})
    return pd.DataFrame(out),pa,pr
res=[]
for name,df in [('validation',va),('external_all',ext),('external_pure',ext[ext.family!='MIX']),('external_mixed',ext[ext.family=='MIX'])]:
    rr,pa,pr=evalset(name,df); res.append(rr)
R=pd.concat(res,ignore_index=True); R.to_csv(f'{OUT}/cg006_practical_benchmark.csv',index=False)
# per-family external atlas performance
pa,prev,_=predict_atlas(ext); ext=ext.copy(); ext['p_atlas']=pa; ext['p_rev']=prev
pf=[]
for fam,g in ext.groupby('family'):
    if fam=='REV':
        pf.append({'family':fam,'metric':'abstain_rate','value':float(((np.abs(g.p_atlas-.5)<.30)|(g.p_rev>=.40)).mean())})
    else:
        pf.append({'family':fam,'metric':'direction_accuracy','value':float(accuracy_score(g.left_is_cause,g.p_atlas>=.5))})
pfdf=pd.DataFrame(pf); pfdf.to_csv(f'{OUT}/cg006_practical_by_family.csv',index=False)
# router confusion on external pure, one orientation/group
exr=ext[ext.family!='MIX'].drop_duplicates('group'); pred=router.predict(exr[scols]);
router_acc=accuracy_score(exr.family,pred)
# blind example cards: choose one correct high-confidence from several families + one REV
examples=[]
for fam in ['ANM','HET','NG','ENV','PNL','MIX','REV']:
    g=ext[ext.family==fam].copy(); g['confidence']=np.abs(g.p_atlas-.5)*2
    row=g.sort_values('confidence',ascending=False).iloc[min(3,len(g)-1)]
    examples.append({'family_hidden_for_demo':fam,'n':int(row.n),'p_left_cause':float(row.p_atlas),'p_reversible':float(row.p_rev),
                     'true_left_cause':int(row.left_is_cause),'triage_call':'LEFT->RIGHT' if row.p_atlas>=.8 and row.p_rev<.4 else ('RIGHT->LEFT' if row.p_atlas<=.2 and row.p_rev<.4 else 'UNRESOLVED')})
pd.DataFrame(examples).to_csv(f'{OUT}/cg006_blind_triage_examples.csv',index=False)
# figures
fig,ax=plt.subplots(figsize=(7.4,4.6))
plot=R[R['set'].isin(['validation','external_pure','external_mixed']) & R.method.isin(['unified_linear','unified_nonlinear','soft_geometry_atlas'])]
for m in ['unified_linear','unified_nonlinear','soft_geometry_atlas']:
    s=plot[plot.method==m]; ax.plot(s['set'],100*s.accuracy_nonreversible,marker='o',label=m.replace('_',' '))
ax.set_ylabel('Direction accuracy (%)'); ax.set_title('Geometry-first causal triage across held-out and mixed SCMs'); ax.grid(axis='y',alpha=.2); ax.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig(f'{OUT}/fig22_practical_benchmark.png',dpi=220); plt.close(fig)
fig,ax=plt.subplots(figsize=(7.4,4.6)); q=pfdf.copy(); ax.bar(q.family,100*q.value); ax.set_ylabel('Percent'); ax.set_title('External geometry triage: direction accuracy, or abstention for reversible data'); ax.grid(axis='y',alpha=.2)
fig.tight_layout(); fig.savefig(f'{OUT}/fig23_practical_by_family.png',dpi=220); plt.close(fig)
print(R.to_string(index=False))
print('\nExternal router family accuracy:',router_acc)
print('\nBy family')
print(pfdf.to_string(index=False))
print('\nExamples')
print(pd.DataFrame(examples).to_string(index=False))

