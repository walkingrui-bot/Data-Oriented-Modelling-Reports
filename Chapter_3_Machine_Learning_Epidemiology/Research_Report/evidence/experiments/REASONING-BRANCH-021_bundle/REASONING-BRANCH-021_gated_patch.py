import importlib.util, numpy as np, pandas as pd, math
from pathlib import Path
spec=importlib.util.spec_from_file_location('r21','/mnt/data/REASONING-BRANCH-021.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
OUT=Path('/mnt/data')
Z=m.Z; STATES=m.STATES; SID=m.SID; train_idx=m.train_idx; test_idx=m.test_idx; K=m.K

def fit_aff(train_ids,test_ids,a):
    if len(train_ids)==0 or len(test_ids)==0: return np.nan,len(train_ids),len(test_ids)
    yt=np.array([SID[m.step(STATES[i],a)] for i in train_ids]); yv=np.array([SID[m.step(STATES[i],a)] for i in test_ids])
    Xtr=Z[train_ids]; Ytr=Z[yt]; Xte=Z[test_ids]; Yte=Z[yv]
    Phi=np.c_[Xtr,np.ones(len(Xtr))]; Phite=np.c_[Xte,np.ones(len(Xte))]
    lam=1e-3; R=np.eye(K+1)*lam; R[-1,-1]*=.1
    C=np.linalg.solve(Phi.T@Phi+R,Phi.T@Ytr); P=Phite@C
    return float(np.mean(np.sum((P-Yte)**2,axis=1))),len(train_ids),len(test_ids)

def compare_gate(z):
    g,x,b,c=z
    if b==m.UNSET: return 'no_branch'
    cc=m.compare_code(g,x,b)
    return {m.CMP_BRANCH_BETTER:'branch_better',m.CMP_TIE:'tie',m.CMP_MAIN_BETTER:'main_better'}[cc]

def correct_gate(z):
    g,x,b,c=z
    if b==m.UNSET: return 'no_branch'
    return {m.CMP_UNSET:'cmp_unset',m.CMP_BRANCH_BETTER:'branch_better',m.CMP_TIE:'tie',m.CMP_MAIN_BETTER:'main_better'}[c]

rows=[]
for a,gf in [('COMPARE',compare_gate),('CORRECT',correct_gate)]:
    groups=sorted(set(gf(z) for z in STATES))
    total_sse=0; ntest=0
    for gg in groups:
        tr=np.array([i for i in train_idx if gf(STATES[i])==gg]); te=np.array([i for i in test_idx if gf(STATES[i])==gg])
        mse,ntr,nte=fit_aff(tr,te,a)
        rows.append(dict(action=a,gate=gg,n_train=ntr,n_test=nte,gated_affine_mse=mse))
        if not np.isnan(mse): total_sse += mse*nte; ntest += nte
    rows.append(dict(action=a,gate='__weighted_total__',n_train=sum(1 for i in train_idx),n_test=ntest,gated_affine_mse=total_sse/ntest))
df=pd.DataFrame(rows); df.to_csv(OUT/'REASONING-BRANCH-021_gated_operator.csv',index=False)
print(df.to_string(index=False))
