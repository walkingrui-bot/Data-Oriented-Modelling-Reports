# MODEL-SCALE-CORRIDOR-025 | 模型大小、训练集覆盖与“道路宽窄”

## 触发问题
前面的 teacher-dimension、control-flow 与 reasoning-locus 实验已经把“底层参数空间很高维、局部有效控制却很低维”分开。本轮进一步问：同一训练世界下，大模型与小模型真正差在哪里？假说不是“大模型有更多方向盘”，而是大模型可能把 predictive terrain 摊得更开；小模型把不同未来状态挤得更近，因此正确答案需要更精密的局部路径。

## 设计
- 固定同一个 400-case reasoning universe、同一词表、同一固定 visible CoT `THINK → CHECK → FINAL`、同一 final-answer objective。
- 只改变 hidden width：8 / 16 / 32 / 64 / 128；对应约 1.7k / 4.1k / 12.4k / 42.8k / 158.9k 参数。每个条件 2 个共同 seed。
- 训练集 unique coverage：25% / 50% / 100%。子集采用嵌套平衡设计：每个 goal×start×main-op 组合始终存在，只逐步增加 counterfactual relation 的覆盖。
- 统一在 CHECK 后停机读取完整 recurrent state，再继续同一个 FINAL suffix。

## 第一版测量与现场修正：raw hidden radius 不可跨模型比较
最初直接用 hidden-space RMS perturbation 到 answer flip 的半径定义“道路宽度”。结果对 seed 与 width 的变化很大，并没有稳定随模型大小增长。结合前文 gauge-control 结果，确认这个读数依赖 hidden coordinate 的缩放/旋转，不能直接跨模型比较。第一版结果保留为测量失败记录，不用于 scaling 结论。

因此新增 gauge-aware geometry：用每只模型在固定 400-case probe universe 上的 hidden covariance C 定义自然状态度量。局部几何道路宽度写为

`r_geo(h) = answer_margin / sqrt(g(h)^T C g(h))`

其中 g 是 answer margin 对 stopped hidden state 的梯度。另把 hidden cloud PCA-whiten 后，计算每个正确 state 到最近不同-answer state 的距离，定义为 **predictive-state separation / terrain spreading**。这个 separation 对线性可逆坐标重参数化不敏感。

## 主结果：大模型最稳定增加的是“状态摊开”，不是控制轴数量
两 seed 平均结果：

```
 coverage  hidden      params  full_acc  wcrowd  state_d95  ctrl_rank  geo_width
   0.2500       8   1706.0000    0.6900  0.2410     6.0000     1.5716     1.2991
   0.2500      16   4122.0000    0.6975  0.5469    10.5000     1.7023     1.1221
   0.2500      32  12410.0000    0.7275  0.6612    10.5000     1.8317     1.4346
   0.2500      64  42810.0000    0.7075  0.8474    16.0000     1.5898     1.3278
   0.2500     128 158906.0000    0.7175  0.9696    24.5000     1.9325     1.3032
   0.5000       8   1706.0000    0.7163  0.2466     6.0000     1.5656     1.1408
   0.5000      16   4122.0000    0.8137  0.6357     9.0000     1.6901     1.9270
   0.5000      32  12410.0000    0.8350  0.7672    12.0000     2.0534     1.7274
   0.5000      64  42810.0000    0.8500  0.9769    16.0000     2.0283     1.6148
   0.5000     128 158906.0000    0.8525  1.0832    29.5000     2.2564     1.3299
   1.0000       8   1706.0000    0.9888  0.8449     6.5000     1.8220     1.1068
   1.0000      16   4122.0000    1.0000  0.9223     8.0000     2.1904     1.3124
   1.0000      32  12410.0000    1.0000  1.0118    15.0000     2.1747     1.6299
   1.0000      64  42810.0000    1.0000  1.0642    13.5000     2.0940     1.6560
   1.0000     128 158906.0000    1.0000  1.1020    25.5000     2.1453     1.2760
```

在每一个 coverage 条件内，hidden width 与 whitened state separation 的 Spearman 相关都约 0.96–0.99。具体地：
- 25% coverage：width 8→128 时，predictive-state separation 0.241→0.970；full-world accuracy 0.690→0.718。
- 50% coverage：width 8→128 时，predictive-state separation 0.247→1.083；full-world accuracy 0.716→0.852。
- 100% coverage：width 8→128 时，predictive-state separation 0.845→1.102；full-world accuracy 0.989→1.000。

与此同时，hidden-state 几何维数明显增长：state d95 与参数规模的全体 Spearman≈0.95；但 gauge-aware control stable rank 只在约 1.4–2.7 的范围内波动，没有随模型大小成比例增长。

这给出一个很具体的 scaling picture：

`larger capacity -> more room to separate predictive states`

而不是

`larger capacity -> proportionally more online control axes`

## 训练集与模型大小的分工
训练集 coverage 是当前有限世界里最强的 accuracy 因子：coverage 与 full-world accuracy 的 Spearman≈0.91。参数规模与 accuracy 的关系较弱，而且依赖 coverage。

- 25% coverage：即使 width 128 已把 hidden terrain 显著摊开，accuracy 仍只有约 0.718。空间有了，但训练痕迹没有规定所有区域该怎样接到答案。
- 50% coverage：width 8→128 时 accuracy 约 0.716→0.853；容量开始把已有训练约束展开成更可分离的 predictive states。
- 100% coverage：width 8 已约 0.989，width≥16 均达到 1.000；继续增大模型主要改变内部表示几何，而不是可见准确率。

因此当前证据支持一个三因素关系：

`dataset constraints × representational capacity × optimization history -> predictive-state geometry -> answer`

训练集决定“哪些道路与连接必须存在”；容量决定“这些 predictive distinctions 能被摊开到多大的内部空间”；优化历史决定同样的容量和数据最终落在哪一种具体几何。

## “路宽”需要拆成两个量
本轮最重要的修正是：直觉上的 road width 至少包含两个不同数学对象。

1. **Local basin width**：离当前 answer decision boundary 的 covariance-normalized 局部半径 `r_geo`。它没有随模型大小单调增加，且明显受训练落点影响。
2. **Inter-route separation / terrain spreading**：不同 future-equivalence / answer states 在模型自身自然几何里的间隔。这个量随模型大小非常稳定地增加，并与 accuracy 显著相关。

所以“大模型路更宽”的更精确版本不是“每个点离边界都更远”，而是：**大模型把不同可能未来摊到更分离的内部区域，减少 state aliasing；小模型则更容易把不同未来压在相近的表示区域里。**

## 与此前研究线的统一
- TEACHER-DIMENSION-TRANSFER：老师决定需要几条独立控制自由度，architecture 提供容量上限。
- REASONING-LOCATOR：正确推理状态存在于 layer×time predictive dynamics，而不是 visible CoT 本身。
- 本轮：当 architecture capacity 超过最低任务维数后，额外容量主要可以用于扩大 predictive-state embedding / separation，而 control rank 并不同比例上升。

统一 picture：

`training world / trace -> required predictive distinctions -> model capacity unfolds them in hidden geometry -> low-dimensional local control moves among them -> final answer`

## 证据范围
直接证据来自同一 400-case 合成 reasoning universe、2-layer GRU、5 个 hidden widths、3 个 unique-data coverage、2 seeds。当前实验支持“容量显著改变 predictive-state separation，而数据覆盖强烈决定正确连接与泛化准确率”；它还没有把这一 scaling law 外推为真实大语言模型的普适定律。

## 原始文件
- `MODEL-SCALE-CORRIDOR-025_models.csv`
- `MODEL-SCALE-CORRIDOR-025_aggregate.csv`
- `MODEL-SCALE-CORRIDOR-025_geo_models.csv`
- `MODEL-SCALE-CORRIDOR-025_geo_aggregate.csv`
- `MODEL-SCALE-CORRIDOR-025_spearman.csv`
- `MODEL-SCALE-CORRIDOR-025_accuracy.png`
- `MODEL-SCALE-CORRIDOR-025_spreading.png`
- `MODEL-SCALE-CORRIDOR-025_state_d95.png`
- `MODEL-SCALE-CORRIDOR-025_control_rank.png`
- `MODEL-SCALE-CORRIDOR-025_local_width.png`
- `MODEL-SCALE-CORRIDOR-025_spreading_vs_accuracy.png`
- `MODEL-SCALE-CORRIDOR-025_fast.py`
- `MODEL-SCALE-CORRIDOR-025_geometry.py`