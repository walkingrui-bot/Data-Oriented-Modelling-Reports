from pathlib import Path
import os
RESULTS_DIR=Path(os.environ.get('MDM_OUTPUT_DIR', str(Path.cwd()/'mdm_validation_results')))
RESULTS_DIR.mkdir(parents=True,exist_ok=True)
import os, json, math, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
import networkx as nx
from scipy.optimize import minimize
from sklearn.preprocessing import StandardScaler, OneHotEncoder, SplineTransformer
from sklearn.linear_model import LogisticRegression, Ridge, PoissonRegressor
from sklearn.metrics import accuracy_score, log_loss, mean_squared_error, mean_absolute_error, mean_poisson_deviance, roc_auc_score
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

warnings.filterwarnings('ignore')
OUT=str(RESULTS_DIR)
os.makedirs(OUT,exist_ok=True)
RNG=np.random.default_rng(20260928)

# ---------- MODECHOICE ----------
def mode_design(df, scaler=None, fit=False):
    cont=df[['ttme','invc','invt','gc']].to_numpy(float)
    if fit:
        scaler=StandardScaler().fit(cont)
    cont=scaler.transform(cont)
    mode=df['mode'].astype(int).to_numpy()
    # drop mode 1 as reference, add modes 2,3,4
    md=np.column_stack([(mode==m).astype(float) for m in [2,3,4]])
    return np.column_stack([cont,md]), scaler

def fit_conditional_softmax(X,y,groups):
    # groups are integer IDs; each group one chosen row
    uniq=np.unique(groups)
    idxs=[np.where(groups==g)[0] for g in uniq]
    def fg(beta):
        z=X@beta
        nll=0.0
        grad=np.zeros_like(beta)
        for idx in idxs:
            zz=z[idx]; zz=zz-zz.max(); p=np.exp(zz); p=p/p.sum()
            yy=y[idx]
            nll -= np.dot(yy, np.log(np.maximum(p,1e-15)))
            grad += X[idx].T@(p-yy)
        # tiny L2 for stability
        nll += 1e-4*np.dot(beta,beta)
        grad += 2e-4*beta
        return nll,grad
    res=minimize(lambda b: fg(b)[0], np.zeros(X.shape[1]), jac=lambda b: fg(b)[1], method='L-BFGS-B', options={'maxiter':500})
    return res.x, res.success

def grouped_metrics(scores,y,groups):
    nll=[]; acc=[]
    for g in np.unique(groups):
        idx=np.where(groups==g)[0]
        s=scores[idx]; s=s-s.max(); p=np.exp(s); p=p/p.sum()
        chosen=np.argmax(y[idx]); pred=np.argmax(p)
        acc.append(pred==chosen)
        nll.append(-np.log(max(p[chosen],1e-15)))
    return float(np.mean(acc)), float(np.mean(nll))

mc=sm.datasets.modechoice.load_pandas().data.copy()
ids=np.array(sorted(mc['individual'].unique()))
mc_rows=[]
for seed in range(60):
    rng=np.random.default_rng(1000+seed)
    tr_ids=rng.choice(ids,size=int(.7*len(ids)),replace=False)
    tr_mask=mc['individual'].isin(tr_ids).to_numpy(); te_mask=~tr_mask
    tr=mc.loc[tr_mask].copy(); te=mc.loc[te_mask].copy()
    Xtr,sc=mode_design(tr,fit=True); Xte,_=mode_design(te,scaler=sc,fit=False)
    ytr=tr['choice'].to_numpy(float); yte=te['choice'].to_numpy(float)
    gtr=tr['individual'].to_numpy(); gte=te['individual'].to_numpy()
    # flat logistic
    flat=LogisticRegression(C=1000,max_iter=2000,solver='lbfgs').fit(Xtr,ytr)
    flat_scores=flat.decision_function(Xte)
    fa,fnll=grouped_metrics(flat_scores,yte,gte)
    # conditional
    beta,ok=fit_conditional_softmax(Xtr,ytr,gtr)
    ca,cnll=grouped_metrics(Xte@beta,yte,gte)
    mc_rows.append({'seed':seed,'flat_choice_acc':fa,'flat_set_nll':fnll,'conditional_choice_acc':ca,'conditional_set_nll':cnll,'opt_success':ok})
mc_df=pd.DataFrame(mc_rows); mc_df.to_csv(f'{OUT}/modechoice_blind_results.csv',index=False)

# ---------- ENGEL ----------
def engel_fit_predict(xtr,ytr,xte,weights=None):
    spl=SplineTransformer(n_knots=6,degree=3,include_bias=False,knots='quantile')
    Ztr=spl.fit_transform(np.asarray(xtr).reshape(-1,1)); Zte=spl.transform(np.asarray(xte).reshape(-1,1))
    sc=StandardScaler().fit(Ztr); Ztr=sc.transform(Ztr); Zte=sc.transform(Zte)
    model=Ridge(alpha=1.0)
    model.fit(Ztr,ytr,sample_weight=weights)
    return model.predict(Zte)

def coverage_weights(x,bins=8,clip=10):
    x=np.asarray(x,float)
    edges=np.linspace(x.min(),x.max(),bins+1)
    b=np.clip(np.digitize(x,edges[1:-1],right=False),0,bins-1)
    counts=np.bincount(b,minlength=bins)
    target=len(x)/bins
    w=np.array([target/max(counts[i],1) for i in b])
    w=np.clip(w,1/clip,clip)
    w=w/np.mean(w)
    return w,edges

def macro_rmse(y,p,x,edges):
    b=np.clip(np.digitize(x,edges[1:-1],right=False),0,len(edges)-2)
    vals=[]
    for k in range(len(edges)-1):
        m=b==k
        if m.sum()>=2:
            vals.append(mean_squared_error(y[m],p[m])**0.5)
    return float(np.mean(vals)) if vals else np.nan, len(vals)

en=sm.datasets.engel.load_pandas().data.copy()
x=en['income'].to_numpy(float); y=en['foodexp'].to_numpy(float)
en_rows=[]
for seed in range(120):
    tr,te=train_test_split(np.arange(len(x)),test_size=.3,random_state=2000+seed)
    w,edges=coverage_weights(x[tr],bins=8,clip=8)
    p0=engel_fit_predict(x[tr],y[tr],x[te],None)
    p1=engel_fit_predict(x[tr],y[tr],x[te],w)
    rm0=mean_squared_error(y[te],p0)**0.5; rm1=mean_squared_error(y[te],p1)**0.5
    ma0,nb0=macro_rmse(y[te],p0,x[te],edges); ma1,nb1=macro_rmse(y[te],p1,x[te],edges)
    en_rows.append({'seed':seed,'rmse_plain':rm0,'rmse_coverage':rm1,'macro_rmse_plain':ma0,'macro_rmse_coverage':ma1,'test_bins_used':nb0})
en_df=pd.DataFrame(en_rows); en_df.to_csv(f'{OUT}/engel_blind_results.csv',index=False)

# ---------- RAND HIE ----------
rh=sm.datasets.randhie.load_pandas(); X=np.asarray(rh.exog,float); y=np.asarray(rh.endog,float)
rh_rows=[]
for seed in range(25):
    tr,te=train_test_split(np.arange(len(y)),test_size=.25,random_state=3000+seed)
    sc=StandardScaler().fit(X[tr]); Xtr=sc.transform(X[tr]); Xte=sc.transform(X[te])
    ridge=Ridge(alpha=10.0).fit(Xtr,y[tr]); pr=np.clip(ridge.predict(Xte),1e-6,None)
    pois=PoissonRegressor(alpha=1e-3,max_iter=2000,tol=1e-8).fit(Xtr,y[tr]); pp=np.clip(pois.predict(Xte),1e-6,None)
    rh_rows.append({'seed':seed,
        'ridge_poisson_deviance':mean_poisson_deviance(y[te],pr),'poisson_poisson_deviance':mean_poisson_deviance(y[te],pp),
        'ridge_rmse':mean_squared_error(y[te],pr)**0.5,'poisson_rmse':mean_squared_error(y[te],pp)**0.5,
        'ridge_mae':mean_absolute_error(y[te],pr),'poisson_mae':mean_absolute_error(y[te],pp)})
rh_df=pd.DataFrame(rh_rows); rh_df.to_csv(f'{OUT}/randhie_blind_results.csv',index=False)

# ---------- LES MIS ----------
G0=nx.Graph(nx.les_miserables_graph())
nodes=list(G0.nodes()); idx={u:i for i,u in enumerate(nodes)}
all_non=[(u,v) for i,u in enumerate(nodes) for v in nodes[i+1:] if not G0.has_edge(u,v)]

def scores_for_pairs(G,pairs):
    n=len(nodes); A=np.zeros((n,n),float)
    for u,v in G.edges():
        A[idx[u],idx[v]]=A[idx[v],idx[u]]=1.0
    deg=A.sum(1)
    # powers
    A2=A@A; A3=A2@A
    # SVD rank 8
    U,s,Vt=np.linalg.svd(A,full_matrices=False); r=min(8,len(s)); R=(U[:,:r]*s[:r])@Vt[:r,:]
    # row cosine
    norms=np.linalg.norm(A,axis=1)
    out={k:[] for k in ['PA','CN','AA','A3','SVD8','Cosine']}
    for u,v in pairs:
        i,j=idx[u],idx[v]
        out['PA'].append(deg[i]*deg[j]); out['CN'].append(A2[i,j]); out['A3'].append(A3[i,j]); out['SVD8'].append(R[i,j])
        common=np.where((A[i]>0)&(A[j]>0))[0]
        aa=sum(1/max(np.log(max(deg[w],2)),1e-12) for w in common)
        out['AA'].append(aa)
        out['Cosine'].append(float(A[i]@A[j]/max(norms[i]*norms[j],1e-12)))
    return out

lm_rows=[]
edges=list(G0.edges())
for seed in range(100):
    rng=np.random.default_rng(4000+seed)
    hidx=rng.choice(len(edges),size=max(1,int(.12*len(edges))),replace=False)
    hidden=[edges[i] for i in hidx]
    G=G0.copy(); G.remove_edges_from(hidden)
    neg=[all_non[i] for i in rng.choice(len(all_non),size=len(hidden),replace=False)]
    pairs=hidden+neg; yy=np.array([1]*len(hidden)+[0]*len(neg))
    scs=scores_for_pairs(G,pairs)
    row={'seed':seed,'n_hidden':len(hidden)}
    for k,v in scs.items():
        try: row[k+'_auc']=roc_auc_score(yy,v)
        except: row[k+'_auc']=.5
    lm_rows.append(row)
lm_df=pd.DataFrame(lm_rows); lm_df.to_csv(f'{OUT}/lesmis_blind_results.csv',index=False)

# ---------- SUMMARY ----------
def ci_summary(s):
    a=np.asarray(s,float); return {'mean':float(np.nanmean(a)),'sd':float(np.nanstd(a,ddof=1)),'median':float(np.nanmedian(a)),
                                  'q025':float(np.nanquantile(a,.025)),'q975':float(np.nanquantile(a,.975))}
summary={
 'ModeChoice':{k:ci_summary(mc_df[k]) for k in ['flat_choice_acc','conditional_choice_acc','flat_set_nll','conditional_set_nll']},
 'Engel':{k:ci_summary(en_df[k]) for k in ['rmse_plain','rmse_coverage','macro_rmse_plain','macro_rmse_coverage']},
 'RAND_HIE':{k:ci_summary(rh_df[k]) for k in ['ridge_poisson_deviance','poisson_poisson_deviance','ridge_rmse','poisson_rmse','ridge_mae','poisson_mae']},
 'Les_Miserables':{k:ci_summary(lm_df[k]) for k in ['PA_auc','CN_auc','AA_auc','A3_auc','SVD8_auc','Cosine_auc']}
}
# decisions hit flags
summary['hit_flags']={
 'ModeChoice_NLL': bool(mc_df['conditional_set_nll'].mean()<mc_df['flat_set_nll'].mean()),
 'ModeChoice_acc_nonreduce': bool(mc_df['conditional_choice_acc'].mean()>=mc_df['flat_choice_acc'].mean()-1e-12),
 'Engel_macro': bool(en_df['macro_rmse_coverage'].mean()<en_df['macro_rmse_plain'].mean()),
 'RANDHIE_deviance': bool(rh_df['poisson_poisson_deviance'].mean()<rh_df['ridge_poisson_deviance'].mean()),
 'LesMis_relation_vs_PA': bool(lm_df[['CN_auc','AA_auc','A3_auc','SVD8_auc','Cosine_auc']].mean().max()>lm_df['PA_auc'].mean())
}
open(f'{OUT}/blind_validation_summary.json','w').write(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))

# ---------- FIGURES ----------
# Figure 1: precommit vs reveal key deltas
labels=['ModeChoice\nset NLL','Engel\nmacro RMSE','RAND HIE\nPoisson dev.','Les Mis\nAUC']
base=[mc_df.flat_set_nll.mean(),en_df.macro_rmse_plain.mean(),rh_df.ridge_poisson_deviance.mean(),lm_df.PA_auc.mean()]
mech=[mc_df.conditional_set_nll.mean(),en_df.macro_rmse_coverage.mean(),rh_df.poisson_poisson_deviance.mean(),lm_df[['CN_auc','AA_auc','A3_auc','SVD8_auc','Cosine_auc']].mean().max()]
# normalize improvement direction so positive is better
imp=[(base[0]-mech[0])/base[0]*100,(base[1]-mech[1])/base[1]*100,(base[2]-mech[2])/base[2]*100,(mech[3]-base[3])/base[3]*100]
plt.figure(figsize=(8,4.8)); plt.bar(labels,imp); plt.axhline(0,linewidth=1); plt.ylabel('Relative improvement (%)'); plt.title('Blind SOP validation: precommitted mechanism-aware operation'); plt.tight_layout(); plt.savefig(f'{OUT}/fig_blind_summary.png',dpi=180); plt.close()

plt.figure(figsize=(8,4.8))
means=lm_df[[c for c in lm_df.columns if c.endswith('_auc')]].mean().sort_values(ascending=False)
plt.bar(means.index.str.replace('_auc',''),means.values); plt.axhline(.5,linewidth=1); plt.ylabel('ROC AUC'); plt.title('Les Misérables edge recovery: mechanism-native relation scores'); plt.tight_layout(); plt.savefig(f'{OUT}/fig_lesmis_auc.png',dpi=180); plt.close()

plt.figure(figsize=(7.5,4.6))
vals=[mc_df.flat_set_nll.mean(),mc_df.conditional_set_nll.mean()]
plt.bar(['Flat i.i.d. logistic','Group-normalized choice kernel'],vals); plt.ylabel('Choice-set NLL (lower is better)'); plt.title('ModeChoice blind validation'); plt.tight_layout(); plt.savefig(f'{OUT}/fig_modechoice_nll.png',dpi=180); plt.close()

plt.figure(figsize=(7.5,4.6))
vals=[en_df.macro_rmse_plain.mean(),en_df.macro_rmse_coverage.mean()]
plt.bar(['Ordinary training','Coverage-balanced training'],vals); plt.ylabel('Macro-RMSE across income regions'); plt.title('Engel blind validation'); plt.tight_layout(); plt.savefig(f'{OUT}/fig_engel_macro.png',dpi=180); plt.close()
