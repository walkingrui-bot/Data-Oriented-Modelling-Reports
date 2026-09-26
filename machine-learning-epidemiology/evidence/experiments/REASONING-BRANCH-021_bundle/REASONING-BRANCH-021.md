# REASONING-BRANCH-021 | 分支、反事实、比较与纠错：推理控制代数的闭环层

## 研究触发与当时讨论
REASONING-STATE-020 已把 reasoning state 定义为 future-response equivalence class，并用 STORE/RESET 证明“回到同一局部位置”不等于“回到同一推理状态”。下一刀继续加入 BRANCH / COUNTERFACTUAL / COMPARE / CORRECT，检验推理是否进一步出现“保留主状态、在旁路上模拟、比较两个可达状态、再用比较结果修正主状态”的闭环算子。

本轮同时为“语言模型与自然推理的数学差异”准备接口：不比较主观体验，只比较两类系统必须携带的 predictive state、算子闭包与可见/隐藏状态关系。

## 1. 完全可枚举的 branch-reasoning world
对象空间为 Z_5。reasoning state 写为 r=(g,x,b,c)：g 是目标，x 是当前 committed/main cursor，b 是 counterfactual branch（UNSET 或 Z_5），c 是比较结果（branch better / tie / main better / UNSET）。合法状态总数 275。

低层动作 R+1/R+2/R*2/RNEG 只作用于 committed main；BRANCH 把 main 快照到 branch；CF+1/CF+2/CF*2/CFNEG 只作用于 branch；COMPARE 根据 branch 与 main 到 goal 的距离写入比较状态；CORRECT 读取比较状态，仅在 branch 更优时把 branch commit 为新的 main，并清空 branch/comparison。

## 2. Reasoning state 仍然可以由 future-response 等价类定义
对每个 state 枚举 11 个动作长度 0–3 的全部 1464 个未来程序，并读取最终 committed answer。275 个内部状态得到 173 个 predictive equivalence classes。predictive-state stable rank=6.996，95% energy dimension=15。

因此 020 的定义在加入 branch/counterfactual 后继续成立：reasoning state 不是“当前主值”或“当前输出”，而是从此处继续施加所有允许控制程序时的未来行为类。

## 3. BRANCH：立即输出完全不变，但未来状态已经改变
BRANCH 只复制 x→b，不改变 committed main，因此 immediate READ 保持不变的比例为 100.0%。但 BRANCH 前后的 future-signature RMS 平均距离为 0.0276。这给出了第二种“隐形推理动作”：它不改变当前答案，却扩大了未来可达控制结构。

## 4. COUNTERFACTUAL：旁路运动不改当前答案，却能在后续比较/纠错后改变主轨迹
所有 CF relation step 都只移动 branch，因此 immediate committed answer 保持比例为 100.0%。经过 COMPARE→CORRECT 后，main 被 counterfactual branch 替换的比例为 36.0%；平均 goal-distance 改善为 0.450。

这把 counterfactual 的数学角色写得很清楚：它首先修改一个“当前不被输出读出”的旁路状态；只有后续 compare/correct gate 打开时，这个旁路才进入 committed trajectory。

## 5. COMPARE 与 CORRECT 构成显式闭环控制
COMPARE 本身不改变 committed main，immediate answer 保持 100.0%，但其前后 future-signature RMS=0.0684：它写入的是后续 CORRECT 会读取的 control state。
把 COMPARE→CORRECT 交换成 CORRECT→COMPARE，结果在 36.0% 的单步反事实病例中改变；在标准两步 counterfactual 程序中改变率为 32.0%。
CORRECT 在全部病例中“从不使 goal distance 变差”的比例为 100.0%，平均 distance gain=0.450。把比较符号强制翻转后，最终输出在 72.0% 病例改变，平均 distance penalty=0.900。

因此 CORRECT 不是一个固定变换，而是由比较状态驱动的 feedback selector。BRANCH→COUNTERFACTUAL→COMPARE→CORRECT 形成了本系列第一个明确的 closed-loop reasoning macro。

## 6. 算子拟合与非交换组合
11 类动作在 predictive-state PCA 坐标上用 state-dependent affine operator 拟合，相对 fixed shift 平均降低 held-out error 85.55%。全部 action pairs 的真实内部状态非交换比例平均为 42.58%。正确两步 operator composition 的平均 MSE=20.975，反序 composition=245.350。

### 6.1 高层算子开始从平滑变换跨到门控/分区控制
单一 affine operator 对四个 main-relation actions 的 held-out error 相对 fixed shift 降低约 99.94%，对四个 counterfactual-relation actions 降低约 95.85%，BRANCH 降低 98.61%；但 COMPARE 的单一 affine fit 不再优于 fixed shift（-2.71%），CORRECT 也只降低 61.92%。这不是把 COMPARE/CORRECT 排除出算子框架，而是暴露出新的算子类型：COMPARE 先把状态按“branch 更优 / tie / main 更优”分区，CORRECT 再由这个离散 gate 条件性选择 x'=b 或 x'=x。

因此 reasoning algebra 到这一层不再只有平滑 state transformation，而出现 **state partition + gated rewrite**。COMPARE 的 gate-conditioned affine 对照把 MSE 从 21.824 降到 9.400；CORRECT 的核心仍由离散 selection 决定，直接写成分段控制律比单一 affine embedding 更自然：

    CORRECT(g,x,b,c) = (g,b,UNSET,UNSET),  if c=branch_better
                         (g,x,UNSET,UNSET),  if c=tie or main_better
                         identity,             if comparison is unset

这一步把“比较/纠错”与普通关系运动分开：前者的本体是条件控制律，而不是另一根固定连续向量。

## 7. 新增 reasoning generator 的几何
以 main relation movements 的前三主轴作为低层关系运动子空间，counterfactual relation movements 有 93.81% 能量位于该子空间之外；BRANCH/COMPARE/CORRECT 三个 meta actions 有 67.56% 能量位于其外。沿标准 BRANCH→CF→CF→COMPARE→CORRECT 轨迹，movement stable rank=5.589，top-3 movement energy=45.82%。

结果支持 reasoning hierarchy 继续按“旧关系算子的复用 + 新控制坐标”增长：counterfactual relation 复用了同一关系变换家族，但作用在新的 branch fiber 上；COMPARE/CORRECT 则引入对 branch/main 关系本身的高层控制。

## 8. 本轮对推理的更新定义
020 的 retained commitment / re-entry 现在可以推进为：

> **Reasoning is closed-loop control over a factored relational state: the system can preserve a committed trajectory, instantiate counterfactual branches, compare alternative reachable states, and conditionally rewrite the committed trajectory from that comparison.**

中文：**推理是对分解关系状态的闭环控制：系统能够保留已承诺轨迹、建立反事实分支、比较多个可达状态，并根据比较结果条件性地重写主轨迹。**

## 9. 原始数据与图件
- `REASONING-BRANCH-021_summary.csv`
- `REASONING-BRANCH-021_operator_fit.csv`
- `REASONING-BRANCH-021_composition.csv`
- `REASONING-BRANCH-021_movement.csv`
- `REASONING-BRANCH-021_branch.csv`
- `REASONING-BRANCH-021_counterfactual.csv`
- `REASONING-BRANCH-021_compare.csv`
- `REASONING-BRANCH-021_correct.csv`
- `REASONING-BRANCH-021_wrong_compare.csv`
- `REASONING-BRANCH-021_standard_interventions.csv`
- `REASONING-BRANCH-021_surface_aliasing.csv`
- `REASONING-BRANCH-021_trajectory_movements.csv`
- `REASONING-BRANCH-021_operator_fit.png`
- `REASONING-BRANCH-021_silent_state.png`
- `REASONING-BRANCH-021_correction_interventions.png`
- `REASONING-BRANCH-021_state_count.png`
- `REASONING-BRANCH-021.py`

## 证据边界
本轮仍是完全可枚举的合成关系世界。它直接支持 branch/counterfactual/compare/correct 这组高层控制算子可以形成可测的 reasoning algebra，并能与低层 relation movement 分开。它不把该构造直接等同于人脑机制；其价值是为真实 LLM 与自然推理提供一个纯数学比较坐标。