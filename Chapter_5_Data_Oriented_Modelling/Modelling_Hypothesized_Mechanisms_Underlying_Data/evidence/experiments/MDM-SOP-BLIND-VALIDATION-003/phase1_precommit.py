from pathlib import Path
import os
RESULTS_DIR=Path(os.environ.get('MDM_OUTPUT_DIR', str(Path.cwd()/'mdm_validation_results')))
RESULTS_DIR.mkdir(parents=True,exist_ok=True)
import json, hashlib, datetime, math
import numpy as np, pandas as pd
import statsmodels.api as sm
import networkx as nx
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

OUT=str(RESULTS_DIR/'blind_precommit.json')

def local_diag(X, k=15):
    X=np.asarray(X,float)
    Xs=StandardScaler().fit_transform(X)
    n=len(Xs); kk=min(k,n-1)
    nn=NearestNeighbors(n_neighbors=kk+1).fit(Xs)
    d,_=nn.kneighbors(Xs)
    d=d[:,1:]
    r=d.mean(1)
    q10,q50,q90=np.quantile(r,[.1,.5,.9])
    gap=d[:,-1]/np.maximum(np.median(d[:,:-1],axis=1),1e-12) if kk>2 else np.ones(n)
    return {
      'n':int(n),'d':int(Xs.shape[1]),'k':int(kk),
      'local_scale_q10':float(q10),'local_scale_q50':float(q50),'local_scale_q90':float(q90),
      'scale_heterogeneity_q90_q10':float(q90/max(q10,1e-12)),
      'scale_cv':float(r.std()/max(r.mean(),1e-12)),
      'gap_q90':float(np.quantile(gap,.9)),
      'gap_q95':float(np.quantile(gap,.95)),
    }

def occupancy_diag(x,bins=8):
    x=np.asarray(x,float)
    edges=np.linspace(np.nanmin(x),np.nanmax(x),bins+1)
    counts,_=np.histogram(x,edges)
    pos=counts[counts>0]
    p=counts/counts.sum()
    ent=-np.sum(p[p>0]*np.log(p[p>0]))/np.log(bins)
    return {'bins':bins,'counts':counts.tolist(),'max_min_positive':float(pos.max()/pos.min()),
            'normalized_entropy':float(ent),'max_bin_share':float(counts.max()/counts.sum())}

pre={
 'title':'MDM-SOP-BLIND-VALIDATION-003 precommit',
 'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'rule':'All decisions below are based on design/feature/topology diagnostics only. Targets and downstream scores are not inspected until this file is written and hashed.',
 'datasets':{}
}

# 1 ModeChoice: inspect design without choice target.
d=sm.datasets.modechoice.load_pandas().data.copy()
X_mc=d[['ttme','invc','invt','gc','hinc','psize']]
gsizes=d.groupby('individual').size()
modes=d.groupby('individual')['mode'].nunique()
pre['datasets']['ModeChoice']={
 'diagnostics':{**local_diag(X_mc), 'n_groups':int(gsizes.size),'group_size_unique':sorted(map(int,gsizes.unique())),
                'modes_per_group_unique':sorted(map(int,modes.unique()))},
 'mechanism_target':'predict one selected alternative within each individual choice set',
 'decision':'GROUP_CHOICE_KERNEL',
 'prediction':'Flat i.i.d. row training is mechanism-misaligned. A group-normalized conditional-choice likelihood should improve held-out choice-set log loss and should not reduce choice-set accuracy.',
 'no_op_allowed':False
}

# 2 Engel: use income as coverage axis, food expenditure hidden as target until phase 2.
e=sm.datasets.engel.load_pandas().data.copy()
X_en=e[['income']]
pre['datasets']['Engel']={
 'diagnostics':{**local_diag(X_en,k=10), 'income_occupancy':occupancy_diag(X_en['income'],8)},
 'mechanism_target':'recover the food-expenditure response law across the observed income support, giving comparable importance to different income regions',
 'decision':'COVERAGE_BALANCED_STRUCTURE_TRAINING',
 'prediction':'Equal-width coverage-balanced training should improve macro-RMSE across income regions; ordinary RMSE may improve less or remain similar because natural occupancy is intentionally not the primary target.',
 'no_op_allowed':True
}

# 3 RAND HIE: feature geometry plus documented count outcome type; no outcome values.
r=sm.datasets.randhie.load_pandas()
X_rh=r.exog.copy()
pre['datasets']['RAND_HIE']={
 'diagnostics':local_diag(X_rh.sample(n=5000,random_state=1701),k=20),
 'measurement_mechanism':'mdvis is a nonnegative count of medical visits (dataset variable semantics); values not inspected in phase 1',
 'mechanism_target':'predict visit counts with a likelihood consistent with count-valued observations',
 'decision':'COUNT_LIKELIHOOD_KERNEL',
 'prediction':'A Poisson log-link learner should improve Poisson deviance over a Gaussian/Ridge baseline; RMSE need not be the main winner because the target mechanism is count likelihood.',
 'no_op_allowed':False
}

# 4 Les Miserables graph: topology only.
G=nx.les_miserables_graph()
Gu=nx.Graph(G)
n=Gu.number_of_nodes(); m=Gu.number_of_edges(); c=nx.number_connected_components(Gu)
cycle=m-n+c
clust=nx.average_clustering(Gu, weight=None)
deg=np.array([x for _,x in Gu.degree()],float)
pre['datasets']['Les_Miserables']={
 'diagnostics':{'n_nodes':n,'n_edges':m,'components':c,'cycle_rank':int(cycle),'average_clustering':float(clust),
                'degree_mean':float(deg.mean()),'degree_max':int(deg.max()),'weighted_input':True},
 'mechanism_target':'recover held-out relations in a one-mode undirected relation network',
 'decision':'RELATION_NATIVE_KERNEL',
 'prediction':'Because the observed graph has substantial path/cycle redundancy, path- or neighborhood-native scores (3-hop/Adamic-Adar/SVD) should outperform a simple degree/prevalence baseline; no state-mixing kernel is required.',
 'no_op_allowed':True
}

s=json.dumps(pre,ensure_ascii=False,indent=2,sort_keys=True)
open(OUT,'w',encoding='utf-8').write(s)
h=hashlib.sha256(s.encode()).hexdigest()
open(RESULTS_DIR/'blind_precommit.sha256','w').write(h+'  blind_precommit.json\n')
print(s)
print('SHA256',h)
