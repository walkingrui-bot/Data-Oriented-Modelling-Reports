import os
import time,json,math,multiprocessing as mp
from pathlib import Path
import numpy as np,pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
INPUT=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent.parent/'027')))
OUT=Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_027')))
OUT.mkdir(exist_ok=True, parents=True);TOPK=5;NS=8
X=sparse.load_npz(INPUT/'do026_X.npz').tocsr();Q=sparse.load_npz(INPUT/'do026_Q.npz').tocsr();A=np.load(INPUT/'do026_balanced_assign8.npy');N=X.shape[0];QN=Q.shape[0]
def topk(a,k=5):
 a=np.asarray(a)
 if a.size<=k:return np.argsort(-a)
 ii=np.argpartition(-a,k-1)[:k];return ii[np.argsort(-a[ii])]
CS=(Q@X.T).toarray();REF=[topk(CS[i]) for i in range(QN)];shards=[np.where(A==s)[0] for s in range(NS)]
svd=TruncatedSVD(64,random_state=0);Y=normalize(svd.fit_transform(X));cent=np.vstack([normalize(Y[idx].mean(axis=0,keepdims=True))[0] for idx in shards]);ys=Y@cent.T;backup=np.zeros(N,int)
for i in range(N):backup[i]=next(int(s) for s in np.argsort(-ys[i]) if s!=A[i])
hit=np.zeros(N,int)
for r in REF:
 for j in r:hit[j]+=1
hot=np.lexsort((np.arange(N),-hit))[:math.ceil(N*.25)];rep_sets={'none':np.array([],int),'hot25':hot,'full1':np.arange(N)}
physical={}
for pol,rset in rep_sets.items():
 rs=set(map(int,rset));physical[pol]=[np.array(sorted(set(map(int,shards[s]))|{i for i in rs if backup[i]==s}),int) for s in range(NS)]
shard_hit=np.array([hit[shards[s]].sum() for s in range(NS)]);CRIT=int(np.argmax(shard_hit))
# precompute true local results; pressure test then measures scheduling only
payload={}
for pol,phys in physical.items():
 payload[pol]=[]
 for ids in phys:
  M=(Q@X[ids].T).toarray(); payload[pol].append([(ids[ii:=topk(M[r],TOPK)].astype(np.int32),M[r,ii].astype(np.float32)) for r in range(QN)])
def merge(pol,received):
 rec=[];ex=[]
 for qi in range(QN):
  best={}
  for s in received:
   ids,sc=payload[pol][s][qi]
   for gid,v in zip(ids,sc):
    gid=int(gid);v=float(v);best[gid]=max(best.get(gid,-1e30),v)
  if not best:rec.append(0);ex.append(False);continue
  ids=np.array(list(best));sc=np.array([best[int(i)] for i in ids]);G=set(ids[topk(sc,TOPK)].tolist());R=set(map(int,REF[qi]));rec.append(len(G&R)/TOPK);ex.append(G==R)
 return np.mean(rec),np.mean(ex)
def worker(s,inq,outq):
 while True:
  x=inq.get()
  if x is None:break
  tid,delay=x
  if delay:time.sleep(delay)
  outq.put((tid,s,time.perf_counter()))
DELAY=.35;DEADLINE=.08;REPS=9;ctx=mp.get_context('fork');rows=[]
# one persistent process set is sufficient because payload not in workers
inqs=[ctx.Queue() for _ in range(NS)];outq=ctx.Queue();ps=[ctx.Process(target=worker,args=(s,inqs[s],outq)) for s in range(NS)]
for p in ps:p.start()
# warmup
for s in range(NS):inqs[s].put((-1,0))
w=0
while w<NS:
 if outq.get()[0]==-1:w+=1
for pol in rep_sets:
 for mode in ['barrier','deadline']:
  walls=[];recs=[];exs=[];counts=[]
  for rr in range(REPS):
   tid=10000+rr+(100 if mode=='deadline' else 0)+(1000*list(rep_sets).index(pol));t0=time.perf_counter()
   for s in range(NS):inqs[s].put((tid,DELAY if s==CRIT else 0.0))
   recv=[]
   if mode=='barrier':
    while len(recv)<NS:
     x=outq.get()
     if x[0]==tid:recv.append(x[1])
   else:
    while time.perf_counter()-t0<DEADLINE and len(recv)<NS-1:
     rem=max(.001,DEADLINE-(time.perf_counter()-t0))
     try:x=outq.get(timeout=rem)
     except Exception:break
     if x[0]==tid:recv.append(x[1])
   wall=time.perf_counter()-t0;r,e=merge(pol,recv);walls.append(wall);recs.append(r);exs.append(e);counts.append(len(recv))
   # allow slow message to arrive then drain stale ids before next task
   time.sleep(max(0,DELAY-(time.perf_counter()-t0))+.02)
   while True:
    try:outq.get_nowait()
    except Exception:break
  rows.append({'replication':pol,'mode':mode,'critical_shard':CRIT,'critical_reference_hit_share':shard_hit[CRIT]/(QN*TOPK),'injected_delay_s':DELAY,'deadline_s':DEADLINE,'repetitions':REPS,'median_wall_s':float(np.median(walls)),'mean_wall_s':float(np.mean(walls)),'mean_recall_at5':float(np.mean(recs)),'mean_exact_top5':float(np.mean(exs)),'mean_shards_received':float(np.mean(counts))})
for q in inqs:q.put(None)
for p in ps:p.join()
df=pd.DataFrame(rows);df.to_csv(OUT/'do027_straggler_timeout.csv',index=False);print(df.to_string(index=False))
p=OUT/'do027_summary.json';d=json.loads(p.read_text());d['straggler']=df.to_dict('records');p.write_text(json.dumps(d,indent=2))
