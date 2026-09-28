from pathlib import Path
import os
RESULTS_DIR=Path(os.environ.get('MDM_OUTPUT_DIR', str(Path.cwd()/'mdm_validation_results')))
RESULTS_DIR.mkdir(parents=True,exist_ok=True)
import numpy as np, pandas as pd
import statsmodels.api as sm
from sklearn.model_selection import KFold, train_test_split
from sklearn.preprocessing import SplineTransformer, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_squared_error

OUT=str(RESULTS_DIR)
en=sm.datasets.engel.load_pandas().data.copy(); x=en['income'].to_numpy(float); y=en['foodexp'].to_numpy(float)

def fitpred(xtr,ytr,xte,w=None):
    spl=SplineTransformer(n_knots=6,degree=3,include_bias=False,knots='quantile')
    Ztr=spl.fit_transform(xtr[:,None]); Zte=spl.transform(xte[:,None])
    sc=StandardScaler().fit(Ztr); Ztr=sc.transform(Ztr); Zte=sc.transform(Zte)
    m=Ridge(alpha=1.0).fit(Ztr,ytr,sample_weight=w); return m.predict(Zte)

def weights(x,bins=8,clip=8):
    edges=np.linspace(x.min(),x.max(),bins+1); b=np.clip(np.digitize(x,edges[1:-1]),0,bins-1)
    c=np.bincount(b,minlength=bins); target=len(x)/bins
    w=np.array([target/max(c[i],1) for i in b]); w=np.clip(w,1/clip,clip); return w/w.mean(),edges

def macro(y,p,x,edges):
    b=np.clip(np.digitize(x,edges[1:-1]),0,len(edges)-2); vals=[]
    for k in range(len(edges)-1):
        m=b==k
        if m.sum()>=2: vals.append(mean_squared_error(y[m],p[m])**.5)
    return np.mean(vals) if vals else np.nan

rows=[]
for seed in range(80):
    tr,te=train_test_split(np.arange(len(x)),test_size=.3,random_state=5000+seed)
    # inner micro-probe: 4-fold, target macro-RMSE
    kf=KFold(4,shuffle=True,random_state=6000+seed)
    scores={'plain':[],'coverage':[]}
    for itr,iva in kf.split(tr):
        a=tr[itr]; b=tr[iva]
        w,edges=weights(x[a])
        pp=fitpred(x[a],y[a],x[b],None); pc=fitpred(x[a],y[a],x[b],w)
        scores['plain'].append(macro(y[b],pp,x[b],edges)); scores['coverage'].append(macro(y[b],pc,x[b],edges))
    mp=np.nanmean(scores['plain']); mc=np.nanmean(scores['coverage'])
    choice='coverage' if mc<mp else 'plain'
    w,edges=weights(x[tr]); p0=fitpred(x[tr],y[tr],x[te],None); p1=fitpred(x[tr],y[tr],x[te],w)
    ps=p1 if choice=='coverage' else p0
    rows.append({'seed':seed,'choice':choice,'inner_macro_plain':mp,'inner_macro_coverage':mc,
                 'outer_macro_plain':macro(y[te],p0,x[te],edges),'outer_macro_coverage':macro(y[te],p1,x[te],edges),'outer_macro_selected':macro(y[te],ps,x[te],edges),
                 'outer_rmse_plain':mean_squared_error(y[te],p0)**.5,'outer_rmse_coverage':mean_squared_error(y[te],p1)**.5,'outer_rmse_selected':mean_squared_error(y[te],ps)**.5})
df=pd.DataFrame(rows); df.to_csv(f'{OUT}/engel_nested_microprobe.csv',index=False)
print(df['choice'].value_counts().to_dict())
for c in ['outer_macro_plain','outer_macro_coverage','outer_macro_selected','outer_rmse_plain','outer_rmse_coverage','outer_rmse_selected']:
 print(c,df[c].mean(),df[c].median())
print('selected beats forced coverage', np.mean(df.outer_macro_selected < df.outer_macro_coverage))
print('selected beats plain', np.mean(df.outer_macro_selected < df.outer_macro_plain))
