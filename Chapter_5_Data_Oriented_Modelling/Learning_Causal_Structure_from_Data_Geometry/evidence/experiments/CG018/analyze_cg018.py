from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parent;OLD=R.parent/'cg017'
if (R/'reference_cg017').exists():OLD=R/'reference_cg017'
F=R/'figures';F.mkdir(exist_ok=True)
old=pd.read_csv(OLD/'results.csv');new=pd.read_csv(R/'results.csv');assert len(new)==36
allr=pd.concat([old,new],ignore_index=True);s=allr.groupby(['task','mode']).mean(numeric_only=True);s.to_csv(R/'combined_summary.csv')
order=['direct','blank','continuous','structured','mechanism_blank','mechanism_feedback']
names=['Direct','Blank','Continuous','Numeric candidates','Mechanism blank','Mechanism feedback']
cols=['#9ba5b2','#596d81','#4c94ae','#bd7b3d','#53836c','#945d88']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.dpi':200})
fig,axes=plt.subplots(1,2,figsize=(10,4.5))
for ax,task in zip(axes,['synthetic','real']):
 for k,mode in enumerate(order):
  vals=allr[(allr.task==task)&(allr['mode']==mode)].groupby('seed').loss.mean().values
  ax.barh(k,vals.mean(),color=cols[k]);ax.scatter(vals,k+np.linspace(-.10,.10,len(vals)),c='black',s=15,zorder=3)
 ax.set_yticks(range(6),names if task=='synthetic' else ['']*6);ax.invert_yaxis();ax.set_xlabel('Mixture NLL' if task=='synthetic' else 'Target-mean standardized MSE');ax.set_title('A  Causal worlds' if task=='synthetic' else 'B  Sachs completion',loc='left')
fig.tight_layout();fig.savefig(F/'fig57_mechanism_results.png');plt.close(fig)
fold=allr[allr.task=='real'].pivot_table(index='fold',columns='mode',values='loss');fold.to_csv(R/'real_target_summary.csv')
aq=pd.read_csv(R/'all_query_results.csv');aq.groupby('mode').mean(numeric_only=True).to_csv(R/'all_query_summary.csv')

a=np.load(R/'synthetic_data.npz');ix=a['split']==2;support=a['support'][ix];trueB=a['true_B'][ix];truth=a['all_query_truth'][ix];query=a['query'][ix];worlds=a['worlds'][ix]
def nll(p,y):
 logits=p[:,9:];logits=logits-logits.max(1,keepdims=True);lp=logits-np.log(np.exp(logits).sum(1,keepdims=True));ld=-.5*((p[:,:9].reshape(-1,3,3)-y[:,None,:])/.15)**2
 ll=lp+ld.sum(-1)-3*np.log(.15*np.sqrt(2*np.pi));m=ll.max(1);return -(m+np.log(np.exp(ll-m[:,None]).sum(1))).mean()
coverage=[];trajectory=[]
for mode in ['mechanism_blank','mechanism_feedback']:
 for seed in [11,22,33]:
  tr=np.load(R/'predictions'/f'synthetic_worlds_{mode}_{seed}_full_trace.npz')
  for step in range(5):trajectory.append({'mode':mode,'seed':seed,'step':step,'nll':nll(tr['step_prediction'][:,step],a['y'][ix])})
  # Observation-only inputs duplicated across the three worlds; select first once per group.
  for start in range(0,len(query),6):
   pred=tr['simulations'][start,-1];gold=truth[start:start+6:2]
   dist=np.sqrt(((pred[:,None,:,:]-gold[None,:,:,:])**2).mean((2,3)))
   w=tr['weights'][start,-1];hit=((dist<=.20)&(w[:,None]>=.10)).any(0).mean()
   bd=np.sqrt(((tr['B'][start,-1,:,None]-trueB[start:start+6:2][None])**2).mean((2,3)))
   ri,ci=linear_sum_assignment(bd)
   coverage.append({'mode':mode,'seed':seed,'group':int(a['group'][ix][start]),'joint_world_coverage':float(hit),'assigned_relation_rmse':float(bd[ri,ci].mean())})
pd.DataFrame(coverage).to_csv(R/'joint_world_coverage.csv',index=False)
t=pd.DataFrame(trajectory);t.to_csv(R/'trajectory_summary.csv',index=False)
cv=pd.DataFrame(coverage).groupby('mode').mean(numeric_only=True)

fig,axes=plt.subplots(1,2,figsize=(10,3.7))
for mode,label,col in zip(['mechanism_blank','mechanism_feedback'],names[-2:],cols[-2:]):
 tt=t[t['mode']==mode].groupby('step').nll.mean();axes[0].plot(tt.index,tt.values,'o-',label=label,color=col)
axes[0].set_xticks(range(5));axes[0].set_xlabel('Recurrent updates completed');axes[0].set_ylabel('Test NLL');axes[0].set_title('A  Generated mechanisms across steps',loc='left',fontsize=10);axes[0].legend(fontsize=8)
v=aq.groupby('mode').loss.mean().reindex(order)
axes[1].barh(np.arange(6),v,color=cols);axes[1].set_yticks(range(6),names);axes[1].invert_yaxis();axes[1].set_xlabel('Mean NLL across all three do-queries');axes[1].set_title('B  Expanded query evaluation',loc='left',fontsize=10)
fig.tight_layout();fig.savefig(F/'fig58_world_queries.png');plt.close(fig)

div=((worlds[:,:,None,:]-worlds[:,None,:,:])**2).sum(-1).max((1,2));case=int(np.argmax(np.where(support==0,div,-1)));start=case//6*6
tr=np.load(R/'predictions'/'synthetic_worlds_mechanism_feedback_11_full_trace.npz');pred=tr['B'][case,-1];gold=trueB[start:start+6:2];cost=np.sqrt(((pred[:,None]-gold[None])**2).mean((2,3)));rr,cc=linear_sum_assignment(cost);perm=rr[np.argsort(cc)]
fig,axes=plt.subplots(2,3,figsize=(9,5.2))
for j in range(3):
 for row,B in enumerate([gold[j],pred[perm[j]]]):
  ax=axes[row,j];im=ax.imshow(B,vmin=-1,vmax=1,cmap='RdBu_r');ax.set_xticks(range(3));ax.set_yticks(range(3));ax.set_xlabel('Source variable');ax.set_ylabel('Response variable')
  for u in range(3):
   for v in range(3):ax.text(v,u,f'{B[u,v]:.2f}',ha='center',va='center',fontsize=9,color='white' if abs(B[u,v])>.55 else 'black')
  ax.set_title(f'True world {j+1}' if row==0 else f'Generated candidate; w={tr["weights"][case,-1,perm[j]]:.2f}',fontsize=10)
fig.suptitle('Same observational covariance, several generated relation systems',fontsize=12);fig.tight_layout();fig.savefig(F/'fig59_candidate_relations.png');plt.close(fig)
caseinfo={'test_index':case,'group':int(a['group'][ix][case]),'selection':'maximum true consequence separation, observation-only cases; seed11 fixed','true_relations':gold.tolist(),'generated_relations_matched':pred[perm].tolist(),'generated_weights_matched':tr['weights'][case,-1,perm].tolist(),'joint_effect_rms_matched':np.sqrt(((tr['simulations'][case,-1,perm]-truth[start:start+6:2])**2).mean((1,2))).tolist()}
(R/'illustrative_case.json').write_text(json.dumps(caseinfo,indent=2))

c=pd.read_csv(R/'mechanism_edits.csv');assert len(c)==72;c['loss_change']=c.loss-c.base_loss
assert c[c.condition=='noop'].prediction_rms.max()==0
cs=c.groupby(['task','condition']).mean(numeric_only=True);cs.to_csv(R/'mechanism_edit_summary.csv')
fig,axes=plt.subplots(1,2,figsize=(10,3.7))
for ax,task in zip(axes,['synthetic','real']):
 conds=['cut','zero_effect','edge_flip'];vals=[cs.loc[(task,k),'loss_change'] for k in conds]
 ax.bar(range(3),vals,color=['#596d81','#4c94ae','#945d88']);ax.axhline(0,color='black',lw=.7);ax.set_xticks(range(3),['Cut feedback','Zero simulated\nconsequences','Flip one edge']);ax.set_ylabel('Change in NLL' if task=='synthetic' else 'Change in MSE');ax.set_title('A  Causal worlds' if task=='synthetic' else 'B  Sachs completion',loc='left')
fig.tight_layout();fig.savefig(F/'fig60_mechanism_edits.png');plt.close(fig)

fig,ax=plt.subplots(figsize=(9,3.5))
for mode,label,col in [('structured','Numeric candidates',cols[3]),('mechanism_blank',names[4],cols[4]),('mechanism_feedback',names[5],cols[5])]:ax.plot(range(5),fold[mode],'o-',label=label,color=col)
ax.set_xticks(range(5),[v.upper() for v in fold.index]);ax.set_ylabel('Standardized MSE');ax.set_title('Learned local equations across held-out Sachs environments',loc='left');ax.legend(fontsize=9)
fig.tight_layout();fig.savefig(F/'fig62_real_mechanisms.png');plt.close(fig)

edit_rows=[]
for path in (R/'predictions').glob('*mechanism_feedback*_trace.npz'):
 if 'full_trace' in path.name:continue
 z=np.load(path);task=path.name.split('_')[0];p=z['step_prediction'];q=z['edge_flip_step_prediction']
 def mean_prediction(pp):
  ww=np.exp(pp[...,9:]-pp[...,9:].max(-1,keepdims=True));ww/=ww.sum(-1,keepdims=True)
  return (pp[...,:9].reshape(*pp.shape[:-1],3,3)*ww[...,None]).sum(-2)
 delta=mean_prediction(q)-mean_prediction(p) if task=='synthetic' else q-p
 for step in range(5):
  dd=delta[:,step]
  if task=='synthetic':v=np.sqrt(np.mean(dd*dd))
  else:
   mm=np.tile(np.load(R/'mask_bank.npy'),(4,1));v=np.sqrt((dd*dd*(1-mm)).sum()/(1-mm).sum())
  edit_rows.append({'task':task,'run':path.stem,'step':step,'prediction_rms':float(v)})
ed=pd.DataFrame(edit_rows);ed.to_csv(R/'edge_edit_trajectory.csv',index=False)
fig,ax=plt.subplots(figsize=(8,3.4))
for task,col,label in [('synthetic',cols[4],'Causal worlds'),('real',cols[5],'Sachs')]:
 tt=ed[ed.task==task].groupby('step').prediction_rms.mean();ax.plot(tt.index,tt.values,'o-',color=col,label=label)
ax.set_xticks(range(5));ax.set_xlabel('Stage (edge edited at stage 1)');ax.set_ylabel('Prediction RMS displacement');ax.legend();ax.set_title('A temporary relation edit through subsequent computation',loc='left')
fig.tight_layout();fig.savefig(F/'fig61_edge_edit_trajectory.png');plt.close(fig)

facts={'new_fits':len(new),'internal_interventions':len(c),'joint_coverage':cv.joint_world_coverage.to_dict(),'relation_rmse':cv.assigned_relation_rmse.to_dict(),'all_query_nll':aq.groupby('mode').loss.mean().to_dict(),'new_synthetic_nll':s.loc['synthetic','loss'].to_dict(),'new_real_mse':s.loc['real','loss'].to_dict(),'edited_next_relation_rms':cs.next_B_rms.to_dict()}
facts['edited_next_relation_rms']={str(k):v for k,v in facts['edited_next_relation_rms'].items()}
(R/'key_findings.json').write_text(json.dumps(facts,indent=2));print(json.dumps(facts,indent=2))
