#!/usr/bin/env python3
from pathlib import Path
from itertools import product
import hashlib, json, math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUT=Path('/mnt/data')
N=7
REL=['R+1','R+2','R*2','RNEG']
META=['STORE','RESET']
ACTIONS=REL+META
UNSET=N

# ---------- controlled reasoning world ----------
def rel_apply(x,a):
    if a=='R+1': return (x+1)%N
    if a=='R+2': return (x+2)%N
    if a=='R*2': return (2*x)%N
    if a=='RNEG': return (-x)%N
    raise KeyError(a)

def step(state,a):
    # state = (start,cursor,memory), memory=UNSET if empty
    s,x,m=state
    if a in REL: return (s,rel_apply(x,a),m)
    if a=='STORE': return (s,x,x)
    if a=='RESET': return (s,s,m)
    raise KeyError(a)

def read(state):
    s,x,m=state
    return UNSET if m==UNSET else ((m-x)%N)

def run(state,program):
    z=state
    for a in program: z=step(z,a)
    return z

# all predictive probes: action programs up to depth 3 followed by READ
PROBES=[()]
for k in [1,2,3]: PROBES += list(product(ACTIONS,repeat=k))
# all states
STATES=[(s,x,m) for s in range(N) for x in range(N) for m in range(N+1)]
SID={z:i for i,z in enumerate(STATES)}

# future-response signature q(s): one-hot READ result after each probe
D=(N+1)*len(PROBES)
Q=np.zeros((len(STATES),D),dtype=np.float64)
for i,z in enumerate(STATES):
    for j,p in enumerate(PROBES):
        y=read(run(z,p)); Q[i,j*(N+1)+y]=1.0

# predictive equivalence classes (exact signatures)
packed=np.packbits(Q.astype(np.uint8),axis=1)
keys=[bytes(r) for r in packed]
classes={}
for i,k in enumerate(keys): classes.setdefault(k,[]).append(i)

# PCA state geometry
mu=Q.mean(0); X=Q-mu
U,S,Vt=np.linalg.svd(X/np.sqrt(len(X)),full_matrices=False)
ev=S*S; frac=ev/ev.sum(); cum=np.cumsum(frac)
stable=float(ev.sum()/ev.max()); part=float(ev.sum()**2/(ev@ev)); d95=int(np.searchsorted(cum,.95)+1); d99=int(np.searchsorted(cum,.99)+1)
K=d99
B=Vt[:K].T
Z=X@B

# heldout split deterministic by state tuple
def bucket(z,mod=5):
    h=hashlib.sha256(str(z).encode()).digest(); return int.from_bytes(h[:4],'little')%mod
train_idx=np.array([i for i,z in enumerate(STATES) if bucket(z)!=0]); test_idx=np.array([i for i,z in enumerate(STATES) if bucket(z)==0])

# fit action-specific affine operator in predictive-state PCA space
ops={}; one_rows=[]
for a in ACTIONS:
    yt=np.array([SID[step(STATES[i],a)] for i in train_idx]); yv=np.array([SID[step(STATES[i],a)] for i in test_idx])
    Xtr=Z[train_idx]; Ytr=Z[yt]; Xte=Z[test_idx]; Yte=Z[yv]
    shift=(Ytr-Xtr).mean(0); reset=Ytr.mean(0)
    Phi=np.c_[Xtr,np.ones(len(Xtr))]; Phite=np.c_[Xte,np.ones(len(Xte))]
    lam=1e-5; R=np.eye(K+1)*lam; R[-1,-1]=lam*.1
    C=np.linalg.solve(Phi.T@Phi+R,Phi.T@Ytr)
    ops[a]=C
    pred=Phite@C
    mse=lambda P: float(np.mean(np.sum((P-Yte)**2,axis=1)))
    one_rows.append(dict(action=a,kind=('relation' if a in REL else 'meta'),n_train=len(train_idx),n_test=len(test_idx),
                         mse_identity=mse(Xte),mse_fixed_shift=mse(Xte+shift),mse_fixed_reset=mse(np.repeat(reset[None,:],len(Xte),0)),mse_affine_operator=mse(pred),
                         improvement_vs_shift=1-mse(pred)/mse(Xte+shift),improvement_vs_reset=1-mse(pred)/mse(np.repeat(reset[None,:],len(Xte),0))))
one=pd.DataFrame(one_rows)

def apply_aff(C,z): return np.r_[z,1.]@C

# two-step composition on heldout states, all action pairs
comp_rows=[]
for a,b in product(ACTIONS,repeat=2):
    errs=[]; rev=[]; direct=[]
    for i in test_idx:
        z0=Z[i]; true=Z[SID[step(step(STATES[i],a),b)]]
        ph=apply_aff(ops[b],apply_aff(ops[a],z0))
        phr=apply_aff(ops[a],apply_aff(ops[b],z0))
        errs.append(np.sum((ph-true)**2)); rev.append(np.sum((phr-true)**2))
        direct.append(np.sum((z0-true)**2))
    comp_rows.append(dict(a=a,b=b,correct_mse=np.mean(errs),reversed_mse=np.mean(rev),identity_mse=np.mean(direct),noncommutative_gain=1-np.mean(errs)/np.mean(rev) if np.mean(rev)>0 else np.nan))
comp=pd.DataFrame(comp_rows)

# exact noncommutativity in world: fraction states where ab != ba and read signatures differ
nc=[]
for a,b in product(ACTIONS,repeat=2):
    state_diff=[]; qdist=[]; read_diff=[]
    for i,z in enumerate(STATES):
        zab=step(step(z,a),b); zba=step(step(z,b),a)
        state_diff.append(zab!=zba)
        qdist.append(np.linalg.norm(Q[SID[zab]]-Q[SID[zba]])/math.sqrt(D))
        read_diff.append(read(zab)!=read(zba))
    nc.append(dict(a=a,b=b,state_noncommute_frac=np.mean(state_diff),future_signature_rms=np.mean(qdist),immediate_read_diff_frac=np.mean(read_diff)))
ncdf=pd.DataFrame(nc)

# movement geometry: all action displacement vectors in predictive state
mov_rows=[]; Mrel=[]; Mmeta=[]
for a in ACTIONS:
    DD=np.vstack([Z[SID[step(z,a)]]-Z[SID[z]] for z in STATES])
    _,ss,vv=np.linalg.svd(DD/np.sqrt(len(DD)),full_matrices=False); ee=ss*ss; ff=ee/ee.sum() if ee.sum() else ee
    mov_rows.append(dict(action=a,kind=('relation' if a in REL else 'meta'),stable_rank=float(ee.sum()/ee.max()) if ee.max()>0 else 0,
                         d95=int(np.searchsorted(np.cumsum(ff),.95)+1) if ee.sum()>0 else 0,top1=float(ff[0]),top3=float(ff[:3].sum()),mean_norm=float(np.linalg.norm(DD,axis=1).mean())))
    (Mrel if a in REL else Mmeta).append(DD)
mov=pd.DataFrame(mov_rows)
Mrel=np.vstack(Mrel); Mmeta=np.vstack(Mmeta)
# relation movement subspace vs meta movement subspace principal angles
_,sr,Vrel=np.linalg.svd(Mrel,full_matrices=False); _,sm,Vmeta=np.linalg.svd(Mmeta,full_matrices=False)
er=sr*sr; em=sm*sm
kr=min(3,np.sum(sr>1e-10)); km=min(3,np.sum(sm>1e-10)); A=Vrel[:kr].T; Bm=Vmeta[:km].T
sv=np.linalg.svd(A.T@Bm,compute_uv=False); angles=np.degrees(np.arccos(np.clip(sv,-1,1)))
# meta residual energy outside top-3 relation movement space
P=A@A.T; meta_total=np.sum(Mmeta*Mmeta); meta_proj=np.sum((Mmeta@P)**2); meta_out=1-meta_proj/meta_total

# reasoning tasks: A path length 3; STORE; RESET; B path length 3; READ
# enumerate all 7*4^6=28672 tasks
trace_rows=[]; reentry=[]; swap=[]; remove_store=[]
for s in range(N):
  for aa in product(REL,repeat=3):
    # state after A
    z0=(s,s,UNSET); z=z0
    pathA=[]
    for a in aa: z=step(z,a); pathA.append(z[1])
    z_store=step(z,'STORE'); z_reset=step(z_store,'RESET')
    reentry.append(dict(start=s,A='>'.join(aa),A_end=z[1],same_cursor=int(z_reset[1]==z0[1]),
                        raw_state_equal=int(z_reset==z0),future_rms=float(np.linalg.norm(Q[SID[z_reset]]-Q[SID[z0]])/math.sqrt(D)),
                        pca_distance=float(np.linalg.norm(Z[SID[z_reset]]-Z[SID[z0]]))))
    for bb in product(REL,repeat=3):
        zz=z_reset; pathB=[]
        for b in bb: zz=step(zz,b); pathB.append(zz[1])
        y=read(zz)
        # counterfactual swap RESET then STORE after A: memory becomes start
        zs=step(step(z,'RESET'),'STORE'); zsw=zs
        for b in bb: zsw=step(zsw,b)
        ysw=read(zsw)
        # no store: reset then B, memory unset
        zn=step(z,'RESET')
        for b in bb: zn=step(zn,b)
        yn=read(zn)
        swap.append(dict(start=s,A='>'.join(aa),B='>'.join(bb),gold=y,swap_store_reset=ysw,changed=int(y!=ysw)))
        remove_store.append(dict(start=s,A='>'.join(aa),B='>'.join(bb),gold=y,no_store=yn,changed=int(y!=yn)))
        if len(trace_rows)<5000:
            trace_rows.append(dict(start=s,A='>'.join(aa),B='>'.join(bb),A1=pathA[0],A2=pathA[1],A3=pathA[2],B1=pathB[0],B2=pathB[1],B3=pathB[2],answer=y))
reentry=pd.DataFrame(reentry); swap=pd.DataFrame(swap); remove_store=pd.DataFrame(remove_store); traces=pd.DataFrame(trace_rows)

# same visible cursor but different memory: pair states by (start,cursor), compare predictive signatures across memories
amb=[]
for s in range(N):
  for x in range(N):
    ids=[SID[(s,x,m)] for m in range(N+1)]
    ds=[]
    for i in range(len(ids)):
      for j in range(i+1,len(ids)):
        ds.append(np.linalg.norm(Q[ids[i]]-Q[ids[j]])/math.sqrt(D))
    amb.append(dict(start=s,cursor=x,mean_future_rms=float(np.mean(ds)),min_future_rms=float(np.min(ds)),max_future_rms=float(np.max(ds))))
amb=pd.DataFrame(amb)

# reasoning trace local movement: legal program and action-specific gain across stages
# use representative all tasks sample, compute displacements in Z along actual action sequence
rng=np.random.default_rng(20); samples=[]
for _ in range(5000):
    s=int(rng.integers(N)); aa=[REL[int(rng.integers(4))] for _ in range(3)]; bb=[REL[int(rng.integers(4))] for _ in range(3)]
    prog=aa+['STORE','RESET']+bb
    z=(s,s,UNSET)
    for stage,a in enumerate(prog):
        z2=step(z,a); d=Z[SID[z2]]-Z[SID[z]]
        samples.append(dict(stage=stage,action=a,kind=('relation' if a in REL else 'meta'),norm=float(np.linalg.norm(d)),**{f'd{i}':d[i] for i in range(min(K,16))}))
        z=z2
traj=pd.DataFrame(samples)
M=traj[[c for c in traj if c.startswith('d')]].to_numpy()
_,st,_=np.linalg.svd(M/np.sqrt(len(M)),full_matrices=False); et=st*st; ft=et/et.sum(); traj_sr=float(et.sum()/et.max()); traj_d95=int(np.searchsorted(np.cumsum(ft),.95)+1)

# save outputs
one.to_csv(OUT/'REASONING-STATE-020_operator_fit.csv',index=False)
comp.to_csv(OUT/'REASONING-STATE-020_composition.csv',index=False)
ncdf.to_csv(OUT/'REASONING-STATE-020_noncommutativity.csv',index=False)
mov.to_csv(OUT/'REASONING-STATE-020_movement.csv',index=False)
reentry.to_csv(OUT/'REASONING-STATE-020_reentry.csv',index=False)
swap.to_csv(OUT/'REASONING-STATE-020_store_reset_swap.csv',index=False)
remove_store.to_csv(OUT/'REASONING-STATE-020_remove_store.csv',index=False)
amb.to_csv(OUT/'REASONING-STATE-020_same_cursor_diff_memory.csv',index=False)
traces.to_csv(OUT/'REASONING-STATE-020_example_traces.csv',index=False)
traj.to_csv(OUT/'REASONING-STATE-020_trace_movements.csv',index=False)

summary={
 'states':len(STATES),'predictive_probes':len(PROBES),'predictive_signature_dim':D,'predictive_equivalence_classes':len(classes),
 'predictive_state_stable_rank':stable,'predictive_state_participation_rank':part,'predictive_state_d95':d95,'predictive_state_d99':d99,'pca_dim_used':K,
 'operator_mse_shift_mean':float(one.mse_fixed_shift.mean()),'operator_mse_affine_mean':float(one.mse_affine_operator.mean()),'operator_improvement_vs_shift_mean':float(one.improvement_vs_shift.mean()),
 'composition_correct_mse_mean':float(comp.correct_mse.mean()),'composition_reversed_mse_mean':float(comp.reversed_mse.mean()),
 'noncommuting_pair_mean_state_fraction':float(ncdf.state_noncommute_frac.mean()),'noncommuting_pair_max_state_fraction':float(ncdf.state_noncommute_frac.max()),
 'relation_movement_stable_rank_mean':float(mov[mov.kind=='relation'].stable_rank.mean()),'meta_movement_stable_rank_mean':float(mov[mov.kind=='meta'].stable_rank.mean()),
 'meta_energy_outside_top3_relation_subspace':float(meta_out),'relation_meta_principal_angles_deg':'|'.join(f'{x:.3f}' for x in angles),
 'reentry_same_cursor_fraction':float(reentry.same_cursor.mean()),'reentry_raw_state_equal_fraction':float(reentry.raw_state_equal.mean()),'reentry_future_rms_mean':float(reentry.future_rms.mean()),'reentry_pca_distance_mean':float(reentry.pca_distance.mean()),
 'same_cursor_diff_memory_future_rms_mean':float(amb.mean_future_rms.mean()),'same_cursor_diff_memory_min_rms_global':float(amb.min_future_rms.min()),
 'store_reset_swap_answer_change_fraction':float(swap.changed.mean()),'remove_store_answer_change_fraction':float(remove_store.changed.mean()),
 'reasoning_trace_movement_stable_rank':traj_sr,'reasoning_trace_movement_d95':traj_d95,'reasoning_trace_top3_energy':float(ft[:3].sum())}
pd.DataFrame([summary]).to_csv(OUT/'REASONING-STATE-020_summary.csv',index=False)

# figures
plt.figure(figsize=(7,4)); plt.plot(np.arange(1,21),cum[:20],marker='o'); plt.axhline(.95,ls='--'); plt.xlabel('predictive-state SVD mode'); plt.ylabel('cumulative energy'); plt.title('Reasoning predictive-state spectrum'); plt.tight_layout(); plt.savefig(OUT/'REASONING-STATE-020_predictive_spectrum.png',dpi=180); plt.close()
plt.figure(figsize=(7,4));
xx=np.arange(len(one)); w=.36
plt.bar(xx-w/2,one.mse_fixed_shift,width=w,label='fixed shift'); plt.bar(xx+w/2,one.mse_affine_operator,width=w,label='state operator'); plt.xticks(xx,one.action,rotation=30); plt.ylabel('held-out MSE'); plt.title('Reasoning actions require state-dependent operators'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'REASONING-STATE-020_operator_fit.png',dpi=180); plt.close()
plt.figure(figsize=(6,4)); vals=[reentry.future_rms.mean(),amb.mean_future_rms.mean()]; plt.bar(['RESET re-entry\nsame cursor','same cursor\ndifferent memory'],vals); plt.ylabel('future-signature RMS'); plt.title('Same visible location, different reasoning state'); plt.tight_layout(); plt.savefig(OUT/'REASONING-STATE-020_reentry.png',dpi=180); plt.close()
plt.figure(figsize=(6,4)); plt.bar(['STORE→RESET','RESET→STORE'],[0,swap.changed.mean()]); plt.ylabel('fraction final answers changed'); plt.ylim(0,1); plt.title('Reasoning operator order is causal'); plt.tight_layout(); plt.savefig(OUT/'REASONING-STATE-020_order_intervention.png',dpi=180); plt.close()

# markdown report
lines=[]
A=lines.append
A('# REASONING-STATE-020 | 从语言控制代数到推理状态：未来响应等价类、回退、记忆与高层算子')
A('')
A('## 研究触发与当时讨论')
A('语言线 015–019 已把语言写成作用于关系/预测状态上的状态依赖非交换生成控制代数。下一步不再问“语言如何运动”，而问：当系统开始保存中间关系、回到旧位置、比较两条路径并提交结果时，是否出现一个可独立定义的 reasoning state？本轮 deliberately 不把“推理=语言”写进设计，而是用可完全枚举的关系世界检验：推理是否可以由 future-response equivalence、关系算子、记忆算子与回退/比较控制共同定义。')
A('')
A('第一版曾尝试训练一个自由生成 GRU 同时记住两条三步路径；模型能读出 phase 与后期 diff，但自由生成尚未稳定学会关系计算，因此该版本没有进入证据链。本轮改为完全可枚举 reasoning world，把模型学习不充分从机制问题中移除，直接检验数学对象本身。')
A('')
A('## 1. 受控关系推理世界')
A(f'对象空间为 Z_{N}。四个关系算子为 R+1, R+2, R*2, RNEG，另有 STORE 与 RESET 两个高层控制动作。reasoning state 写为 r=(s,x,m)：s 为起点，x 为当前 cursor，m 为已保存的中间关系结果；m=UNSET 表示尚未保存。READ(r)=(m-x) mod {N}。完整状态共 {len(STATES)} 个。')
A('')
A('标准推理程序为：三步 A 路径 → STORE → RESET → 三步 B 路径 → READ。它要求系统先把 A 的终点写入 memory，再把 cursor 退回起点，在同一世界中走第二条路径，最后比较 memory 与 cursor。')
A('')
A('## 2. 推理状态的操作性定义：future-response equivalence')
A('对每个状态 r，枚举长度 0–3 的全部未来控制程序（6 个动作的 259 个 probes），记录每个 program 之后 READ 的离散结果。把这些结果的一热向量拼接成 q(r)。定义 r~r\' 当且仅当对全部 probes 有相同未来响应。')
A('')
A(f'392 个内部状态得到 {len(classes)} 个 predictive equivalence classes；也就是说，本实验的 future-response signature 足以把所有 reasoning states 区分开。q(r) 的原始维数为 {D}，SVD stable rank={stable:.3f}，95% 能量维数={d95}，99%={d99}。这里“reasoning state”不是某个词或当前对象，而是“从这里继续做任何允许的控制操作时，未来会怎样”的等价类。')
A('')
A('## 3. 同一个表面位置可以是不同推理状态')
A('RESET 是本轮最关键的干预。标准 A 路径完成 STORE 后执行 RESET，cursor 精确回到最初的 start；如果只观察当前位置，系统“回到了原点”。但 memory 已经写入 A endpoint，因此 future-response state 没有回到原点。')
A('')
A(f'全部 {len(reentry)} 个 start×A-path 条件中，RESET 后 cursor 与初始 cursor 相同的比例为 {reentry.same_cursor.mean():.3f}；完整 reasoning state 真正相等的比例为 {reentry.raw_state_equal.mean():.3f}。两者 future-signature RMS 平均距离为 {reentry.future_rms.mean():.4f}，PCA reasoning-state distance 平均为 {reentry.pca_distance.mean():.4f}。')
A('')
A(f'进一步固定同一 start 与同一 cursor，只改变 memory，未来响应仍保持明显分离：平均 pairwise future-signature RMS={amb.mean_future_rms.mean():.4f}。这直接支持：reasoning state 至少包含当前局部对象之外的 retained relational commitment。')
A('')
A('## 4. 推理动作是状态变换算子')
A('在 q(r) 的 99%-energy PCA 坐标中，对每个动作拟合 affine operator T_a(z)=A_a z+b_a，并在未参与拟合的状态上预测动作后的 future-response state。')
A('')
for _,r in one.iterrows(): A(f'- {r.action}: fixed-shift MSE={r.mse_fixed_shift:.6g}; state-operator MSE={r.mse_affine_operator:.6g}; improvement={100*r.improvement_vs_shift:.2f}%.')
A('')
A(f'六类动作平均相对 fixed-shift 的 held-out 误差下降为 {100*one.improvement_vs_shift.mean():.2f}%。同一个操作不是给状态加一根固定向量；它作用于当前 predictive/reasoning state，并产生条件化转移。')
A('')
A('## 5. 推理代数非交换；正确组合可预测后续状态')
A(f'对全部 36 个两动作组合，在 held-out reasoning states 上用 T_b(T_a(z)) 预测真实两步 future state；平均 MSE={comp.correct_mse.mean():.6g}。把相同两动作反序成 T_a(T_b(z))，平均 MSE={comp.reversed_mse.mean():.6g}。世界本身的 action pairs 平均有 {100*ncdf.state_noncommute_frac.mean():.2f}% 状态满足 ab 与 ba 产生不同内部状态，最高为 {100*ncdf.state_noncommute_frac.max():.1f}%。')
A('')
A(f'直接在完整推理程序中交换 STORE 与 RESET，最终 answer 改变比例为 {100*swap.changed.mean():.2f}%；删除 STORE 后 READ 落入 UNSET/不同答案的比例为 {100*remove_store.changed.mean():.2f}%。因此高层 reasoning operator 的次序不是文本排版，而是因果计算。')
A('')
A('## 6. 关系运动与高层 reasoning generator')
A(f'四个 relation actions 的 movement stable rank 平均为 {mov[mov.kind=="relation"].stable_rank.mean():.3f}；STORE/RESET 为 {mov[mov.kind=="meta"].stable_rank.mean():.3f}。把 relation movement 的前三主方向作为低层关系运动子空间，STORE/RESET 的运动能量有 {100*meta_out:.2f}% 落在该三维子空间之外。前三维 relation/meta 子空间 principal angles 为 {", ".join(f"{x:.2f}°" for x in angles)}。')
A('')
A('因此推理向上生长的方式与 LANGUAGE-HIERARCHICAL-GENERATORS-019 的结构一致：大量步骤复用已有关系算子的有序复合；当任务要求“保存一个关系结果”“回到旧位置但保留承诺”时，会引入少量新的高层 generator，而不是把全部状态空间重新发明一遍。')
A('')
A('## 7. 本轮对“推理是什么”的工作定义')
A('本轮支持把 reasoning state 定义为历史在未来可控行为上的等价类：')
A('')
A('    R = H / ~future')
A('    h1 ~future h2  iff  F(p | h1) = F(p | h2) for every admissible future control program p.')
A('')
A('推理动作 g 属于作用在 R 上的非交换 generator family；标准推理轨迹是')
A('')
A('    r_{t+1} = G(a_t, r_t)[r_t].')
A('')
A('语言动作主要改变当前关系/预测状态；推理开始于系统进一步获得对“关系状态本身”的控制：保存某个中间关系、返回旧局部位置、在保留历史承诺的情况下重新展开另一条轨迹、比较多个可达状态，再把比较结果写回后续状态。')
A('')
A('因此本轮最简工作定义是：')
A('')
A('> **Reasoning is recursive control over an augmented relational state: a noncommutative sequence of operators that preserves, revisits, transforms and compares relational commitments according to their future consequences.**')
A('')
A('中文：**推理是对增广关系状态的递归控制：系统用非交换算子保存、回访、变换并比较关系承诺，并以这些操作对未来可达状态的后果作为计算对象。**')
A('')
A('这一定义把“回到同一个地方”和“回到同一个推理状态”严格区分开。RESET 后 cursor 可以完全相同，但只要 memory/commitment 改变，future-response equivalence class 就不同。推理因而不是沿文本表面前进，而是在一个带有记忆、分支与比较结构的关系状态空间中穿行。')
A('')
A('## 8. 与 Language Control Algebra v0.1 的合并')
A('Language Control Algebra 的 state X 可扩展为 reasoning state R，其中不只含当前 predictive relation，还含 retained commitments / working relational memory。层级生长律继续成立：')
A('')
A('    G_reason = closure_o(G_language / G_relation) direct-sum R_memory direct-sum R_compare ...')
A('')
A('本轮实验证实的第一个新增项是 memory/re-entry generator：STORE 与 RESET 共同允许系统返回同一局部位置而保持不同 future-response state。后续实验将继续加入 BRANCH / COUNTERFACTUAL / COMPARE / CORRECT 等动作，测试推理是否继续表现为“旧生成代数的递归闭包 + 少量高层 generator”。')
A('')
A('## 原始数据与图件')
for f in ['REASONING-STATE-020_summary.csv','REASONING-STATE-020_operator_fit.csv','REASONING-STATE-020_composition.csv','REASONING-STATE-020_noncommutativity.csv','REASONING-STATE-020_movement.csv','REASONING-STATE-020_reentry.csv','REASONING-STATE-020_store_reset_swap.csv','REASONING-STATE-020_remove_store.csv','REASONING-STATE-020_same_cursor_diff_memory.csv','REASONING-STATE-020_example_traces.csv','REASONING-STATE-020_trace_movements.csv','REASONING-STATE-020_predictive_spectrum.png','REASONING-STATE-020_operator_fit.png','REASONING-STATE-020_reentry.png','REASONING-STATE-020_order_intervention.png','REASONING-STATE-020.py']:
    A(f'- `{f}`')
A('')
A('## 证据边界')
A('本轮是完全可枚举的合成关系推理世界，作用是验证“future-response reasoning state + noncommutative operator algebra + memory/re-entry generator”这一数学形式可以被明确构造、测量和因果干预。它直接支持这套数学结构在该 reasoning world 中成立；自然语言推理与真实 LLM 是否使用同构的 memory/re-entry/compare generators，需要后续在真实模型轨迹上继续测量。')

(OUT/'REASONING-STATE-020.md').write_text('\n'.join(lines),encoding='utf-8')

print(pd.DataFrame([summary]).T.to_string(header=False))
print('\nOPERATOR FIT\n',one.to_string(index=False))
print('\nMOVEMENT\n',mov.to_string(index=False))
print('\nANGLES',angles,'meta_out',meta_out)
