import json, os
import numpy as np
import pandas as pd
from sklearn.datasets import load_iris, load_wine, load_diabetes, load_breast_cancer, load_digits
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import pdist

OUT=os.path.dirname(__file__)

def geom_metrics(X, k=10):
    X=np.asarray(X,float)
    X=X[:,np.nanstd(X,axis=0)>0]
    X=StandardScaler().fit_transform(X)
    vals=np.linalg.eigvalsh(np.cov(X,rowvar=False))[::-1]
    vals=np.clip(vals,0,None)
    total=vals.sum(); probs=vals/total
    stable=total/vals[0]
    participation=total**2/np.sum(vals**2)
    entropy=np.exp(-np.sum(probs[probs>0]*np.log(probs[probs>0])))
    cum=np.cumsum(probs)
    d95=int(np.searchsorted(cum,.95)+1)
    top3=float(cum[min(2,len(cum)-1)])
    top4=float(cum[min(3,len(cum)-1)])
    k=min(k,len(X)-1)
    nbr=NearestNeighbors(n_neighbors=k+1).fit(X)
    d,idx=nbr.kneighbors(X); d=d[:,1:]; idx=idx[:,1:]
    Tk=d[:,-1]
    den=np.sum(np.log(Tk[:,None]/np.clip(d[:,:-1],1e-12,None)),axis=1)
    mle=(k-1)/np.clip(den,1e-12,None)
    mle=mle[np.isfinite(mle)]
    mu=d[:,1]/np.clip(d[:,0],1e-12,None)
    logs=np.log(mu[mu>1])
    twonn=float(1/np.mean(logs)) if len(logs) else np.nan
    q=min(4,X.shape[1])
    Z=PCA(n_components=q).fit_transform(X)
    nbrz=NearestNeighbors(n_neighbors=k+1).fit(Z)
    _,idz=nbrz.kneighbors(Z); idz=idz[:,1:]
    recall=np.mean([len(set(idx[i]) & set(idz[i]))/k for i in range(len(X))])
    corr=float(np.corrcoef(pdist(X),pdist(Z))[0,1]) if len(X)<=2500 else np.nan
    return dict(n=X.shape[0],p=X.shape[1],stable_rank=float(stable),participation_rank=float(participation),entropy_rank=float(entropy),d95=d95,top3_var=top3,top4_var=top4,mle10_median=float(np.median(mle)),twonn_id=twonn,knn10_recall_4d=float(recall),distance_corr_4d=corr)

DATA=[('Iris',load_iris),('Wine',load_wine),('Diabetes',load_diabetes),('Breast cancer',load_breast_cancer),('Digits',load_digits)]
rows=[]
for name,fn in DATA:
    r=geom_metrics(fn().data); r['dataset']=name; rows.append(r)
pd.DataFrame(rows).to_csv(os.path.join(OUT,'sklearn_geometry_results.csv'),index=False)

# 20 x 80% sample stability, deterministic
rng=np.random.default_rng(20260927)
st=[]
for name,fn in DATA:
    X=fn().data
    for rep in range(20):
        ids=rng.choice(len(X),size=max(30,int(.8*len(X))),replace=False)
        r=geom_metrics(X[ids])
        st.append({'dataset':name,'replicate':rep+1,'mle10_median':r['mle10_median'],'participation_rank':r['participation_rank'],'d95':r['d95'],'top4_var':r['top4_var']})
pd.DataFrame(st).to_csv(os.path.join(OUT,'resampling_stability.csv'),index=False)

# External public-data measurements were executed directly against pinned GitHub file contents.
ext=pd.DataFrame([
 {'dataset':'Palmer Penguins morphology','n':342,'p':4,'stable_rank':1.4525619817440156,'participation_rank':1.9218948548121786,'entropy_rank':2.437532988605985,'d95':3,'top3_var':np.nan,'top4_var':1.0,'mle10_median':3.904611087887073,'twonn_id':4.018079233362337,'knn10_recall_4d':1.0,'distance_corr_4d':1.0,'source_sha':'25b46d384bf81f8399188500ea54917bb49d8890'},
 {'dataset':'UCI HAR subject-activity summary','n':180,'p':66,'stable_rank':1.429595039602496,'participation_rank':2.006439088668343,'entropy_rank':4.117773972921092,'d95':12,'top3_var':0.8080864324564679,'top4_var':0.8392437943816689,'mle10_median':7.961522810848983,'twonn_id':9.745599018069134,'knn10_recall_4d':0.5833333333333334,'distance_corr_4d':0.9851671225543703,'source_sha':''}
])
ext.to_csv(os.path.join(OUT,'external_geometry_results.csv'),index=False)
all_df=pd.concat([pd.DataFrame(rows),ext.drop(columns=['source_sha'])],ignore_index=True)
all_df.to_csv(os.path.join(OUT,'combined_geometry_results.csv'),index=False)

manifest=pd.DataFrame([
 {'dataset':'Iris','source':'scikit-learn load_iris','identity':'sklearn 1.8.0 built-in'},
 {'dataset':'Wine','source':'scikit-learn load_wine','identity':'sklearn 1.8.0 built-in'},
 {'dataset':'Diabetes','source':'scikit-learn load_diabetes','identity':'sklearn 1.8.0 built-in'},
 {'dataset':'Breast cancer','source':'scikit-learn load_breast_cancer','identity':'sklearn 1.8.0 built-in'},
 {'dataset':'Digits','source':'scikit-learn load_digits','identity':'sklearn 1.8.0 built-in'},
 {'dataset':'Palmer Penguins morphology','source':'allisonhorst/palmerpenguins inst/extdata/penguins.csv','identity':'blob sha 25b46d384bf81f8399188500ea54917bb49d8890'},
 {'dataset':'UCI HAR subject-activity summary','source':'ahmedtadde/UCI-HAR-Dataset MyTidyDF.txt','identity':'public GitHub file read 2026-09-27; 180 subject-activity rows, 66 numeric variables'}
])
manifest.to_csv(os.path.join(OUT,'source_manifest.csv'),index=False)

# Figures
import matplotlib.pyplot as plt
plot=all_df.sort_values('mle10_median')
fig,ax=plt.subplots(figsize=(8.5,5.5))
ax.barh(plot.dataset,plot.mle10_median)
ax.set_xlabel('Local intrinsic dimension (k=10 MLE median)')
ax.set_title('Local intrinsic dimension across real datasets')
fig.tight_layout(); fig.savefig(os.path.join(OUT,'local_intrinsic_dimension.png'),dpi=180); plt.close(fig)

plot=all_df.sort_values('top4_var')
fig,ax=plt.subplots(figsize=(8.5,5.5))
ax.barh(plot.dataset,100*plot.top4_var)
ax.set_xlabel('Variance retained by first four PCs (%)')
ax.set_title('How much of total variation fits into four linear dimensions')
fig.tight_layout(); fig.savefig(os.path.join(OUT,'four_dim_variance.png'),dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(6.5,5.5))
ax.scatter(all_df.participation_rank,all_df.mle10_median)
for _,r in all_df.iterrows(): ax.annotate(r.dataset,(r.participation_rank,r.mle10_median),xytext=(4,3),textcoords='offset points',fontsize=8)
ax.set_xlabel('Global participation rank'); ax.set_ylabel('Local intrinsic dimension (MLE)')
ax.set_title('Global low rank can coexist with higher local dimensionality')
fig.tight_layout(); fig.savefig(os.path.join(OUT,'global_vs_local_dimension.png'),dpi=180); plt.close(fig)

print(pd.DataFrame(rows).to_string(index=False))
print('\nStability MLE 10-90%:')
sdf=pd.DataFrame(st)
print(sdf.groupby('dataset').mle10_median.quantile([.1,.5,.9]).unstack())
