import os
from pathlib import Path
import json, zipfile, hashlib, os
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
INPUT=Path(os.environ.get('B3_INPUT_DIR', str(Path(__file__).resolve().parent)))
OUT=Path(os.environ.get('B3_OUTPUT_DIR', str(Path.cwd()/'reproduction_027')))
OUT.mkdir(exist_ok=True, parents=True)
f=pd.read_csv(INPUT/'do027_single_shard_failure.csv')
r=pd.read_csv(INPUT/'do027_replication_storage.csv')
s=pd.read_csv(INPUT/'do027_straggler_timeout.csv')
u=pd.read_csv(INPUT/'do027_concurrent_updates.csv')

# summary tables
summ=f.groupby('replication').agg(mean_recall=('all_healthy_recall_at5','mean'),worst_recall=('all_healthy_recall_at5','min'),mean_exact=('all_healthy_exact_top5','mean'),mean_routed4_recall=('routed_top4_recall_at5','mean'),worst_routed4_recall=('routed_top4_recall_at5','min')).reset_index()
summ=summ.merge(r,left_on='replication',right_on='policy').drop(columns=['policy'])
summ.to_csv(OUT/'do027_failure_policy_summary.csv',index=False)
upd=u.groupby('mode').agg(median_updates_per_s=('updates_per_s','median'),mean_lost_fraction=('lost_fraction','mean'),max_lost_fraction=('lost_fraction','max'),mean_error_objects=('objects_with_count_error','mean')).reset_index()
upd.to_csv(OUT/'do027_update_summary.csv',index=False)

# Figure A: storage vs worst recovery
fig,ax=plt.subplots(figsize=(7.4,4.8))
off={'none':(5,5),'hot25':(5,-14),'boundary25':(5,7),'full1':(5,-10)}
for _,z in summ.iterrows():
    ax.scatter(z.storage_overhead_ratio*100,z.worst_recall*100,s=70)
    ax.annotate(z.replication,(z.storage_overhead_ratio*100,z.worst_recall*100),xytext=off.get(z.replication,(5,5)),textcoords='offset points')
ax.set_xlabel('Sparse-state storage overhead (%)');ax.set_ylabel('Worst single-shard-failure recall@5 (%)');ax.set_title('027A — Redundancy buys measurable failure recovery');ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(OUT/'fig027A_redundancy_recovery.png',dpi=190);plt.close(fig)

# Figure B: per-shard recovery
fig,ax=plt.subplots(figsize=(8.0,4.8))
for pol in ['none','hot25','boundary25','full1']:
    z=f[f.replication==pol].sort_values('failed_shard');ax.plot(z.failed_shard,z.all_healthy_recall_at5*100,marker='o',label=pol)
ax.set_xlabel('Failed primary shard');ax.set_ylabel('Recall@5 after failure (%)');ax.set_ylim(75,101);ax.set_title('027B — Recovery depends on which shard disappears');ax.grid(True,alpha=.25);ax.legend();fig.tight_layout();fig.savefig(OUT/'fig027B_shard_failure_profile.png',dpi=190);plt.close(fig)

# Figure C: straggler latency/quality
fig,ax=plt.subplots(figsize=(7.6,4.8))
# barrier points coincide by construction; render them as one common completion point
b=s[s['mode']=='barrier'].iloc[0]
ax.scatter(b.median_wall_s*1000,100,s=80)
ax.annotate('wait-all barrier (all policies)',(b.median_wall_s*1000,100),xytext=(-88,-28),textcoords='offset points',fontsize=8)
for pol,dy in [('none',-10),('hot25',2),('full1',-2)]:
    q=s[(s.replication==pol)&(s['mode']=='quorum7')].iloc[0]
    ax.scatter(q.median_wall_s*1000,q.mean_recall_at5*100,s=70)
    ax.annotate(f'{pol} quorum7',(q.median_wall_s*1000,q.mean_recall_at5*100),xytext=(7,dy),textcoords='offset points',fontsize=8)
ax.set_xlabel('Coordinator wait / orchestration wall time (ms)');ax.set_ylabel('Recall@5 (%)');ax.set_title('027C — A slow shard creates a latency–completeness decision');ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(OUT/'fig027C_straggler_tradeoff.png',dpi=190);plt.close(fig)

# Figure D: update throughput
order=['naive_rmw','global_lock','shard_locks'];med=[u[u['mode']==m].updates_per_s.median() for m in order]
fig,ax=plt.subplots(figsize=(7.4,4.8));ax.bar(order,med);ax.set_ylabel('Median updates/s');ax.set_title('027D — Ownership-scoped synchronization preserves parallelism');ax.tick_params(axis='x',rotation=15);ax.grid(True,axis='y',alpha=.25);fig.tight_layout();fig.savefig(OUT/'fig027D_update_throughput.png',dpi=190);plt.close(fig)

# Figure E: update correctness
lost=[u[u['mode']==m].lost_fraction.mean()*100 for m in order]
fig,ax=plt.subplots(figsize=(7.4,4.8));ax.bar(order,lost);ax.set_ylabel('Mean lost updates (%)');ax.set_title('027E — Uncoordinated concurrent writes lose state');ax.tick_params(axis='x',rotation=15);ax.grid(True,axis='y',alpha=.25);fig.tight_layout();fig.savefig(OUT/'fig027E_update_loss.png',dpi=190);plt.close(fig)

# Markdown evidence note
crit=int(s.critical_shard.iloc[0]);critshare=float(s.critical_reference_hit_share.iloc[0])
