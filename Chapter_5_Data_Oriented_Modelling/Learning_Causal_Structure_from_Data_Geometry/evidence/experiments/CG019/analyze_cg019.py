from pathlib import Path
import json, hashlib, shutil
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

R=Path(__file__).resolve().parent; F=R/'figures'; F.mkdir(exist_ok=True)
s=pd.read_csv(R/'summary.csv'); c=pd.read_csv(R/'group_level_controls.csv'); e=pd.read_csv(R/'edge_semantic_summary.csv'); eq=pd.read_csv(R/'edge_delete_query_level.csv'); dq=pd.read_csv(R/'double_do_query_level.csv')

# Figure 63: double-do world solving vs answer superposition, bars = seed means, points = individual seeds.
fig,ax=plt.subplots(figsize=(7.2,4.5))
modes=['mechanism_blank','mechanism_feedback']; labels=['Mechanism Blank','Mechanism Feedback']; methods=['mechanism_solve','single_do_superposition']; mlab=['Relation-system solve','Single-do superposition']
x=np.arange(2); width=.34
for j,meth in enumerate(methods):
    vals=[]
    for mode in modes:
        g=s[(s.test=='double_do')&(s['subset']=='all')&(s['mode']==mode)&(s.method==meth)]
        vals.append(g.nll.mean())
    ax.bar(x+(j-.5)*width,vals,width,label=mlab[j])
    for i,mode in enumerate(modes):
        g=s[(s.test=='double_do')&(s['subset']=='all')&(s['mode']==mode)&(s.method==meth)]
        ax.scatter(np.full(len(g),x[i]+(j-.5)*width),g.nll,zorder=3,s=28)
ax.set_xticks(x,labels); ax.set_ylabel('NLL (lower is better)'); ax.set_title('CG-019: unseen double interventions',loc='left'); ax.legend(frameon=False,loc='upper right')
fig.tight_layout(); fig.savefig(F/'fig63_double_do_world_reuse.png',dpi=180); plt.close(fig)

# Figure 64: semantic edge edit vs wrong/no edit.
fig,ax=plt.subplots(figsize=(7.2,4.5))
methods2=['apply_true_edge_delete','wrong_edge_delete','ignore_edge_delete']; lab2=['Delete requested edge','Delete wrong edge','Ignore deletion']
width=.24
for j,meth in enumerate(methods2):
    vals=[]
    for mode in modes:
        g=s[(s.test=='edge_delete')&(s['subset']=='all')&(s['mode']==mode)&(s.method==meth)]
        vals.append(g.nll.mean())
    ax.bar(x+(j-1)*width,vals,width,label=lab2[j])
    for i,mode in enumerate(modes):
        g=s[(s.test=='edge_delete')&(s['subset']=='all')&(s['mode']==mode)&(s.method==meth)]
        ax.scatter(np.full(len(g),x[i]+(j-1)*width),g.nll,zorder=3,s=26)
ax.set_xticks(x,labels); ax.set_ylabel('NLL (lower is better)'); ax.set_title('CG-019: the requested relation coordinate matters',loc='left'); ax.legend(frameon=False,fontsize=8,loc='lower right')
fig.tight_layout(); fig.savefig(F/'fig64_edge_delete_semantics.png',dpi=180); plt.close(fig)

# Figure 65: true vs predicted effect of deleting requested edge, average prediction across 3 seeds within each architecture for each query key.
sem=eq[eq.method=='apply_true_edge_delete'].copy()
keys=['mode','group','case','support','edge_index','response','source','true_edge','true_delta_response']
avg=sem.groupby(keys,as_index=False).pred_delta_response.mean()
fig,ax=plt.subplots(figsize=(7.0,5.2))
for mode,label in zip(modes,labels):
    g=avg[avg['mode']==mode]
    ax.scatter(g.true_delta_response,g.pred_delta_response,s=8,alpha=.25,label=label)
lo=min(avg.true_delta_response.min(),avg.pred_delta_response.min()); hi=max(avg.true_delta_response.max(),avg.pred_delta_response.max())
ax.plot([lo,hi],[lo,hi],lw=1)
ax.axhline(0,lw=.7); ax.axvline(0,lw=.7)
ax.set_xlabel('True change after deleting the edge'); ax.set_ylabel('Predicted change from editing generated relation'); ax.set_title('CG-019: edge edits carry semantic displacement',loc='left'); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(F/'fig65_edge_edit_delta.png',dpi=180); plt.close(fig)

# Compact machine-readable findings.
double=s[(s.test=='double_do')&(s['subset']=='all')].groupby(['mode','method'])[['nll','mse','coverage']].mean().reset_index()
edge=s[(s.test=='edge_delete')&(s['subset']=='all')].groupby(['mode','method'])[['nll','mse','coverage']].mean().reset_index()
sem_mean=e.groupby('mode')[['delta_corr','delta_sign_accuracy','delta_mse']].mean().reset_index()
facts={'double_do':double.to_dict('records'),'edge_delete':edge.to_dict('records'),'edge_semantics':sem_mean.to_dict('records'),'group_controls':c.to_dict('records')}
(R/'key_findings.json').write_text(json.dumps(facts,indent=2,ensure_ascii=False))
print(json.dumps(facts,indent=2,ensure_ascii=False))
