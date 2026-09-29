from pathlib import Path
import sys,json,re
import numpy as np,pandas as pd,torch
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT));import run_cg022_engineered_world as core
z=np.load(ROOT/'synthetic_data.npz');ix=z['split']==2
x=torch.tensor(z['x'][ix],dtype=torch.float32);y=torch.tensor(z['y'][ix],dtype=torch.float32);groups=z['group'][ix];support=z['support'][ix]

def family(name):
    if name.startswith('half'):return 'edge half'
    if name.startswith('flip'):return 'edge flip'
    if name.startswith('del'):return 'edge delete'
    if re.match(r'^do\d_[+-]',name):return 'single-do'
    return 'double-do'

def load_state(kind,seed):
    if kind=='baseline':
        sys.path.insert(0,'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021');import run_cg021_free_pool as old
        ck=torch.load(f'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021/models/pool8_{seed}.pt',map_location='cpu',weights_only=False);m=old.FreePool(8);m.load_state_dict(ck['state_dict']);m.eval()
        with torch.no_grad():_,tr=m(x,trace=True);return tr['B'][:,-1],tr['logits'][:,-1]
    stem={'broad':'world_program','balanced':'balanced','evidence':'evidence_coupled'}[kind]
    ck=torch.load(ROOT/'models'/f'{stem}_{seed}.pt',map_location='cpu',weights_only=False);m=core.WorldProgram(8);m.load_state_dict(ck['state_dict']);m.eval()
    with torch.no_grad():return m.form_world(x,steps=4)

def orig_nll(B,lg):
    q=x[:,-3:].argmax(-1);ss=[]
    for qi in range(3):ss.append(core.apply_operator(B,{'type':'do','targets':[qi],'values':[1.]}))
    S=torch.stack(ss,2);mus=S[torch.arange(len(B))[:,None],torch.arange(B.shape[1])[None,:],q[:,None]]
    return core.mix_nll(mus,lg,y).numpy()

orig=[]
for kind in ['baseline','broad','balanced','evidence']:
  for seed in [11,22]:
    B,lg=load_state(kind,seed);vals=orig_nll(B,lg)
    for i,v in enumerate(vals):orig.append({'variant':kind,'seed':seed,'instance':i,'group':int(groups[i]),'support':int(support[i]),'nll':float(v)})
orig=pd.DataFrame(orig);orig.to_csv(ROOT/'original_query_detail.csv',index=False)

base=pd.read_csv(ROOT/'baseline_operator_detail.csv');base['variant']='baseline'
broad=pd.read_csv(ROOT/'operator_detail.csv');broad['variant']='broad'
bal=pd.read_csv(ROOT/'balanced_operator_detail.csv');bal['variant']='balanced'
ev=pd.read_csv(ROOT/'evidence_coupled_operator_detail.csv');ev['variant']='evidence'
allop=pd.concat([base,broad,bal,ev],ignore_index=True);allop['family']=allop.operator.map(family);allop.to_csv(ROOT/'all_operator_detail.csv',index=False)

rng=np.random.default_rng(22022)
def paired(df,a,b,n=10000):
    tab=df.groupby(['variant','group']).nll.mean().unstack(0);d=(tab[a]-tab[b]).dropna().to_numpy();bs=np.array([rng.choice(d,len(d),replace=True).mean() for _ in range(n)])
    return {'improvement':float(d.mean()),'ci95':[float(np.quantile(bs,.025)),float(np.quantile(bs,.975))],'group_improved_rate':float((d>0).mean())}

summary={}
for label,df in [('original',orig),('train_bank',allop[allop.bank=='train_bank']),('heldout_bank',allop[allop.bank=='heldout_bank'])]:summary['baseline_to_evidence_'+label]=paired(df,'baseline','evidence')
for label,df in [('original',orig),('heldout_bank',allop[allop.bank=='heldout_bank'])]:summary['balanced_to_evidence_'+label]=paired(df,'balanced','evidence')

# exact means
means=[]
for v in ['baseline','broad','balanced','evidence']:
    means.append({'variant':v,'original_query_nll':orig[orig.variant==v].nll.mean(),'train_bank_nll':allop[(allop.variant==v)&(allop.bank=='train_bank')].nll.mean(),'heldout_bank_nll':allop[(allop.variant==v)&(allop.bank=='heldout_bank')].nll.mean()})
pd.DataFrame(means).to_csv(ROOT/'engineering_summary.csv',index=False)

# family means and paired effects on held-out set only
hf=allop[allop.bank=='heldout_bank']; fam=hf.groupby(['variant','family']).agg(nll=('nll','mean'),mse=('mse','mean')).reset_index();fam.to_csv(ROOT/'heldout_family_summary.csv',index=False)
fe=[]
for f in ['single-do','double-do','edge half','edge flip']:
    e=paired(hf[hf.family==f],'baseline','evidence');e['family']=f;fe.append(e)
pd.DataFrame(fe).to_json(ROOT/'heldout_family_effects.json',orient='records',indent=2)
summary['heldout_family_effects']=fe

# final evidence model result summaries
er=pd.read_csv(ROOT/'evidence_coupled_results.csv');br=pd.read_csv(ROOT/'balanced_results.csv')
for c in ['heldout_support_improvement','support_observation_nll_gain','support_operator_bank_gain','wrong_support_own_degradation','wrong_support_donor_preferred','effective_worlds']:
    summary['evidence_'+c+'_mean']=float(er[c].mean())
summary['state_replay_max_abs']=float(er.state_replay_max_abs.max())
# wrong support discriminative subset >.4 RMS
wd=pd.read_csv(ROOT/'wrong_support_eval.csv');wd=wd[wd.variant=='evidence_coupled'].copy();yy=z['y'][ix];wd['truth_sep']=[np.sqrt(np.mean((yy[int(r.receiver)]-yy[int(r.donor)])**2)) for _,r in wd.iterrows()];s=wd[wd.truth_sep>.4]
summary['wrong_support_discriminative_n']=int(len(s));summary['wrong_support_discriminative_degradation']=float(s.own_degradation.mean());summary['wrong_support_discriminative_donor_preferred']=float(s.donor_preferred.mean())
# rollout evidence coupled
roll=pd.read_csv(ROOT/'evidence_coupled_rollout.csv');rs=roll.groupby('step').agg(heldout_nll=('heldout_bank_nll','mean'),B_step_rms=('B_step_rms','mean')).reset_index();rs.to_csv(ROOT/'evidence_rollout_summary.csv',index=False);summary['rollout_step4_nll']=float(rs.loc[rs.step==4,'heldout_nll'].iloc[0]);summary['rollout_step20_nll']=float(rs.loc[rs.step==20,'heldout_nll'].iloc[0]);summary['rollout_step20_B_step_rms']=float(rs.loc[rs.step==20,'B_step_rms'].iloc[0])
# B distance comparison baseline from CG021
sd=pd.read_csv('/mnt/data/cg021_work/CAUSAL_GEOMETRY_021/state_dynamics.csv');q=sd[sd.variant=='pool8'];summary['baseline_weighted_B_dist']=float(q.weighted_B_dist_final.mean());summary['baseline_best_B_dist']=float(q.best_B_dist_final.mean());summary['evidence_weighted_B_dist']=float(er.weighted_B_dist.mean());summary['evidence_best_B_dist']=float(er.best_B_dist.mean())
(ROOT/'key_findings.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))

# figures
M=pd.DataFrame(means);fig,ax=plt.subplots(figsize=(8.2,5));xx=np.arange(3);w=.19
for j,v in enumerate(M.variant):ax.bar(xx+(j-1.5)*w,M.loc[j,['original_query_nll','train_bank_nll','heldout_bank_nll']],width=w,label=v)
ax.set_xticks(xx,['Original query','Training operator bank','Held-out operator bank']);ax.set_ylabel('NLL (lower is better)');ax.set_title('CG-022: engineering the world state for reusable consequence generation');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig77_engineering_comparison.png',dpi=200);plt.close(fig)

order=['single-do','double-do','edge half','edge flip'];fig,ax=plt.subplots(figsize=(8.2,5));xx=np.arange(4);w=.19
for j,v in enumerate(['baseline','broad','balanced','evidence']):
    vals=[float(fam[(fam.variant==v)&(fam.family==f)].nll.iloc[0]) for f in order];ax.bar(xx+(j-1.5)*w,vals,width=w,label=v)
ax.set_xticks(xx,['New single-do values','Held-out double-do','Edge half','Edge flip']);ax.set_ylabel('NLL (lower is better)');ax.set_title('Held-out operations improve without relation-matrix supervision');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig78_heldout_operator_families.png',dpi=200);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.4,4.6));xx=np.arange(2);w=.26
ax.bar(xx-w,br.support_observation_nll_gain,width=w,label='Balanced: support response');ax.bar(xx,er.support_observation_nll_gain,width=w,label='Evidence-coupled: support response');ax.bar(xx+w,er.support_operator_bank_gain,width=w,label='Evidence-coupled: downstream bank');ax.set_xticks(xx,['seed 11','seed 22']);ax.axhline(0,linewidth=1);ax.set_ylabel('NLL improvement from support');ax.set_title('Evidence coupling connects support to later consequence generation');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'figures/fig79_support_assimilation.png',dpi=200);plt.close(fig)

fig,ax=plt.subplots(figsize=(7.2,4.5));ax.plot(rs.step,rs.heldout_nll,marker='o');ax.set_xlabel('World updates');ax.set_ylabel('Held-out operator-bank NLL');ax.set_title('Executable world state remains stable beyond the training window');fig.tight_layout();fig.savefig(ROOT/'figures/fig80_rollout_generalization.png',dpi=200);plt.close(fig)

# support boundary plot
ws=pd.read_csv(ROOT/'wrong_support_summary.csv');ws=ws[ws.variant.isin(['baseline','balanced','evidence_coupled'])].copy();labels=['baseline','balanced','evidence-coupled'];correct=[0,br.heldout_support_improvement.mean(),er.heldout_support_improvement.mean()];wrong=[float(ws.loc[ws.variant=='baseline','own_degradation'].iloc[0]),float(ws.loc[ws.variant=='balanced','own_degradation'].iloc[0]),float(ws.loc[ws.variant=='evidence_coupled','own_degradation'].iloc[0])]
fig,ax=plt.subplots(figsize=(7.2,4.5));xx=np.arange(3);w=.34;ax.bar(xx-w/2,correct,width=w,label='Correct-support held-out gain');ax.bar(xx+w/2,wrong,width=w,label='Wrong-support original-query degradation');ax.axhline(0,linewidth=1);ax.set_xticks(xx,labels);ax.set_ylabel('NLL change / improvement');ax.set_title('Correct evidence helps downstream operators; wrong-evidence routing is still conservative');ax.legend(fontsize=8);fig.tight_layout();fig.savefig(ROOT/'figures/fig81_evidence_boundary.png',dpi=200);plt.close(fig)

print(json.dumps(summary,indent=2,ensure_ascii=False));print('\nMEANS\n',pd.DataFrame(means).to_string(index=False));print('\nHELDOUT FAMILIES\n',fam.to_string(index=False))
