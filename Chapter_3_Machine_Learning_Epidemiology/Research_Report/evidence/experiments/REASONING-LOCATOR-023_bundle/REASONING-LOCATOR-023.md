# REASONING-LOCATOR-023 | CoT 不是完整思考过程时，推理状态在模型哪里？

## 设计

三层自回归 GRU 接收 goal/start/main relation/counterfactual relation。中间可见 CoT 被固定为同一个 teacher-forced 模板 `THINK → CHECK → FINAL`，对所有 400 个病例完全相同。最终 next-token answer 必须选择更接近 goal 的 main/branch 候选。于是表面 CoT 字符本身无法携带病例特异推理状态。
最终 400/400 world answer accuracy = 1.0000。

## 1. 逐层停机可读性
- main: best held-out linear readout=0.8652, at SEP/layer 1.
- branch: best held-out linear readout=0.7865, at SEP/layer 1.
- cmp: best held-out linear readout=0.6067, at FINAL/layer 2.
- corrected: best held-out linear readout=0.7865, at SEP/layer 1.
- answer: best held-out linear readout=1.0000, at THINK/layer 3.
线性可读性只标记“哪里存在信息”；因果身份由下一节 transplant 决定。

## 2. 同一 visible CoT 下的 causal hidden transplant
donor/recipient 保持 goal/start/main relation 相同，只改变 counterfactual relation；visible `THINK/CHECK/FINAL` 完全相同，但 comparison 与 answer 不同。模型在指定 token 后真正停机，只替换一层 recurrent hidden state，再继续喂 recipient 原来的相同 suffix。
- full-state transplant: best donor-answer adoption=1.0000 at FINAL/layer 3.
- <=2D comparison-centroid subspace transplant: best donor-answer adoption=0.3529 at FINAL/layer 3; recipient-answer change=0.3922.
visible CoT 不变而 hidden-state transplant 改变未来输出，因此 reasoning state 至少部分位于 recurrent predictive state，而不是 CoT token identity。

## 3. “推理在哪里”的数学判据
定义 model reasoning locus 为 layer × time 上满足三条性质的 predictive state：① 可区分 future-equivalence classes；② 局部 future-response geometry 随 branch/compare state 变化；③ hidden-state 或低秩子空间干预可按 donor 状态因果重定向未来。对本 GRU，这个 locus 是可停机保存的 h_t；对 Transformer/SSM 可对应 residual/KV/recurrent state 的同类对象。

## 4. CoT 的位置
CoT 可以作为外部控制接口、时间刻度和工作记忆，但不是完整推理状态。这里 CoT 严格固定，内部仍形成不同 main/branch/comparison/correction states；所以“模型在想什么”必须从 hidden predictive dynamics 和 future-control geometry 看，而不能只读可见 CoT。

## 5. 时间定位：在固定 CoT 模板下，因果 reasoning state 逐步显现

第三层 hidden-state transplant 的 donor-answer adoption 随可见模板推进：THINK=0.468，CHECK=0.767，FINAL=1.000。因此 reasoning state 并不是只在最终 readout 瞬间出现；在 THINK 后已经具有可搬运的未来影响，CHECK 后显著增强，FINAL 时形成几乎完整的 answer-determining state。

同时 CHECK/layer3 的 full-state transplant donor adoption=0.767，而 comparison-centroid <=2D patch 只有 0.157。这说明当前 output-only 模型的功能性 reasoning state 不是一个干净的单独 comparison axis，而是更分布式的 predictive state。
