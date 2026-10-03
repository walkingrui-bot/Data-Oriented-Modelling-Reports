from pathlib import Path
import json, pandas as pd, numpy as np
import matplotlib.pyplot as plt
ROOT=Path('/mnt/data/INTERNAL_COORDINATION_009'); R=ROOT/'results'; F=ROOT/'figures'; F.mkdir(exist_ok=True)
h=pd.read_csv(R/'seed0_training_history.csv'); final=pd.read_csv(R/'final_branch_metrics.csv'); fr=pd.read_csv(R/'freeze_after_200.csv'); st=pd.read_csv(R/'modality_stress.csv'); le=pd.read_csv(R/'ganglion_lesions.csv'); ge=pd.read_csv(R/'ganglion_delta_geometry.csv'); mt=pd.read_csv(R/'seed0_matrix_trajectory.csv')
# 1 mixed metrics trajectory
m=h[h.branch=='mixed'].sort_values('step')
plt.figure(figsize=(7.2,4.2)); plt.plot(m.step,m.num_pinball_both,marker='o'); plt.xlabel('Training step'); plt.ylabel('Numeric pinball loss (both evidence)'); plt.title('Mixed training: numeric distribution score'); plt.tight_layout(); plt.savefig(F/'fig1_numeric_trajectory.png',dpi=180); plt.close()
plt.figure(figsize=(7.2,4.2)); plt.plot(m.step,m.lang_acc_both,marker='o'); plt.xlabel('Training step'); plt.ylabel('Language semantic accuracy (both evidence)'); plt.ylim(0,1); plt.title('Mixed training: language semantic accuracy'); plt.tight_layout(); plt.savefig(F/'fig2_language_trajectory.png',dpi=180); plt.close()
# 2 ganglion dynamics
plt.figure(figsize=(7.2,4.2)); plt.plot(m.step,m.grad_cos_num_lang,marker='o',label='gradient cosine'); plt.plot(m.step,m.paired_cosine_gap,marker='s',label='paired-state cosine gap'); plt.axhline(0,linewidth=.8); plt.xlabel('Training step'); plt.ylabel('Score'); plt.title('Shared ganglion: early common pressure, later modality residuals'); plt.legend(); plt.tight_layout(); plt.savefig(F/'fig3_ganglion_dynamics.png',dpi=180); plt.close()
# 3 singular values of delta M seed0 final branches
end=mt[mt.step==800]
plt.figure(figsize=(7.2,4.2))
for br in ['numeric','language','mixed']:
 row=end[end.branch==br].iloc[0]; vals=[row[f'delta_sv{i}'] for i in range(1,11)]; plt.plot(range(1,11),vals,marker='o',label=br)
plt.xlabel('Singular direction'); plt.ylabel('Singular value of M - M0'); plt.title('Ganglion parameter change spectrum (seed 0)'); plt.legend(); plt.tight_layout(); plt.savefig(F/'fig4_delta_spectrum.png',dpi=180); plt.close()
# 4 lesion medians
ls=le.groupby(['type','k'])[['num_pinball_both','lang_acc_both','paired_cosine_gap']].median().reset_index(); ls.to_csv(R/'lesion_medians.csv',index=False)
plt.figure(figsize=(7.2,4.2))
for typ in ['top_delta','random_matched']:
 q=ls[(ls.type==typ)&(ls.k>0)]; plt.plot(q.k,q.num_pinball_both,marker='o',label=typ)
plt.xlabel('Number of removed / matched directions'); plt.ylabel('Numeric pinball loss'); plt.title('Removing learned ganglion directions vs matched random perturbation'); plt.legend(); plt.tight_layout(); plt.savefig(F/'fig5_lesion_numeric.png',dpi=180); plt.close()
plt.figure(figsize=(7.2,4.2))
for typ in ['top_delta','random_matched']:
 q=ls[(ls.type==typ)&(ls.k>0)]; plt.plot(q.k,q.lang_acc_both,marker='o',label=typ)
plt.xlabel('Number of removed / matched directions'); plt.ylabel('Language semantic accuracy'); plt.ylim(0.6,.9); plt.title('Learned ganglion directions jointly support language'); plt.legend(); plt.tight_layout(); plt.savefig(F/'fig6_lesion_language.png',dpi=180); plt.close()
# summary table
rows=[]
for br in ['numeric','language','mixed']:
 s=final[final.branch==br]
 rows.append({'condition':br,'numeric_self_pinball':float(s.num_pinball_num.median()),'language_self_accuracy':float(s.lang_acc_text.median()),'numeric_from_text_pinball':float(s.num_pinball_text.median()),'language_from_numeric_accuracy':float(s.lang_acc_num.median()),'both_numeric_pinball':float(s.num_pinball_both.median()),'both_language_accuracy':float(s.lang_acc_both.median()),'both_probe_R2':float(s.probe_r2_both.median()),'paired_cosine_gap':float(s.paired_cosine_gap.median())})
pd.DataFrame(rows).to_csv(R/'main_comparison.csv',index=False)
# derived statements JSON
mix=final[final.branch=='mixed']; num=final[final.branch=='numeric']; lang=final[final.branch=='language']
les2top=le[(le.type=='top_delta')&(le.k==2)];les2rand=le[(le.type=='random_matched')&(le.k==2)]
der={
 'numeric_specialist_advantage_pct': float((mix.num_pinball_num.median()/num.num_pinball_num.median()-1)*100),
 'language_specialist_advantage_points': float((lang.lang_acc_text.median()-mix.lang_acc_text.median())*100),
 'cross_num_to_language_acc': float(mix.lang_acc_num.median()),
 'cross_language_to_num_pinball': float(mix.num_pinball_text.median()),
 'mixed_both_num_pinball': float(mix.num_pinball_both.median()),
 'mixed_both_lang_acc': float(mix.lang_acc_both.median()),
 'mixed_both_probe_r2': float(mix.probe_r2_both.median()),
 'freeze_num_pinball': float(fr.num_pinball_both.median()), 'freeze_lang_acc':float(fr.lang_acc_both.median()), 'freeze_probe_r2':float(fr.probe_r2_both.median()),
 'delta_cos_num_lang':float(ge.cos_num_lang.median()), 'delta_cos_mix_num':float(ge.cos_mixed_num.median()), 'delta_cos_mix_lang':float(ge.cos_mixed_lang.median()),
 'lesion2_top_num_pinball':float(les2top.num_pinball_both.median()),'lesion2_random_num_pinball':float(les2rand.num_pinball_both.median()),'lesion2_top_lang_acc':float(les2top.lang_acc_both.median()),'lesion2_random_lang_acc':float(les2rand.lang_acc_both.median())
}
with open(R/'derived_summary.json','w') as f:json.dump(der,f,indent=2)
print(json.dumps(der,indent=2))
