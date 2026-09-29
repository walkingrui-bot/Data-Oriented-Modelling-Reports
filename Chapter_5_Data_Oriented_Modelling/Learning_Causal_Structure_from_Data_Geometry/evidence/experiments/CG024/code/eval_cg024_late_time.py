from pathlib import Path
import sys, numpy as np, pandas as pd, torch
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT))
import run_cg023_coordinate_world as cg
import run_cg024_sequential_acceptance as r
OUT=Path('/mnt/data/cg024_final/CAUSAL_GEOMETRY_024');D=cg.D
rows=[];dat=np.load(ROOT/'world_data.npz');Ms,bs,eqbank,tmbank=dat['M'],dat['b'],dat['eqbank'],dat['tmbank'];test_ids=np.arange(500,600)
for seed in [11,22]:
 ck=torch.load(OUT/'models'/f'cg024_{seed}_final.pt',map_location='cpu',weights_only=False);model=cg.WorldProgram();model.load_state_dict(ck['world']);model.eval();rng=np.random.default_rng(24100)
 with torch.no_grad():
  for w in test_ids:
   c,k=r.make_context(rng,w,eqbank,tmbank);C=r.tensor(c[None]);KI=r.tensor(k[None],torch.long);M,b,lg=model.form_world(C,KI,steps=4)
   # consume exact RNG sequence for impulse, clamp, persistent_force in the original eval loop
   for typ,name in [(0,'impulse'),(1,'clamp'),(2,'persistent_force')]:
    for h in [8,16,32,64,128]:
     off=2 if h>=4 else 1;tau=h-off;j=int(rng.integers(D));val=float(rng.uniform(-1.5,1.5));x0=rng.uniform(-1.3,1.3,D).astype('float32')
     if typ!=2: continue
     truth=r.rollout_event_np(Ms[w],bs[w],x0,h,typ,j,val,tau);H=r.tensor([h],torch.long);T=r.tensor([typ],torch.long);J=r.tensor([j],torch.long);V=r.tensor([val]);TA=r.tensor([tau],torch.long);X=r.tensor(x0[None])
     pc=cg.expected(r.exec_event_torch(M,b,X,H,T,J,V,TA),lg)[0].numpy(); late=min(h-1,tau+1);pl=cg.expected(r.exec_event_torch(M,b,X,H,T,J,V,r.tensor([late],torch.long)),lg)[0].numpy()
     rows += [{'seed':seed,'world_id':int(w),'operation':'persistent_force','horizon':h,'condition':'correct','mse':float(((pc-truth)**2).mean())},{'seed':seed,'world_id':int(w),'operation':'persistent_force','horizon':h,'condition':'wrong_time_late','mse':float(((pl-truth)**2).mean())}]
pd.DataFrame(rows).to_csv(OUT/'persistent_force_late_time_control.csv',index=False)
print('done',len(rows))
