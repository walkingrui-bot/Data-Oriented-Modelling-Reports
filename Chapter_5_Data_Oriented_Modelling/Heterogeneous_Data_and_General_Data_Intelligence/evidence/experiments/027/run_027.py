import os
import os, time, json, math, multiprocessing as mp
from pathlib import Path
from collections import defaultdict
import numpy as np, pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

INPUT=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent.parent/'027')))
OUT=Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_027')))
OUT.mkdir(exist_ok=True, parents=True); TOPK=5; NS=8
X=sparse.load_npz(INPUT/'do026_X.npz').tocsr(); Q=sparse.load_npz(INPUT/'do026_Q.npz').tocsr(); A=np.load(INPUT/'do026_balanced_assign8.npy')
N=X.shape[0]; QN=Q.shape[0]

def topk(a,k=5):
    a=np.asarray(a)
    if a.size<=k: return np.argsort(-a)
    ii=np.argpartition(-a,k-1)[:k]
    return ii[np.argsort(-a[ii])]

# ---- Frozen real workload from 026 ----
CS=(Q@X.T).toarray()
REF=[topk(CS[i],TOPK) for i in range(QN)]
shards=[np.where(A==s)[0] for s in range(NS)]
raw_proxy=np.diff(X.indptr).astype(np.int64)  # sparse-state payload proxy; raw bytes unavailable in saved array

# SVD state for compact routing / backup placement
svd=TruncatedSVD(n_components=64,random_state=0)
Y=normalize(svd.fit_transform(X)); QY=normalize(svd.transform(Q))
cent=np.zeros((NS,Y.shape[1]))
for s,idx in enumerate(shards): cent[s]=normalize(Y[idx].mean(axis=0,keepdims=True))[0]

# Four prototypes/shard, same routing family as 026
P=[]; PO=[]
for s,idx in enumerate(shards):
    k=min(4,len(idx))
    c=normalize(KMeans(n_clusters=k,random_state=0,n_init=10).fit(Y[idx]).cluster_centers_)
    P.append(c); PO.extend([s]*k)
P=np.vstack(P); PO=np.asarray(PO)
proto=QY@P.T
base_shard_score=np.full((QN,NS),-np.inf)
for z,s in enumerate(PO): base_shard_score[:,s]=np.maximum(base_shard_score[:,s],proto[:,z])

# Actual workload hit frequency and dependency-boundary score
hit=np.zeros(N,dtype=int)
for r in REF:
    for j in r: hit[j]+=1
S=(X@X.T).toarray(); np.fill_diagonal(S,-1)
knn=[]; boundary=np.zeros(N,dtype=int)
for i in range(N):
    js=topk(S[i],5); knn.append(js)
    boundary[i]=sum(A[j]!=A[i] for j in js)

# Semantic backup owner: best non-primary centroid for each state object
backup=np.zeros(N,dtype=int)
ys=Y@cent.T
for i in range(N):
    order=np.argsort(-ys[i]); backup[i]=next(int(s) for s in order if s!=A[i])

# deterministic replication policies
K25=int(math.ceil(N*0.25))
# stable tie-break: score desc then index asc
hot_order=np.lexsort((np.arange(N),-hit))
bound_order=np.lexsort((np.arange(N),-boundary,-hit))
rep_sets={
    'none': np.array([],dtype=int),
    'hot25': hot_order[:K25],
    'boundary25': bound_order[:K25],
    'full1': np.arange(N,dtype=int),
}

# physical contents by policy
physical={}
for pol,rset in rep_sets.items():
    phys=[]
    rset=set(map(int,rset))
    for s in range(NS):
        ids=set(map(int,shards[s]))
        for i in rset:
            if backup[i]==s: ids.add(i)
        phys.append(np.array(sorted(ids),dtype=int))
    physical[pol]=phys

# payload overhead measured using actual TF-IDF sparse bytes per row
row_bytes=np.zeros(N,dtype=np.int64)
for i in range(N):
    row_bytes[i]=X.data[X.indptr[i]:X.indptr[i+1]].nbytes + X.indices[X.indptr[i]:X.indptr[i+1]].nbytes
base_bytes=int(row_bytes.sum())
rep_meta=[]
for pol,rset in rep_sets.items():
    extra=int(row_bytes[np.asarray(rset,dtype=int)].sum()) if len(rset) else 0
    rep_meta.append({'policy':pol,'replicated_objects':len(rset),'object_fraction':len(rset)/N,'sparse_state_extra_bytes':extra,'storage_overhead_ratio':extra/base_bytes})

# -------- A: one-shard loss --------
fail_rows=[]
for pol in rep_sets:
    phys=physical[pol]
    # prototypes over physical content so router knows backups exist
    PP=[]; PPO=[]
    for s,idx in enumerate(phys):
        k=min(4,len(idx))
        c=normalize(KMeans(n_clusters=k,random_state=0,n_init=10).fit(Y[idx]).cluster_centers_)
        PP.append(c); PPO.extend([s]*k)
    PP=np.vstack(PP); PPO=np.asarray(PPO)
    ps=QY@PP.T; shardscore=np.full((QN,NS),-np.inf)
    for z,s in enumerate(PPO): shardscore[:,s]=np.maximum(shardscore[:,s],ps[:,z])
    for failed in range(NS):
        healthy=[s for s in range(NS) if s!=failed]
        # best possible over all healthy physical contents
        avail=np.array(sorted(set().union(*[set(map(int,phys[s])) for s in healthy])),dtype=int)
        rec_all=[]; ex_all=[]
        for qi in range(QN):
            got=avail[topk(CS[qi,avail],TOPK)]
            R=set(map(int,REF[qi])); G=set(map(int,got)); rec_all.append(len(R&G)/TOPK); ex_all.append(R==G)
        # compact routed top4 among healthy
        rec4=[]; ex4=[]; frac4=[]
        for qi in range(QN):
            ss=[s for s in np.argsort(-shardscore[qi]) if s!=failed][:4]
            cand=np.array(sorted(set().union(*[set(map(int,phys[s])) for s in ss])),dtype=int)
            got=cand[topk(CS[qi,cand],TOPK)]
            R=set(map(int,REF[qi])); G=set(map(int,got)); rec4.append(len(R&G)/TOPK); ex4.append(R==G); frac4.append(len(cand)/N)
        fail_rows.append({
            'replication':pol,'failed_shard':failed,'failed_primary_objects':len(shards[failed]),
            'reference_hit_share_on_failed_shard':sum(hit[shards[failed]])/(QN*TOPK),
            'all_healthy_recall_at5':np.mean(rec_all),'all_healthy_exact_top5':np.mean(ex_all),
            'routed_top4_recall_at5':np.mean(rec4),'routed_top4_exact_top5':np.mean(ex4),'routed_top4_scored_fraction':np.mean(frac4)
        })
fail_df=pd.DataFrame(fail_rows); fail_df.to_csv(OUT/'do027_single_shard_failure.csv',index=False)
pd.DataFrame(rep_meta).to_csv(OUT/'do027_replication_storage.csv',index=False)

# -------- B: actual straggler/timeout process experiment --------
# Choose the shard that owns the largest share of central top-5 hits (measured, not invented).
shard_hit=np.array([hit[shards[s]].sum() for s in range(NS)])
CRIT=int(np.argmax(shard_hit))
DELAY=0.35; DEADLINE=0.16; REPS=5

# result merge helper
def compute_local(xsub, ids, q):
    M=(q@xsub.T).toarray(); oi=[]; os=[]
    for r in range(M.shape[0]):
        ii=topk(M[r],TOPK); oi.append(ids[ii].astype(np.int32)); os.append(M[r,ii].astype(np.float32))
    return oi,os

def proc_once(s, ids, delay, qout):
    if delay>0: time.sleep(delay)
    oi,os=compute_local(X[ids],ids,Q)
    qout.put((s,oi,os))

def merge_payload(payloads):
    rec=[]; ex=[]
    for qi in range(QN):
        ids=[]; sc=[]
        for _,oi,os in payloads:
            ids.extend(oi[qi].tolist()); sc.extend(os[qi].tolist())
        if not ids:
            rec.append(0); ex.append(False); continue
        ids=np.asarray(ids); sc=np.asarray(sc); ii=topk(sc,TOPK); G=set(ids[ii].tolist()); R=set(map(int,REF[qi])); rec.append(len(G&R)/TOPK); ex.append(G==R)
    return float(np.mean(rec)),float(np.mean(ex))

strag=[]
for pol in ['none','hot25','full1']:
    phys=physical[pol]
    for mode in ['barrier','deadline']:
        walls=[]; recs=[]; exs=[]; nrecv=[]
        for rr in range(REPS):
            ctx=mp.get_context('fork'); qout=ctx.Queue(); ps=[]; t0=time.perf_counter()
            for s in range(NS):
                p=ctx.Process(target=proc_once,args=(s,phys[s],DELAY if s==CRIT else 0.0,qout)); p.start(); ps.append(p)
            payload=[]
            if mode=='barrier':
                for _ in range(NS): payload.append(qout.get())
            else:
                while time.perf_counter()-t0 < DEADLINE and len(payload)<NS:
                    rem=max(0.001,DEADLINE-(time.perf_counter()-t0))
                    try: payload.append(qout.get(timeout=rem))
                    except Exception: break
            wall=time.perf_counter()-t0
            for p in ps:
                if p.is_alive(): p.terminate()
                p.join()
            r,e=merge_payload(payload); walls.append(wall); recs.append(r); exs.append(e); nrecv.append(len(payload))
        strag.append({'replication':pol,'mode':mode,'critical_shard':CRIT,'critical_reference_hit_share':shard_hit[CRIT]/(QN*TOPK),'injected_delay_s':DELAY,'deadline_s':DEADLINE,'repetitions':REPS,'median_wall_s':float(np.median(walls)),'mean_wall_s':float(np.mean(walls)),'mean_recall_at5':float(np.mean(recs)),'mean_exact_top5':float(np.mean(exs)),'mean_shards_received':float(np.mean(nrecv))})
pd.DataFrame(strag).to_csv(OUT/'do027_straggler_timeout.csv',index=False)

# -------- C: concurrent state updates over real dependency-derived targets --------
# Directed semantic-neighbour updates, repeated only for timing/contention amortization.
directed=[]
for i,js in enumerate(knn):
    for j in js: directed.append((i,int(j)))
base_targets=np.array([j for _,j in directed],dtype=np.int32)
NOPS=120000
reps=(NOPS+len(base_targets)-1)//len(base_targets); targets=np.tile(base_targets,reps)[:NOPS]
WORKERS=8; TRIALS=5

G_ARR=None; G_LOCK=None; G_LOCKS=None; G_A=None

def init_arr(arr,lock=None,locks=None,a=None):
    global G_ARR,G_LOCK,G_LOCKS,G_A; G_ARR=arr;G_LOCK=lock;G_LOCKS=locks;G_A=a

def upd_naive(tg):
    arr=np.frombuffer(G_ARR,dtype=np.int64)
    for z,t in enumerate(tg):
        old=arr[int(t)]
        if (z & 31)==0: time.sleep(0)
        arr[int(t)]=old+1

def upd_global(tg):
    arr=np.frombuffer(G_ARR,dtype=np.int64)
    for t in tg:
        with G_LOCK: arr[int(t)]+=1

def upd_shardlock(tg):
    arr=np.frombuffer(G_ARR,dtype=np.int64)
    for t in tg:
        with G_LOCKS[int(G_A[int(t)])]: arr[int(t)]+=1

def run_updates(mode):
    ctx=mp.get_context('fork'); arr=ctx.RawArray('q',N); chunks=np.array_split(targets,WORKERS)
    lock=ctx.Lock() if mode=='global_lock' else None
    locks=[ctx.Lock() for _ in range(NS)] if mode=='shard_locks' else None
    fn={'naive_rmw':upd_naive,'global_lock':upd_global,'shard_locks':upd_shardlock}[mode]
    t0=time.perf_counter(); ps=[]
    for c in chunks:
        p=ctx.Process(target=fn,args=(c,)); p.start(); ps.append(p)
    # globals inherited by fork must be set before process start; this wrapper cannot use initializer
    # fallback: restart using module globals is handled outside (see below)
    for p in ps: p.join()
    wall=time.perf_counter()-t0; vals=np.frombuffer(arr,dtype=np.int64).copy()
    return wall,vals

# direct fork-global runner
def bench_mode(mode):
    global G_ARR,G_LOCK,G_LOCKS,G_A
    ctx=mp.get_context('fork'); rows=[]; chunks=np.array_split(targets,WORKERS)
    for tr in range(TRIALS):
        arr=ctx.RawArray('q',N); G_ARR=arr; G_A=A; G_LOCK=ctx.Lock() if mode=='global_lock' else None; G_LOCKS=[ctx.Lock() for _ in range(NS)] if mode=='shard_locks' else None
        fn={'naive_rmw':upd_naive,'global_lock':upd_global,'shard_locks':upd_shardlock}[mode]
        t0=time.perf_counter(); ps=[ctx.Process(target=fn,args=(c,)) for c in chunks]
        for p in ps:p.start()
        for p in ps:p.join()
        wall=time.perf_counter()-t0; vals=np.frombuffer(arr,dtype=np.int64).copy(); actual=int(vals.sum())
        rows.append({'mode':mode,'trial':tr,'workers':WORKERS,'operations':NOPS,'wall_seconds':wall,'updates_per_s':NOPS/wall,'actual_applied':actual,'lost_updates':NOPS-actual,'lost_fraction':(NOPS-actual)/NOPS,'objects_with_count_error':int(np.sum(vals!=np.bincount(targets,minlength=N)))})
    return rows
updrows=[]
for mode in ['naive_rmw','global_lock','shard_locks']: updrows.extend(bench_mode(mode))
pd.DataFrame(updrows).to_csv(OUT/'do027_concurrent_updates.csv',index=False)

# summary
fm=fail_df.groupby('replication').agg(mean_recall=('all_healthy_recall_at5','mean'),worst_recall=('all_healthy_recall_at5','min'),mean_routed4=('routed_top4_recall_at5','mean'),worst_routed4=('routed_top4_recall_at5','min')).reset_index()
storage=pd.DataFrame(rep_meta)
fs=fm.merge(storage,on='replication' if 'replication' in storage.columns else 'policy',how='left') if False else None
upd=pd.DataFrame(updrows).groupby('mode').agg(median_qps=('updates_per_s','median'),mean_lost_fraction=('lost_fraction','mean'),max_lost_fraction=('lost_fraction','max'),mean_error_objects=('objects_with_count_error','mean')).reset_index()
summary={
 'workload':{'objects':N,'queries':QN,'shards':NS,'topk':TOPK,'dependency_directed_edges':len(directed),'concurrent_update_ops':NOPS},
 'critical_shard':{'id':CRIT,'reference_hit_share':float(shard_hit[CRIT]/(QN*TOPK)),'objects':len(shards[CRIT])},
 'failure_summary':fm.to_dict('records'),
 'replication_storage':rep_meta,
 'straggler':strag,
 'concurrent_updates':upd.to_dict('records'),
 'evidence_statement':'All retrieval/state objects and queries are the frozen real ontology workload saved by DISTRIBUTED-ONTOLOGY-COORDINATION-026. Faults, delay, and concurrency are controlled stress injections; no synthetic document content is introduced.'
}
with open(OUT/'do027_summary.json','w') as f:json.dump(summary,f,indent=2)
print(json.dumps(summary,indent=2))
