"""Recalculate publication statistics from packaged evidence; performs no training."""
from pathlib import Path
import ast,json,hashlib,math
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
E=ROOT/'evidence/experiments'
paths=[]
def find(name):
 p=next(E.rglob(name));paths.append(p);return p
src=find('REASONING-BRANCH-021.py')
allowed={'N','UNSET','CMP_UNSET','CMP_BRANCH_BETTER','CMP_TIE','CMP_MAIN_BETTER','REL_BASE','REL_CF','META','ACTIONS'}
tree=ast.parse(src.read_text());nodes=[]
for n in tree.body:
 if isinstance(n,ast.Assign) and all(isinstance(t,ast.Name) and t.id in allowed for t in n.targets):nodes.append(n)
 if isinstance(n,ast.FunctionDef) and n.name in {'rel_apply','cyclic_dist','compare_code','step','run','read','valid_states'}:nodes.append(n)
ns={};exec(compile(ast.Module(body=nodes,type_ignores=[]),str(src),'exec'),ns)
states=ns['valid_states']();idx={x:i for i,x in enumerate(states)};acts=ns['ACTIONS'];T=np.array([[idx[ns['step'](x,a)] for a in acts] for x in states]);out=np.array([ns['read'](x) for x in states])
classes=out.copy();counts=[len(set(classes))]
for _ in range(6):
 sig=[(int(out[i]),*(int(v) for v in classes[T[i]])) for i in range(len(states))];mp={};classes=np.array([mp.setdefault(s,len(mp)) for s in sig]);counts.append(len(mp))
assert counts==[5,65,105,173,258,275,275]
witness=[(1,0,5,3),(1,0,2,3)];program=['R+1','R+2','COMPARE','CORRECT'];outputs=[ns['read'](ns['run'](x,program)) for x in witness];assert outputs==[2,1]
f=pd.read_csv(find('LANGUAGE-HIERARCHICAL-GENERATORS-017_phrases.csv'));w=f.n_test
comp=float(np.average(f.mse_composed,weights=w));direct=float(np.average(f.mse_direct,weights=w))
phrase={'items':len(f),'composed_weighted_mse':comp,'direct_weighted_mse':direct,'pooled_relative_reduction':1-direct/comp,'weighted_mean_item_reduction':float(np.average(1-f.mse_direct/f.mse_composed,weights=w))}
p=pd.read_csv(find('MODEL-SCALE-CORRIDOR-025_geo_models.csv'))
assert len(p)==30 and not p.duplicated(['hidden','coverage','seed']).any()
corr=p[['params','n_train','full_acc','state_d95','median_whitened_crowding','control_geo_stable_rank']].corr(method='spearman')
scale={'models':len(p),'seeds':sorted(map(int,p.seed.unique())),'epoch_range':[int(p.epochs.min()),int(p.epochs.max())], 'within_coverage_width_separation_spearman':{str(c):float(g[['hidden','median_whitened_crowding']].corr(method='spearman').iloc[0,1]) for c,g in p.groupby('coverage')},'size_d95_spearman':float(corr.loc['params','state_d95']),'coverage_accuracy_spearman':float(corr.loc['n_train','full_acc']),'control_stable_rank_range':[float(p.control_geo_stable_rank.min()),float(p.control_geo_stable_rank.max())]}
a=p.groupby(['coverage','hidden']).mean(numeric_only=True);a.to_csv(ROOT/'evidence/editorial/scale_recalculated_means.csv')
for key,cols in [('coverage_width',['coverage','hidden']),('coverage_width_separation',['coverage','hidden','median_whitened_crowding'])]:
 X=p[cols].copy();X['hidden']=np.log2(X.hidden);X=np.c_[np.ones(len(p)),X];b=np.linalg.lstsq(X,p.full_acc,rcond=None)[0];pred=X@b
 scale[key]={'coefficients':b.tolist(),'r_squared':float(1-sum((pred-p.full_acc)**2)/sum((p.full_acc-p.full_acc.mean())**2))}
result={'operation':'Deterministic recomputation from archived files; no neural training','future_partition':{'states':len(states),'actions':len(acts),'horizons':list(range(7)),'classes':counts,'fixed_length_bits':math.ceil(math.log2(counts[-1])),'witness':witness,'program':program,'outputs':outputs},'phrase_estimands':phrase,'scale':scale,'inputs':[{'path':str(x.relative_to(ROOT)),'sha256':hashlib.sha256(x.read_bytes()).hexdigest()} for x in paths]}
(ROOT/'evidence/editorial/recalculation_results.json').write_text(json.dumps(result,indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(7.0,4.1));labels=['Visible goal and main','Future horizon 0 to 3','All future programs'];vals=[25,173,275]
bars=ax.bar(labels,vals,color=['#A9B8C6','#3476A5','#184A69'],width=.58)
for bar,v in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,v+5,str(v),ha='center',fontsize=11)
ax.set_ylim(0,310);ax.set_ylabel('Distinguishable states');ax.set_title('Future horizon determines the state count');ax.spines[['top','right']].set_visible(False);ax.tick_params(axis='x',labelsize=9);fig.tight_layout();fig.savefig(ROOT/'figures/state_count_audited.png',dpi=200);plt.close(fig)
print(json.dumps({'future_classes':counts,'phrase':phrase,'scale':scale},indent=2))
