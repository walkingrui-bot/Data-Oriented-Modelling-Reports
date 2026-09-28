import os
import time, math, multiprocessing as mp, queue, json
from pathlib import Path
from collections import defaultdict
import numpy as np, pandas as pd
from scipy import sparse
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import KMeans
from sklearn.preprocessing import normalize

INPUT=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent.parent/'027')))
OUT=Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_028')))
OUT.mkdir(exist_ok=True, parents=True); NS=8; TOPK=5; ROUTE_K=4; NPLANS=240
CRIT=6; DELAY=0.35; DEADLINE=0.08
X=sparse.load_npz(INPUT/'do026_X.npz').tocsr(); Q=sparse.load_npz(INPUT/'do026_Q.npz').tocsr(); A=np.load(INPUT/'do026_balanced_assign8.npy')
N=X.shape[0]


def topk(a,k=5):
    a=np.asarray(a).ravel()
    if len(a)<=k: return np.argsort(-a)
    ii=np.argpartition(-a,k-1)[:k]
    return ii[np.argsort(-a[ii])]

# Frozen real retrieval/dependency workload
CS=(Q[:NPLANS]@X.T).toarray()
REF=[topk(CS[i],TOPK) for i in range(NPLANS)]
shards=[np.where(A==s)[0] for s in range(NS)]
S=(X@X.T).toarray(); np.fill_diagonal(S,-np.inf)
DEPS=[topk(S[i],2).astype(int) for i in range(N)]
ref_targets=[]
for qi in range(NPLANS):
    z=set(map(int,REF[qi]))
    for j in REF[qi]: z.update(map(int,DEPS[int(j)]))
    ref_targets.append(np.array(sorted(z),dtype=int))

# Compact routing and replica placement, frozen family from 026/027
svd=TruncatedSVD(n_components=64,random_state=0)
Y=normalize(svd.fit_transform(X)); QY=normalize(svd.transform(Q[:NPLANS]))
cent=np.zeros((NS,Y.shape[1]))
for s,idx in enumerate(shards): cent[s]=normalize(Y[idx].mean(axis=0,keepdims=True))[0]
ys=Y@cent.T
backup=np.zeros(N,dtype=int)
for i in range(N):
    order=np.argsort(-ys[i]); backup[i]=next(int(s) for s in order if s!=A[i])
# hit heat from full 500-query frozen workload, as 027
CS500=(Q@X.T).toarray(); hit=np.zeros(N,dtype=int)
for qi in range(Q.shape[0]):
    for j in topk(CS500[qi],TOPK): hit[j]+=1
hot_order=np.lexsort((np.arange(N),-hit)); hot25=set(map(int,hot_order[:int(math.ceil(N*.25))]))


def make_physical(rep):
    phys=[]
    for s in range(NS):
        ids=set(map(int,shards[s]))
        if rep=='hot25':
            for i in hot25:
                if backup[i]==s: ids.add(i)
        elif rep=='full1':
            for i in range(N):
                if backup[i]==s: ids.add(i)
        phys.append(np.array(sorted(ids),dtype=int))
    return phys


def route_scores(phys):
    P=[]; PO=[]
    for s,idx in enumerate(phys):
        k=min(4,len(idx))
        c=normalize(KMeans(n_clusters=k,random_state=0,n_init=10).fit(Y[idx]).cluster_centers_)
        P.append(c); PO.extend([s]*k)
    P=np.vstack(P); PO=np.asarray(PO)
    ps=QY@P.T; sc=np.full((NPLANS,NS),-np.inf)
    for z,s in enumerate(PO): sc[:,s]=np.maximum(sc[:,s],ps[:,z])
    return sc

# Worker uses real local sparse matrix and shared mutable state.
def worker_loop(s, phys_ids, reqq, respq, values, versions):
    local_ids=np.asarray(phys_ids,dtype=int)
    Xloc=X[local_ids]
    vals=np.frombuffer(values,dtype=np.int64); vers=np.frombuffer(versions,dtype=np.int64)
    while True:
        cmd=reqq.get()
        if cmd['op']=='stop': return
        rid=cmd['rid']; op=cmd['op']
        if op=='search':
            d=cmd.get('delay',0.0)
            if d: time.sleep(d)
            sc=(Q[cmd['qi']]@Xloc.T).toarray().ravel(); ii=topk(sc,TOPK)
            respq.put((rid,op,s,local_ids[ii].tolist(),sc[ii].tolist()))
        elif op=='read':
            ids=np.asarray(cmd['ids'],dtype=int)
            respq.put((rid,op,s,ids.tolist(),vals[ids].tolist(),vers[ids].tolist()))
        elif op=='unsafe_set':
            ids=cmd['ids']; newv=cmd['newv']
            for i,v in zip(ids,newv): vals[int(i)]=int(v); vers[int(i)]+=1
            respq.put((rid,op,s,len(ids)))
        elif op=='cas_set':
            ids=cmd['ids']; exp=cmd['exp']; newv=cmd['newv']; conflict=[]
            for i,e,v in zip(ids,exp,newv):
                i=int(i)
                if int(vers[i])==int(e): vals[i]=int(v); vers[i]+=1
                else: conflict.append((i,int(vals[i]),int(vers[i])))
            respq.put((rid,op,s,conflict))
        elif op=='atomic_add':
            ids=cmd['ids']; deltas=cmd.get('deltas',[1]*len(ids))
            for i,d in zip(ids,deltas): vals[int(i)]+=int(d); vers[int(i)]+=1
            respq.put((rid,op,s,len(ids)))
        elif op=='snapshot':
            ids=np.asarray(cmd['ids'],dtype=int)
            respq.put((rid,op,s,ids.tolist(),vals[ids].tolist(),vers[ids].tolist()))

class Cluster:
    def __init__(self, phys):
        self.ctx=mp.get_context('fork')
        self.values=self.ctx.RawArray('q',N); self.versions=self.ctx.RawArray('q',N)
        self.reqq=[]; self.respq=[]; self.procs=[]; self.stale=[[] for _ in range(NS)]
        for s in range(NS):
            rq=self.ctx.Queue(); pq=self.ctx.Queue()
            p=self.ctx.Process(target=worker_loop,args=(s,phys[s],rq,pq,self.values,self.versions)); p.start()
            self.reqq.append(rq); self.respq.append(pq); self.procs.append(p)
    def close(self):
        for q in self.reqq: q.put({'op':'stop'})
        for p in self.procs:
            p.join(timeout=1)
            if p.is_alive(): p.terminate(); p.join()
    def send(self,s,cmd): self.reqq[s].put(cmd)
    def recv(self,s,rid,timeout=2.0):
        t0=time.perf_counter()
        # stale buffered first
        keep=[]
        for item in self.stale[s]:
            if item[0]==rid: self.stale[s]=keep+[x for x in self.stale[s] if x is not item]; return item
            keep.append(item)
        while True:
            rem=max(0.001,timeout-(time.perf_counter()-t0))
            if rem<=0.001 and time.perf_counter()-t0>=timeout: raise queue.Empty
            item=self.respq[s].get(timeout=rem)
            if item[0]==rid: return item
            self.stale[s].append(item)
    def vals(self): return np.frombuffer(self.values,dtype=np.int64).copy()


def merge_payload(payloads):
    best={}
    for item in payloads:
        ids=item[3]; sc=item[4]
        for i,v in zip(ids,sc):
            if i not in best or v>best[i]: best[i]=v
    if not best: return np.array([],dtype=int)
    ids=np.fromiter(best.keys(),dtype=int); sc=np.array([best[i] for i in ids])
    return ids[topk(sc,min(TOPK,len(ids)))]


def groups_by_owner(ids):
    d=defaultdict(list)
    for i in ids: d[int(A[int(i)])].append(int(i))
    return d

PHASE=[]
for i in range(NPLANS):
    if i<40: PHASE.append('healthy_a')
    elif i<80: PHASE.append('shard_down')
    elif i<100: PHASE.append('recovery')
    elif i<140: PHASE.append('straggler')
    elif i<180: PHASE.append('healthy_b')
    elif i<220: PHASE.append('version_conflict')
    else: PHASE.append('final')

# fixed external update schedule in conflict phase: central top-1 object
conf_target={i:int(REF[i][0]) for i in range(180,220)}


def run_policy(name,rep,adaptive,versioned):
    phys=make_physical(rep); rscore=route_scores(phys); cl=Cluster(phys)
    health=[True]*NS; known_slow=set(); pending=defaultdict(lambda:defaultdict(int))
    pending_peak=0; reroutes=0; timeouts=0; cas_retries=0; dropped_writes=0; replayed=0
    rows=[]; intended=np.zeros(N,dtype=np.int64); external=np.zeros(N,dtype=np.int64)
    # every policy experiences same exogenous updates, independent of its retrieval success
    for i in range(180,220): external[conf_target[i]]+=1
    try:
      for qi in range(NPLANS):
        phase=PHASE[qi]
        # phase transitions
        if qi==40: health[CRIT]=False
        if qi==80:
            health[CRIT]=True
            # replay deferred deltas on recovery
            if pending[CRIT]:
                ids=list(pending[CRIT].keys()); ds=[pending[CRIT][x] for x in ids]; rid=f'replay-{qi}'
                cl.send(CRIT,{'op':'atomic_add','rid':rid,'ids':ids,'deltas':ds}); cl.recv(CRIT,rid)
                replayed+=sum(ds); pending[CRIT].clear()
        if qi==100: known_slow=set()  # initially unknown at straggler entry
        if qi==140: known_slow.clear()

        t0=time.perf_counter(); route=np.argsort(-rscore[qi]).tolist(); payload=[]; contacted=[]; plan_reroutes=0; plan_timeout=0
        accepted=True
        if adaptive:
            eligible=[s for s in route if health[s] and s not in known_slow]
            selected=eligible[:ROUTE_K]
        else:
            selected=route[:ROUTE_K]
            if any(not health[s] for s in selected): accepted=False

        if accepted:
            # send real local searches
            for s in selected:
                delay=DELAY if (phase=='straggler' and s==CRIT) else 0.0
                rid=f'q{qi}-s{s}-{name}'
                cl.send(s,{'op':'search','rid':rid,'qi':qi,'delay':delay}); contacted.append((s,rid))
            if adaptive and phase=='straggler' and CRIT in selected and CRIT not in known_slow:
                # collect fast responses up to deadline; abandon slow shard once three responses are available
                deadline=time.perf_counter()+DEADLINE; got=[]; missing=[]
                while time.perf_counter()<deadline and len(got)<len(contacted):
                    progress=False
                    for s,rid in contacted:
                        if any(x[0]==s for x in got): continue
                        try:
                            item=cl.respq[s].get_nowait()
                            if item[0]==rid: got.append((s,item)); progress=True
                            else: cl.stale[s].append(item)
                        except queue.Empty: pass
                    if len(got)>=ROUTE_K-1: break
                    if not progress: time.sleep(0.0005)
                payload.extend([x[1] for x in got])
                got_s={x[0] for x in got}
                if CRIT not in got_s:
                    known_slow.add(CRIT); plan_timeout=1; timeouts+=1
                    # progressive expansion: replace the slow shard by next best healthy, noncontacted shard
                    cand=next((s for s in route if health[s] and s not in known_slow and s not in [x[0] for x in contacted]),None)
                    if cand is not None:
                        rid=f'q{qi}-reroute-s{cand}-{name}'; cl.send(cand,{'op':'search','rid':rid,'qi':qi,'delay':0.0})
                        payload.append(cl.recv(cand,rid)); plan_reroutes+=1; reroutes+=1
                # If critical returned in time, gather any other missing selected response normally.
                for s,rid in contacted:
                    if s in got_s or (s==CRIT and s in known_slow): continue
                    try: payload.append(cl.recv(s,rid,timeout=1.0))
                    except queue.Empty: pass
            else:
                for s,rid in contacted:
                    try: payload.append(cl.recv(s,rid,timeout=2.0))
                    except queue.Empty: accepted=False; break

        got=merge_payload(payload) if accepted else np.array([],dtype=int)
        R=set(map(int,REF[qi])); G=set(map(int,got)); recall=len(R&G)/TOPK if len(got) else 0.0; exact=(R==G)
        target=set(map(int,got))
        for j in got: target.update(map(int,DEPS[int(j)]))
        target=np.array(sorted(target),dtype=int)
        rt=set(map(int,ref_targets[qi])); cov=len(set(map(int,target))&rt)/len(rt) if len(rt) else 1.0; texact=(set(map(int,target))==rt)
        immediate=True; plan_dropped=0; plan_deferred=0; plan_cas=0; conflict_in_plan=0

        if accepted:
            intended[target]+=1
            g=groups_by_owner(target)
            reads={}
            # read snapshots from live owners; unavailable writes are either deferred or lost
            for s,ids in g.items():
                if not health[s]:
                    immediate=False
                    if adaptive:
                        for x in ids: pending[s][x]+=1; plan_deferred+=1
                    else:
                        plan_dropped+=len(ids); dropped_writes+=len(ids)
                    continue
                rid=f'read-{qi}-{s}-{name}'; cl.send(s,{'op':'read','rid':rid,'ids':ids}); rr=cl.recv(s,rid); reads[s]=(rr[3],rr[4],rr[5])
            # fixed exogenous update, same policy-independent target during conflict phase
            if phase=='version_conflict':
                ext=conf_target[qi]; so=int(A[ext]); rid=f'ext-{qi}-{name}'
                cl.send(so,{'op':'atomic_add','rid':rid,'ids':[ext],'deltas':[1]}); cl.recv(so,rid)
                if ext in target: conflict_in_plan=1
            # commit snapshots
            for s,(ids,oldv,oldver) in reads.items():
                if not versioned:
                    rid=f'uset-{qi}-{s}-{name}'; nv=[int(v)+1 for v in oldv]
                    cl.send(s,{'op':'unsafe_set','rid':rid,'ids':ids,'newv':nv}); cl.recv(s,rid)
                else:
                    rid=f'cas-{qi}-{s}-{name}'; nv=[int(v)+1 for v in oldv]
                    cl.send(s,{'op':'cas_set','rid':rid,'ids':ids,'exp':oldver,'newv':nv}); rr=cl.recv(s,rid)
                    conflicts=rr[3]
                    if conflicts:
                        plan_cas+=len(conflicts); cas_retries+=len(conflicts)
                        # recompute +1 from current authoritative state and retry with returned version
                        ids2=[c[0] for c in conflicts]; exp2=[c[2] for c in conflicts]; nv2=[c[1]+1 for c in conflicts]
                        rid2=f'cas2-{qi}-{s}-{name}'; cl.send(s,{'op':'cas_set','rid':rid2,'ids':ids2,'exp':exp2,'newv':nv2}); rr2=cl.recv(s,rid2)
                        if rr2[3]: raise RuntimeError('second CAS conflict in sequential-owner prototype')
        else:
            # exogenous update still occurs in the environment during conflict phase even if a plan fails
            if phase=='version_conflict':
                ext=conf_target[qi]; so=int(A[ext]); rid=f'extfail-{qi}-{name}'
                cl.send(so,{'op':'atomic_add','rid':rid,'ids':[ext],'deltas':[1]}); cl.recv(so,rid)

        pending_now=sum(sum(d.values()) for d in pending.values()); pending_peak=max(pending_peak,pending_now)
        rows.append({'policy':name,'query':qi,'phase':phase,'accepted':accepted,'recall_at5':recall,'exact_top5':exact,'reference_target_coverage':cov,'exact_reference_target_set':texact,
                     'latency_s':time.perf_counter()-t0,'contacted_shards':len(payload),'reroutes':plan_reroutes,'timeout':plan_timeout,
                     'target_objects':len(target),'deferred_writes':plan_deferred,'dropped_writes':plan_dropped,'cas_retries':plan_cas,'conflict_target_in_plan':conflict_in_plan,'pending_after_plan':pending_now})
      # final drain all pending after system fully healthy
      health=[True]*NS
      for s,d in list(pending.items()):
          if d:
              ids=list(d.keys()); ds=[d[x] for x in ids]; rid=f'final-replay-{s}-{name}'
              cl.send(s,{'op':'atomic_add','rid':rid,'ids':ids,'deltas':ds}); cl.recv(s,rid); replayed+=sum(ds); d.clear()
      actual=cl.vals()
    finally:
      cl.close()

    # policy-internal expected state: its own accepted work + fixed exogenous updates
    expected=intended+external
    internal_l1=int(np.abs(actual-expected).sum()); internal_den=int(expected.sum())
    # serial reference mission: central reference plan for every query + same exogenous updates
    oracle=np.zeros(N,dtype=np.int64)
    for z in ref_targets: oracle[z]+=1
    oracle+=external
    oracle_l1=int(np.abs(actual-oracle).sum()); oracle_den=int(oracle.sum())
    df=pd.DataFrame(rows)
    summary={
      'policy':name,'replication':rep,'adaptive':adaptive,'versioned_commit':versioned,
      'plans':NPLANS,'accepted_rate':float(df.accepted.mean()),'mean_recall_at5':float(df.recall_at5.mean()),'exact_top5_rate':float(df.exact_top5.mean()),
      'mean_reference_target_coverage':float(df.reference_target_coverage.mean()),'exact_reference_target_set_rate':float(df.exact_reference_target_set.mean()),
      'median_latency_ms':float(df.latency_s.median()*1000),'p95_latency_ms':float(df.latency_s.quantile(.95)*1000),
      'failure_phase_accepted_rate':float(df[df.phase=='shard_down'].accepted.mean()),'failure_phase_mean_recall':float(df[df.phase=='shard_down'].recall_at5.mean()),
      'straggler_phase_median_latency_ms':float(df[df.phase=='straggler'].latency_s.median()*1000),'straggler_phase_mean_recall':float(df[df.phase=='straggler'].recall_at5.mean()),
      'reroutes':int(reroutes),'timeouts':int(timeouts),'cas_retries':int(cas_retries),'conflict_plans_hit':int(df.conflict_target_in_plan.sum()),
      'dropped_writes':int(dropped_writes),'replayed_writes':int(replayed),'pending_peak':int(pending_peak),
      'internal_state_l1_error':internal_l1,'internal_state_error_fraction':internal_l1/internal_den if internal_den else 0.0,
      'reference_oracle_l1_error':oracle_l1,'reference_oracle_error_fraction':oracle_l1/oracle_den if oracle_den else 0.0,
      'final_exact_object_fraction_vs_internal':float(np.mean(actual==expected)),
      'final_exact_object_fraction_vs_reference':float(np.mean(actual==oracle)),
      'actual_total_state_increments':int(actual.sum()),'internal_expected_increments':internal_den,'reference_expected_increments':oracle_den,
    }
    return df,summary,actual,expected,oracle

policies=[
 ('static_barrier_none','none',False,False),
 ('adaptive_hot25_unsafe','hot25',True,False),
 ('adaptive_hot25_versioned','hot25',True,True),
 ('adaptive_full1_versioned','full1',True,True),
]
allrows=[]; sums=[]
for p in policies:
    print('RUN',p,flush=True)
    df,s,actual,expected,oracle=run_policy(*p); allrows.append(df); sums.append(s)
    np.save(OUT/f'do028_final_state_{p[0]}.npy',actual)
    print(json.dumps(s,indent=2),flush=True)
plan=pd.concat(allrows,ignore_index=True); plan.to_csv(OUT/'do028_plan_trace.csv',index=False)
sdf=pd.DataFrame(sums); sdf.to_csv(OUT/'do028_policy_summary.csv',index=False)
phase=plan.groupby(['policy','phase']).agg(plans=('query','count'),accepted_rate=('accepted','mean'),mean_recall_at5=('recall_at5','mean'),mean_target_coverage=('reference_target_coverage','mean'),median_latency_ms=('latency_s',lambda x:1000*x.median()),p95_latency_ms=('latency_s',lambda x:1000*x.quantile(.95)),deferred_writes=('deferred_writes','sum'),dropped_writes=('dropped_writes','sum'),cas_retries=('cas_retries','sum'),reroutes=('reroutes','sum')).reset_index()
phase.to_csv(OUT/'do028_phase_summary.csv',index=False)
meta={'objects':N,'plans':NPLANS,'shards':NS,'topk':TOPK,'route_shards':ROUTE_K,'critical_shard':CRIT,'straggler_delay_s':DELAY,'adaptive_deadline_s':DEADLINE,
      'phases':{'healthy_a':[0,39],'shard_down':[40,79],'recovery':[80,99],'straggler':[100,139],'healthy_b':[140,179],'version_conflict':[180,219],'final':[220,239]},
      'evidence':'Real ontology objects, query vectors, shard assignment and semantic dependencies are frozen from 026/027. Failure, delay and exogenous version changes are controlled stress injections. Eight persistent worker processes execute local sparse retrieval and owner-scoped state operations.'}
(OUT/'do028_summary.json').write_text(json.dumps({'meta':meta,'policies':sums},indent=2),encoding='utf-8')
print('\nSUMMARY\n',sdf.to_string(index=False))
