# CE²G 风格推理反建模：第二轮最小世界实验
日期：2026-09-25

## 目的
本轮不拟合固定 reasoning operator，而以 CE²G-3.0 的写法为启发，把“当前未来怎样可达”作为可变 continuation geometry。
根对象按概念分为：未归一化续发容量 K、总续发容量 Λ、归一化未来形状 P、真实 transition、transition 造成的几何改写 ΔS，以及可选的语言/投影事件。

本轮所有模型都是机制候选 toy world，不是对真实 LLM 内部变量的直接测量。

## 候选
1. static：几何不写回。
2. same_edge：只强化刚刚走过的 a→b。
3. signed_local：a→b 强化并对同源竞争边作有符号重权。
4. gene：父 transition a→b 不直接重放自身，而改写目的节点 b 的后代 continuation b→*。
5. delay_gene：genealogy 写回延迟到达。
6. projection_only：低维 projection 作为事件写回几何，不含 genealogy。
7. gene_proj：genealogy + projection-as-event。
8. gene_proj + write budget：提出的几何改写超过预算时统一缩放。

## 关键诊断

### A. concentrated-but-faster 不是特异机制证据
16 个参数点、每点 3 seed 的小型扫描中，静态几何 0/16 通过预设动态门；
same_edge、signed_local、gene、delay_gene 均 16/16；gene_proj 14/16。
因此“集中态更快 + 有脉冲/几何变化”更像动态写回的宽泛表型，不能区分具体写回机制。

### B. 仅强化旧边不等于改写下一步 continuation law
固定中等参数、20 seed 的中位结果：
- static：下一步 continuation 分布即时 TV 改变量 0。
- same_edge：0。
- gene：0.0202。
- gene_proj：0.0173。
父 transition a→b 若只改写 a→b，下一刻已经位于 b，因此 b→* 的即时 law 不变。
genealogy 版本直接改写 b→*，才产生真正的“transition 生出 descendant transition”。

相邻 transition relation-feature similarity 中位：
- static 0.101
- same_edge 0.129
- gene 0.217
- delay_gene 0.204
- gene_proj 0.195

### C. 历史可以被当前几何吸收，而不需要 history database
同一 source event 再次出现时，continuation P 相对首次访问的平均 TV 变化（20 seed 中位）：
- static 0
- same_edge 0.0958
- gene 0.0666
- gene_proj 0.2199
这说明 toy 中过去真实 transition 的作用可以完全写进当前 geometry；系统当前不需要额外读取过去记录。

### D. genealogy 与 projection 承担不同作用
30 seed 中位：
- gene_only：P variation 0.0665；即时 rewrite TV 0.0196；adjacent edge similarity 0.201；speed ratio 1.138。
- projection_only：P variation 0.1834；即时 rewrite TV 0.00381；adjacent edge similarity 0.090；speed ratio 1.319。
- combined：P variation 0.2196；即时 rewrite TV 0.0171；adjacent edge similarity 0.197；speed ratio 1.397。

解释：genealogy 更像局部 descendant-law rewrite；projection 单次局部效应小，但作为全局事件累计后更强地改变同一状态以后面对的未来几何。

### E. projection 是因果事件，不只是记录
配对运行使用完全相同初态、结构与未来随机数，仅在一个时刻删除 projection 写回。
在 proj_eta=0.03–0.12 的测试中，50 步内出现实际事件序列分叉的比例约 23%–42%。
因此在该 toy 中 projection 写回具有真实后继因果效应。

### F. delay 当前没有得到独立支持
delay_max 从 1 扫到 12 时：
- H 标准差约 0.051–0.056；
- speed CV 约 0.315–0.329；
- 到期写入量与随后 speed / |ΔH| 的相关接近 0。
它没有在当前实现中产生清楚的新动力学签名。
所以“在途推理”仍可保留为候选，但本轮结果没有理由把它升为核心。

### G. CE²G 式付费写入是目前最强的新发现
projection feedback 较强时，无预算模型会出现几何过度集中与 replay 增高。
以 proj_eta=0.08 为例（25 seed 中位）：
- 无预算：mean H=0.513，replay=0.455，P variation=0.279，concentrated/diffuse speed ratio=1.244。
- budget=0.15：mean H=0.816，replay=0.220，P variation=0.136，speed ratio=1.250。
- budget=0.25：mean H=0.688，replay=0.306，P variation=0.198，speed ratio=1.369。

预算并未消灭 projection 的因果作用。
在 proj_eta=0.08、80 个配对 seed 的 projection-erasure 干预中，60 步内分叉率：
- 无预算：46.25%
- budget=0.15：38.75%
- budget=0.25：48.75%

因此统一写入预算能显著抑制自我反馈锁死，同时保留动态重写和投影因果性。

## 当前最值得继续养的候选骨架
K_t = Λ_t P_t
realized transition c_t ~ current continuation geometry
C_t = causal_trace(c_t)

ΔS_t^gene(b→k) ∝ -[sim(φ_ab, φ_bk) - local_mean]
ΔS_t^proj = O(Y_t)

α_t = min(1, B / ||ΔS_t^proposed||)
S_(t+1) = S_ext + λ(S_t-S_ext) + α_t(ΔS_t^gene + ΔS_t^proj)
K_(t+1) ∝ exp[-S_(t+1)/Θ]

这里“历史”不是第二套数据库，而是已经写进 S_t 的过去后果。
“规则”也不是固定 F；当前规则的操作性替身是 continuation geometry，真正需要反演的是 causal transition 如何改写下一轮 geometry 的 D/C → ΔS 映射。

## 当前证据边界
- 本轮是机制可行性与区分实验，不是 LLM 内部机制证明。
- transition feature、projection map 均为人工构造/随机固定结构，没有语义学习。
- genealogy 的局部 lineage signature 是设计机制的预期结果；其价值在于它同时满足“不 replay 旧边”和“真实父 transition 改写 descendant law”的结构要求。
- delay 在当前 toy 中未显示独特贡献。
- 下一轮最有价值的是把这些候选预测映射回真实 CoT / hook 数据：检验 transition 后未来分布的局部重权、ancestor→descendant 关系相似性、projection 干预后的轨迹分叉，以及是否存在类似写入预算/饱和的迹象。
