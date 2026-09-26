# GCM Engineering Round 2
## 从 Attention heatmap 到可观测、可定位、可控制的生成函数仪表

### 1. 这轮真正要解决的问题

上一轮已经说明：raw attention 不是“历史发言权”本身。工程上真正需要的不是再造一张更漂亮的 attention 图，而是回答四个不同问题：

1. 模型现在已经在形成哪一种未来？
2. 哪些历史关系真正会改变那个未来？
3. 这种影响会在第几步变得可见？
4. 当前网络的什么位置仍然有干预杠杆？

这轮把它们整理为 GCM 的四个工程仪表：

- **Future-State Readout（未来状态读数）**
- **Influence Horizon Profile（影响时域谱）**
- **Future Causal Influence / cheap influence estimators（未来因果影响及其廉价近似）**
- **Future Control Gain（未来控制增益）**

Attention 被保留，但降为其中一种 routing telemetry。

---

## 2. 公平的 Attention 基线

为了避免故意选错 attention 位置，本轮先在训练数据上选择每个 seed 最能恢复相关历史的 layer / query read-position，再把该位置固定到 held-out 测试集。

因此这里的 raw-attention 58.3% 不是“随便平均 attention”的弱基线，而是经过训练集校准后的公平版本。

3 seeds × 64 held-out examples：

| 指标 | 找到真正改变未来的历史 Top-1 | ROC-AUC | AP | 与 exact FCI 的 Spearman |
|---|---:|---:|---:|---:|
| train-selected raw attention | 58.3% | 0.772 | 0.709 | 0.273 |
| attention × future-gradient | 58.3% | 0.708 | 0.529 | 0.291 |
| future gradient norm | 69.3% | 0.817 | 0.629 | 0.471 |
| directional future gradient | 79.2% | 0.870 | 0.756 | 0.533 |
| **3-point integrated directional future gradient** | **100%** | **1.000** | **1.000** | 0.735 |
| **batched future-margin counterfactual** | **100%** | **1.000** | **1.000** | **0.806** |
| exact FCI | 100% | 1.000 | 1.000 | 1.000 |

一个重要负结果也保留：

> 简单把 attention 乘上 future-gradient，没有自动变成好的因果指标。

这说明“给 attention 加一点梯度”仍然把工程对象放错了层级。真正有效的改进来自直接把目标改成“未来 continuation 会怎样变化”。

---

## 3. 第一个可实际部署的近似：Directional Future Gradient

定义一个未来分支分数 s_H，表示当前历史支持哪一种未来 continuation。

对历史位置 i，不只看梯度范数，而看一个**真实可发生的反事实方向** delta_i：

DFG_i = | grad_{e_i} s_H dot delta_i |

一次 backward 即可同时得到所有历史位置的 DFG。

结果：
- Top-1 = 79.2%
- ROC-AUC = 0.870
- 明显高于公平 raw attention 的 58.3%

这给工程师一个很直接的原则：

> 不要只问“这里梯度大不大”；问“沿一个有语义意义的历史改变方向走，未来分布会动多少”。

---

## 4. 三点积分以后，廉价梯度近似已经可以追平源定位

普通 DFG 仍然受局部线性误差影响。本轮沿同一个真实反事实方向取 3 个积分点，构造：

Integrated Directional Future Gradient

它仍然不需要逐个历史位置做完整自回归 rollout；所有历史位置可以批处理。

3 seeds × 64 examples：

**相关历史 Top-1 = 100%**

这并不表示它和 exact FCI 在所有数值上相同：
- 与 exact FCI 的平均 Spearman = 0.735
- 但在本任务最重要的工程问题——“到底是谁在塑造未来”——上全部选对。

因此它可以作为一个很有潜力的工程中档仪表：

- 比 raw attention 更接近真实未来影响；
- 比完整 FCI 更便宜；
- 保留可微、可批处理性质。

---

## 5. 一个更简单的工程版本：Batched Future-Margin Counterfactual

如果系统能够构造合理的候选反事实，则甚至不必 backward。

把：
- 原历史
- 历史位置 1 的反事实
- 历史位置 2 的反事实
- …
一次放进 batch。

只读一个**未来 continuation margin**，比较它改变多少。

本轮：
- Top-1 = 100%
- ROC-AUC = 1.000
- AP = 1.000
- 与 exact FCI 的 Spearman = 0.806

这提示一个现实 LLM 的可行工作流：

1. Attention / lexical / retrieval 信号只做廉价候选筛选；
2. 对少量候选 span / relation packet 做 batched future-margin counterfactual；
3. 只对最后需要精确判断的少数候选跑完整 FCI。

换句话说：

**Attention 可以留下，但更适合作为 prefilter，而不是最终的重要性判决。**

---

## 6. 第二个新对象：Influence Horizon Profile

同一个历史关系可能现在完全不改变下一 token，但已经决定更远的未来。

本任务就是刻意这样设计：
- A/B 在未来第 1、2 步输出完全相同；
- 第 3、4 步才真正分叉。

真实相关历史的 counterfactual TV：

| horizon | 相关历史 | 无关历史 |
|---|---:|---:|
| 1 | 0.000054 | 0.000044 |
| 2 | 0.000056 | 0.000049 |
| 3 | **0.998948** | 0.000128 |
| 4 | **0.998897** | 0.000071 |

192/192 个 held-out case 的“影响开始超过 TV=0.1”的第一步都在 horizon 3。

所以一个单独的 importance score 不够。

应该画：

I_i(H) = 第 i 段历史对未来第 H 步的影响

这就是 **Influence Horizon Profile（影响时域谱）**。

它告诉工程师：

- 谁现在正在起作用；
- 谁目前潜伏；
- 谁会在几 token 后突然成为决定性约束。

这是 next-token attention 无法直接给出的信息。

---

## 7. 第三个新对象：Future-State Readout

在第 3 个 token 真正分叉之前，模型内部是否已经形成未来模式？

用一个很小的非线性 probe 读取 prompt-end hidden state：

| layer | 未来模式 held-out readout |
|---|---:|
| 1 | 67.2% |
| 2 | 66.1% |
| 3 | 82.3% |
| 4 | **89.6%** |

也就是说，越往后，“未来准备怎么生成”越来越容易被读出来。

这提供一个传感器概念：

> **Future-State Readout = 当前 hidden state 对未来 continuation family 的可读程度。**

它不声称 probe 就是机制；它只是在线观测仪表。

---

## 8. 第四个新对象：Future Control Gain

“哪里最容易读懂”不等于“哪里最适合控制”。

本轮直接对每一层、每一个 prompt 位置加入一个可微 residual intervention delta，并定义：

ControlGain(l,p) = || d s_H / d delta_(l,p) ||

这是“一单位局部干预，未来 continuation score 能变化多少”的局部控制增益。

层平均：

| layer | Future-State Readout | mean Control Gain |
|---|---:|---:|
| 1 | 67.2% | **0.497** |
| 2 | 66.1% | 0.252 |
| 3 | 82.3% | 0.129 |
| 4 | **89.6%** | **0.000** |

这形成一个非常清楚的工程分离：

> **深层更像传感器：容易看清“已经形成什么”。**
>
> **早层更像执行器：还有足够下游计算可以把未来真正推走。**

在这个模型里，Layer 1 的 QUERY 位点是平均控制增益最高的位置之一；到了最后一层，历史位置的信息路由已经完成，再改过去位置几乎没有杠杆。

---

## 9. Control Gain 不是只在微分里好看

为了验证梯度 Control Gain 是否真的能预测有限幅度的实际干预，本轮在 36 条独立轨迹上，对 layer × prompt-position 的所有位点：

1. 用梯度预测控制增益；
2. 沿该位点的梯度方向做 norm=0.75 的真实 finite intervention；
3. 比较实际 future-score 改变量。

结果：

- Spearman(predicted, realized) = **0.995**
- Pearson(predicted, realized) = **0.984**

因此 Control Gain 在这个构造世界里不只是一个局部解释量，它非常准确地告诉工程师：

> **哪里下手真的有用。**

---

## 10. GCM 2.0：比 Attention 更工程化的四张图

现在不建议再只做一张 attention heatmap。

一个更实用的生成函数仪表盘应该同时显示：

### A. Future-State Readout
模型现在已经在形成哪类未来？

### B. Influence Horizon Profile
哪些历史关系会在第几步开始改变未来？

### C. Future Influence
谁真正拥有 future-changing power？

建议三级成本：
- DFG：一次 backward，便宜；
- 3-point Integrated DFG：中等成本，本轮源定位 100%；
- batched future-margin / exact FCI：高置信度校准。

### D. Future Control Gain
现在从哪层、哪个位置下手还有杠杆？

这四张图分别回答：

**状态、来源、时机、杠杆。**

Attention 只覆盖其中的一部分 routing 现象。

---

## 11. 最适合工程师的一句话

不要再只问：

> “模型现在 attention 在哪里？”

改成连续四问：

> **它现在准备往哪种未来生成？**
>
> **谁会在未来第几步真正改变它？**
>
> **这种影响现在有多强？**
>
> **我从哪里动手还能把它推走？**

这才是“模型正在拟合生成函数”这一理论对应的工程观测接口。

---

## 12. 当前边界

这是 3 个独立 seed 的小型 delayed-divergence Transformer proof-of-mechanism。

本轮已经证明：
- raw attention 即使公平调层，也明显弱于面向未来的因果/梯度量；
- 延迟未来影响可以在 next token 完全看不见时存在；
- 3-point integrated directional future gradient 和 batched future-margin 在本任务上全部找对真正相关历史；
- gradient Control Gain 能极准确预测真实有限干预效果；
- 可读性和可控性确实是不同工程轴。

尚未证明：
- 这些数值会以同样效应量出现在大型自然语言模型；
- 3-point IDFG 在开放式、无明确反事实方向的自然语言中仍会保持 100%；
- 自然语言中最佳的 counterfactual unit 应该是 token、span、relation packet 还是更高层状态。

下一步真实 LLM 工程重点已经非常明确：
**先构造 continuation signature，再比较 span-level DFG / integrated DFG / batched future-margin 与 exact short-horizon FCI；同时画 layer-position Control Gain map。**
