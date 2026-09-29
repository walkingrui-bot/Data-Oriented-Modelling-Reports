from pathlib import Path
import sys, json, math
import numpy as np, pandas as pd, torch
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
import run_cg022_engineered_world as core
import run_cg022_balanced as bal

z=np.load(ROOT/'synthetic_data.npz'); ix=z['split']==2
x=torch.tensor(z['x'][ix],dtype=torch.float32); y=torch.tensor(z['y'][ix],dtype=torch.float32); tb=torch.tensor(z['true_B'][ix],dtype=torch.float32); groups=z['group'][ix]; support=z['support'][ix]
SEEDS=[11,22]

def family(name):
    if name.startswith('half'): return 'edge half (held-out)'
    if name.startswith('flip'): return 'edge flip (held-out)'
    if name.startswith('del'): return 'edge delete (trained)'
    if name.startswith('do'):
        # double names have a second variable marker after first numeric section
        body=name[2:]
        if '_' in body and any(f'_{q}' in body for q in ['0','1','2']): return 'double-do'
        # robust: names generated for double start do0+1_1+1 etc; single do0_+1
        first=body.split('_')[0]
        return 'single-do' if len(first)==1 else 'double-do'
    return 'other'

def nll_original(m,B,lg):
    q=x[:,-3:].argmax(-1); sims=[]
    for qi in range(3): sims.append(core.apply_operator(B,{'type':'do','targets':[qi],'values':[1.]}))
    S=torch.stack(sims,2); mus=S[torch.arange(len(B))[:,None],torch.arange(B.shape[1])[None,:],q[:,None]]
    return core.mix_nll(mus,lg,y).detach().numpy()

def load_states(kind,seed):
    if kind=='baseline':
        sys.path.insert(0,'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021'); import run_cg021_free_pool as old
        ck=torch.load(f'/mnt/data/cg021_work/CAUSAL_GEOMETRY_021/models/pool8_{seed}.pt',map_location='cpu',weights_only=False); m=old.FreePool(8);m.load_state_dict(ck['state_dict']);m.eval()
        with torch.no_grad(): _,tr=m(x,trace=True); return tr['B'][:,-1],tr['logits'][:,-1]
    name='world_program' if kind=='broad' else 'balanced'
    ck=torch.load(ROOT/'models'/f'{name}_{seed}.pt',map_location='cpu',weights_only=False);m=core.WorldProgram(8);m.load_state_dict(ck['state_dict']);m.eval()
    with torch.no_grad():B,lg=m.form_world(x,steps=4)
    return B,lg

# per-instance original-query NLL for exact paired comparisons
orig=[]
for kind in ['baseline','broad','balanced']:
    for seed in SEEDS:
        B,lg=load_states(kind,seed); vals=nll_original(None,B,lg)
        for i,v in enumerate(vals):orig.append({'variant':kind,'seed':seed,'instance':i,'group':int(groups[i]),'support':int(support[i]),'nll':float(v)})
orig=pd.DataFrame(orig);orig.to_csv(ROOT/'original_query_detail.csv',index=False)

# operator detail files
base=pd.read_csv(ROOT/'baseline_operator_detail.csv');base['variant']='baseline'
broad=pd.read_csv(ROOT/'operator_detail.csv');broad['variant']='broad'
balanced=pd.read_csv(ROOT/'balanced_operator_detail.csv')
allop=pd.concat([base,broad,balanced],ignore_index=True);allop['family']=allop.operator.map(family);allop.to_csv(ROOT/'all_operator_detail.csv',index=False)

# bootstrap at independent 100-group level, averaging repeated instances and seeds
rng=np.random.default_rng(22022)
def paired_boot(df, a,b, value='nll', n=10000):
    g=df.groupby(['variant','group'])[value].mean().unstack(0); d=g[a]-g[b] # positive => b is lower/better
    vals=d.dropna().to_numpy(); boots=np.array([rng.choice(vals,len(vals),replace=True).mean() for _ in range(n)])
    return float(vals.mean()),[float(np.quantile(boots,.025)),float(np.quantile(boots,.975))],float((vals>0).mean())

summary={}
# old baseline -> balanced (positive improvement)
for label,df in [('original',orig),('train_bank',allop[allop.bank=='train_bank']),('heldout_bank',allop[allop.bank=='heldout_bank'])]:
    mean,ci,rate=paired_boot(df,'baseline','balanced');summary[label]={'baseline_to_balanced_improvement':mean,'ci95':ci,'group_improved_rate':rate}
# broad engineering iteration -> balanced
for label,df in [('original',orig),('heldout_bank',allop[allop.bank=='heldout_bank'])]:
    mean,ci,rate=paired_boot(df,'broad','balanced');summary['broad_to_balanced_'+label]={'improvement':mean,'ci95':ci,'group_improved_rate':rate}

# family table, held-out only plus trained delete for edge comparison
fam=allop.groupby(['variant','family']).agg(nll=('nll','mean'),mse=('mse','mean')).reset_index();fam.to_csv(ROOT/'operator_family_summary.csv',index=False)
# family paired baseline vs balanced by group
family_effect=[]
for famname in sorted(allop.family.unique()):
    df=allop[allop.family==famname]
    if set(['baseline','balanced']).issubset(df.variant.unique()):
        mean,ci,rate=paired_boot(df,'baseline','balanced');family_effect.append({'family':famname,'nll_improvement':mean,'ci_low':ci[0],'ci_high':ci[1],'group_improved_rate':rate})
pd.DataFrame(family_effect).to_csv(ROOT/'operator_family_effects.csv',index=False)

# support evidence assimilation from balanced results and support/no-support heldout group difference
br=pd.read_csv(ROOT/'balanced_results.csv')
summary['support_observation_nll_gain_mean']=float(br.support_observation_nll_gain.mean());summary['support_observation_improved_rate_mean']=float(br.support_observation_improved_rate.mean());summary['heldout_support_improvement_mean']=float(br.heldout_support_improvement.mean())
summary['balanced_effective_worlds_mean']=float(br.effective_worlds.mean());summary['balanced_weighted_B_dist_mean']=float(br.weighted_B_dist.mean());summary['balanced_best_B_dist_mean']=float(br.best_B_dist.mean())
summary['state_replay_max_abs']=float(max(br.state_replay_B_max_abs.max(),br.state_replay_logit_max_abs.max()))
# long rollout summary
roll=pd.read_csv(ROOT/'balanced_rollout.csv'); rs=roll.groupby('step').agg(heldout_nll=('heldout_bank_nll','mean'),B_step_rms=('B_step_rms','mean')).reset_index();rs.to_csv(ROOT/'rollout_summary.csv',index=False)
summary['rollout_step4_heldout_nll']=float(rs.loc[rs.step==4,'heldout_nll'].iloc[0]);summary['rollout_step20_heldout_nll']=float(rs.loc[rs.step==20,'heldout_nll'].iloc[0]);summary['rollout_step20_B_step_rms']=float(rs.loc[rs.step==20,'B_step_rms'].iloc[0])
(ROOT/'key_findings.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False))

# Figure 77: main engineering comparison
means=[]
for kind in ['baseline','broad','balanced']:
    oq=orig[orig.variant==kind].nll.mean(); tr=allop[(allop.variant==kind)&(allop.bank=='train_bank')].nll.mean(); he=allop[(allop.variant==kind)&(allop.bank=='heldout_bank')].nll.mean();means.append((kind,oq,tr,he))
md=pd.DataFrame(means,columns=['variant','Original query','Training operator bank','Held-out operator bank'])
fig,ax=plt.subplots(figsize=(8,5));xx=np.arange(3);w=.24
for j,v in enumerate(md.variant):ax.bar(xx+(j-1)*w,md.loc[j,['Original query','Training operator bank','Held-out operator bank']].astype(float),width=w,label=v)
ax.set_xticks(xx,['Original query','Training bank','Held-out bank']);ax.set_ylabel('NLL (lower is better)');ax.set_title('CG-022: consequence training turns the world state into a broader executable program');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig77_engineering_comparison.png',dpi=200);plt.close(fig)

# Figure 78: held-out families
hf=fam[fam.family.str.contains('held-out|double-do|single-do')].copy();order=['single-do','double-do','edge half (held-out)','edge flip (held-out)'];hf=hf[hf.family.isin(order)]
fig,ax=plt.subplots(figsize=(8,5));xx=np.arange(len(order));w=.24
for j,v in enumerate(['baseline','broad','balanced']):
    vals=[float(hf[(hf.variant==v)&(hf.family==f)].nll.iloc[0]) for f in order];ax.bar(xx+(j-1)*w,vals,width=w,label=v)
ax.set_xticks(xx,['Single-do values','Double-do','Edge half','Edge flip']);ax.set_ylabel('NLL (lower is better)');ax.set_title('Held-out operations improve without relation-matrix supervision');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig78_heldout_operator_families.png',dpi=200);plt.close(fig)

# Figure 79: support assimilation, seed values
fig,ax=plt.subplots(figsize=(7,4.5));xx=np.arange(2);w=.32
ax.bar(xx-w/2,br.support_observation_nll_gain,width=w,label='Support observation NLL gain');ax.bar(xx+w/2,br.heldout_support_improvement,width=w,label='Held-out bank support gain');ax.set_xticks(xx,['seed 11','seed 22']);ax.axhline(0,linewidth=1);ax.set_ylabel('NLL improvement');ax.set_title('Support evidence now changes the executable world in a useful direction');ax.legend();fig.tight_layout();fig.savefig(ROOT/'figures/fig79_support_assimilation.png',dpi=200);plt.close(fig)

# Figure 80: rollout
fig,ax=plt.subplots(figsize=(7,4.5));ax.plot(rs.step,rs.heldout_nll,marker='o');ax.set_xlabel('World updates');ax.set_ylabel('Held-out operator-bank NLL');ax.set_title('The engineered world program remains executable beyond the training window');fig.tight_layout();fig.savefig(ROOT/'figures/fig80_rollout_generalization.png',dpi=200);plt.close(fig)

print(json.dumps(summary,indent=2))
print('\nFAMILY SUMMARY\n',fam.to_string(index=False))
