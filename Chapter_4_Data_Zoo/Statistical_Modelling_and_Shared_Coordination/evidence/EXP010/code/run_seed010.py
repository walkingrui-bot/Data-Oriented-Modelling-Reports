import os,sys,runpy,json,torch,pandas as pd,numpy as np
from pathlib import Path
# Load definitions only up to the execution block of experiment_010
src=Path('/mnt/data/INTERNAL_COORDINATION_010/code/experiment_010.py').read_text()
prefix=src.split('rows=[];crossdiff=[];special=[]')[0]
ns={};exec(prefix,ns)
seed=int(sys.argv[1]);RES=Path('/mnt/data/INTERNAL_COORDINATION_010/results')
Net=ns['Net']; NumExpert=ns['NumExpert']; LangExpert=ns['LangExpert']; train_base=ns['train_base']; train_experts=ns['train_experts']; choose_alphas=ns['choose_alphas']; blend_metrics=ns['blend_metrics']; tr=ns['tr'];te=ns['te']
# reduce residual budget here
ns['EXPERT_STEPS']=300
# Function train_experts closes over global EXPERT_STEPS in ns only if redefined; re-exec with modified line
prefix2=prefix.replace('EXPERT_STEPS=650','EXPERT_STEPS=300').replace('EXPERT_STEPS=1000','EXPERT_STEPS=300')
ns={};exec(prefix2,ns)
Net=ns['Net']; NumExpert=ns['NumExpert']; LangExpert=ns['LangExpert']; train_base=ns['train_base']; train_experts=ns['train_experts']; choose_alphas=ns['choose_alphas']; blend_metrics=ns['blend_metrics']; tr=ns['tr'];te=ns['te']
ck=RES/f'base_mixed_seed{seed}.pt'
if seed==0 and (RES/'seed0_precision_bundle.pt').exists():
 mixed=Net(seed);mixed.load_state_dict(torch.load(RES/'seed0_precision_bundle.pt',map_location='cpu')['mixed']);torch.save(mixed.state_dict(),ck)
elif ck.exists():
 mixed=Net(seed);mixed.load_state_dict(torch.load(ck,map_location='cpu'))
else:
 mixed=train_base(seed,'mixed');torch.save(mixed.state_dict(),ck)
ref=pd.read_csv('/mnt/data/INTERNAL_COORDINATION_009/results/final_branch_metrics.csv')
spn=float(ref[(ref.seed==seed)&(ref.branch=='numeric')].num_pinball_num.iloc[0]);spl=float(ref[(ref.seed==seed)&(ref.branch=='language')].lang_acc_text.iloc[0])
rng=np.random.default_rng(202610+seed);perm=rng.permutation(tr);nv=max(35,int(.1*len(perm)));val=perm[:nv];sub=perm[nv:]
dummyN=NumExpert('small');dummyL=LangExpert(mixed,'small');base=blend_metrics(mixed,dummyN,dummyL,te,0,0)
rows=[{'seed':seed,'capacity':'none','alpha_num':0,'alpha_lang':0,'expert_params':0,'numeric_specialist_pinball':spn,'language_specialist_acc':spl,**{f'{mode}_{k}':v for mode,z in base.items() for k,v in z.items()}}]
cross=[]
for cap in ['small','medium','precision']:
 ne,le=train_experts(mixed,cap,seed,sub);an,al=choose_alphas(mixed,ne,le,val);met=blend_metrics(mixed,ne,le,te,an,al);rec={'seed':seed,'capacity':cap,'alpha_num':an,'alpha_lang':al,'numeric_specialist_pinball':spn,'language_specialist_acc':spl,**{f'{mode}_{k}':v for mode,z in met.items() for k,v in z.items()}};rec['expert_params']=sum(p.numel() for p in ne.parameters())+sum(p.numel() for p in le.net.parameters());rows.append(rec)
 rb=blend_metrics(mixed,ne,le,te,0,0);cross.append({'seed':seed,'capacity':cap,'text_to_numeric_abs_diff':abs(met['text']['num_pinball']-rb['text']['num_pinball']),'numeric_to_language_abs_diff':abs(met['num']['lang_acc']-rb['num']['lang_acc'])})
 if seed==0 and cap=='precision':torch.save({'mixed':mixed.state_dict(),'num_expert':ne.state_dict(),'lang_expert':le.net.state_dict(),'alpha_num':an,'alpha_lang':al},RES/'seed0_precision_bundle_300.pt')
pd.DataFrame(rows).to_csv(RES/f'seed{seed}_precision_results.csv',index=False);pd.DataFrame(cross).to_csv(RES/f'seed{seed}_cross_invariance.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
