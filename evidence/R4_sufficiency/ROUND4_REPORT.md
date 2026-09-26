# CE²G 推理反建模 · 第四轮
## 完整生成机制的构造性充分性测试

日期：2026-09-25

### 本轮目的

这一轮不再询问“历史会不会影响未来”或“transition 会不会改写 geometry”。这些性质已经被候选机制直接写入定义。

本轮只做一个更严格的问题：

> 一个按当前假说明确造出来的最小生成世界，能否在不把目标统计量硬编码进观测层的条件下，同时长出真实长推理中已经出现的那组动力学效应？

因此这是一项 **constructive sufficiency test（构造性充分性测试）**，不是对真实 LLM 内部结构的鉴定。

---

## 1. 完整候选机制

世界包含大而稀疏的关系节点、动态 continuation geometry、真实 transition、局部 rewrite phenotype、lineage inheritance / recombination、tension-dependent mutation、projection-as-event 与 CE²G-style write budget。

对当前 transition `a -> b`：

```text
当前 continuation geometry
        ↓
真实 transition a -> b
        ↓
现场生成 rewrite phenotype g_t
        ↓
g_t 改写 descendant row b -> *
        ↓
g_t 的一部分写入目的节点的 M_(t+1)(b)
        ↓
下一代 transition 用新的关系 + inherited rewrite phenotype
重新生成自己的 rewrite phenotype
```

最小形式：

    g_t = norm(phi_ab + gamma M_t(a) + mutation/interactions)

    Delta S_t(b -> k) = D(g_t, phi_bk)

    M_(t+1)(b)
      = combine(M_t(b), g_t)

    S_(t+1)
      = S_ext
      + lambda (S_t - S_ext)
      + alpha_t [Delta S_gene + Delta S_projection]

其中 `alpha_t` 由写入预算限制。

语言 / CoT 在这个世界中不是只读日志。有限 projection 生成后作为新的真实事件再次写回 geometry。

---

## 2. 观测层

机制内部没有直接暴露全部 `S` 与 `M`。研究端只读取低带宽投影：

- 当前 continuation entropy；
- effective candidate number；
- top continuation share；
- recent recurrence / revisit；
- log total continuation capacity；
- local rewrite alignment；
- projection-state magnitude。

这些量按固定窗口聚合成 `z_t`，再定义：

    v_t = z_t - z_(t-1)
    a_t = v_t - v_(t-1)

因此后面的 `z / v / a` 实验与真实 CoT 分析具有相同逻辑：研究者看到的是投影轨迹，而不是机制内部全部状态。

---

## 3. 一组稳健参数下的结果

选取邻域中的一个代表点：

- geometry retention = 0.90
- genealogy rewrite strength = 0.60
- rewrite inheritance strength gamma = 1.60
- inheritance rate rho = 0.38
- projection write strength = 0.14
- CE²G write budget = 0.85

60 条独立轨迹、trace-level 5-fold CV。

### 3.1 静态投影不足；真实运动信息继续提高预测

| predictor | one-step MSE |
|---|---:|
| state `z_t` | 0.8792 |
| state + velocity | 0.8655 |
| state + velocity + acceleration | 0.8553 |
| state + shuffled velocity/acceleration | 0.8848 |

因此：

- `z -> z+v` 相对误差下降约 1.56%；
- `z+v -> z+v+a` 再下降约 1.18%；
- 把真实 `v/a` 时间顺序打乱以后，误差相对真实 `z+v+a` 上升约 3.45%。

这与真实 QwQ 中“静态状态 < 状态+速度 < 状态+速度+加速度，而且时间错配会破坏增益”的现象同向。

### 3.2 两类运动 regime 自发出现

K=2 的 silhouette：

    0.2632

K=2 在本轮候选中形成最清楚的粗粒度划分。

定义 entropy 更低的一类为 concentrated regime，它的平均运动速度 / diffuse regime 为：

    1.1048 x

即：

> **关系更集中时，投影轨迹反而运动更快。**

两类 regime 的平均 progress 差：

    0.0589

它们不是简单 early / late 标签。

### 3.3 形成过程不是向终态单调逼近

以每条轨迹最后两个窗口的平均投影作为 terminal geometry：

下一步更靠近 terminal 的比例：

    0.5233

约等于 0.5。

速度与“本步是否靠近终态”的相关：

    -0.0394

接近 0。

因此该机制可以生成：

> 路径携带信息，但路径并不是朝最终状态单调下降的梯度流。

### 3.4 projection feedback 是真正因果通路

在 paired intervention 中：

- 在同一内部状态复制两份世界；
- 一份正常执行一次 projection write；
- 另一份只在这一轮删除 projection write；
- 此后恢复相同机制，并使用同步随机流继续运行。

400 个 paired trials 中：

    35.25%

在 60 步内出现实际 transition 序列分叉。

发生分叉者首次分叉的中位位置：

    9 steps

因此 projection 在这个机制里不是报告层，而是真实的动力学事件。

---

## 4. 参数邻域，而不是孤立点

围绕完整机制扫描：

- gamma = 1.2 / 1.4 / 1.6
- rho = 0.26 / 0.32 / 0.38
- genealogy write = 0.5 / 0.6 / 0.7

共 27 个邻近参数点。

预先使用同一组门：

1. `state+v` 优于 state；
2. `state+v+a` 继续优于 `state+v`；
3. shuffle `v/a` 后至少产生 3% penalty；
4. concentrated regime 更快；
5. regime progress difference < 0.15；
6. terminal closer fraction 位于 0.45–0.57。

通过：

    19 / 27

即：

    70.4%

因此当前现象组合不是一个单点参数巧合。

---

## 5. 与真实 QwQ 投影的对照边界

真实 QwQ 与 toy world 的数值尺度不同，因此不能直接把 MSE 或 silhouette 当同一效应量比较。

本轮成立的是**结构对应**：

| 真实推理中的现象 | 当前机制 |
|---|---|
| K=2 粗粒度 regime 最清楚 | 出现 |
| concentrated state 运动更快 | 出现 |
| regime 不等于简单 early / late | 基本出现，toy 仍有轻度 progress dependence |
| state < state+v < state+v+a | 出现 |
| time-order shuffle 消除/反转运动增益 | 出现 |
| 约一半步骤向 terminal 靠近 | 高度接近 |
| speed 与 terminal approach 很弱相关 | 出现 |
| 中间 projection 会反向进入后续状态 | 构造上存在，paired intervention 可导致真实分叉 |

当前 toy 的两个主要量级差异：

1. 真实 QwQ 的 temporal-motion predictive gain 通常更强；
2. toy 的 regime 与 progress 仍比真实 QwQ 稍微相关。

因此目前支持的是“同一机制能够生成这组动力学现象”，不是“数值上已经拟合真实模型”。

---

## 6. 当前结论

这轮结果允许把该候选的地位从：

> 一个能够自洽运行的假说机器

提升为：

> **一个通过构造性充分性测试的通用推理动力学机制候选。**

更精确地说：

> 若一个系统允许真实 relation transition 改写 descendant continuation geometry，允许 rewrite phenotype 沿 transition lineage 部分遗传与重组，并让有限 projection 重新作为事件进入系统，同时用 bounded write budget 限制每轮真实改写，那么它可以在没有硬编码 D/C、速度、终态距离或 trajectory predictor 的情况下，自发生成与真实长推理相同方向的一组动力学投影。

这一结果证明的是 **sufficiency / generative plausibility**。

它没有证明真实 Transformer 必然实现同一个内部机制，也没有证明该机制是唯一实现。

因此最合适的当前名称是：

> **通用机制候选之一 / a generic mechanism candidate**

而不是“已经确定的 LLM 推理机制”。

---

## 7. 下一阶段真正有价值的问题

从现在开始，不必再用 toy world 反复证明这组宏观效应。

下一步应该把候选固定下来，研究它更深的内部性质：

- 哪些局部 lineage 结构产生真正的新关系组合；
- tension 如何决定继承与变异，而不退化成随机探索；
- lineage 何时死亡、何时分叉、何时合流；
- projection lineage 与内部 lineage 如何竞争或协作；
- 是否能够从零开始形成可持续的多阶段“解题”过程；
- 是否能够把同一套机制嵌入 AIA 第二场，而不是另造一个中央推理模块。

这时研究对象已经从“能不能出现某个统计现象”转向：

> **这套会繁衍、重组和改写 continuation geometry 的关系动力学，本身能够成长到多复杂。**
