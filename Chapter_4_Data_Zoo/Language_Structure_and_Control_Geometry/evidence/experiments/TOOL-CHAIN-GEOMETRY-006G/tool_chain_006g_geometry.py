import os,json,random,csv,importlib.util,math
import numpy as np
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold,cross_val_score

OUT='/mnt/data/tool_chain_006g_evidence';os.makedirs(OUT,exist_ok=True)
spec=importlib.util.spec_from_file_location('g','/mnt/data/tool_chain_006g_train.py');g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
SEED_D=26092821

def collect():
    groups={k:[] for k in ['raw_seen','raw_unseen','canon_seen','canon_unseen']}; meta=[]
    configs=[('raw_seen',g.CELLS[1],g.SEEN_STYLES),('raw_unseen',g.CELLS[1],g.UNSEEN_STYLES),('canon_seen',g.CELLS[0],g.SEEN_STYLES),('canon_unseen',g.CELLS[0],g.UNSEEN_STYLES)]
    pair_id=0
    for pi,pseed in enumerate([SEED_D+50000,SEED_D+60000,SEED_D+70000],1):
        rr=random.Random(pseed);tasks=[g.make_task(rr) for _ in range(200)]
        for ti,t in enumerate(tasks):
            states={name:{'lines':[t.request],'w':t.init.copy(),'ctr':0,'rng':random.Random(pseed+100000+ti)} for name,_,_ in configs}
            for step,a in enumerate(t.oracle):
                # decision prefix before action; collect only after at least one result exists
                if step>0 and any(x.startswith('RESULT ') and ('"value"' in x or '"data"' in x or '"result"' in x or '"payload"' in x or '"observation"' in x or '"reply"' in x or '"measurement"' in x) for x in states['raw_seen']['lines']):
                    for name,_,_ in configs:groups[name].append(g.features(states[name]['lines']))
                    meta.append({'pair_id':pair_id,'panel':pi,'task_id':ti,'kind':t.kind,'step':step,'oracle_tool':a.tool});pair_id+=1
                if a.tool=='DONE': break
                for name,cell,styles in configs:
                    s=states[name];s['ctr']=g.append_exec(s['lines'],s['w'],a,s['ctr'],s['rng'],cell,pseed+100000+ti+step,styles)
    return {k:np.stack(v).astype(np.float64) for k,v in groups.items()},meta

def zfit(X):
    mu=X.mean(0);sd=X.std(0);mask=sd>1e-9;return (X[:,mask]-mu[mask])/sd[mask],mu,sd,mask

def spectrum_stats(Z):
    # covariance eig spectrum via SVD of centered standardized data
    Z=Z-Z.mean(0);s=np.linalg.svd(Z,compute_uv=False,full_matrices=False);eig=(s*s)/max(1,len(Z)-1);tot=eig.sum();mx=eig[0] if len(eig) else 0
    stable=tot/mx if mx>0 else 0;part=(tot*tot)/(np.square(eig).sum()) if np.square(eig).sum()>0 else 0
    cs=np.cumsum(eig)/tot if tot>0 else np.zeros_like(eig);p95=int(np.searchsorted(cs,.95)+1) if len(cs) else 0;top4=float(cs[min(3,len(cs)-1)]) if len(cs) else 0
    return {'stable_rank':float(stable),'participation_rank':float(part),'pca95':p95,'top4_energy':top4,'eig':eig}

def twonn_id(Z):
    if len(Z)<4:return float('nan')
    nn=NearestNeighbors(n_neighbors=3,metric='euclidean').fit(Z);d=nn.kneighbors(Z,return_distance=True)[0][:,1:3]
    r=np.maximum(d[:,1]/np.maximum(d[:,0],1e-12),1+1e-12);logs=np.log(r);m=logs[np.isfinite(logs)&(logs>0)]
    return float(1/m.mean()) if len(m) else float('nan')

def dist_cv(Z,seed=1,npairs=5000):
    rr=np.random.default_rng(seed);n=len(Z);i=rr.integers(0,n,npairs);j=rr.integers(0,n,npairs);ok=i!=j;i=i[ok];j=j[ok];d=np.linalg.norm(Z[i]-Z[j],axis=1);return float(d.std()/d.mean()) if d.mean()>0 else 0

def knn4_retention(Z,k=10):
    n=len(Z);kk=min(k+1,n);full=NearestNeighbors(n_neighbors=kk).fit(Z).kneighbors(return_distance=False)[:,1:]
    pc=PCA(n_components=min(4,Z.shape[1],n-1),svd_solver='full').fit_transform(Z);low=NearestNeighbors(n_neighbors=kk).fit(pc).kneighbors(return_distance=False)[:,1:]
    vals=[len(set(full[i])&set(low[i]))/k for i in range(n)];return float(np.mean(vals))

def domain_mix(A,B):
    X=np.vstack([A,B]);y=np.r_[np.zeros(len(A),int),np.ones(len(B),int)];nn=NearestNeighbors(n_neighbors=11).fit(X).kneighbors(return_distance=False)[:,1:]
    same=np.mean([np.mean(y[idx]==y[i]) for i,idx in enumerate(nn)])
    # 5-fold logistic separability
    cv=StratifiedKFold(5,shuffle=True,random_state=1);clf=LogisticRegression(max_iter=2000,C=1.0);acc=float(cross_val_score(clf,X,y,cv=cv,scoring='accuracy').mean())
    return {'knn_same_domain_fraction':float(same),'logistic5cv_accuracy':acc}

def matched_disp(A,B):
    d=np.linalg.norm(A-B,axis=1);cos=np.sum(A*B,1)/(np.linalg.norm(A,axis=1)*np.linalg.norm(B,axis=1)+1e-12)
    return {'mean_l2':float(d.mean()),'median_l2':float(np.median(d)),'mean_cosine':float(cos.mean()),'exact_fraction':float(np.mean(d<1e-12))}

def profile_pair(A,B,label):
    X=np.vstack([A,B]);Z,mu,sd,mask=zfit(X);ZA=Z[:len(A)];ZB=Z[len(A):]
    st=spectrum_stats(Z);res={'n_per_group':len(A),'active_dims':int(mask.sum()),'combined':{k:v for k,v in st.items() if k!='eig'},'twonn_id':twonn_id(Z),'pairwise_distance_cv':dist_cv(Z,seed=17),'knn4d_retention':knn4_retention(Z),'domain':domain_mix(ZA,ZB),'matched':matched_disp(ZA,ZB)}
    # 20x 80% bootstrap for spectrum + ID
    rr=np.random.default_rng(123);boots=[];n=len(A)
    for b in range(20):
        ia=rr.choice(n,int(.8*n),replace=False);ib=rr.choice(n,int(.8*n),replace=False);XX=np.vstack([A[ia],B[ib]]);ZZ,_,_,_=zfit(XX);ss=spectrum_stats(ZZ);boots.append([ss['stable_rank'],ss['participation_rank'],ss['pca95'],twonn_id(ZZ)])
    ba=np.asarray(boots,float);res['bootstrap20_80pct']={'stable_rank_mean':float(np.nanmean(ba[:,0])),'stable_rank_sd':float(np.nanstd(ba[:,0],ddof=1)),'participation_rank_mean':float(np.nanmean(ba[:,1])),'participation_rank_sd':float(np.nanstd(ba[:,1],ddof=1)),'pca95_mean':float(np.nanmean(ba[:,2])),'twonn_mean':float(np.nanmean(ba[:,3])),'twonn_sd':float(np.nanstd(ba[:,3],ddof=1))}
    return res

groups,meta=collect();res={'experiment':'TOOL-CHAIN-GEOMETRY-006G data-geometry precheck','rows_per_representation':len(meta),'raw_seen_vs_unseen':profile_pair(groups['raw_seen'],groups['raw_unseen'],'raw'),'canonical_seen_vs_unseen':profile_pair(groups['canon_seen'],groups['canon_unseen'],'canonical')}
# direct matched raw/canonical delta on native feature scale too
res['native_matched']={'raw':matched_disp(groups['raw_seen'],groups['raw_unseen']),'canonical':matched_disp(groups['canon_seen'],groups['canon_unseen'])}
json.dump(res,open(OUT+'/data_geometry_precheck.json','w'),indent=2)
with open(OUT+'/data_geometry_pairs.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(meta[0]));w.writeheader();w.writerows(meta)
np.savez_compressed(OUT+'/data_geometry_prefixes.npz',**groups)
print(json.dumps(res))
