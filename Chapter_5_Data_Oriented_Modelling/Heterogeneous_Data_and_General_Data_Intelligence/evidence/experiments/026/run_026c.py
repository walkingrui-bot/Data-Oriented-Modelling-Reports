from pathlib import Path
import os
import time, multiprocessing as mp, numpy as np, pandas as pd
from scipy import sparse
INPUT=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent.parent/'027')))
OUT=str(Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_026'))))
Path(OUT).mkdir(exist_ok=True, parents=True)
X=sparse.load_npz(str(INPUT)+'/do026_X.npz').tocsr(); Q=sparse.load_npz(str(INPUT)+'/do026_Q.npz').tocsr(); A=np.load(str(INPUT)+'/do026_balanced_assign8.npy')
TOPK=5
# repeat real query set to 2048 dispatches; only scheduling workload is repeated
reps=(2048+Q.shape[0]-1)//Q.shape[0]; QB=sparse.vstack([Q]*reps)[:2048].tocsr()
shards=[np.where(A==s)[0] for s in range(8)]
Xsh=[X[idx] for idx in shards]
G_XSH=None; G_Q=None; G_SH=None

def init_worker(xsh,q,sh):
 global G_XSH,G_Q,G_SH; G_XSH=xsh; G_Q=q; G_SH=sh

def topk_rows(M,k=5):
 out=[]
 for r in range(M.shape[0]):
  a=M[r]
  if len(a)<=k: ind=np.argsort(-a)
  else:
   ind=np.argpartition(-a,k-1)[:k]; ind=ind[np.argsort(-a[ind])]
  out.append((ind,a[ind]))
 return out

def task(arg):
 s,st,en=arg; M=(G_Q[st:en]@G_XSH[s].T).toarray(); loc=topk_rows(M,TOPK); ids=G_SH[s]
 return [(ids[ii].astype(np.int32), ss.astype(np.float32)) for ii,ss in loc]

def central(bs):
 t=time.perf_counter(); chk=0
 for st in range(0,QB.shape[0],bs):
  M=(QB[st:st+bs]@X.T).toarray()
  for ii,ss in topk_rows(M,TOPK): chk+=int(ii.sum())
 return time.perf_counter()-t,chk

def dist(bs):
 ctx=mp.get_context('fork'); tasks=[]
 for st in range(0,QB.shape[0],bs):
  en=min(QB.shape[0],st+bs)
  for s in range(8): tasks.append((s,st,en))
 t=time.perf_counter();
 with ctx.Pool(8,initializer=init_worker,initargs=(Xsh,QB,shards)) as pool:
  res=pool.map(task,tasks,chunksize=1)
 # merge each batch's 8 shard outputs; task order is batch-major
 chk=0; ti=0
 for st in range(0,QB.shape[0],bs):
  en=min(QB.shape[0],st+bs); local=res[ti:ti+8]; ti+=8
  for r in range(en-st):
   ids=[]; sc=[]
   for sr in local:
    ids.extend(sr[r][0].tolist()); sc.extend(sr[r][1].tolist())
   ids=np.array(ids); sc=np.array(sc)
   if len(sc)<=TOPK: take=np.argsort(-sc)
   else:
    take=np.argpartition(-sc,TOPK-1)[:TOPK]; take=take[np.argsort(-sc[take])]
   chk+=int(ids[take].sum())
 return time.perf_counter()-t,chk
rows=[]
for bs in [16,64,256,2048]:
 w,c=central(bs); rows.append({'mode':'centralized','workers':1,'batch_size':bs,'queries':QB.shape[0],'wall_seconds':w,'qps':QB.shape[0]/w,'checksum':c})
 w,c=dist(bs); rows.append({'mode':'distributed_broadcast','workers':8,'batch_size':bs,'queries':QB.shape[0],'wall_seconds':w,'qps':QB.shape[0]/w,'checksum':c})
df=pd.DataFrame(rows); df.to_csv(OUT+'/do026_process_benchmark.csv',index=False); print(df.to_string(index=False))
