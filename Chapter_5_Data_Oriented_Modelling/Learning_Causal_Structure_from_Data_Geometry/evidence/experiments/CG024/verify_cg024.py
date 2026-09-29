from pathlib import Path
import sys,json,numpy as np,pandas as pd,torch
ROOT=Path(__file__).resolve().parent
CODE=ROOT/'code';sys.path.insert(0,str(CODE))
import run_cg023_coordinate_world as cg
REF=ROOT/'reference_cg023';dat=np.load(REF/'world_data.npz');Ms,bs,eqbank,tmbank=dat['M'],dat['b'],dat['eqbank'],dat['tmbank']

def make_context(rng,w,n=8):
 ne=n//2;pe=rng.choice(16,ne,replace=False);pt=rng.choice(16,n-ne,replace=False);c=np.concatenate([eqbank[w,pe],tmbank[w,pt]],0);k=np.r_[np.zeros(ne,np.int64),np.ones(n-ne,np.int64)];o=rng.permutation(n);return c[o].astype('float32'),k[o]
res=[]
for seed in [11,22]:
 ck=torch.load(ROOT/'models'/f'cg024_{seed}_final.pt',map_location='cpu',weights_only=False);m=cg.WorldProgram();m.load_state_dict(ck['world']);m.eval();rng=np.random.default_rng(24600);C=[];KI=[]
 for w in range(500,532):c,k=make_context(rng,w);C.append(c);KI.append(k)
 C=torch.tensor(np.stack(C));KI=torch.tensor(np.stack(KI))
 with torch.no_grad():
  M2,b2,l2=m.form_world(C,KI,steps=2);Mr,br,lr=m.form_world(C,KI,steps=2,start_state=(M2,b2,l2));M4,b4,l4=m.form_world(C,KI,steps=4)
  replay=max(float((Mr-M4).abs().max()),float((br-b4).abs().max()),float((lr-l4).abs().max()));rowsum=float(M4.abs().sum(-1).max());diag=float(torch.diagonal(M4,dim1=-2,dim2=-1).abs().max())
 res.append({'seed':seed,'state_replay_max_abs':replay,'max_row_abs_sum':rowsum,'max_diagonal_abs':diag,'selected_step':int(ck['selected_step'])})
# validate acceptance files
acc=pd.read_csv(ROOT/'acceptance_summary_final_complete.csv')
required=[('impulse','correct_minus_ignore'),('clamp','correct_minus_ignore'),('persistent_force','correct_minus_ignore'),('compound_force_plus_impulse','correct_minus_omit_second')]
checks=[]
for op,cmp in required:
 row=acc[(acc.operation==op)&(acc.comparison==cmp)].iloc[0];checks.append({'operation':op,'comparison':cmp,'mean':float(row['mean']),'ci95_high':float(row['hi']),'primary_pass':bool(row['hi']<0)})
out={'checkpoints':res,'primary_acceptance':checks,'all_primary_pass':all(x['primary_pass'] for x in checks),'n_eval_rows':int(len(pd.read_csv(ROOT/'sequential_eval_detail_final.csv')))}
(ROOT/'verification.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
