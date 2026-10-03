import json, os, numpy as np, torch, sys, csv
sys.path.insert(0,'/mnt/data'); import importlib,internal_coord_003_multilang_fast as m; importlib.reload(m)
# load metric sources
paths={
0:{'self':'/mnt/data/IC003v2_self600.json','bind':'/mnt/data/IC003v2_bind650.json','shuffle':'/mnt/data/IC003v2_shuffle650.json'},
2:{'self':'/mnt/data/IC003_s2_self.json','bind':'/mnt/data/IC003_s2_bind.json','shuffle':'/mnt/data/IC003_s2_shuffle.json'},
3:{'self':'/mnt/data/IC003_s3_self.json','bind':'/mnt/data/IC003_s3_bind.json','shuffle':'/mnt/data/IC003_s3_shuffle.json'}}
state_paths={
0:{'self':'/mnt/data/IC003v2_self600.pt','bind':'/mnt/data/IC003v2_bind650.pt','shuffle':'/mnt/data/IC003v2_shuffle650.pt'},
2:{'self':'/mnt/data/IC003_s2_self.pt','bind':'/mnt/data/IC003_s2_bind.pt','shuffle':'/mnt/data/IC003_s2_shuffle.pt'},
3:{'self':'/mnt/data/IC003_s3_self.pt','bind':'/mnt/data/IC003_s3_bind.pt','shuffle':'/mnt/data/IC003_s3_shuffle.pt'}}
exec_a=json.load(open('/mnt/data/IC003_execution_audit.json'))

def metric_obj(seed,cond):
 d=json.load(open(paths[seed][cond])); return d[cond]

def retrieval(Z):
 n,d,v=Z.shape; acc=[]; same=[]; diff=[]; mar=[]; rng=np.random.default_rng(0)
 for a in range(v):
  for b in range(v):
   if a==b: continue
   A=Z[:,:,a]; B=Z[:,:,b]; D=((A[:,None,:]-B[None,:,:])**2).sum(-1)
   true=D[np.arange(n),np.arange(n)]; Dw=D.copy(); Dw[np.arange(n),np.arange(n)]=np.inf; wrong=Dw.min(1)
   acc.append(np.mean(D.argmin(1)==np.arange(n))); mar.append(np.mean(wrong-true)); same.extend(np.sqrt(true)); j=(np.arange(n)+rng.integers(1,n,size=n))%n; diff.extend(np.sqrt(D[np.arange(n),j]))
 return dict(retrieval_acc=float(np.mean(acc)),min_pair_acc=float(np.min(acc)),margin=float(np.mean(mar)),same_diff_ratio=float(np.mean(same)/np.mean(diff)))

def distmat(Z):
 # average euclidean distance across same-scene representations
 n,d,v=Z.shape; D=np.zeros((v,v))
 for a in range(v):
  for b in range(v): D[a,b]=np.linalg.norm(Z[:,:,a]-Z[:,:,b],axis=1).mean()
 return D

rows=[]; Zs={}
test=m.ALL_SCENES[1000:1200]
for seed in [0,2,3]:
 for cond in ['self','bind','shuffle']:
  q=metric_obj(seed,cond)
  model=m.M().to(m.DEVICE); model.load_state_dict(torch.load(state_paths[seed][cond],map_location='cpu')); model.eval(); Z=m.allZ(model,test); Zs[(seed,cond)]=Z
  r=retrieval(Z)
  e=exec_a[f's{seed}_{cond}']
  row={'seed':seed,'condition':cond,
       'cross_sem_acc':q['cross_sem_acc'],'cross_tok_acc':q['cross_tok_acc'],
       'same_scene_cos':q['same_scene_cos'],'probe_r2_mean':q['probe_r2_mean'],
       **r,'execution_equivalence':e['execution_equivalence'],'cross_exact':e['cross_exact'],'parse_rate':e['parse_rate']}
  rows.append(row)
with open('/mnt/data/IC003_per_seed.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
summary={}
for cond in ['self','bind','shuffle']:
 rr=[x for x in rows if x['condition']==cond]; summary[cond]={}
 for k in ['cross_sem_acc','cross_tok_acc','same_scene_cos','probe_r2_mean','retrieval_acc','min_pair_acc','same_diff_ratio','execution_equivalence','cross_exact','parse_rate']:
  vals=[x[k] for x in rr]; summary[cond][k]={'median':float(np.median(vals)),'min':float(np.min(vals)),'max':float(np.max(vals)),'values':vals}
json.dump(summary,open('/mnt/data/IC003_summary.json','w'),indent=2)
# first binding deltas
fds=[]
for seed,f in [(0,'/mnt/data/IC003v2_bind650.json'),(2,'/mnt/data/IC003_s2_bind.json'),(3,'/mnt/data/IC003_s3_bind.json')]:
 d=json.load(open(f)); fd=d['first_delta']; fds.append({'seed':seed,**fd})
with open('/mnt/data/IC003_first_update.csv','w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=fds[0].keys());w.writeheader();w.writerows(fds)
# save mean distance matrices
np.savez('/mnt/data/IC003_geometry_matrices.npz', **{f's{seed}_{cond}':distmat(Z) for (seed,cond),Z in Zs.items()})
# representative scene 0 matrices seed0
np.savez('/mnt/data/IC003_scene_matrices_seed0.npz', scene=np.array(test[0],dtype=object), self=Zs[(0,'self')][0], bind=Zs[(0,'bind')][0], shuffle=Zs[(0,'shuffle')][0])
print(json.dumps(summary,indent=2))
