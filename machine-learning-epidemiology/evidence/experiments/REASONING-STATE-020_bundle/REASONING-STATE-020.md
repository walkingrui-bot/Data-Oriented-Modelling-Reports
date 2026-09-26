# REASONING-STATE-020 | 从语言控制代数到推理状态：未来响应等价类、回退、记忆与高层算子

## 研究触发与当时讨论
语言线 015–019 已把语言写成作用于关系/预测状态上的状态依赖非交换生成控制代数。下一步不再问“语言如何运动”，而问：当系统开始保存中间关系、回到旧位置、比较两条路径并提交结果时，是否出现一个可独立定义的 reasoning state？本轮 deliberately 不把“推理=语言”写进设计，而是用可完全枚举的关系世界检验：推理是否可以由 future-response equivalence、关系算子、记忆算子与回退/比较控制共同定义。

第一版曾尝试训练一个自由生成 GRU 同时记住两条三步路径；模型能读出 phase 与后期 diff，但自由生成尚未稳定学会关系计算，因此该版本没有进入证据链。本轮改为完全可枚举 reasoning world，把模型学习不充分从机制问题中移除，直接检验数学对象本身。

## 1. 受控关系推理世界
对象空间为 Z_7。四个关系算子为 R+1, R+2, R*2, RNEG，另有 STORE 与 RESET 两个高层控制动作。reasoning state 写为 r=(s,x,m)：s 为起点，x 为当前 cursor，m 为已保存的中间关系结果；m=UNSET 表示尚未保存。READ(r)=(m-x) mod 7。完整状态共 392 个。

标准推理程序为：三步 A 路径 → STORE → RESET → 三步 B 路径 → READ。它要求系统先把 A 的终点写入 memory，再把 cursor 退回起点，在同一世界中走第二条路径，最后比较 memory 与 cursor。

## 2. 推理状态的操作性定义：future-response equivalence
对每个状态 r，枚举长度 0–3 的全部未来控制程序（6 个动作的 259 个 probes），记录每个 program 之后 READ 的离散结果。把这些结果的一热向量拼接成 q(r)。定义 r~r' 当且仅当对全部 probes 有相同未来响应。

392 个内部状态得到 392 个 predictive equivalence classes；也就是说，本实验的 future-response signature 足以把所有 reasoning states 区分开。q(r) 的原始维数为 2072，SVD stable rank=8.758，95% 能量维数=64，99%=91。这里“reasoning state”不是某个词或当前对象，而是“从这里继续做任何允许的控制操作时，未来会怎样”的等价类。

## 3. 同一个表面位置可以是不同推理状态
RESET 是本轮最关键的干预。标准 A 路径完成 STORE 后执行 RESET，cursor 精确回到最初的 start；如果只观察当前位置，系统“回到了原点”。但 memory 已经写入 A endpoint，因此 future-response state 没有回到原点。

全部 448 个 start×A-path 条件中，RESET 后 cursor 与初始 cursor 相同的比例为 1.000；完整 reasoning state 真正相等的比例为 0.000。两者 future-signature RMS 平均距离为 0.3880，PCA reasoning-state distance 平均为 17.6392。

进一步固定同一 start 与同一 cursor，只改变 memory，未来响应仍保持明显分离：平均 pairwise future-signature RMS=0.3880。这直接支持：reasoning state 至少包含当前局部对象之外的 retained relational commitment。

## 4. 推理动作是状态变换算子
在 q(r) 的 99%-energy PCA 坐标中，对每个动作拟合 affine operator T_a(z)=A_a z+b_a，并在未参与拟合的状态上预测动作后的 future-response state。

- R+1: fixed-shift MSE=222.433; state-operator MSE=1.04935; improvement=99.53%.
- R+2: fixed-shift MSE=222.413; state-operator MSE=0.835936; improvement=99.62%.
- R*2: fixed-shift MSE=184.881; state-operator MSE=11.0632; improvement=94.02%.
- RNEG: fixed-shift MSE=184.46; state-operator MSE=1.59937; improvement=99.13%.
- STORE: fixed-shift MSE=241.249; state-operator MSE=12.6328; improvement=94.76%.
- RESET: fixed-shift MSE=164.751; state-operator MSE=14.8207; improvement=91.00%.

六类动作平均相对 fixed-shift 的 held-out 误差下降为 96.34%。同一个操作不是给状态加一根固定向量；它作用于当前 predictive/reasoning state，并产生条件化转移。

## 5. 推理代数非交换；正确组合可预测后续状态
对全部 36 个两动作组合，在 held-out reasoning states 上用 T_b(T_a(z)) 预测真实两步 future state；平均 MSE=14.3992。把相同两动作反序成 T_a(T_b(z))，平均 MSE=167.373。世界本身的 action pairs 平均有 68.25% 状态满足 ab 与 ba 产生不同内部状态，最高为 100.0%。

直接在完整推理程序中交换 STORE 与 RESET，最终 answer 改变比例为 87.50%；删除 STORE 后 READ 落入 UNSET/不同答案的比例为 100.00%。因此高层 reasoning operator 的次序不是文本排版，而是因果计算。

## 6. 关系运动与高层 reasoning generator
四个 relation actions 的 movement stable rank 平均为 17.392；STORE/RESET 为 13.226。把 relation movement 的前三主方向作为低层关系运动子空间，STORE/RESET 的运动能量有 94.71% 落在该三维子空间之外。前三维 relation/meta 子空间 principal angles 为 67.33°, 90.00°, 90.00°。

因此推理向上生长的方式与 LANGUAGE-HIERARCHICAL-GENERATORS-019 的结构一致：大量步骤复用已有关系算子的有序复合；当任务要求“保存一个关系结果”“回到旧位置但保留承诺”时，会引入少量新的高层 generator，而不是把全部状态空间重新发明一遍。

## 7. 高维 reasoning state 与低维实际运动可以同时成立

完整 future-response state 本身并不只有两三维：392 个 predictive states 的 stable rank=8.758，participation rank=34.824，95% energy 需要 64 个模态。也就是说，reasoning state 可以保存大量彼此独立的关系区分。

但沿标准“3 步 A → STORE → RESET → 3 步 B”合法推理程序实际发生的 movement 明显更集中：trajectory-movement stable rank=3.118，前三模态解释 53.22% movement energy。这个结果与此前语言/模型控制线的结构一致：**状态内容可以高维，而一次实际推理过程使用的主要运动自由度可以远低于完整状态空间。**

STORE/RESET 顺序交换使 87.5% 的最终答案改变；剩余 12.5% 恰好对应 A 路径终点等于 start 的代数退化条件，因此两个顺序在这些病例中保存同一 memory value。也就是说，在所有非退化 A endpoint 条件中，顺序交换对 answer 的改变率为 100%。

## 7. 本轮对“推理是什么”的工作定义
本轮支持把 reasoning state 定义为历史在未来可控行为上的等价类：

    R = H / ~future
    h1 ~future h2  iff  F(p | h1) = F(p | h2) for every admissible future control program p.

推理动作 g 属于作用在 R 上的非交换 generator family；标准推理轨迹是

    r_{t+1} = G(a_t, r_t)[r_t].

语言动作主要改变当前关系/预测状态；推理开始于系统进一步获得对“关系状态本身”的控制：保存某个中间关系、返回旧局部位置、在保留历史承诺的情况下重新展开另一条轨迹、比较多个可达状态，再把比较结果写回后续状态。

因此本轮最简工作定义是：

> **Reasoning is recursive control over an augmented relational state: a noncommutative sequence of operators that preserves, revisits, transforms and compares relational commitments according to their future consequences.**

中文：**推理是对增广关系状态的递归控制：系统用非交换算子保存、回访、变换并比较关系承诺，并以这些操作对未来可达状态的后果作为计算对象。**

这一定义把“回到同一个地方”和“回到同一个推理状态”严格区分开。RESET 后 cursor 可以完全相同，但只要 memory/commitment 改变，future-response equivalence class 就不同。推理因而不是沿文本表面前进，而是在一个带有记忆、分支与比较结构的关系状态空间中穿行。

## 8. 与 Language Control Algebra v0.1 的合并
Language Control Algebra 的 state X 可扩展为 reasoning state R，其中不只含当前 predictive relation，还含 retained commitments / working relational memory。层级生长律继续成立：

    G_reason = closure_o(G_language / G_relation) direct-sum R_memory direct-sum R_compare ...

本轮实验证实的第一个新增项是 memory/re-entry generator：STORE 与 RESET 共同允许系统返回同一局部位置而保持不同 future-response state。后续实验将继续加入 BRANCH / COUNTERFACTUAL / COMPARE / CORRECT 等动作，测试推理是否继续表现为“旧生成代数的递归闭包 + 少量高层 generator”。

## 原始数据与图件
- `REASONING-STATE-020_summary.csv`
- `REASONING-STATE-020_operator_fit.csv`
- `REASONING-STATE-020_composition.csv`
- `REASONING-STATE-020_noncommutativity.csv`
- `REASONING-STATE-020_movement.csv`
- `REASONING-STATE-020_reentry.csv`
- `REASONING-STATE-020_store_reset_swap.csv`
- `REASONING-STATE-020_remove_store.csv`
- `REASONING-STATE-020_same_cursor_diff_memory.csv`
- `REASONING-STATE-020_example_traces.csv`
- `REASONING-STATE-020_trace_movements.csv`
- `REASONING-STATE-020_predictive_spectrum.png`
- `REASONING-STATE-020_operator_fit.png`
- `REASONING-STATE-020_reentry.png`
- `REASONING-STATE-020_order_intervention.png`
- `REASONING-STATE-020.py`

## 证据边界
本轮是完全可枚举的合成关系推理世界，作用是验证“future-response reasoning state + noncommutative operator algebra + memory/re-entry generator”这一数学形式可以被明确构造、测量和因果干预。它直接支持这套数学结构在该 reasoning world 中成立；自然语言推理与真实 LLM 是否使用同构的 memory/re-entry/compare generators，需要后续在真实模型轨迹上继续测量。