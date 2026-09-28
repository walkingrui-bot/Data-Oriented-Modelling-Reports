from pathlib import Path
import os
import time,multiprocessing as mp, numpy as np,pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize
from sklearn.cluster import KMeans
INPUT=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent.parent/'027')))
OUT=str(Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_026'))))
Path(OUT).mkdir(exist_ok=True, parents=True); TOPK=5
X=sparse.load_npz(str(INPUT)+'/do026_X.npz').tocsr(); Q=sparse.load_npz(str(INPUT)+'/do026_Q.npz').tocsr(); A=np.load(str(INPUT)+'/do026_balanced_assign8.npy'); N=X.shape[0]
shards=[np.where(A==s)[0] for s in range(8)]; Xsh=[X[idx] for idx in shards]
svd=TruncatedSVD(64,random_state=0); Y=normalize(svd.fit_transform(X)); QY=normalize(svd.transform(Q))
P=[]; PS=[]
for s,idx in enumerate(shards):
 p=normalize(KMeans(n_clusters=min(4,len(idx)),random_state=0,n_init=10).fit(Y[idx]).cluster_centers_); P.append(p)
P=np.vstack(P); owners=np.repeat(np.arange(8),4)
proto=QY@P.T; ss=np.full((Q.shape[0],8),-np.inf)
for z,s in enumerate(owners): ss[:,s]=np.maximum(ss[:,s],proto[:,z])
# central refs for base queries
def topk(a,k=5):
 if len(a)<=k:return np.argsort(-a)
 i=np.argpartition(-a,k-1)[:k];return i[np.argsort(-a[i])]
ref=[]
CS=(Q@X.T).toarray()
for r in range(Q.shape[0]):ref.append(topk(CS[r]))
# benchmark repeated real queries
reps=(2048+Q.shape[0]-1)//Q.shape[0]; QB=sparse.vstack([Q]*reps)[:2048].tocsr(); baseidx=np.arange(QB.shape[0])%Q.shape[0]
G_XSH=None;G_QB=None;G_SH=None
def init(xsh,qb,sh):
 global G_XSH,G_QB,G_SH;G_XSH=xsh;G_QB=qb;G_SH=sh
def worker(arg):
 s,qids=arg
 if len(qids)==0:return s,[],[]
 M=(G_QB[qids]@G_XSH[s].T).toarray(); gids=G_SH[s]; outi=[];outs=[]
 for r in range(M.shape[0]):
  ii=topk(M[r],TOPK);outi.append(gids[ii].astype(np.int32));outs.append(M[r,ii].astype(np.float32))
 return s,qids,(outi,outs)
rows=[]
for m in [2,4,8]:
 selected=np.argsort(-ss,axis=1)[:,:m]
 q_by_sh=[[] for _ in range(8)]
 for qi,b in enumerate(baseidx):
  for s in selected[b]:q_by_sh[int(s)].append(qi)
 tasks=[(s,np.array(q_by_sh[s],dtype=np.int32)) for s in range(8)]
 ctx=mp.get_context('fork');t=time.perf_counter()
 with ctx.Pool(8,initializer=init,initargs=(Xsh,QB,shards)) as pool:res=pool.map(worker,tasks)
 # assemble per query candidates
 cand_ids=[[] for _ in range(QB.shape[0])];cand_sc=[[] for _ in range(QB.shape[0])]
 for s,qids,payload in res:
  if len(qids)==0:continue
  outi,outs=payload
  for pos,qi in enumerate(qids):cand_ids[int(qi)].extend(outi[pos].tolist());cand_sc[int(qi)].extend(outs[pos].tolist())
 rec=[];exact=[]
 for qi,b in enumerate(baseidx):
  ids=np.array(cand_ids[qi]);sc=np.array(cand_sc[qi]);ii=topk(sc,TOPK);got=set(ids[ii].tolist());R=set(ref[b].tolist());rec.append(len(got&R)/TOPK);exact.append(got==R)
 wall=time.perf_counter()-t
 rows.append({'mode':f'routed_top{m}','workers':8,'queries':QB.shape[0],'wall_seconds':wall,'qps':QB.shape[0]/wall,'mean_recall_at5':np.mean(rec),'exact_top5_rate':np.mean(exact),'mean_shards_contacted':m,'summary_bytes':P.nbytes})
pd.DataFrame(rows).to_csv(OUT+'/do026_routed_process_benchmark.csv',index=False);print(pd.DataFrame(rows).to_string(index=False))
