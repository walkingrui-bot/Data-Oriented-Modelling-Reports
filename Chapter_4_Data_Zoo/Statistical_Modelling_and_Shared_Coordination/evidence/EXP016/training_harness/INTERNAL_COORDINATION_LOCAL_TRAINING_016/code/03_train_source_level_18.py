#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
import numpy as np
import pandas as pd
import torch
from torch import nn
from sklearn.base import clone
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score, average_precision_score, brier_score_loss
from sklearn.model_selection import StratifiedGroupKFold

PASSPORTS=[
("DP-GEN-01","gwas_credible_sets"),("DP-GEN-02","gene_burden"),("DP-GEN-03","eva"),("DP-GEN-04","genomics_england"),("DP-GEN-05","gene2phenotype"),("DP-GEN-06","uniprot_literature"),("DP-GEN-07","uniprot_variants"),("DP-GEN-08","orphanet"),("DP-GEN-09","clingen"),("DP-SOM-01","cancer_gene_census"),("DP-SOM-02","intogen"),("DP-PWY-01","cancer_biomarkers"),("DP-PWY-02","crispr_screen"),("DP-PWY-03","crispr"),("DP-PWY-04","reactome"),("DP-LIT-01","europepmc"),("DP-RNA-01","expression_atlas"),("DP-ANM-01","impc")]

def fnv1a32(s):
    h=2166136261
    for ch in str(s): h=((h^ord(ch))*16777619)&0xffffffff
    return h

def flatten(v):
    if v is None:return []
    if isinstance(v,(list,tuple,np.ndarray)):return list(v)
    try:
        if pd.isna(v):return []
    except Exception:pass
    return [v]

def disease_bridge(d):
    b={}
    for row in d.itertuples(index=False):
        cur=str(getattr(row,"id"));b[cur]=cur
        for f in ["obsoleteTerms","obsoleteXRefs","dbXRefs"]:
            if hasattr(row,f):
                for v in flatten(getattr(row,f)):b[str(v)]=cur
    return b

def build_matrix(cache):
    assoc=pd.read_parquet(cache/"association_by_datasource_direct_26.06.parquet")
    disease=pd.read_parquet(cache/"disease_26.06.parquet")
    term=pd.read_parquet(cache/"terminal_cohort_26278.parquet")
    b=disease_bridge(disease)
    term=term.rename(columns={"ensembl_id":"targetId"}).copy()
    term["diseaseId"]=term["efo_id_norm"].astype(str).map(b).fillna(term["efo_id_norm"].astype(str))
    needed={d for _,d in PASSPORTS}
    assoc=assoc[assoc["aggregationValue"].isin(needed)].copy()
    score=assoc.pivot_table(index=["targetId","diseaseId"],columns="aggregationValue",values="associationScore",aggfunc="max")
    cnt=assoc.pivot_table(index=["targetId","diseaseId"],columns="aggregationValue",values="evidenceCount",aggfunc="sum")
    nov=None
    if "currentNovelty" in assoc:
        nov=assoc.pivot_table(index=["targetId","diseaseId"],columns="aggregationValue",values="currentNovelty",aggfunc="max")
    X=term[["targetId","diseaseId","label"]].merge(score.add_suffix("__score").reset_index(),on=["targetId","diseaseId"],how="left").merge(cnt.add_suffix("__count").reset_index(),on=["targetId","diseaseId"],how="left")
    if nov is not None:X=X.merge(nov.add_suffix("__novelty").reset_index(),on=["targetId","diseaseId"],how="left")
    for _,ds in PASSPORTS:
        for suf in ["__score","__count","__novelty"]:
            c=ds+suf
            if c not in X:X[c]=0.0
        X[ds+"__availability"]=X[ds+"__score"].notna().astype(float)
        X[ds+"__score"]=X[ds+"__score"].fillna(0).clip(0,1)
        X[ds+"__count"]=np.log1p(X[ds+"__count"].fillna(0))
        X[ds+"__novelty"]=pd.to_numeric(X[ds+"__novelty"],errors="coerce").fillna(0)
    X["split"]=X["targetId"].map(lambda x:"train" if fnv1a32(x)%100<70 else ("validation" if fnv1a32(x)%100<85 else "test"))
    return X

class EBScore:
    def fit(self,X,y):
        self.base=(y.sum()+10)/(len(y)+20);return self
    def predict_proba(self,X):
        s=np.clip(X[:,0],0,1);p=np.clip(.7*self.base+.3*s,1e-5,1-1e-5);return np.c_[1-p,p]

def simplex_weight(pred,y,step=.05):
    best=(np.array([0.,1.,0.]),1e9)
    for a in np.arange(0,1+1e-9,step):
      for b in np.arange(0,1-a+1e-9,step):
        w=np.array([a,b,1-a-b]);p=np.clip(pred@w,1e-6,1-1e-6);l=log_loss(y,p,labels=[0,1])
        if l<best[1]:best=(w,l)
    return best[0]

def stat_moe_states(df):
    tr=df[df.split=="train"].reset_index(drop=True);va=df[df.split=="validation"].reset_index(drop=True);te=df[df.split=="test"].reset_index(drop=True)
    sgkf=StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=20261002)
    states={s:np.zeros((len(x),len(PASSPORTS),4),np.float32) for s,x in [("train",tr),("validation",va),("test",te)]}
    for j,(pid,ds) in enumerate(PASSPORTS):
        cols=[ds+"__score",ds+"__count",ds+"__availability"]
        Xtr=tr[cols].to_numpy(float);ytr=tr.label.to_numpy(int)
        experts=[LogisticRegression(max_iter=1000,class_weight=None),HistGradientBoostingClassifier(max_depth=3,max_iter=120,learning_rate=.05),EBScore()]
        oof=np.zeros((len(tr),3))
        for ti,vi in sgkf.split(Xtr,ytr,tr.targetId):
            for e,proto in enumerate(experts):
                model=clone(proto) if hasattr(proto,"get_params") else EBScore()
                model.fit(Xtr[ti],ytr[ti]);oof[vi,e]=model.predict_proba(Xtr[vi])[:,1]
        w=simplex_weight(oof,ytr)
        finals=[]
        for proto in experts:
            model=clone(proto) if hasattr(proto,"get_params") else EBScore();model.fit(Xtr,ytr);finals.append(model)
        for split,frame in [("train",tr),("validation",va),("test",te)]:
            X=frame[cols].to_numpy(float)
            pred=oof@w if split=="train" else np.column_stack([m.predict_proba(X)[:,1] for m in finals])@w
            states[split][:,j,0]=pred
            states[split][:,j,1]=-(pred*np.log(np.clip(pred,1e-6,1))+(1-pred)*np.log(np.clip(1-pred,1e-6,1)))
            states[split][:,j,2]=frame[ds+"__novelty"].to_numpy(float)
            states[split][:,j,3]=frame[ds+"__availability"].to_numpy(float)
    return (tr,va,te),states

class Ganglion(nn.Module):
    def __init__(self,p=18,f=4,d=24):
        super().__init__();self.interfaces=nn.ModuleList([nn.Sequential(nn.Linear(f,d),nn.Tanh()) for _ in range(p)]);self.core=nn.Sequential(nn.Linear(d,d),nn.Tanh());self.out=nn.Linear(d,1)
    def forward(self,x):
        h=torch.stack([m(x[:,i,:]) for i,m in enumerate(self.interfaces)],1);a=x[:,:,3:4];z=(h*a).sum(1)/a.sum(1).clamp_min(1);r=self.core(z);return self.out(r).squeeze(-1)

def fit_model(model,x,y,epochs=250,lr=2e-3):
    device="mps" if torch.backends.mps.is_available() else ("cuda" if torch.cuda.is_available() else "cpu");model.to(device);x=torch.tensor(x,dtype=torch.float32,device=device);y=torch.tensor(y,dtype=torch.float32,device=device);opt=torch.optim.Adam(model.parameters(),lr=lr)
    for _ in range(epochs):
        opt.zero_grad();loss=nn.functional.binary_cross_entropy_with_logits(model(x),y);loss.backward();opt.step()
    return model,device

def pred(model,x,device):
    with torch.no_grad():return torch.sigmoid(model(torch.tensor(x,dtype=torch.float32,device=device))).cpu().numpy()

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--cache-dir",type=Path,default=Path("data/cache"));ap.add_argument("--out-dir",type=Path,default=Path("results/source_level_18"));args=ap.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    df=build_matrix(args.cache_dir);(tr,va,te),st=stat_moe_states(df)
    torch.manual_seed(20261002);m,dev=fit_model(Ganglion(),st["train"],tr.label.to_numpy())
    p=pred(m,st["test"],dev);y=te.label.to_numpy(int)
    metrics={"n_train":len(tr),"n_validation":len(va),"n_test":len(te),"device":dev,"logloss":float(log_loss(y,p,labels=[0,1])),"brier":float(brier_score_loss(y,p)),"auroc":float(roc_auc_score(y,p)),"auprc":float(average_precision_score(y,p))}
    (args.out_dir/"metrics.json").write_text(json.dumps(metrics,indent=2));df.to_parquet(args.out_dir/"joined_18_source_level.parquet",index=False);torch.save(m.state_dict(),args.out_dir/"ganglion.pt");print(json.dumps(metrics,indent=2))
if __name__=="__main__":main()
