import torch,copy,pandas as pd,numpy as np
from pathlib import Path
src=Path('/mnt/data/INTERNAL_COORDINATION_010/code/experiment_010.py').read_text();prefix=src.split('rows=[];crossdiff=[];special=[]')[0]
ns={};exec(prefix,ns)
Net=ns['Net'];NumExpert=ns['NumExpert'];LangExpert=ns['LangExpert'];blend_metrics=ns['blend_metrics'];te=ns['te']
RES=Path('/mnt/data/INTERNAL_COORDINATION_010/results');rows=[]
for seed in [0,1,2]:
 base=Net(seed);base.load_state_dict(torch.load(RES/f'base_mixed_seed{seed}.pt',map_location='cpu'))
 pack=torch.load(RES/f'seed{seed}_precision_long.pt',map_location='cpu');ne=NumExpert('precision');ne.load_state_dict(pack['num_expert']);le=LangExpert(base,'precision');le.net.load_state_dict(pack['lang_expert']);an=float(pack['alpha_num']);al=float(pack['alpha_lang'])
 init=Net(seed);M0=init.M.detach();d=base.M.detach()-M0;U,S,Vh=torch.linalg.svd(d,full_matrices=False);rem=(U[:,:2]*S[:2])@Vh[:2,:];norm=float(torch.linalg.norm(rem))
 variants={'full':base,'top2_lesion':copy.deepcopy(base)};variants['top2_lesion'].M.data.copy_(base.M.detach()-rem)
 g=torch.Generator().manual_seed(9917+seed);R=torch.randn(d.shape,generator=g);R=R/(torch.linalg.norm(R)+1e-12)*norm;variants['random_matched']=copy.deepcopy(base);variants['random_matched'].M.data.copy_(base.M.detach()-R)
 for name,m in variants.items():
  # reset language expert base pointer to lesioned version
  lex=LangExpert(m,'precision');lex.net.load_state_dict(pack['lang_expert'])
  met=blend_metrics(m,ne,lex,te,an,al)
  rows.append({'seed':seed,'variant':name,'removed_norm':0 if name=='full' else norm,'both_num_pinball':met['both']['num_pinball'],'both_lang_acc':met['both']['lang_acc'],'text_to_numeric':met['text']['num_pinball'],'numeric_to_language':met['num']['lang_acc']})
pd.DataFrame(rows).to_csv(RES/'ganglion_retention_after_precision.csv',index=False)
print(pd.DataFrame(rows).to_string(index=False))
