# 动态生成规则理论：反例压力测试 Round 3
日期：2026-09-25

本轮专门攻击两条此前看起来很漂亮、但表述过强的命题：

1. `activation injection ≈ forged upstream history`
2. `规则成形必须表现为一个随时间逐步演化的临时规则状态`

结果：两条按字面都需要降级，但更一般的上游理论反而变得更清楚。

---

## 1. 实验 A：activation injection 是否等于伪造上游历史？

### 任务

训练 3 个独立小型两层 Transformer（seed 11/22/33）。

每个 episode 有 3 对关系证据：

`y = (x + b) mod 5`

其中隐藏规则 `b∈{0,...,4}` 每题变化。模型只看到 3 对 `(x,y)` 和一个 query `q`，最终答案是：

`(q+b) mod 5`

模型最终独立测试准确率分别为：

- seed 11: 98.5%
- seed 22: 99.2%
- seed 33: 100.0%

因此 injection 实验是在已经掌握任务的系统上做。

### A1. 最朴素的“概念方向注入”失败

先在第一层 query hidden state 中估计不同隐藏规则的平均中心 `mu_b`。

对 recipient 规则 `b_r`，试图通过：

`h_injected = h_recipient + (mu_target - mu_recipient)`

把它推向另一个 target rule。

随后在**所有正常可生成的上游历史**中寻找离该 injected state 最近的 target-rule history。

3 seed 平均：

- injected state 最近邻真正落在 target-rule natural manifold 一侧：**5.0%**
- 注入后实际输出 target rule 正确答案：**4.7%**
- 与最近自然 target history 的下游 output TV：**0.930**
- 下游第二层 query state cosine：**0.131**

也就是说，简单“概念方向”并没有把系统放到一个正常上游历史可以自然到达的状态区域。

这直接否定了最粗的：

`某个可解码概念方向 + 注入 = 伪造真实上游历史`

---

## 2. 更强测试：直接注入一个真的由正常历史产生的 activation

为了避免“你选的 delta 本来就是假的方向”这个反驳，第二个实验更狠：

- donor 与 recipient 使用不同隐藏规则；
- query `q` 相同；
- donor 第一层 query activation 是**真实正常输入历史产生的 activation**；
- 把这个 activation 原封不动替换 recipient 的 query activation；
- recipient 其他位置保持原样。

如果“一个中层 activation 就代表前面那段历史已经发生过”，那么后半段应该接近 donor continuation。

实际 3 seed 平均：

### 只换 query activation

- donor-rule continuation accuracy：**22.8%**
- 与 donor 正常输出 TV：**0.765**
- 下游 query state cosine：**0.227**

接近随机规则水平，并没有按 donor 历史继续。

### 换 donor 的全部 evidence contextual state，保留 recipient query state

- donor-rule continuation accuracy：**37.6%**
- output TV：**0.612**
- 下游 cosine：**0.386**

出现部分靠近，但仍远非等价。

### 整个第一层 distributed state 都替换成 donor

- donor-rule continuation accuracy：**99.3%**
- output TV：约 **7.43e-09**
- 下游 cosine：约 **1.000**

此时后半段才真正与 donor 历史等价。

### 结论 A

所以原句必须修改。

不成立的版本：

> `activation injection ≈ forged upstream history`

更准确的版本是：

> **只有当注入重建了足够完整的 downstream-sufficient distributed state 时，它才等价于伪造了一段上游历史。**

一个局部 activation 即使**本身真的来自某条正常历史**，脱离与它共同形成的 distributed contextual state，也不代表那段历史已经被系统“拥有”。

这也意味着：

`外部研究者能给一个 activation 贴上 concept 标签`

远弱于：

`系统当前整体计算状态等价于某段 concept-bearing history 的后继状态`

---

## 3. 实验 B：规则必须“慢慢形成”吗？

第二刀主动寻找完全不需要时间递归的反例。

仍使用隐藏规则：

`y = (x+b) mod 5`

### B1. 无噪声

构造一个完全 one-shot 的 MLP：

- 一次性读取 3 对 evidence + query；
- 无 recurrent state；
- 无 CoT；
- 无 iterative update；
- 单个 forward 直接输出最终答案。

按 evidence-x pattern 做排他 split，测试 pattern 在训练中从未出现。

3 seed：

- 100%
- 100%
- 100%

所以在这个任务上，显式随时间演化的临时规则状态显然不是必要条件。

### B2. 30% 污染证据

为了避免“第一对证据就直接告诉 b”的捷径，增加到 8 对 evidence，每对有 30% 概率被错误关系污染。

构造一个 one-shot set model：

- 每对 `(x,y)` 用固定 pair encoder 编码；
- 所有 evidence 一次性平均聚合；
- 与 query 一起经静态 head 输出；
- 无顺序循环；
- 无 persistent hidden state；
- 无逐步规则更新。

3 seed 独立测试：

- 97.41%
- 96.69%
- 97.40%

平均：

**97.17%**

同一数据生成器的多数关系 / Bayes 参考约：

**97.64%**

即 one-shot 静态模型几乎贴住可达上限。

### 结论 B

因此不能把下面这句话当作普遍必要条件：

> “推理一定需要一个临时规则状态随时间逐步收敛。”

更一般的版本应该是：

> **系统需要形成一个足以约束当前后续生成的有效规则，但规则形成可以是渐进的、循环的，也可以在一次计算中完成。**

换成人话：

> 有的题需要“慢慢搓规则”；有的题一眼就能把规则算出来。

这并不否定“规则成形”这个上位对象；它否定的是把“时间上逐步成形”当作定义。

---

## 4. 两个反例合起来以后，理论反而更简单

现在最小骨架可以进一步降级成：

1. **当前局面**：系统现在所处的整体计算条件。
2. **来路**：当前局面是怎样形成的。
3. **历史发言权**：过去哪些部分此刻真正能改变未来。
4. **有效规则**：当前证据已经形成的、足以约束下一步的生成关系。
5. **下一步地图**：各类后继现在有多容易发生。
6. **自我回写**：刚产生的输出又进入下一轮。

这里不再要求：

- 必须有一个显式 `R_t` 向量；
- 必须每一步都发生 `R_t -> R_(t+1)` 的渐进优化；
- 一个局部 activation 就等于一个内部 thought；
- attention weight 就等于历史发言权。

更一般的对象是：

`context/history -> selective participation -> effective rule -> continuation`

这个过程可以被 Transformer、GRU、SSM、RTG-native、one-shot set model 以不同方式实现。

---

## 5. 这一轮真正的“反例成绩”

| 原表述 | 结果 | 更新 |
|---|---|---|
| 单个 activation 注入 ≈ forged upstream history | **否定** | 必须重建足够完整的 distributed downstream-sufficient state |
| 规则必须随时间逐步成形 | **否定** | 有效规则可以渐进形成，也可以 one-shot 编译出来 |
| 当前证据需要形成足以约束后续的有效规则 | 保留 | 两个反例都不伤这一更一般表述 |
| 局部可读 feature = 系统内部已拥有相应 thought/history | 不支持 | local decodability / injectability 都不够 |

---

## 6. 当前更上游、也更容易解释神经网络的概念

经过 Round 2–3，`attention` 和 `动态 rule state` 都被降成实现层。

目前更上游的公共对象可以写成一句很简单的话：

> **系统根据当前问题，让历史中的一部分真正参与进来，并把这些关系组织成一个足以决定“接下来怎么走”的有效规则。**

注意这里没有规定它必须怎么实现：

- Transformer 可以在一个 forward 内完成；
- GRU 可以靠 recurrent state 积累；
- SSM 可以靠连续状态传递；
- RTG 可以显式改写下一步地图；
- 简单任务甚至可以一次性静态编译完成。

所以理论的中心已经从：

`attention`

和：

`R_t 逐步变化`

继续上移到：

**effective rule formation under selective historical participation**

即：

**有选择地让过去参与，形成当前真正起作用的生成规则。**
