# CE²G 推理反建模 · 第三轮：Transition Genealogy 与可繁衍 Rewrite Phenotype

日期：2026-09-25

## 本轮问题

第二轮表明，父 transition 直接改写下一步 continuation geometry 可以形成一代 genealogy，但单纯“父 transition 与子 transition 更相似”不能稳定形成多代谱系。把该效应强行调强时，reversal / 路径锁定开始上升。

因此第三轮把“繁衍”的对象从 transition 表面形状改成：transition 发生以后，它将如何改写下一代 continuation geometry 的局部 rewrite phenotype。

候选从固定的几何更新算子推进为：

    D_t  ->  D_(t+1)

即几何 S_t 在变化，产生几何变化的有效局部写入法则也允许随真实 transition 改变。

## 最小候选

每条 transition a->b 有表面 relation feature phi_ab。每个当前节点携带一个由此前真实 transition 留下的局部 rewrite field M_t(a)。它不是 history database，只作为当前世界的一部分存在。

一次真实 transition 的有效 rewrite code：

    G_t = norm(phi_ab + gamma * M_t(a))

G_t 不要求下一代 transition 与父代相同，只决定父 transition 怎样重权下一代 b->k。随后真实 transition 把自己的 rewrite phenotype 写入目的地：

    M_(t+1)(b) = (1-rho) M_t(b) + rho G_t

候选写入继续通过 CE²G-style budget 限制后再进入 geometry。

## 结果 1：固定 rewrite law 只能稳定传一代

geometry-only genealogy 的 branching counterfactual 中，父 transition 对第一代 descendant 的相似度增益清楚，第二代以后迅速衰减。参数扫显示：要强行获得较深表面相似度，往往伴随 reversal / 路径锁定升高。

因此“繁衍 = 后代表面越来越像祖先”不是一个好的最小机制。

## 结果 2：让 rewrite phenotype 可繁衍以后，多代谱系出现

30 个独立 seed 的中位数：

| model | code lag1 | code lag2 | code lag3 | code lag4 | raw lag1 | raw lag2 | reversal |
|---|---:|---:|---:|---:|---:|---:|---:|
| fixed D | 0.0292 | 0.0175 | 0.0120 | 0.0141 | 0.0292 | 0.0175 | 0.0931 |
| reproducing D, gamma=1 | 0.4247 | 0.2439 | 0.2051 | 0.2021 | 0.0283 | 0.0224 | 0.0931 |

最关键的结构：rewrite code 在多代保持明显相似；raw transition feature 只维持很弱的相似；reversal 基本不增加。

换句话说：后代表面可以不像祖先，但继承祖先“怎样写下一代世界”的方式。

## 结果 3：真实 ancestry 比打乱 ancestry 保留更多 rewrite-code 连续性

40 个 seed 的中位数：

| condition | code lag1 | code lag2 | code lag3 | code lag4 | raw lag1 | reversal |
|---|---:|---:|---:|---:|---:|---:|
| real | 0.4311 | 0.2444 | 0.2060 | 0.2013 | 0.0312 | 0.0940 |
| shuffled ancestry | 0.1541 | 0.1602 | 0.1649 | 0.1606 | 0.0309 | 0.0931 |
| no inheritance | 0.0298 | 0.0079 | 0.0138 | 0.0155 | 0.0298 | 0.0931 |

- real − shuffled, code lag1: mean 0.2754; 95% bootstrap CI [0.2666, 0.2839]
- real − shuffled, code lag2: mean 0.0826; 95% bootstrap CI [0.0747, 0.0907]
- real − shuffled, code lag3: mean 0.0447; 95% bootstrap CI [0.0379, 0.0515]
- real − shuffled, code lag4: mean 0.0386; 95% bootstrap CI [0.0309, 0.0463]
- raw lag1: mean difference 0.0009; CI [-0.0042, 0.0058]
- reversal: mean difference 0.0006; CI [-0.0033, 0.0044]

谱系信号主要存在于 rewrite code，而不是简单行为重复。

## 结果 4：同 geometry、同当前 transition，只换 rewrite state，下一轮几何仍改变

750 次 mechanism-state transplant 中：当前 geometry 相同、当前节点相同、强制发生同一个 a->b transition，只把源位置携带的 M_t(a) 换成另一份 history-produced rewrite state。

gamma=1 时，下一轮 b->* continuation law 的 TV difference 中位数 = 0.0099。
25-step paired rollout 中，13.9% 发生轨迹分叉；发生分叉的样本中首次分叉中位为第 9 步。

gamma=0 的对照中该效应回到 0；随 gamma 增大才出现。

这表示在该候选世界里存在一种与“当前 continuation geometry”可分离的动态变量：它不必改变此刻发生哪条 transition，而会改变这条 transition 发生以后，世界怎样被改写。

## 当前机制候选

第三轮把候选从

    S_t --fixed D--> S_(t+1)

推进为：

    (S_t, D_t) --C_t--> (S_(t+1), D_(t+1))

其中 D_t 不必是一个全局矩阵；它可以表现为局部、稀疏、沿真实 transition genealogy 传播的 rewrite phenotype。

这是 toy-world 机制结果，不是对真实 LLM 内部结构的直接证明。它产生的可证伪预测是：后代 transition 可以不复制祖先表面行为，但祖先仍可通过可遗传 rewrite effect 改变多代未来；打乱真实 ancestry 应优先破坏 rewrite-level 连续性；在保持当前 observable state 与当前 action 相同的情况下，交换 history-produced rewrite state 应改变 action 之后的后继动力学。

## 下一刀

真实 reasoning 上最值得检验的问题已经从“哪一层表示了当前规则”变成：

> 同一类当前计算事件发生后，不同形成历史是否导致不同的后继内部重组规律？

这比静态 rule probe 更接近当前候选。