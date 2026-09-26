#!/usr/bin/env python3
from pathlib import Path
from itertools import product
import hashlib, math, json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

OUT=Path('/mnt/data')
N=5
UNSET=N
CMP_UNSET=3
CMP_BRANCH_BETTER=0
CMP_TIE=1
CMP_MAIN_BETTER=2
REL_BASE=['R+1','R+2','R*2','RNEG']
REL_CF=['CF+1','CF+2','CF*2','CFNEG']
META=['BRANCH','COMPARE','CORRECT']
ACTIONS=REL_BASE+REL_CF+META


def rel_apply(x,a):
    if a.endswith('+1'): return (x+1)%N
    if a.endswith('+2'): return (x+2)%N
    if a.endswith('*2'): return (2*x)%N
    if a.endswith('NEG'): return (-x)%N
    raise KeyError(a)

def cyclic_dist(x,g):
    d=(x-g)%N
    return min(d,N-d)

def compare_code(g,x,b):
    dx=cyclic_dist(x,g); db=cyclic_dist(b,g)
    if db<dx: return CMP_BRANCH_BETTER
    if db==dx: return CMP_TIE
    return CMP_MAIN_BETTER

def step(z,a):
    # z=(goal,main,branch,cmp), valid-state constraints enforced by transition
    g,x,b,c=z
    if a in REL_BASE:
        return (g,rel_apply(x,a),b,CMP_UNSET)
    if a in REL_CF:
        if b==UNSET: return z
        return (g,x,rel_apply(b,a),CMP_UNSET)
    if a=='BRANCH':
        return (g,x,x,CMP_UNSET)
    if a=='COMPARE':
        if b==UNSET: return z
        return (g,x,b,compare_code(g,x,b))
    if a=='CORRECT':
        if b==UNSET or c==CMP_UNSET: return z
        nx=b if c==CMP_BRANCH_BETTER else x
        return (g,nx,UNSET,CMP_UNSET)
    raise KeyError(a)

def run(z,prog):
    for a in prog: z=step(z,a)
    return z

def read(z):
    # committed answer is signed modular displacement of main from target
    g,x,b,c=z
    return (x-g)%N

def valid_states():
    out=[]
    for g in range(N):
      for x in range(N):
        out.append((g,x,UNSET,CMP_UNSET))
        for b in range(N):
            out.append((g,x,b,CMP_UNSET))
            out.append((g,x,b,compare_code(g,x,b)))
    return out

STATES=valid_states(); SID={z:i for i,z in enumerate(STATES)}
assert len(STATES)==N*N*(1+2*N)
# future programs up to depth 3; enough to expose branch->compare->correct
PROBES=[()]
for k in [1,2,3]: PROBES += list(product(ACTIONS,repeat=k))
D=len(PROBES)*N
Q=np.zeros((len(STATES),D),dtype=np.uint8)
for i,z in enumerate(STATES):
    for j,p in enumerate(PROBES):
        y=read(run(z,p)); Q[i,j*N+y]=1
# exact future-response classes
packed=np.packbits(Q,axis=1); keys=[bytes(r) for r in packed]
classes={}
for i,k in enumerate(keys): classes.setdefault(k,[]).append(i)
# centered predictive geometry via state Gram matrix
X=Q.astype(float)-Q.mean(axis=0,keepdims=True)
G=(X@X.T)/len(STATES)
w,U=np.linalg.eigh(G); ix=np.argsort(w)[::-1]; w=np.maximum(w[ix],0); U=U[:,ix]
positive=w>1e-12; wpos=w[positive]; Upos=U[:,positive]
frac=wpos/wpos.sum(); cum=np.cumsum(frac)
stable=float(wpos.sum()/wpos.max()); part=float(wpos.sum()**2/(wpos@wpos)); d95=int(np.searchsorted(cum,.95)+1); d99=int(np.searchsorted(cum,.99)+1)
K=d99
Z=Upos[:,:K]*np.sqrt(wpos[:K]*len(STATES))[None,:]

# deterministic split

def bucket(z,mod=5):
    h=hashlib.sha256(str(z).encode()).digest(); return int.from_bytes(h[:4],'little')%mod
train_idx=np.array([i for i,z in enumerate(STATES) if bucket(z)!=0]); test_idx=np.array([i for i,z in enumerate(STATES) if bucket(z)==0])

# action-specific state operators
ops={}; op_rows=[]
for a in ACTIONS:
    yt=np.array([SID[step(STATES[i],a)] for i in train_idx]); yv=np.array([SID[step(STATES[i],a)] for i in test_idx])
    Xtr=Z[train_idx]; Ytr=Z[yt]; Xte=Z[test_idx]; Yte=Z[yv]
    shift=(Ytr-Xtr).mean(0); reset=Ytr.mean(0)
    Phi=np.c_[Xtr,np.ones(len(Xtr))]; Phite=np.c_[Xte,np.ones(len(Xte))]
    lam=1e-5; R=np.eye(K+1)*lam; R[-1,-1]*=.1
    C=np.linalg.solve(Phi.T@Phi+R,Phi.T@Ytr); ops[a]=C
    pred=Phite@C
    mse=lambda P: float(np.mean(np.sum((P-Yte)**2,axis=1)))
    ms=mse(Xte+shift); mo=mse(pred); mr=mse(np.repeat(reset[None,:],len(Xte),0))
    kind='relation-main' if a in REL_BASE else ('relation-counterfactual' if a in REL_CF else 'meta')
    op_rows.append(dict(action=a,kind=kind,mse_fixed_shift=ms,mse_fixed_reset=mr,mse_state_operator=mo,improvement_vs_shift=1-mo/ms if ms>0 else np.nan))
opdf=pd.DataFrame(op_rows)

def apply_aff(C,z): return np.r_[z,1.]@C
# exact pairwise noncommutativity + fitted composition
comp_rows=[]
for a,b in product(ACTIONS,repeat=2):
    exact=[]; qdist=[]; corr=[]; rev=[]
    for i in test_idx:
        zab=step(step(STATES[i],a),b); zba=step(step(STATES[i],b),a)
        exact.append(zab!=zba); qdist.append(np.linalg.norm(Q[SID[zab]].astype(float)-Q[SID[zba]].astype(float))/math.sqrt(D))
        true=Z[SID[zab]]; corr.append(np.sum((apply_aff(ops[b],apply_aff(ops[a],Z[i]))-true)**2)); rev.append(np.sum((apply_aff(ops[a],apply_aff(ops[b],Z[i]))-true)**2))
    comp_rows.append(dict(a=a,b=b,state_noncommute_frac=np.mean(exact),future_rms=np.mean(qdist),correct_mse=np.mean(corr),reversed_mse=np.mean(rev)))
comp=pd.DataFrame(comp_rows)

# movement geometry by action
move_rows=[]; matrices={}
for a in ACTIONS:
    M=np.vstack([Z[SID[step(z,a)]]-Z[SID[z]] for z in STATES]); matrices[a]=M
    _,s,_=np.linalg.svd(M/np.sqrt(len(M)),full_matrices=False); e=s*s; f=e/e.sum() if e.sum() else e
    move_rows.append(dict(action=a,kind=('main' if a in REL_BASE else ('cf' if a in REL_CF else 'meta')),stable_rank=float(e.sum()/e.max()) if e.max()>0 else 0,d95=int(np.searchsorted(np.cumsum(f),.95)+1) if e.sum()>0 else 0,top3=float(f[:3].sum()),mean_norm=float(np.linalg.norm(M,axis=1).mean())))
move=pd.DataFrame(move_rows)
Mbase=np.vstack([matrices[a] for a in REL_BASE]); _,sb,Vb=np.linalg.svd(Mbase,full_matrices=False); kb=3; B=Vb[:kb].T; P=B@B.T
for group,name in [([matrices[a] for a in REL_CF],'cf'),([matrices[a] for a in META],'meta')]:
    M=np.vstack(group); total=np.sum(M*M); proj=np.sum((M@P)**2); 
    if name=='cf': cf_out=1-proj/total
    else: meta_out=1-proj/total

# Branch latent-state diagnostics
branch_rows=[]; cf_rows=[]; compare_rows=[]; correct_rows=[]; wrong_rows=[]
for g in range(N):
  for x in range(N):
    z0=(g,x,UNSET,CMP_UNSET); zb=step(z0,'BRANCH')
    branch_rows.append(dict(goal=g,main=x,immediate_same=int(read(z0)==read(zb)),future_rms=float(np.linalg.norm(Q[SID[z0]].astype(float)-Q[SID[zb]].astype(float))/math.sqrt(D))))
    for cf in REL_CF:
        zcf=step(zb,cf)
        # CF action leaves committed answer unchanged
        zcmp=step(zcf,'COMPARE'); zcor=step(zcmp,'CORRECT')
        before_dist=cyclic_dist(x,g); after_dist=cyclic_dist(zcor[1],g)
        cf_rows.append(dict(goal=g,main=x,cf_action=cf,branch=zcf[2],immediate_same=int(read(zcf)==read(zb)),corrected_main=zcor[1],changed_main=int(zcor[1]!=x),distance_before=before_dist,distance_after=after_dist,distance_gain=before_dist-after_dist))
        compare_rows.append(dict(goal=g,main=x,cf_action=cf,compare_code=zcmp[3],immediate_same=int(read(zcmp)==read(zcf)),future_rms=float(np.linalg.norm(Q[SID[zcmp]].astype(float)-Q[SID[zcf]].astype(float))/math.sqrt(D)),correct_after_compare=read(zcor),correct_before_compare=read(step(zcf,'CORRECT')),order_changes_result=int(read(zcor)!=read(step(zcf,'CORRECT')))))
        # force wrong comparison by flipping better/worse; tie stays tie
        c=zcmp[3]
        wc=CMP_MAIN_BETTER if c==CMP_BRANCH_BETTER else (CMP_BRANCH_BETTER if c==CMP_MAIN_BETTER else c)
        zwrong=(zcmp[0],zcmp[1],zcmp[2],wc); zwc=step(zwrong,'CORRECT')
        wrong_rows.append(dict(goal=g,main=x,cf_action=cf,true_cmp=c,wrong_cmp=wc,true_main=zcor[1],wrong_main=zwc[1],output_changed=int(read(zcor)!=read(zwc)),true_distance=cyclic_dist(zcor[1],g),wrong_distance=cyclic_dist(zwc[1],g),distance_penalty=cyclic_dist(zwc[1],g)-cyclic_dist(zcor[1],g)))
        correct_rows.append(dict(goal=g,main=x,cf_action=cf,cmp=c,main_before=x,branch=zcf[2],main_after=zcor[1],changed=int(zcor[1]!=x),distance_before=before_dist,distance_after=after_dist,never_worse=int(after_dist<=before_dist)))
branch=pd.DataFrame(branch_rows); cfdf=pd.DataFrame(cf_rows); comparedf=pd.DataFrame(compare_rows); correctdf=pd.DataFrame(correct_rows); wrongdf=pd.DataFrame(wrong_rows)

# Standard two-CF-step programs and intervention ablations
std=[]
for g in range(N):
  for x in range(N):
    for cfa,cfb in product(REL_CF,repeat=2):
        z0=(g,x,UNSET,CMP_UNSET)
        z=run(z0,['BRANCH',cfa,cfb,'COMPARE','CORRECT'])
        z_no_branch=run(z0,[cfa,cfb,'COMPARE','CORRECT'])
        z_swap=run(z0,['BRANCH',cfa,cfb,'CORRECT','COMPARE'])
        std.append(dict(goal=g,start=x,cf1=cfa,cf2=cfb,baseline_read=read(z),baseline_main=z[1],baseline_dist=cyclic_dist(z[1],g),no_branch_read=read(z_no_branch),swap_compare_correct_read=read(z_swap),no_branch_changed=int(read(z)!=read(z_no_branch)),swap_changed=int(read(z)!=read(z_swap))))
std=pd.DataFrame(std)

# surface aliasing and minimal predictive-state lower bound
alias=[]
for g in range(N):
  for x in range(N):
    ids=[i for i,z in enumerate(STATES) if z[0]==g and z[1]==x]
    ds=[]; diffs=[]
    for ii in range(len(ids)):
      for jj in range(ii+1,len(ids)):
        ds.append(np.linalg.norm(Q[ids[ii]].astype(float)-Q[ids[jj]].astype(float))/math.sqrt(D)); diffs.append(keys[ids[ii]]!=keys[ids[jj]])
    alias.append(dict(goal=g,main=x,hidden_states=len(ids),pairwise_future_inequivalence=np.mean(diffs),mean_future_rms=np.mean(ds),max_future_rms=np.max(ds)))
alias=pd.DataFrame(alias)

# trajectory movement for canonical branch/cf/compare/correct programs
rng=np.random.default_rng(21); tr=[]
for _ in range(4000):
    g=int(rng.integers(N)); x=int(rng.integers(N)); cfs=[REL_CF[int(rng.integers(4))] for _ in range(2)]
    prog=['BRANCH']+cfs+['COMPARE','CORRECT']; z=(g,x,UNSET,CMP_UNSET)
    for stage,a in enumerate(prog):
        z2=step(z,a); d=Z[SID[z2]]-Z[SID[z]]
        tr.append(dict(stage=stage,action=a,norm=float(np.linalg.norm(d)),**{f'd{i}':d[i] for i in range(min(K,24))})); z=z2
traj=pd.DataFrame(tr); M=traj[[c for c in traj.columns if c.startswith('d')]].to_numpy(); _,st,_=np.linalg.svd(M/np.sqrt(len(M)),full_matrices=False); et=st*st; ft=et/et.sum(); traj_sr=float(et.sum()/et.max()); traj_d95=int(np.searchsorted(np.cumsum(ft),.95)+1)

summary={
 'states':len(STATES),'actions':len(ACTIONS),'future_probes':len(PROBES),'future_signature_dim':D,'predictive_equivalence_classes':len(classes),
 'predictive_stable_rank':stable,'predictive_participation_rank':part,'predictive_d95':d95,'predictive_d99':d99,
 'operator_improvement_vs_shift_mean':float(opdf.improvement_vs_shift.mean()),'composition_correct_mse_mean':float(comp.correct_mse.mean()),'composition_reversed_mse_mean':float(comp.reversed_mse.mean()),
 'pair_noncommute_mean':float(comp.state_noncommute_frac.mean()),'branch_immediate_same':float(branch.immediate_same.mean()),'branch_future_rms_mean':float(branch.future_rms.mean()),
 'cf_immediate_same':float(cfdf.immediate_same.mean()),'cf_changes_committed_after_compare_correct':float(cfdf.changed_main.mean()),'cf_mean_distance_gain':float(cfdf.distance_gain.mean()),
 'compare_immediate_same':float(comparedf.immediate_same.mean()),'compare_future_rms_mean':float(comparedf.future_rms.mean()),'compare_correct_order_changes_result':float(comparedf.order_changes_result.mean()),
 'correct_changes_main':float(correctdf.changed.mean()),'correct_never_worse':float(correctdf.never_worse.mean()),'correct_mean_distance_gain':float((correctdf.distance_before-correctdf.distance_after).mean()),
 'wrong_compare_changes_output':float(wrongdf.output_changed.mean()),'wrong_compare_mean_distance_penalty':float(wrongdf.distance_penalty.mean()),
 'standard_no_branch_changed':float(std.no_branch_changed.mean()),'standard_swap_compare_correct_changed':float(std.swap_changed.mean()),
 'cf_energy_outside_base_top3':float(cf_out),'meta_energy_outside_base_top3':float(meta_out),
 'trajectory_movement_stable_rank':traj_sr,'trajectory_movement_d95':traj_d95,'trajectory_top3_energy':float(ft[:3].sum()),
 'surface_states':N*N,'mean_hidden_states_per_surface':float(alias.hidden_states.mean()),'surface_pair_future_inequivalence':float(alias.pairwise_future_inequivalence.mean()),'surface_mean_future_rms':float(alias.mean_future_rms.mean()),
 'min_predictive_states_exact_serial':len(classes),'min_hidden_bits_exact_serial':int(math.ceil(math.log2(len(classes)))),'visible_surface_bits':int(math.ceil(math.log2(N*N))),'extra_hidden_bits_lower_bound':float(math.log2(len(classes)/(N*N)))
}
# save
for name,df in [('operator_fit',opdf),('composition',comp),('movement',move),('branch',branch),('counterfactual',cfdf),('compare',comparedf),('correct',correctdf),('wrong_compare',wrongdf),('standard_interventions',std),('surface_aliasing',alias),('trajectory_movements',traj)]:
    df.to_csv(OUT/f'REASONING-BRANCH-021_{name}.csv',index=False)
pd.DataFrame([summary]).to_csv(OUT/'REASONING-BRANCH-021_summary.csv',index=False)

# figures
plt.figure(figsize=(7,4)); xx=np.arange(len(opdf)); wbar=.36; plt.bar(xx-wbar/2,opdf.mse_fixed_shift,width=wbar,label='fixed shift'); plt.bar(xx+wbar/2,opdf.mse_state_operator,width=wbar,label='state operator'); plt.xticks(xx,opdf.action,rotation=45,ha='right'); plt.ylabel('held-out MSE'); plt.title('Branch reasoning actions are state-dependent operators'); plt.legend(); plt.tight_layout(); plt.savefig(OUT/'REASONING-BRANCH-021_operator_fit.png',dpi=180); plt.close()
plt.figure(figsize=(6.5,4)); plt.bar(['BRANCH','CF step','COMPARE'],[branch.future_rms.mean(),np.mean([np.linalg.norm(Q[SID[step(step((g,x,UNSET,CMP_UNSET),'BRANCH'),cf)]].astype(float)-Q[SID[step((g,x,UNSET,CMP_UNSET),'BRANCH')]].astype(float))/math.sqrt(D) for g in range(N) for x in range(N) for cf in REL_CF]),comparedf.future_rms.mean()]); plt.ylabel('future-signature RMS'); plt.title('Silent actions change future reasoning state'); plt.tight_layout(); plt.savefig(OUT/'REASONING-BRANCH-021_silent_state.png',dpi=180); plt.close()
plt.figure(figsize=(6.5,4)); plt.bar(['Correct order','COMPARE/CORRECT swapped','Forced wrong comparison'],[0,std.swap_changed.mean(),wrongdf.output_changed.mean()]); plt.ylabel('fraction outcomes changed'); plt.ylim(0,1); plt.title('Comparison and correction are causal operators'); plt.tight_layout(); plt.savefig(OUT/'REASONING-BRANCH-021_correction_interventions.png',dpi=180); plt.close()
plt.figure(figsize=(6.5,4)); plt.bar(['Full reasoning states','Visible (goal,main) projection'],[len(classes),N*N]); plt.ylabel('distinguishable predictive states'); plt.title('Reasoning state exceeds visible serial state'); plt.tight_layout(); plt.savefig(OUT/'REASONING-BRANCH-021_state_count.png',dpi=180); plt.close()

# Report 021
s=summary
L=[]; A=L.append
A('# REASONING-BRANCH-021 | 分支、反事实、比较与纠错：推理控制代数的闭环层')
A('')
A('## 研究触发与当时讨论')
A('REASONING-STATE-020 已把 reasoning state 定义为 future-response equivalence class，并用 STORE/RESET 证明“回到同一局部位置”不等于“回到同一推理状态”。下一刀继续加入 BRANCH / COUNTERFACTUAL / COMPARE / CORRECT，检验推理是否进一步出现“保留主状态、在旁路上模拟、比较两个可达状态、再用比较结果修正主状态”的闭环算子。')
A('')
A('本轮同时为“语言模型与自然推理的数学差异”准备接口：不比较主观体验，只比较两类系统必须携带的 predictive state、算子闭包与可见/隐藏状态关系。')
A('')
A('## 1. 完全可枚举的 branch-reasoning world')
A(f'对象空间为 Z_{N}。reasoning state 写为 r=(g,x,b,c)：g 是目标，x 是当前 committed/main cursor，b 是 counterfactual branch（UNSET 或 Z_{N}），c 是比较结果（branch better / tie / main better / UNSET）。合法状态总数 {len(STATES)}。')
A('')
A('低层动作 R+1/R+2/R*2/RNEG 只作用于 committed main；BRANCH 把 main 快照到 branch；CF+1/CF+2/CF*2/CFNEG 只作用于 branch；COMPARE 根据 branch 与 main 到 goal 的距离写入比较状态；CORRECT 读取比较状态，仅在 branch 更优时把 branch commit 为新的 main，并清空 branch/comparison。')
A('')
A('## 2. Reasoning state 仍然可以由 future-response 等价类定义')
A(f'对每个 state 枚举 11 个动作长度 0–3 的全部 {len(PROBES)} 个未来程序，并读取最终 committed answer。{len(STATES)} 个内部状态得到 {len(classes)} 个 predictive equivalence classes。predictive-state stable rank={stable:.3f}，95% energy dimension={d95}。')
A('')
A('因此 020 的定义在加入 branch/counterfactual 后继续成立：reasoning state 不是“当前主值”或“当前输出”，而是从此处继续施加所有允许控制程序时的未来行为类。')
A('')
A('## 3. BRANCH：立即输出完全不变，但未来状态已经改变')
A(f'BRANCH 只复制 x→b，不改变 committed main，因此 immediate READ 保持不变的比例为 {100*branch.immediate_same.mean():.1f}%。但 BRANCH 前后的 future-signature RMS 平均距离为 {branch.future_rms.mean():.4f}。这给出了第二种“隐形推理动作”：它不改变当前答案，却扩大了未来可达控制结构。')
A('')
A('## 4. COUNTERFACTUAL：旁路运动不改当前答案，却能在后续比较/纠错后改变主轨迹')
A(f'所有 CF relation step 都只移动 branch，因此 immediate committed answer 保持比例为 {100*cfdf.immediate_same.mean():.1f}%。经过 COMPARE→CORRECT 后，main 被 counterfactual branch 替换的比例为 {100*cfdf.changed_main.mean():.1f}%；平均 goal-distance 改善为 {cfdf.distance_gain.mean():.3f}。')
A('')
A('这把 counterfactual 的数学角色写得很清楚：它首先修改一个“当前不被输出读出”的旁路状态；只有后续 compare/correct gate 打开时，这个旁路才进入 committed trajectory。')
A('')
A('## 5. COMPARE 与 CORRECT 构成显式闭环控制')
A(f'COMPARE 本身不改变 committed main，immediate answer 保持 {100*comparedf.immediate_same.mean():.1f}%，但其前后 future-signature RMS={comparedf.future_rms.mean():.4f}：它写入的是后续 CORRECT 会读取的 control state。')
A(f'把 COMPARE→CORRECT 交换成 CORRECT→COMPARE，结果在 {100*comparedf.order_changes_result.mean():.1f}% 的单步反事实病例中改变；在标准两步 counterfactual 程序中改变率为 {100*std.swap_changed.mean():.1f}%。')
A(f'CORRECT 在全部病例中“从不使 goal distance 变差”的比例为 {100*correctdf.never_worse.mean():.1f}%，平均 distance gain={summary["correct_mean_distance_gain"]:.3f}。把比较符号强制翻转后，最终输出在 {100*wrongdf.output_changed.mean():.1f}% 病例改变，平均 distance penalty={wrongdf.distance_penalty.mean():.3f}。')
A('')
A('因此 CORRECT 不是一个固定变换，而是由比较状态驱动的 feedback selector。BRANCH→COUNTERFACTUAL→COMPARE→CORRECT 形成了本系列第一个明确的 closed-loop reasoning macro。')
A('')
A('## 6. 算子拟合与非交换组合')
A(f'11 类动作在 predictive-state PCA 坐标上用 state-dependent affine operator 拟合，相对 fixed shift 平均降低 held-out error {100*opdf.improvement_vs_shift.mean():.2f}%。全部 action pairs 的真实内部状态非交换比例平均为 {100*comp.state_noncommute_frac.mean():.2f}%。正确两步 operator composition 的平均 MSE={comp.correct_mse.mean():.3f}，反序 composition={comp.reversed_mse.mean():.3f}。')
A('')
A('## 7. 新增 reasoning generator 的几何')
A(f'以 main relation movements 的前三主轴作为低层关系运动子空间，counterfactual relation movements 有 {100*cf_out:.2f}% 能量位于该子空间之外；BRANCH/COMPARE/CORRECT 三个 meta actions 有 {100*meta_out:.2f}% 能量位于其外。沿标准 BRANCH→CF→CF→COMPARE→CORRECT 轨迹，movement stable rank={traj_sr:.3f}，top-3 movement energy={100*ft[:3].sum():.2f}%。')
A('')
A('结果支持 reasoning hierarchy 继续按“旧关系算子的复用 + 新控制坐标”增长：counterfactual relation 复用了同一关系变换家族，但作用在新的 branch fiber 上；COMPARE/CORRECT 则引入对 branch/main 关系本身的高层控制。')
A('')
A('## 8. 本轮对推理的更新定义')
A('020 的 retained commitment / re-entry 现在可以推进为：')
A('')
A('> **Reasoning is closed-loop control over a factored relational state: the system can preserve a committed trajectory, instantiate counterfactual branches, compare alternative reachable states, and conditionally rewrite the committed trajectory from that comparison.**')
A('')
A('中文：**推理是对分解关系状态的闭环控制：系统能够保留已承诺轨迹、建立反事实分支、比较多个可达状态，并根据比较结果条件性地重写主轨迹。**')
A('')
A('## 9. 原始数据与图件')
for f in ['REASONING-BRANCH-021_summary.csv','REASONING-BRANCH-021_operator_fit.csv','REASONING-BRANCH-021_composition.csv','REASONING-BRANCH-021_movement.csv','REASONING-BRANCH-021_branch.csv','REASONING-BRANCH-021_counterfactual.csv','REASONING-BRANCH-021_compare.csv','REASONING-BRANCH-021_correct.csv','REASONING-BRANCH-021_wrong_compare.csv','REASONING-BRANCH-021_standard_interventions.csv','REASONING-BRANCH-021_surface_aliasing.csv','REASONING-BRANCH-021_trajectory_movements.csv','REASONING-BRANCH-021_operator_fit.png','REASONING-BRANCH-021_silent_state.png','REASONING-BRANCH-021_correction_interventions.png','REASONING-BRANCH-021_state_count.png','REASONING-BRANCH-021.py']:
    A(f'- `{f}`')
A('')
A('## 证据边界')
A('本轮仍是完全可枚举的合成关系世界。它直接支持 branch/counterfactual/compare/correct 这组高层控制算子可以形成可测的 reasoning algebra，并能与低层 relation movement 分开。它不把该构造直接等同于人脑机制；其价值是为真实 LLM 与自然推理提供一个纯数学比较坐标。')
(OUT/'REASONING-BRANCH-021.md').write_text('\n'.join(L),encoding='utf-8')

# 022 mathematical comparison report
lang_teacher=pd.read_csv(OUT/'LANGUAGE-TEACHER-GEOMETRY-015_teacher.csv').iloc[0]
lang_op=pd.read_csv(OUT/'LANGUAGE-GENERATIVE-OPERATORS-016_summary.csv').iloc[0]
reason020=pd.read_csv(OUT/'REASONING-STATE-020_summary.csv').iloc[0]
comparison_rows=[
 ['State carrier','prefix-conditioned hidden state h_t','factored relational state r=(relation, commitment, branch, comparison, ...)','Representation/factorization differs; either can be encoded in a sufficiently large dynamical state.'],
 ['Primitive update','h_{t+1}=F_theta(h_t,e(a_t))','r_{t+1}=G_a(r_t)','Both are state-dependent dynamical operators.'],
 ['Trajectory topology','one realized serial path at each step','committed path + retained/alternative branch fibers + re-entry','Reasoning algebra contains explicit multi-locus state even when only one output is visible.'],
 ['Counterfactual','must be represented inside h_t or serialized into tokens','branch coordinate is a first-class state factor','Difference is native coordinate structure, not computability.'],
 ['Comparison/correction','can be implemented implicitly by hidden dynamics','explicit COMPARE state gates conditional CORRECT','021 gives an explicit closed-loop selector algebra.'],
 ['Observability','token stream is a projection of h_t','committed answer is a projection of richer r_t','Surface equality does not imply state equality in either system.'],
 ['Composition','noncommutative token/state operators','noncommutative relation/meta operators','Shared mathematical family.'],
 ['Low-dimensional motion','language local teacher stable rank ~2.48; operator family rank ~6.02','020 legal reasoning movement stable rank ~3.12; 021 branch loop remains concentrated','Both can have high-dimensional state but lower-dimensional realized control motion.'],
]
pd.DataFrame(comparison_rows,columns=['axis','autoregressive_language_model','natural_reasoning_reference_algebra','mathematical_conclusion']).to_csv(OUT/'LM-vs-NATURAL-REASONING-MATH-022_comparison.csv',index=False)
# exact lower bound from 021
lower={
 'visible_surface_states':N*N,
 'reasoning_predictive_classes':len(classes),
 'states_per_visible_surface':len(STATES)/(N*N),
 'visible_bits_ceiling':math.ceil(math.log2(N*N)),
 'exact_serial_hidden_bits_lower_bound':math.ceil(math.log2(len(classes))),
 'additional_latent_information_log2_ratio':math.log2(len(classes)/(N*N)),
 'same_surface_pair_future_inequivalence':alias.pairwise_future_inequivalence.mean(),
 'same_surface_mean_future_rms':alias.mean_future_rms.mean(),
 'language_teacher_local_stable_rank':float(lang_teacher.teacher_stable),
 'language_operator_family_stable_rank':float(lang_op.operator_stable_rank),
 'reasoning020_state_stable_rank':float(reason020.predictive_state_stable_rank),
 'reasoning020_trajectory_movement_stable_rank':float(reason020.reasoning_trace_movement_stable_rank),
 'reasoning021_state_stable_rank':stable,
 'reasoning021_trajectory_movement_stable_rank':traj_sr,
}
pd.DataFrame([lower]).to_csv(OUT/'LM-vs-NATURAL-REASONING-MATH-022_metrics.csv',index=False)
# comparison figure
plt.figure(figsize=(7,4)); plt.bar(['Language local\nmotion','Language operator\nfamily','Reasoning 020\nstate','Reasoning 020\nmovement','Reasoning 021\nstate','Reasoning 021\nmovement'],[lang_teacher.teacher_stable,lang_op.operator_stable_rank,reason020.predictive_state_stable_rank,reason020.reasoning_trace_movement_stable_rank,stable,traj_sr]); plt.ylabel('stable rank'); plt.title('State complexity and realized control motion are different objects'); plt.xticks(rotation=25,ha='right'); plt.tight_layout(); plt.savefig(OUT/'LM-vs-NATURAL-REASONING-MATH-022_ranks.png',dpi=180); plt.close()

L=[]; A=L.append
A('# LM-vs-NATURAL-REASONING-MATH-022 | 语言模型与自然推理的纯数学比较')
A('')
A('## 定位')
A('本节不比较“谁更像人”，也不把合成 reasoning world 当作真实神经科学证据。这里把“自然推理”定义成一种最低限度的 reference algebra：它必须允许 retained commitment、re-entry、branch、counterfactual manipulation、comparison 与 conditional correction。然后把它与 autoregressive language model 的一般动力学形式比较。')
A('')
A('## 1. 两边首先属于同一个大类：受状态条件化的动力系统')
A('Autoregressive language model 可以写为：')
A('')
A('    h_{t+1}=F_theta(h_t,e(a_t)),     a_{t+1}~pi_theta(.|h_{t+1})')
A('')
A('Reasoning control algebra 写为：')
A('')
A('    r_{t+1}=G_{a_t}(r_t),           y_t=O(r_t)')
A('')
A('因此数学上不存在“一个是神秘思考、一个只是机器”的二分。两者都可以是状态、算子、读出与反馈组成的动力控制系统。真正值得比较的是 state 怎样因子化、哪些 operator 是 primitive、什么信息被外显。')
A('')
A('## 2. 核心差别不是可计算性，而是状态因子化与原生控制接口')
A('标准 autoregressive LM 每一时刻只实现一条 realized token path；任何尚未外显的候选、回退点、比较结果，都必须编码在 hidden state h_t 中，或者通过更多 token 序列化出来。021 的 natural-reasoning reference algebra 则把 committed main、counterfactual branch 与 comparison state 分成显式状态坐标。')
A('')
A('这不是说 LM 不能实现 reasoning。恰恰相反：只要 hidden state 足够，LM 可以模拟整个 reasoning algebra。区别是：如果它真的完成同一个 reasoning task，它的 h_t 内部必须携带一个与 augmented reasoning state 等价的预测信息。')
A('')
A('## 3. 一个精确的 serial-emulation 下界')
A(f'021 有 {len(classes)} 个 future-response 不等价的 reasoning states，但可见 committed surface 只有 goal×main={N*N} 种。每个 visible surface 平均折叠 {len(STATES)/(N*N):.1f} 个不同内部 reasoning states；同一 surface 内 state pairs 的 future-response 不等价比例为 {100*alias.pairwise_future_inequivalence.mean():.2f}%。')
A('')
A('由 deterministic predictive-state / Myhill–Nerode 型下界，任何要精确实现全部未来控制行为的串行系统，必须至少具有与 future-response equivalence classes 一样多的可区分 hidden states。')
A('')
A(f'    |H_min| >= |R / ~future| = {len(classes)}')
A(f'    hidden bits >= ceil(log2 {len(classes)}) = {math.ceil(math.log2(len(classes)))} bits')
A(f'    visible (goal,main) projection only needs ceil(log2 {N*N}) = {math.ceil(math.log2(N*N))} bits')
A(f'    extra predictive information lower bound = log2({len(classes)}/{N*N}) = {math.log2(len(classes)/(N*N)):.3f} bits')
A('')
A('所以“只看当前语言表面”必然不足；但“LLM 隐状态也只是当前表面”同样是错误的。一个能精确做这类 reasoning 的 autoregressive model 必须在 hidden dynamics 中恢复这些额外 predictive distinctions。')
A('')
A('## 4. 自然推理 reference algebra 比普通语言运动新增什么？')
A('语言实验已经给出：局部 teacher motion stable rank≈2.481；35 个字符生成算子族 stable rank≈6.018；算子组合非交换。020/021 显示 reasoning 并不是抛弃这套结构，而是在其上增加新的 factor/control primitives：retained commitment、re-entry、branch fiber、comparison state、conditional correction。')
A('')
A('因此可以写成：')
A('')
A('    G_reason = closure_o(G_language) ⊕ R_memory ⊕ R_reentry ⊕ R_branch ⊕ R_compare ⊕ R_correct ...')
A('')
A('这里“⊕”表示实验上可分离的新 generator component，不要求线性正交。')
A('')
A('## 5. 两边共享“高维状态 + 低维实际运动”结构')
A(f'语言局部 teacher motion stable rank={lang_teacher.teacher_stable:.3f}；language operator family stable rank={lang_op.operator_stable_rank:.3f}。020 reasoning state stable rank={reason020.predictive_state_stable_rank:.3f}，但合法 reasoning trajectory movement stable rank={reason020.reasoning_trace_movement_stable_rank:.3f}。021 加入 branch/correction 后 state stable rank={stable:.3f}，实际 branch-loop movement stable rank={traj_sr:.3f}。')
A('')
A('所以最稳妥的纯数学比较不是“语言模型低维、自然推理高维”。更像是：两者都允许高维 predictive state，但一次真实运行只调用较低维的局部控制方向；自然推理的新增特征是能够把多个关系位置/承诺同时保存在增广 state 中，并用高层 operator 对这些 state factors 做比较和重写。')
A('')
A('## 6. 一个重要等价命题')
A('**Finite emulation proposition.** 对任何有限 reasoning control algebra (R,A,G,O)，存在一个 autoregressive hidden-state dynamical system whose hidden state can encode R exactly and reproduce the same operator/output behavior. 反过来，如果把 autoregressive system 限制到只保存 surface projection P(r)，而存在 r1!=r2、P(r1)=P(r2) 且 r1 not~_future r2，则它不可能精确实现全部 reasoning behavior。')
A('')
A('因此“语言模型 vs 自然推理”的数学分界不是能不能计算，而是：**模型是否在内部建立了与 reasoning algebra 同构/同态的增广 predictive state，以及其 token 控制是否真正实现 branch、compare、correct 等闭环 operator。**')
A('')
A('## 7. 当前纯数学结论')
A('1. LM 与 reasoning 都属于状态依赖动力控制系统；“机制化”不会把其中一方降级。')
A('2. Autoregressive serialization 不是 reasoning 的反面；它是一种实现接口。若要精确支持 reasoning，它必须在 hidden state 中携带被文本表面折叠掉的 branch/commitment/comparison 信息。')
A('3. Natural-reasoning reference algebra 的新增数学对象不是“更多词义”，而是对多个关系状态及其比较结果进行控制的高层 generators。')
A('4. 文本输出是 reasoning state 的投影；同一可见输出可以对应 future-response 不等价的内部状态。')
A('5. 真正需要在真实 LLM 上检验的问题因此被压缩为：hidden-state control field 中是否存在可识别的 branch fiber、comparison gate、conditional correction operator，以及它们是否具有与 020/021 相同的 future-response algebra。')
A('')
A('## 证据边界')
A('“自然推理”在本节中是一个形式化 reference algebra，而不是对人脑神经实现的经验断言。现有自然语言实验与合成 reasoning experiments 支持的是一套可施工的数学比较框架；真实人类推理是否采用同样的状态因子化，需要独立行为/神经数据。')
(OUT/'LM-vs-NATURAL-REASONING-MATH-022.md').write_text('\n'.join(L),encoding='utf-8')

# bundle
import zipfile
with zipfile.ZipFile(OUT/'REASONING-BRANCH-021_bundle.zip','w',zipfile.ZIP_DEFLATED) as zf:
    for p in OUT.glob('REASONING-BRANCH-021*'):
        if p.name.endswith('_bundle.zip'): continue
        zf.write(p,p.name)
with zipfile.ZipFile(OUT/'LM-vs-NATURAL-REASONING-MATH-022_bundle.zip','w',zipfile.ZIP_DEFLATED) as zf:
    for p in OUT.glob('LM-vs-NATURAL-REASONING-MATH-022*'):
        if p.name.endswith('_bundle.zip'): continue
        zf.write(p,p.name)

print(json.dumps(summary,indent=2,ensure_ascii=False))
print('\noperator fit\n',opdf.to_string(index=False))
print('\ninterventions\n',pd.DataFrame({
    'metric':['branch_future_rms','cf_changes_after_compare_correct','compare_order_changes','wrong_compare_output_change','correct_never_worse','no_branch_changed','swap_compare_correct_changed'],
    'value':[branch.future_rms.mean(),cfdf.changed_main.mean(),comparedf.order_changes_result.mean(),wrongdf.output_changed.mean(),correctdf.never_worse.mean(),std.no_branch_changed.mean(),std.swap_changed.mean()]}).to_string(index=False))
