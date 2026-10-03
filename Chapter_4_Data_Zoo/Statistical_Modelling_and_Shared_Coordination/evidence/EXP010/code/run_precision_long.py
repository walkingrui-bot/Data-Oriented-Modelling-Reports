import sys,torch,numpy as np,pandas as pd
from pathlib import Path
src=Path('/mnt/data/INTERNAL_COORDINATION_010/code/experiment_010.py').read_text();prefix=src.split('rows=[];crossdiff=[];special=[]')[0].replace('EXPERT_STEPS=650','EXPERT_STEPS=1200').replace('EXPERT_STEPS=1000','EXPERT_STEPS=1200')
ns={};exec(prefix,ns)
seed=int(sys.argv[1]);RES=Path('/mnt/data/INTERNAL_COORDINATION_010/results');Net=ns['Net'];NumExpert=ns['NumExpert'];LangExpert=ns['LangExpert'];train_experts=ns['train_experts'];blend_metrics=ns['blend_metrics'];tr=ns['tr'];te=ns['te']
mixed=Net(seed);mixed.load_state_dict(torch.load(RES/f'base_mixed_seed{seed}.pt',map_location='cpu'))
rng=np.random.default_rng(991000+seed);perm=rng.permutation(tr);nv=max(70,int(.2*len(perm)));val=perm[:nv];sub=perm[nv:]
ne,le=train_experts(mixed,'precision',seed,sub)
grid=[0,.25,.5,.75]
# choose alphas independently across conditions where local modality is actually present
def score(an,al,ix,sd):return blend_metrics(mixed,ne,le,ix,an,al,seed=sd)
bestn=min(grid,key=lambda a: np.mean([score(a,0,val,770011)['num']['num_pinball'],score(a,0,val,770011)['both']['num_pinball']]))
bestl=max(grid,key=lambda a: np.mean([score(0,a,val,770011)['text']['lang_acc'],score(0,a,val,770011)['both']['lang_acc']]))
met=score(bestn,bestl,te,880001);base=score(0,0,te,880001)
row={'seed':seed,'alpha_num':bestn,'alpha_lang':bestl,**{f'{mode}_{k}':v for mode,z in met.items() for k,v in z.items()},'base_num_num_pinball':base['num']['num_pinball'],'base_text_lang_acc':base['text']['lang_acc'],'base_both_num_pinball':base['both']['num_pinball'],'base_both_lang_acc':base['both']['lang_acc']}
pd.DataFrame([row]).to_csv(RES/f'seed{seed}_precision_long.csv',index=False)
torch.save({'num_expert':ne.state_dict(),'lang_expert':le.net.state_dict(),'alpha_num':bestn,'alpha_lang':bestl},RES/f'seed{seed}_precision_long.pt')
print(row)
