from pathlib import Path
import numpy as np,pandas as pd,json,math,hashlib
import matplotlib.pyplot as plt
ROOT=Path('/mnt/data/cg021_work/CAUSAL_GEOMETRY_021')
z=np.load(ROOT/'synthetic_data.npz'); ix=z['split']==2; y=z['y'][ix]; groups=z['group'][ix]; support=z['support'][ix]
res=pd.read_csv(ROOT/'results.csv');dyn=pd.read_csv(ROOT/'state_dynamics.csv');pulse=pd.read_csv(ROOT/'pulse_evidence.csv')
SIG=.15

def nll_inst(pred,K):
 m=pred[:,:K*3].reshape(-1,K,3);lg=pred[:,K*3:];lg=lg-lg.max(1,keepdims=True);w=np.exp(lg);w/=w.sum(1,keepdims=True)
 ld=-.5*np.square((m-y[:,None,:])/SIG).sum(-1)-3*np.log(SIG*np.sqrt(2*np.pi))
 a=np.log(np.clip(w,1e-12,1))+ld; mx=a.max(1);return -(mx+np.log(np.exp(a-mx[:,None]).sum(1)))
# group-level paired pool8 vs pool3, averaging seeds
rec=[]
for seed in [11,22]:
 vals={}
 for K in [3,8]:
  p=np.load(ROOT/'predictions'/f'pool{K}_{seed}.npz')['prediction']; n=nll_inst(p,K)
  vals[K]=pd.DataFrame({'group':groups,'nll':n}).groupby('group').nll.mean()
 for g in vals[3].index:rec.append({'seed':seed,'group':g,'improvement_pool8_vs_pool3':vals[3][g]-vals[8][g]})
gc=pd.DataFrame(rec).groupby('group').improvement_pool8_vs_pool3.mean().reset_index()
rng=np.random.default_rng(2121);arr=gc.improvement_pool8_vs_pool3.to_numpy();boots=np.array([rng.choice(arr,len(arr),replace=True).mean() for _ in range(10000)])
summary={'pool8_vs_pool3_group_mean_nll_improvement':float(arr.mean()),'pool8_vs_pool3_group_95ci':[float(np.quantile(boots,.025)),float(np.quantile(boots,.975))],'pool8_group_improved_rate':float((arr>0).mean())}
# dynamics aggregate across seeds
agg=dyn.groupby(['variant','support']).mean(numeric_only=True).reset_index();agg.to_csv(ROOT/'dynamics_summary.csv',index=False)
# paired support effect from pulse (normal vs never)
piv=pulse[pulse['mode'].isin(['never','normal','pulse'])].pivot_table(index=['variant','seed'],columns='mode',values=['support_single_query_nll','support_allq_nll'])
rows=[]
for (v,s),r in piv.iterrows():
 rows.append({'variant':v,'seed':s,'query_improvement_normal_vs_never':r[('support_single_query_nll','never')]-r[('support_single_query_nll','normal')],'allq_improvement_normal_vs_never':r[('support_allq_nll','never')]-r[('support_allq_nll','normal')],'query_improvement_pulse_vs_never':r[('support_single_query_nll','never')]-r[('support_single_query_nll','pulse')]})
sup=pd.DataFrame(rows);sup.to_csv(ROOT/'support_effect_summary.csv',index=False)
mem=pulse[pulse['mode']=='memory_summary'].copy();mem.to_csv(ROOT/'pulse_memory_summary.csv',index=False)
# wrong evidence summary
wr=pd.read_csv(ROOT/'wrong_support.csv');ws=wr.groupby(['variant','seed']).agg(donor_preferred_rate=('donor_preferred','mean'),prediction_rms_shift=('prediction_rms_shift','mean'),own_minus_donor_nll=('own_nll_under_wrong_support',lambda x:0)).reset_index()
# overwrite last field explicitly
for i,row in ws.iterrows():
 q=wr[(wr.variant==row.variant)&(wr.seed==row.seed)];ws.loc[i,'own_minus_donor_nll']=(q.own_nll_under_wrong_support-q.donor_nll_under_wrong_support).mean()
ws.to_csv(ROOT/'wrong_support_summary.csv',index=False)
# overall table
ov=res.groupby('variant').agg(mean_nll=('test_nll','mean'),mean_mse=('test_mse','mean'),parameters=('parameters','first')).reset_index();ov.to_csv(ROOT/'summary.csv',index=False)
summary.update({r.variant:{'mean_nll':float(r.mean_nll),'mean_mse':float(r.mean_mse),'parameters':int(r.parameters)} for r in ov.itertuples()})
# key dynamics
for v in ['pool3','pool8']:
 a=agg[(agg.variant==v)&(agg.support==0)].iloc[0];b=agg[(agg.variant==v)&(agg.support==1)].iloc[0]
 summary[v].update({'effective_worlds_pre':float(b.effective_worlds_pre),'effective_worlds_final_support':float(b.effective_worlds_final),'B_update_no_support':float(a.B_update_rms),'B_update_support':float(b.B_update_rms),'weight_TV_no_support':float(a.weight_TV),'weight_TV_support':float(b.weight_TV),'top_slot_change_support':float(b.top_slot_changed)})
 q=sup[sup.variant==v];summary[v].update({'support_query_improvement':float(q.query_improvement_normal_vs_never.mean()),'support_allq_improvement':float(q.allq_improvement_normal_vs_never.mean()),'pulse_query_improvement':float(q.query_improvement_pulse_vs_never.mean())})
 mm=mem[mem.variant==v];summary[v].update({'pulse_B_retained_fraction':float(mm.retained_B_fraction.mean()),'pulse_prediction_shift_vs_never':float(mm.prediction_shift_pulse_vs_never.mean())})
 q=ws[ws.variant==v];summary[v].update({'wrong_support_donor_preferred_rate':float(q.donor_preferred_rate.mean()),'wrong_support_shift':float(q.prediction_rms_shift.mean()),'wrong_support_own_minus_donor_nll':float(q.own_minus_donor_nll.mean())})
(ROOT/'key_findings.json').write_text(json.dumps(summary,indent=2))
# Figures
fig,ax=plt.subplots(figsize=(7.2,4.2));xs=np.arange(2)
means=[ov.loc[ov.variant=='pool3','mean_nll'].iloc[0],ov.loc[ov.variant=='pool8','mean_nll'].iloc[0]];ax.bar(xs,means)
for j,v in enumerate(['pool3','pool8']):
 q=res[res.variant==v];ax.scatter(np.full(len(q),j),q.test_nll,zorder=3)
ax.set_xticks(xs,['3-candidate pool','8-candidate pool']);ax.set_ylabel('Test mixture NLL (lower is better)');ax.set_title('CG-021: Overcomplete unpruned hypothesis pool');fig.tight_layout();fig.savefig(ROOT/'figures/fig71_open_pool_nll.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.4));labels=['pool3\nno support','pool3\nsupport','pool8\nno support','pool8\nsupport'];vals=[];wt=[]
for v in ['pool3','pool8']:
 for s in [0,1]:
  q=agg[(agg.variant==v)&(agg.support==s)].iloc[0];vals.append(q.B_update_rms);wt.append(q.weight_TV)
x=np.arange(4);w=.36;ax.bar(x-w/2,vals,w,label='Relation-state RMS update');ax.bar(x+w/2,wt,w,label='Weight TV change');ax.set_xticks(x,labels);ax.set_ylabel('State change');ax.set_title('New evidence changes world content more than mixture mass');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig72_evidence_rewrite_vs_weight.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.2));pre=[];post=[]
for v in ['pool3','pool8']:
 q=agg[(agg.variant==v)&(agg.support==1)].iloc[0];pre.append(q.effective_worlds_pre);post.append(q.effective_worlds_final)
x=np.arange(2);ax.bar(x-.18,pre,.36,label='Before support reveal');ax.bar(x+.18,post,.36,label='After support reveal');ax.set_xticks(x,['pool3','pool8']);ax.set_ylabel('Effective number of candidates exp(H)');ax.set_title('No pruning rule: the pool does not collapse to a winner');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig73_effective_worlds.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.4));qmeans=[];ameans=[]
for v in ['pool3','pool8']:
 q=sup[sup.variant==v];qmeans.append(q.query_improvement_normal_vs_never.mean());ameans.append(q.allq_improvement_normal_vs_never.mean())
x=np.arange(2);ax.bar(x-.18,qmeans,.36,label='Scored query');ax.bar(x+.18,ameans,.36,label='All 3 queries from same generated worlds');ax.axhline(0,linewidth=1);ax.set_xticks(x,['pool3','pool8']);ax.set_ylabel('NLL improvement from support evidence');ax.set_title('Evidence helps the scored query without guaranteeing a globally better world');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig74_query_vs_world_consistency.png',dpi=180);plt.close(fig)
fig,ax=plt.subplots(figsize=(7.2,4.3));
for v in ['pool3','pool8']:
 q=mem[mem.variant==v];ax.scatter(q.B_imprint_step3,q.B_imprint_step4_after_removal,label=v,s=55)
mx=max(mem.B_imprint_step3.max(),mem.B_imprint_step4_after_removal.max())*1.08;ax.plot([0,mx],[0,mx],linestyle='--',linewidth=1);ax.set_xlabel('World-state imprint immediately after one support pulse');ax.set_ylabel('Imprint one update after support is removed');ax.set_title('A one-step evidence pulse leaves a persistent object-state trace');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig75_pulse_memory.png',dpi=180);plt.close(fig)
print(json.dumps(summary,indent=2))
