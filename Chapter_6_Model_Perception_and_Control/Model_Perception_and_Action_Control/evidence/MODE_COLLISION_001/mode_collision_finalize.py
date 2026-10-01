import json, math, os
from collections import Counter
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
from scipy.spatial.distance import jensenshannon
pairs=json.load(open('mode_collision_pairs.json'))

def ngrams(s,n):
 b=list(s.encode('utf-8'))
 return [tuple(b[i:i+n]) for i in range(len(b)-n+1)]
rows=[]
for n in [1,2,3,4]:
 c0=Counter(); c1=Counter()
 for t,a in pairs:
  c0.update(ngrams(t,n)); c1.update(ngrams(a,n))
 keys=list(set(c0)|set(c1)); p=np.array([c0[k] for k in keys],float); q=np.array([c1[k] for k in keys],float)
 p/=p.sum(); q/=q.sum(); tv=.5*np.abs(p-q).sum(); js=jensenshannon(p,q,base=2.0)**2
 inter=len(set(c0)&set(c1)); union=len(set(c0)|set(c1)); jac=inter/union
 mass_overlap=np.minimum(p,q).sum()
 rows.append(dict(n=n,total_variation=tv,js_divergence_bits=js,support_jaccard=jac,probability_mass_overlap=mass_overlap,unique_text=len(c0),unique_act=len(c1)))
pd.DataFrame(rows).to_csv('MODE_COLLISION_001_tokencode_distribution.csv',index=False)
# pair surface similarity byte edit proxy via LCS-ish normalized prefix? Use SequenceMatcher byte decoded safely.
import difflib
sims=[]
for t,a in pairs:
 sims.append(difflib.SequenceMatcher(None,list(t.encode()),list(a.encode())).ratio())
json.dump({'pair_similarity_mean':float(np.mean(sims)),'median':float(np.median(sims)),'min':float(np.min(sims)),'max':float(np.max(sims))},open('MODE_COLLISION_001_pair_surface_summary.json','w'),indent=2)

# Combine three-seed curves
seed7=pd.read_csv('MODE_COLLISION_001_layerwise_geometry.csv')
seed7_last=seed7[(seed7.stage=='model')&(seed7.trained==True)&(seed7.representation=='decision_last_token')][['layer','linear_probe_acc','fisher_ratio','knn_cross_mix']].copy(); seed7_last['seed']=7; seed7_last.rename(columns={'linear_probe_acc':'probe_acc'},inplace=True)
seed7_mean=seed7[(seed7.stage=='model')&(seed7.trained==True)&(seed7.representation=='sequence_mean')][['layer','linear_probe_acc','fisher_ratio','knn_cross_mix']].copy(); seed7_mean['seed']=7; seed7_mean.rename(columns={'linear_probe_acc':'probe_acc'},inplace=True)
last=[seed7_last]; mean=[seed7_mean]
for seed in [11,19]:
 f=pd.read_csv(f'MODE_COLLISION_001_seed{seed}_geometry.csv')
 last.append(f[f.representation=='last'][['layer','probe_acc','fisher_ratio','knn_cross_mix','seed']])
 mean.append(f[f.representation=='mean'][['layer','probe_acc','fisher_ratio','knn_cross_mix','seed']])
last=pd.concat(last);mean=pd.concat(mean)
last.to_csv('MODE_COLLISION_001_three_seed_decision_geometry.csv',index=False)
mean.to_csv('MODE_COLLISION_001_three_seed_mean_geometry.csv',index=False)
L=last.groupby('layer').agg(probe_mean=('probe_acc','mean'),probe_sd=('probe_acc','std'),fisher_mean=('fisher_ratio','mean'),fisher_sd=('fisher_ratio','std'),mix_mean=('knn_cross_mix','mean'),mix_sd=('knn_cross_mix','std')).reset_index()
M=mean.groupby('layer').agg(probe_mean=('probe_acc','mean'),probe_sd=('probe_acc','std'),fisher_mean=('fisher_ratio','mean'),fisher_sd=('fisher_ratio','std'),mix_mean=('knn_cross_mix','mean'),mix_sd=('knn_cross_mix','std')).reset_index()
L.to_csv('MODE_COLLISION_001_three_seed_decision_summary.csv',index=False);M.to_csv('MODE_COLLISION_001_three_seed_mean_summary.csv',index=False)
# Figure 1: tokencode divergence
D=pd.DataFrame(rows)
fig,ax=plt.subplots(figsize=(7.4,4.6)); ax.plot(D.n,D.total_variation,marker='o',label='Total variation'); ax.plot(D.n,D.js_divergence_bits,marker='o',label='JS divergence (bits)'); ax.plot(D.n,1-D.probability_mass_overlap,marker='o',label='1 - mass overlap'); ax.set_xlabel('Tokencode n-gram order');ax.set_ylabel('Distribution separation');ax.set_xticks([1,2,3,4]);ax.set_title('MODE-COLLISION-001 — Surface tokencode distributions remain overlapping');ax.legend();fig.tight_layout();fig.savefig('mode_collision_001_tokencode_divergence.png',dpi=180);plt.close(fig)
# Figure 2: probe separability across layers
fig,ax=plt.subplots(figsize=(8.2,4.8)); ax.plot(L.layer,L.probe_mean,marker='o',label='Decision state (last token)');ax.fill_between(L.layer,L.probe_mean-L.probe_sd,L.probe_mean+L.probe_sd,alpha=.15);ax.plot(M.layer,M.probe_mean,marker='o',label='Whole-sequence mean');ax.fill_between(M.layer,M.probe_mean-M.probe_sd,M.probe_mean+M.probe_sd,alpha=.15);ax.axhline(.5,linestyle='--',linewidth=1);ax.set_ylim(.45,.8);ax.set_xlabel('Layer (0 = embedding state)');ax.set_ylabel('Held-out linear separability');ax.set_title('MODE-COLLISION-001 — Layerwise mode readability, 3 training seeds');ax.legend();fig.tight_layout();fig.savefig('mode_collision_001_layer_probe.png',dpi=180);plt.close(fig)
# Figure 3: fisher and mix
fig,ax=plt.subplots(figsize=(8.2,4.8));ax.plot(L.layer,L.fisher_mean,marker='o',label='Fisher ratio');ax.set_xlabel('Layer');ax.set_ylabel('Fisher ratio');ax.set_title('MODE-COLLISION-001 — Decision-state geometry sharpens with depth');ax2=ax.twinx();ax2.plot(L.layer,L.mix_mean,marker='s',label='5-NN cross-mode mixing');ax2.set_ylabel('Cross-mode neighbor fraction');lines,labels=ax.get_legend_handles_labels();lines2,labels2=ax2.get_legend_handles_labels();ax.legend(lines+lines2,labels+labels2,loc='best');fig.tight_layout();fig.savefig('mode_collision_001_geometry_curve.png',dpi=180);plt.close(fig)
# Figure 4: dimensional collapse from seed7
q=seed7[(seed7.stage=='model')&(seed7.trained==True)&(seed7.representation=='decision_last_token')].sort_values('layer')
fig,ax=plt.subplots(figsize=(8.2,4.8));ax.plot(q.layer,q.stable_rank,marker='o',label='Decision stable rank');ax.plot(q.layer,q.effective_rank,marker='o',label='Decision effective rank');ax.plot(q.layer,q.token_cloud_stable_rank,marker='o',label='Token-cloud stable rank');ax.set_xlabel('Layer');ax.set_ylabel('Effective dimensionality');ax.set_title('MODE-COLLISION-001 — Layerwise geometric compression');ax.legend();fig.tight_layout();fig.savefig('mode_collision_001_rank_curve.png',dpi=180);plt.close(fig)
# concise overall summary
raw=json.load(open('MODE_COLLISION_001_summary.json'))
out={
 'dataset':'70 real request-for-info / original executable minimal pairs from When2Call MCQ',
 'surface_pair_similarity':json.load(open('MODE_COLLISION_001_pair_surface_summary.json')),
 'tokencode_distribution':rows,
 'surrogate':'8-layer 24D causal Transformer trained only on UTF-8 byte tokencodes; pair-grouped held-out evaluation; 3 seeds for layerwise readability check',
 'seed7_final_train_acc':raw['final_train_acc'],'seed7_final_heldout_acc':raw['final_heldout_acc'],
 'three_seed_decision':L.to_dict('records'),'three_seed_mean':M.to_dict('records'),
 'observations':{
  'surface_absolute_exclusion':False,
  'surface_reason':'all n-gram distributions retain non-zero mass overlap; held-out raw tokencode linear probe is near chance',
  'any_layer_absolute_exclusion':False,
  'best_mean_probe_layer':int(M.loc[M.probe_mean.idxmax(),'layer']),
  'best_mean_probe_acc':float(M.probe_mean.max()),
  'final_mean_probe_acc':float(M.loc[M.layer==M.layer.max(),'probe_mean'].iloc[0]),
  'decision_fisher_trend':'increases with depth on 3-seed mean, but local cross-mode mixing remains near 0.5 rather than collapsing toward 0',
  'interpretation':'controlled surrogate shows learned layerwise reshaping and a mid-layer readability peak for sequence-mean state, but no near-disjoint mode geometry.'
 }
}
json.dump(out,open('MODE_COLLISION_001_complete_summary.json','w'),ensure_ascii=False,indent=2)
print(json.dumps(out,ensure_ascii=False,indent=2)[:16000])
