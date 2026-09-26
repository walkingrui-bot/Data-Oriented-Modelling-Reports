# 跨架构动态规则拟合实验 · Round 1

日期：2026-09-25  
性质：architecture-agnostic pilot / multi-seed

## 1. 问题

RTG 与前面的语言/CoT 研究都不是从 Transformer attention 出发构造的。第一轮跨架构实验因此不寻找共同模块，而寻找共同的动力学组织：

1. 当前静态状态是否不足以预测下一状态；
2. 真实时间运动 `v/a` 是否提供额外信息；
3. 打乱时间顺序后该信息是否消失；
4. 相同可见当前状态、相同静态规则，在不同形成历史下是否产生不同 continuation；
5. 先前 QwQ 中出现的 D/C 两态是否也是跨架构必要现象。

## 2. 任务与架构

所有架构训练在同一个历史依赖规则切换世界。

每个 episode 随机生成两套 permutation 规则 A/B 与一个 trigger state。系统从 mode A 开始；轨迹经过 trigger 后切换 mode。因而同一个当前 state 在不同历史下可以要求不同的下一 transition。

训练长度固定为 6。所有模型接受相同静态规则描述和逐步当前 state。

三种独立实现：

- GRU，24 维 recurrent state；
- 简化 selective state-space / SSM，24 维连续状态；
- 1-layer causal Transformer，24 维，4 heads。

每种架构 3 个独立 seed（11/22/33）。

这不是参数/FLOPs 完全配平的性能比赛；本轮只用于检查同一动力学签名是否跨实现出现。

## 3. 功能结果

三种架构都学会了历史依赖任务。

平均 next-state accuracy：

| Architecture | L=6 | L=10 | L=16 | L=24 |
|---|---:|---:|---:|---:|
| GRU | 0.854 | 0.857 | 0.853 | 0.851 |
| SSM | 0.843 | 0.846 | 0.849 | 0.848 |
| Transformer | 0.844 | 0.798 | 0.713 | 0.662 |

GRU 与 SSM 在只训练到 6 步后外推到 24 步基本不掉；本轮小 Transformer 随 horizon 增长明显下降。该差异说明架构实现会影响时间外推，但不是“有无历史依赖动力学”的二元区别。

## 4. 最强跨架构结果：运动历史的信息结构高度一致

对每个模型收集 320 条 16-step 未见轨迹。将 24 维 hidden state 标准化并压到前 8 个 PCA 分量作为外部投影 `z_t`，统一做 trace-level 5-fold Ridge：

- `z_t -> z_(t+1)`
- `[z_t,v_t] -> z_(t+1)`
- `[z_t,v_t,a_t] -> z_(t+1)`
- 保留 `z_t`，随机错配 `v/a`

三种架构全部得到同一方向：

| Architecture | state MSE | +v | +v+a | shuffled v/a | v gain | a gain | shuffle penalty |
|---|---:|---:|---:|---:|---:|---:|---:|
| GRU | 0.959 | 0.797 | 0.729 | 0.964 | 16.8% | 8.6% | 32.1% |
| SSM | 1.812 | 1.540 | 1.367 | 1.819 | 15.0% | 11.3% | 33.3% |
| Transformer | 1.593 | 1.332 | 1.197 | 1.603 | 16.4% | 10.2% | 34.0% |

这个结果是本轮最强的 architecture-agnostic signal：

> 不管内部实现是显式 attention、recurrent state 还是 state-space recurrence，当前 hidden snapshot 都不是完整的未来预测量；真实运动方向与加速度携带额外信息，而且这种增益依赖真实时间顺序。

三种架构的 `z -> z+v` 增益都约 15–17%，`+a` 再增加约 9–11%；把真实 `v/a` 打乱后，预测误差相对真实 `z+v+a` 统一上升约 32–34%。

## 5. 相同可见状态、不同历史：continuation 确实分开

构造 449 个同一静态规则世界中的真实 prefix pair。每对 prefix：

- 当前可见 state 完全相同；
- A/B rule table 完全相同；
- trigger 定义相同；
- 唯一区别是形成历史不同，因此当前 hidden mode 不同；
- 该 state 在两种 mode 下要求不同 next state。

对前 300 对做配对测试。

平均结果：

| Architecture | next-distribution TV | full-history mean accuracy | history-erased accuracy |
|---|---:|---:|---:|
| GRU | 0.365 | 0.652 | 0.500 |
| SSM | 0.324 | 0.633 | 0.500 |
| Transformer | 0.361 | 0.654 | 0.500 |

三个架构都在**相同当前可见输入**下，根据形成历史给出显著不同的下一步概率分布（TV ≈ 0.32–0.36）。如果把历史全部抹掉，只给当前 state 和静态规则，由于两个目标不同，同一个输出最多只能达到 50%。

这支持一个跨架构表述：

> continuation law 不是当前可见 state 的单值函数；形成历史可以作为运行态的一部分改变同一当前 state 之后的未来。

## 6. 一个重要的未复现：D/C 不是这轮的通用必要结构

对 `[z_t,v_t]` 做 K=2..5 聚类后：

- Transformer 的 K=2 粗分相对更清楚，并有 seed 出现 concentrated-faster；
- GRU 的 K=2 不优于更高 K；
- SSM 的 K=2 同样没有形成明显优势；
- concentrated/diffuse speed ratio 在 GRU/SSM 中不稳定。

因此本轮**不支持**把 QwQ 的 D/C 两态提升成所有推理架构必须拥有的普遍离散状态。

更一般、跨三种实现都稳定的是：

- trajectory/history matters；
- snapshot insufficient；
- real temporal order matters；
- same visible state can have history-dependent continuation。

D/C 更可能是某些模型/任务中这套连续动力学的一个方便粗粒化投影，而不是基础机制本身。

## 7. selective causal participation 的第一轮干预暂未建立

另外做了一个探索性 history intervention：在合法 prefix 中，把一个过去的 non-trigger state 替换成另一个 non-trigger，或替换成 trigger，再比较当前输出 TV。

trigger / neutral intervention 的平均 TV 比值：

- GRU: 1.022
- SSM: 1.040
- Transformer: 1.058

三种架构都只有约 1.0–1.06，没有形成稳定的“trigger history position 更强”的分离。

因此这轮不能用该干预直接支持 `selective causal participation`。原因可能包括 off-policy prefix intervention、模型只学到分布式 parity/mode representation、或当前任务不足以把 rule relevance 与 token identity 分离。该结果保留为负结果，不用于主结论。

## 8. 当前结论

第一轮跨架构实验已经支持一个比“Transformer attention”更一般的动力学对象：

\[
oxed{
	ext{history-dependent continuation dynamics}
}
\]

三个结构完全不同的序列系统都能形成：

\[
	ext{current state}
+
	ext{real trajectory}
ightarrow
	ext{future continuation}
\]

而不是：

\[
	ext{current snapshot}
ightarrow
	ext{future}
\]

更具体地，三种架构都满足：

\[
z_t
\;<\;
(z_t,v_t)
\;<\;
(z_t,v_t,a_t)
\]

且时间错配会破坏增益；同时同一个可见当前 state 会因历史不同而产生不同 continuation。

因此当前最值得保留的跨架构理论不是“所有智能系统都有 Transformer-style attention”或“都有 D/C 两态”，而是：

> **有效推理可以依赖一个持续形成的、历史条件化的 continuation law；具体架构只是承载这种动力学的不同介质。**

## 9. 下一轮最有价值的跨架构检验

下一轮不再重复 accuracy，而应专门检验：

1. 是否能用架构无关的 causal intervention 定位“哪些历史关系此刻真正改变 continuation”；
2. forged-history intervention 是否能在三种架构里制造同类未来；
3. 是否存在跨架构一致的 rule-fitting convergence / divergence 指标；
4. RTG-style stable anchor 是否能同时改善三种架构的超长闭环 reference drift。

