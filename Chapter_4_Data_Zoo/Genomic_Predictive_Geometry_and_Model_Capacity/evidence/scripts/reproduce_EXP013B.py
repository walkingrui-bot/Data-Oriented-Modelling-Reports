from pathlib import Path
import json, math, zipfile, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr

# Provider genotypes must be acquired separately; no observations are embedded.
import argparse, hashlib
ap=argparse.ArgumentParser()
ap.add_argument('--genotype-csv',required=True,help='Fixed 50-by-38 panel, sample column first, original row and feature order')
ap.add_argument('--out',default='EXP013B_reproduced')
args=ap.parse_args()
OUT=Path(args.out); OUT.mkdir(parents=True,exist_ok=True)
matrix=pd.read_csv(args.genotype_csv)
if matrix.shape != (50,39): raise ValueError('Expected 50 rows, one sample-ID column, and 38 SNP columns')
SAMPLES=matrix.iloc[:,0].astype(str).tolist()
D=matrix.iloc[:,1:].to_numpy(float)
P=np.array([int(c.split(':')[-1]) for c in matrix.columns[1:]],dtype=int)
if hashlib.sha256(np.asarray(D,dtype='<f8').tobytes()).hexdigest() != '3c97655a451e4a6d8000969dab185ea7bd0d00f2ccb88fbbdd115e99ec2aa74f':
    raise ValueError('Genotype matrix values/order differ from the archived fixed panel')
# Two deterministic non-overlapping target grids, fixed before resampling analysis.
TARGETS={0:np.array([0,4,8,12,16,20,24,28,32]),1:np.array([2,6,10,14,18,22,26,30,34])}

# Archive exact fixed matrix used here.
dfmat=pd.DataFrame(D,columns=[f'chr21:{p}' for p in P]); dfmat.insert(0,'sample',SAMPLES)
dfmat.to_csv(OUT/'EXP013B_fixed38_genotype_matrix.csv',index=False)
pd.DataFrame([{'target_grid':g,'target_panel_indices':';'.join(map(str,idx)),'target_positions':';'.join(map(str,P[idx]))} for g,idx in TARGETS.items()]).to_csv(OUT/'EXP013B_target_grids.csv',index=False)

EPS=1e-12
def standardize(Atr,Aho):
    mu=Atr.mean(0); sd=Atr.std(0); sd=np.where(sd<1e-8,1.0,sd)
    return (Atr-mu)/sd,(Aho-mu)/sd

def task(train_idx,hold_idx,tidx,outer,grid,K=30,B=200):
    inp=np.setdiff1d(np.arange(D.shape[1]),tidx)
    Xtr,Xho=standardize(D[train_idx][:,inp],D[hold_idx][:,inp])
    Ytr,Yho=standardize(D[train_idx][:,tidx],D[hold_idx][:,tidx])
    n=len(train_idx); nh=len(hold_idx); q=len(tidx)
    Ctr=Xtr.T@Ytr/n; Cho=Xho.T@Yho/nh
    _,s,Vt=np.linalg.svd(Ctr,full_matrices=False); V=Vt.T
    Avec=np.stack([Ctr@V[:,k] for k in range(q)])
    Hvec=np.stack([Cho@V[:,k] for k in range(q)])
    pa=np.sum(Avec*Avec,axis=1); ph=np.sum(Hvec*Hvec,axis=1); cross=np.sum(Avec*Hvec,axis=1)
    hold_rel=np.clip(2*cross/(pa+ph+EPS),0,1)

    # Split-half noise measured along the same full-training directions.
    rng=np.random.default_rng(510000+outer*100+grid)
    rels=[]; pns=[]
    for j in range(K):
        perm=rng.permutation(n); a=perm[:n//2]; b=perm[n//2:]
        CA=Xtr[a].T@Ytr[a]/len(a); CB=Xtr[b].T@Ytr[b]/len(b)
        N=(CA-CB)/2
        pn=np.array([np.sum((N@V[:,k])**2) for k in range(q)])
        rel=np.clip(1-pn/(pa+EPS),0,1)
        rels.append(rel); pns.append(pn)
    rels=np.asarray(rels); pns=np.asarray(pns)
    split_one=rels[0]; split_mean=rels.mean(0); split_median=np.median(rels,axis=0)
    mean_pn=pns.mean(0); deb_power=np.maximum(pa-mean_pn,0)
    split_power_rel=np.clip(deb_power/(pa+EPS),0,1)

    # Whole-training bootstrap: every replicate uses n=30 rather than n/2=15.
    rng=np.random.default_rng(710000+outer*100+grid)
    Z=np.empty((B,q,Xtr.shape[1]))
    for b in range(B):
        ids=rng.integers(0,n,size=n)
        Cb=Xtr[ids].T@Ytr[ids]/n
        Z[b]=np.stack([Cb@V[:,k] for k in range(q)])
    zbar=Z.mean(0)
    noise=np.mean(np.sum((Z-zbar[None,:,:])**2,axis=2),axis=0)
    signal_obs=np.sum(zbar*zbar,axis=1)
    signal_deb=np.maximum(signal_obs-noise/B,0)
    boot_rel=signal_deb/(signal_deb+noise+EPS)

    def pr(x):
        return float((x.sum()**2)/(np.sum(x*x)+EPS)) if x.sum()>0 else 0.0
    def r90(x):
        if x.sum()<=0:return 0
        z=np.sort(x)[::-1]; return int(np.searchsorted(np.cumsum(z)/z.sum(),0.9)+1)

    directions=[]
    for k in range(q):
        directions.append({'outer_split':outer,'target_grid':grid,'direction':k+1,
                           'train_singular_value':s[k], 'holdout_reliability':hold_rel[k],
                           'split_one':split_one[k],'split_mean':split_mean[k],'split_median':split_median[k],
                           'split_power_rel':split_power_rel[k],'bootstrap':boot_rel[k],
                           'train_power':pa[k],'split_noise_power_mean':mean_pn[k],
                           'bootstrap_signal_power_debiased':signal_deb[k],'bootstrap_noise_power':noise[k]})
    summary={'outer_split':outer,'target_grid':grid,
             'hold_effective':hold_rel.sum(),'hold_stable50':int((hold_rel>=0.5).sum()),
             'split_one_effective':split_one.sum(),'split_mean_effective':split_mean.sum(),
             'split_median_effective':split_median.sum(),'split_power_effective':split_power_rel.sum(),
             'bootstrap_effective':boot_rel.sum(),
             'split_effective_cv':float(rels.sum(1).std(ddof=1)/(rels.sum(1).mean()+EPS)),
             'split_debiased_power_PR':pr(deb_power),'split_debiased_power_r90':r90(deb_power),
             'bootstrap_signal_PR':pr(signal_deb),'bootstrap_signal_r90':r90(signal_deb)}
    return directions,summary

DIR=[]; TASK=[]
for outer in range(128):
    perm=np.random.default_rng(410000+outer).permutation(50)
    tr=perm[:30]; ho=perm[30:]
    for grid,tidx in TARGETS.items():
        d,s=task(tr,ho,tidx,outer,grid)
        DIR.extend(d); TASK.append(s)
DIR=pd.DataFrame(DIR); TASK=pd.DataFrame(TASK)
DIR.to_csv(OUT/'EXP013B_direction_level_results.csv',index=False)
TASK.to_csv(OUT/'EXP013B_task_level_results.csv',index=False)

METHODS=['split_one','split_mean','split_median','split_power_rel','bootstrap']
# Raw estimator quality against truly independent 20-person operator agreement.
raw=[]
for m in METHODS:
    x=DIR[m].to_numpy(); y=DIR.holdout_reliability.to_numpy()
    raw.append({'method':m,'direction_MAE_raw':float(np.mean(np.abs(x-y))),
                'direction_RMSE_raw':float(np.sqrt(np.mean((x-y)**2))),
                'pearson_raw':float(pearsonr(x,y)[0]),'spearman_raw':float(spearmanr(x,y).statistic),
                'stable50_accuracy_raw':float(np.mean((x>=0.5)==(y>=0.5)))})
RAW=pd.DataFrame(raw)

# Grouped leave-one-outer-split-out affine calibration; all 18 directions from the held-out split remain unseen.
cal_rows=[]; coeff_rows=[]
for m in METHODS:
    for outer in sorted(DIR.outer_split.unique()):
        tr=DIR.outer_split!=outer; te=DIR.outer_split==outer
        x=DIR.loc[tr,m].to_numpy(); y=DIR.loc[tr,'holdout_reliability'].to_numpy()
        A=np.c_[np.ones_like(x),x]; coef=np.linalg.lstsq(A,y,rcond=None)[0]
        pred=np.clip(coef[0]+coef[1]*DIR.loc[te,m].to_numpy(),0,1)
        for (_,r),pp in zip(DIR.loc[te].iterrows(),pred):
            cal_rows.append({'method':m,'outer_split':int(r.outer_split),'target_grid':int(r.target_grid),'direction':int(r.direction),
                             'holdout_reliability':float(r.holdout_reliability),'predicted_reliability':float(pp)})
        coeff_rows.append({'method':m,'heldout_outer_split':outer,'intercept':float(coef[0]),'slope':float(coef[1])})
CAL=pd.DataFrame(cal_rows); COEFF=pd.DataFrame(coeff_rows)
CAL.to_csv(OUT/'EXP013B_grouped_LOO_calibrated_directions.csv',index=False)
COEFF.to_csv(OUT/'EXP013B_grouped_LOO_coefficients.csv',index=False)

cal=[]
for m in METHODS:
    z=CAL[CAL.method==m]; y=z.holdout_reliability.to_numpy(); p=z.predicted_reliability.to_numpy()
    pred_count=z.assign(pred=z.predicted_reliability>=0.5).groupby(['outer_split','target_grid']).pred.sum().to_numpy()
    true_count=z.assign(true=z.holdout_reliability>=0.5).groupby(['outer_split','target_grid']).true.sum().to_numpy()
    pred_eff=z.groupby(['outer_split','target_grid']).predicted_reliability.sum().to_numpy()
    true_eff=z.groupby(['outer_split','target_grid']).holdout_reliability.sum().to_numpy()
    cal.append({'method':m,'direction_MAE_calibrated':float(np.mean(np.abs(p-y))),
                'direction_RMSE_calibrated':float(np.sqrt(np.mean((p-y)**2))),
                'pearson_calibrated':float(pearsonr(p,y)[0]),'spearman_calibrated':float(spearmanr(p,y).statistic),
                'stable50_accuracy_calibrated':float(np.mean((p>=0.5)==(y>=0.5))),
                'stable_count_MAE':float(np.mean(np.abs(pred_count-true_count))),
                'stable_count_exact_rate':float(np.mean(pred_count==true_count)),
                'effective_support_MAE':float(np.mean(np.abs(pred_eff-true_eff))),
                'effective_support_RMSE':float(np.sqrt(np.mean((pred_eff-true_eff)**2))),
                'mean_pred_stable_count':float(pred_count.mean()),'mean_true_stable_count':float(true_count.mean()),
                'mean_pred_effective':float(pred_eff.mean()),'mean_true_effective':float(true_eff.mean())})
CALSUM=pd.DataFrame(cal)
MET=RAW.merge(CALSUM,on='method')
MET.to_csv(OUT/'EXP013B_estimator_comparison.csv',index=False)

# Final affine coefficients fit to all direction-level calibration data. These are *not* externally validated;
# they are written only so a future blind experiment can lock them before opening capacity/holdout results.
final=[]
for m in METHODS:
    x=DIR[m].to_numpy(); y=DIR.holdout_reliability.to_numpy(); A=np.c_[np.ones_like(x),x]
    a,b=np.linalg.lstsq(A,y,rcond=None)[0]
    final.append({'method':m,'intercept_all_128':float(a),'slope_all_128':float(b)})
FINAL=pd.DataFrame(final); FINAL.to_csv(OUT/'EXP013B_candidate_locked_calibration_coefficients.csv',index=False)

# Figures.
plot=MET.set_index('method').loc[METHODS]
fig,ax=plt.subplots(figsize=(8.0,4.8))
ax.bar(np.arange(len(METHODS))-0.18,plot['spearman_raw'],width=0.36,label='Raw')
ax.bar(np.arange(len(METHODS))+0.18,plot['spearman_calibrated'],width=0.36,label='Grouped-LOO calibrated')
ax.set_xticks(np.arange(len(METHODS)),['15/15 one split','15/15 mean','15/15 median','power debias','full-n bootstrap'],rotation=20,ha='right')
ax.set_ylabel('Spearman with independent holdout reliability')
ax.set_title('EXP013B: whole-training bootstrap preserves direction ordering best')
ax.legend(); fig.tight_layout(); fig.savefig(OUT/'fig21_exp013b_direction_ordering.png',dpi=180); plt.close(fig)

zb=CAL[CAL.method=='bootstrap']
fig,ax=plt.subplots(figsize=(6.6,5.6))
ax.scatter(zb.predicted_reliability,zb.holdout_reliability,s=10,alpha=0.32)
ax.plot([0,1],[0,1],linestyle='--',linewidth=1)
ax.set_xlim(0,1);ax.set_ylim(0,1)
ax.set_xlabel('Bootstrap reliability after grouped-LOO affine calibration')
ax.set_ylabel('Independent 20-person operator reproducibility')
ax.set_title('EXP013B: calibrated bootstrap vs independent people')
fig.tight_layout(); fig.savefig(OUT/'fig22_exp013b_bootstrap_holdout.png',dpi=180); plt.close(fig)

fig,ax=plt.subplots(figsize=(8.0,4.8))
ax.bar(np.arange(len(METHODS)),plot['stable_count_MAE'])
ax.set_xticks(np.arange(len(METHODS)),['15/15 one split','15/15 mean','15/15 median','power debias','full-n bootstrap'],rotation=20,ha='right')
ax.set_ylabel('MAE in number of holdout-stable directions')
ax.set_title('EXP013B: bootstrap improves the count, but cardinality remains imperfect')
fig.tight_layout(); fig.savefig(OUT/'fig23_exp013b_support_count_mae.png',dpi=180); plt.close(fig)

best=MET.sort_values('direction_MAE_calibrated').iloc[0]
boot=MET[MET.method=='bootstrap'].iloc[0]; split=MET[MET.method=='split_mean'].iloc[0]
summary={
 'experiment':'SMALL-N-RELIABILITY-CALIBRATION-013B',
 'status':'post-hoc raw-operator estimator calibration on one real 50-person 1000 Genomes panel; repeated outer resampling; not external blind validation',
 'source':'bionumpy/bionumpy example_data/thousand_genomes.vcf',
 'source_blob_sha':'5faa223e61eb3b301ebc397eab1df22e4f105f8d',
 'fixed_panel':'38 SNPs archived from EXP012; no SNP reselection in EXP013B',
 'outer_design':'128 deterministic 30-train/20-independent-holdout splits x 2 fixed non-overlapping 9-SNP target grids',
 'direction_evaluations':int(len(DIR)),
 'split_half':'30 random 15/15 partitions per task, all evaluated on full-training singular directions',
 'bootstrap':'200 size-30 resamples per task, all evaluated on full-training singular directions',
 'independent_reproducibility':'clip(2 a·b / (||a||^2+||b||^2),0,1), where a=C_train v_k and b=C_holdout v_k',
 'raw_direction_spearman':{r.method:float(r.spearman_raw) for _,r in MET.iterrows()},
 'grouped_LOO_calibrated_direction_MAE':{r.method:float(r.direction_MAE_calibrated) for _,r in MET.iterrows()},
 'grouped_LOO_calibrated_stable50_accuracy':{r.method:float(r.stable50_accuracy_calibrated) for _,r in MET.iterrows()},
 'grouped_LOO_stable_count_MAE':{r.method:float(r.stable_count_MAE) for _,r in MET.iterrows()},
 'bootstrap_vs_split_mean':{
   'raw_spearman_bootstrap':float(boot.spearman_raw),'raw_spearman_split_mean':float(split.spearman_raw),
   'calibrated_direction_MAE_bootstrap':float(boot.direction_MAE_calibrated),'calibrated_direction_MAE_split_mean':float(split.direction_MAE_calibrated),
   'calibrated_stable50_accuracy_bootstrap':float(boot.stable50_accuracy_calibrated),'calibrated_stable50_accuracy_split_mean':float(split.stable50_accuracy_calibrated),
   'stable_count_MAE_bootstrap':float(boot.stable_count_MAE),'stable_count_MAE_split_mean':float(split.stable_count_MAE)
 },
 'finding':'Using all 30 training individuals in bootstrap resamples preserves the ordering of directions that reproduce in independent people much better than 15/15 split-half estimates. A simple grouped-LOO affine calibration turns that ordering advantage into lower direction-level error and better stable-direction classification/counting. However the number of stable directions remains under-resolved: even the bootstrap count is not an exact capacity estimator.',
 'evidence_boundary':'All calibration and evaluation come from repeated resampling of the same 50-person real panel. The candidate coefficients are therefore calibration artifacts to be locked before a new external blind dataset, not a universal law.',
}
with open(OUT/'EXP013B_summary.json','w') as f: json.dump(summary,f,indent=2)
with open(OUT/'EXP013B_PROTOCOL_AND_RESULTS.md','w') as f:
    f.write('# SMALL-N-RELIABILITY-CALIBRATION-013B\n\n')
    f.write('EXP013B returns to the raw real genotype operator. It uses the exact 50-person BioNumPy/1000 Genomes panel and the 38-SNP panel already archived by EXP012. No synthetic data are used. The original EXP012 blind result is not re-run; this is post-hoc measurement calibration.\n\n')
    f.write('For each of 128 deterministic outer resamples, 30 people form the estimator sample and 20 different people form an independent operator reference. Two fixed non-overlapping 9-SNP target grids are evaluated. The right singular directions are defined from the 30-person operator. The independent target for each direction is the symmetric operator agreement R_hold = clip(2 a·b/(||a||²+||b||²),0,1), with a=C_train v_k and b=C_holdout v_k.\n\n')
    f.write('Estimator comparison: (i) one 15/15 split, (ii) mean of 30 15/15 splits, (iii) median of 30 splits, (iv) power-domain debias using mean split noise power, and (v) 200 whole-training bootstrap resamples of size 30. Affine calibration is evaluated with grouped leave-one-outer-split-out folds, so all 18 directions from the held-out people split are absent while the calibration line is fit.\n\n')
    f.write(json.dumps(summary,indent=2))

print(json.dumps(summary,indent=2))
print('\nEstimator comparison:\n',MET.to_string(index=False))
print('\nFinal candidate coefficients:\n',FINAL.to_string(index=False))
