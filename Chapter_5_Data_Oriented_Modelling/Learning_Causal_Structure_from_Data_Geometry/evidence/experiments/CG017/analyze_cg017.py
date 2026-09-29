from pathlib import Path
import json, math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parent
F=R/'figures';F.mkdir(exist_ok=True)
r=pd.read_csv(R/'results.csv');c=pd.read_csv(R/'feedback_interventions.csv')
assert len(r)==72 and len(c)==144
assert not r.duplicated(['task','fold','mode','seed']).any()
assert c[c.condition=='noop'].prediction_rms_shift.max()==0
c['loss_change']=c.loss-c.base_loss
order=['direct','blank','continuous','structured']
labels=['Direct','Blank','Continuous','Structured']
colors=['#8d99ae','#526779','#377b99','#bc6c25']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
summary=r.groupby(['task','mode']).mean(numeric_only=True)
summary.to_csv(R/'summary.csv')
folds=r[r.task=='real'].pivot_table(index='fold',columns='mode',values='loss').reindex(columns=order)
folds.to_csv(R/'real_target_summary.csv')
cs=c.groupby(['task','mode','condition']).mean(numeric_only=True)
cs.to_csv(R/'feedback_summary.csv')

fig,axs=plt.subplots(1,2,figsize=(10,3.4))
for ax,task,title in zip(axs,['synthetic','real'],['A  Intervention consequences in small causal worlds','B  Missing proteins in held-out environments']):
    d=r[r.task==task].groupby(['mode','seed']).loss.mean()
    for k,mode in enumerate(order):
        vv=d.loc[mode].values
        ax.bar(k,vv.mean(),color=colors[k],alpha=.85,width=.65)
        ax.scatter(k+np.linspace(-.10,.10,len(vv)),vv,c='black',s=16,zorder=3)
    ax.set_xticks(range(4),labels,rotation=15);ax.set_title(title,fontsize=10,loc='left')
    ax.set_ylabel('Mixture NLL (lower is better)' if task=='synthetic' else 'Target-mean standardized MSE')
    if task=='synthetic':ax.invert_yaxis()
fig.tight_layout();fig.savefig(F/'fig52_task_results.png');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(10,3.6))
x=np.arange(len(folds))
for mode,color,label in zip(order,colors,labels):axs[0].plot(x,folds[mode],'o-',label=label,color=color)
axs[0].set_xticks(x,[v.upper() for v in folds.index]);axs[0].set_ylabel('Standardized MSE');axs[0].set_title('A  Target-specific performance',loc='left',fontsize=10);axs[0].legend(fontsize=8)
for k,mode in enumerate(['continuous','structured']):
    gain=100*(folds['blank']-folds[mode])/folds['blank']
    axs[1].bar(x+(k-.5)*.32,gain,width=.32,label=mode.title(),color=colors[k+2])
axs[1].axhline(0,color='black',lw=.7);axs[1].set_xticks(x,[v.upper() for v in folds.index]);axs[1].set_ylabel('MSE improvement over Blank (%)');axs[1].set_title('B  Benefit varies by environment',loc='left',fontsize=10);axs[1].legend(fontsize=8)
fig.tight_layout();fig.savefig(F/'fig53_real_targets.png');plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(10,3.5))
for ax,task in zip(axs,['synthetic','real']):
    for k,mode in enumerate(['continuous','structured']):
        vals=[cs.loc[(task,mode,cond),'loss_change'] for cond in ['cut','transplant','rewrite']]
        ax.bar(np.arange(3)+(k-.5)*.3,vals,width=.3,color=colors[k+2],label=mode.title())
    ax.axhline(0,color='black',lw=.7);ax.set_xticks(range(3),['Cut all','Transplant step 2','Rewrite step 2'],rotation=10)
    ax.set_title(('A  Causal worlds' if task=='synthetic' else 'B  Sachs environments'),loc='left');ax.set_ylabel('Change in NLL' if task=='synthetic' else 'Change in MSE');ax.legend(fontsize=8)
fig.tight_layout();fig.savefig(F/'fig54_feedback_edits.png');plt.close(fig)

# Exact existing trajectories, no extra fitting or chosen training runs.
a=np.load(R/'synthetic_data.npz');y=a['y'][a['split']==2];s=a['support'][a['split']==2];worlds=a['worlds'][a['split']==2]
def nll(p,y):
    means=p[:,:9].reshape(-1,3,3); logits=p[:,9:];logits=logits-np.max(logits,axis=1,keepdims=True); lp=logits-np.log(np.exp(logits).sum(1,keepdims=True))
    ld=-.5*((means-y[:,None,:])/.15)**2
    ll=lp+ld.sum(-1)-3*np.log(.15*np.sqrt(2*np.pi));m=ll.max(1)
    return -(m+np.log(np.exp(ll-m[:,None]).sum(1))).mean()
rows=[]
for mode in ['continuous','structured']:
 for seed in [11,22,33]:
    z=np.load(R/'predictions'/f'synthetic_worlds_{mode}_{seed}_trace.npz')
    for cond,key in [('normal','step_output'),('transplant','transplant_step_output'),('rewrite','rewrite_step_output')]:
     for step in range(5):rows.append({'mode':mode,'seed':seed,'condition':cond,'step':step,'nll':nll(z[key][:,step],y)})
traj=pd.DataFrame(rows);traj.to_csv(R/'trajectory_summary.csv',index=False)
fig,axs=plt.subplots(1,2,figsize=(10,3.7))
for mode,color in zip(['continuous','structured'],colors[2:]):
    t=traj[(traj['mode']==mode)&(traj.condition=='normal')].groupby('step').nll.mean()
    axs[0].plot(t.index,t.values,'o-',label=mode.title(),color=color)
axs[0].set_xlabel('Recurrent updates completed');axs[0].set_ylabel('Test NLL from the shared output head');axs[0].set_xticks(range(5));axs[0].set_title('A  Unsupervised intermediate readouts',loc='left',fontsize=10);axs[0].legend(fontsize=8)
# Fixed first maximally ambiguous query: largest separation between known compatible consequences.
div=((worlds[:,:,None,:]-worlds[:,None,:,:])**2).sum(-1).max((1,2))
case=int(np.argmax(np.where(s==0,div,-1)))
z=np.load(R/'predictions'/'synthetic_worlds_structured_11_trace.npz');p=z['prediction'][case];mu=p[:9].reshape(3,3);w=np.exp(p[9:]-p[9:].max());w/=w.sum()
q=a['query'][a['split']==2][case];dims=[j for j in range(3) if j!=q]
ax=axs[1];ww=worlds[case]
ax.scatter(ww[:,dims[0]],ww[:,dims[1]],marker='x',s=90,c='black',lw=2,label='Compatible world effects')
ax.scatter(mu[:,dims[0]],mu[:,dims[1]],s=70+300*w,c=colors[3],alpha=.8,label='Generated candidates')
for j in range(3):ax.annotate(f'w={w[j]:.2f}',(mu[j,dims[0]],mu[j,dims[1]]),xytext=(4,7+j*3),textcoords='offset points',fontsize=8)
ax.set_xlabel(f'Mean effect on variable {dims[0]}');ax.set_ylabel(f'Mean effect on variable {dims[1]}');ax.set_title('B  Same observations, several candidate effects',loc='left',fontsize=10);ax.legend(fontsize=7,loc='best')
fig.tight_layout();fig.savefig(F/'fig55_generated_worlds.png');plt.close(fig)
(R/'illustrative_case.json').write_text(json.dumps({'selection':'largest true effect separation among observation-only test groups; seed11 fixed','test_index':case,'group':int(a['group'][a['split']==2][case]),'query_variable':int(q),'compatible_effects':ww.tolist(),'generated_candidates':mu.tolist(),'generated_weights':w.tolist()},indent=2))

fig,axs=plt.subplots(1,2,figsize=(10,3.5))
for ax,field,title in zip(axs,['input_sensitivity_relative_change','token_participation_ratio'],['A  Input sensitivity after token transplantation','B  Participation ratio of generated tokens']):
    for k,mode in enumerate(['continuous','structured']):
        vals=[summary.loc[(task,mode),field] for task in ['synthetic','real']]
        ax.bar(np.arange(2)+(k-.5)*.3,vals,width=.3,label=mode.title(),color=colors[k+2])
    ax.set_xticks([0,1],['Causal worlds','Sachs']);ax.set_title(title,fontsize=10,loc='left');ax.legend(fontsize=8)
axs[0].set_ylabel('Relative Jacobian change (first 8 cases/run)');axs[1].set_ylabel('Effective covariance dimension')
fig.tight_layout();fig.savefig(F/'fig56_state_geometry.png');plt.close(fig)

realmean=summary.loc['real','loss'];synmean=summary.loc['synthetic','loss']
paired=r[r.task=='synthetic'].pivot(index='seed',columns='mode',values='loss')
facts={'models':len(r),'controls':len(c),'real_structured_vs_blank_relative_improvement':float(1-realmean['structured']/realmean['blank']),'real_continuous_vs_blank_relative_improvement':float(1-realmean['continuous']/realmean['blank']),'synthetic_structured_minus_blank_nll':float(synmean['structured']-synmean['blank']),'synthetic_structured_wins':int((paired.structured<paired.blank).sum()),'real_structured_target_wins':int((folds.structured<folds.blank).sum()),'noop_max_shift':float(c[c.condition=='noop'].prediction_rms_shift.max()),'real_structured_cut_mse':float(cs.loc[('real','structured','cut'),'loss']),'synth_structured_cut_nll':float(cs.loc[('synthetic','structured','cut'),'loss'])}
(R/'key_findings.json').write_text(json.dumps(facts,indent=2))
print(json.dumps(facts,indent=2))
