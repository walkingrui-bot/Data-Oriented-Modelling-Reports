# Overthinking Causal Control — Round 1
## 从 CoT 监视转向“未来控制权换手”

日期：2026-09-25

## 1. 研究问题

如果 CoT 本身越来越不能被当作可信监视器，那么更上游的问题是：

> 在推理继续生成时，究竟是谁正在控制未来 continuation？

本轮把来源拆成三类：

1. 原始提示 / system-prompt 约束；
2. 用户问题本身；
3. 模型已经生成并重新读回的自身历史。

对每一类来源都计算 8-step future causal influence（FCI）：
删除/中和该来源后，未来生成分布会改变多少。

特别定义一个不需要正确答案的量：

**Opposing Self Influence（反向自历史影响）**

如果“自身历史”的未来影响方向与 prompt+question 的共同方向相反，就把这部分记为反向自历史影响。

这直接对应一个可测的 overthinking 上游前兆：

> 模型还没明显答错以前，自身输出是否已经开始对抗原始问题和提示词对未来的控制。

## 2. 构造世界

4000 条独立自回归推理轨迹，每条 120 token。

外部 prompt 和 question 提供稳定参考；模型逐步形成当前生成状态。每个新 token 都被重新读回，并产生一个零均值但会随推理长度放大的 self-conditioned 更新，因此：

- 太早：生成函数尚未充分形成；
- 中段：外部约束已经充分进入状态，自历史尚未夺权；
- 太晚：大量自身输出的累计偏差开始显著改变未来 continuation。

这个世界故意产生一个“先变好、后变坏”的 reasoning-length 曲线。

## 3. 合理区间真的出现了

平均生成分布相对稳定目标的偏差在 token **21** 达到最低。

用“距离最低误差不超过 0.01”定义构造世界中的 near-optimal 区间：

**token 13–33**

然后完全不使用正确答案，只用 GCM 因果量定义一个工程区间：

- prompt+question 的未来因果影响已达到其峰值的至少 95%；
- 与它们方向相反的 self-history FCI < 外部 FCI 的 5%。

得到：

**GCM balance band = token 12–31**

也就是说，仅从“谁在控制未来”就几乎恢复出了真正的有用推理区间。

## 4. 参数邻域验证

固定同一个 GCM 规则，不重新调阈值；扫描：

- external integration = 0.07 / 0.08 / 0.09
- self-feedback growth = 0.45 / 0.55 / 0.65

共 9 个相邻动力学世界。

结果：
- near-optimal band 与 GCM band 的平均 Jaccard = **0.751**
- 中位 Jaccard = **0.818**
- 起点绝对误差中位数 = **1.0 token**
- 终点绝对误差中位数 = **3.0 token**

因此“合理思考区间”不只是长度常数；它随 prompt/question 整合速度和自历史回写强度移动，但同一个因果平衡规则能够追踪它。

## 5. Overthinking 的上游标志

预测“未来 12 token 内是否进入持续明显偏离”。

AUC：

- Self-takeover share: **0.706**
- Causal self-opposition: **0.682**
- Current output deviation: **0.624**
- Visible-CoT EMA imbalance: **0.612**
- Entropy deviation: **0.604**


这里需要把两个不同对象拆开：

**Self-Takeover Share** 回答“未来控制权有多少已经转到自身历史手里”，在严格 trajectory-held-out 排序中 AUC 最高（0.706）。

**Causal Self-Opposition** 回答“自身历史取得的控制权中，有多少已经开始与 prompt+question 的共同方向相反”。它的总体排序 AUC 为 0.682，但在固定低误报率的临近失败预警里更有价值。

所以 overthinking 不是一个单分数问题，而至少有两个轴：

1. **Takeover**：自身历史拿走了多少未来控制权；
2. **Opposition**：这些控制权是否已经开始对抗原始外部约束。

这比把“CoT 看起来乱不乱”压成一个表面分数更接近生成函数正在发生的变化。

## 6. 固定低误报率的早期预警

所有阈值只在一半轨迹上校准，再固定到另一半轨迹。

用距离未来失败至少 24 token 的窗口校准约 5% safe false alarm rate。

测试集结果：

- Causal self-opposition: safe FPR=0.048, 12-token pre-failure detection=0.914, median lead=6.0 token
- Self-takeover share: safe FPR=0.056, 12-token pre-failure detection=0.429, median lead=7.0 token
- Current output deviation: safe FPR=0.054, 12-token pre-failure detection=0.883, median lead=5.0 token
- Visible-CoT EMA imbalance: safe FPR=0.050, 12-token pre-failure detection=0.872, median lead=4.0 token
- Entropy deviation: safe FPR=0.056, 12-token pre-failure detection=0.149, median lead=12.0 token


其中 Causal Self-Opposition：
- safe false-alarm ≈ 4.8%
- 在真正可见失败前 12 token 内捕捉约 91.4% 的失败轨迹
- 告警中位提前约 6 token

当前 output deviation 在相近误报率下：
- 捕捉约 88.3%
- 中位提前约 5 token

可见 CoT 的 EMA 表面失衡：
- 在约 5.0% safe false-alarm 下捕捉约 87.2%
- 中位提前约 4 token

Self-Takeover Share 的全局排序 AUC 更高，但用同样的固定低误报阈值做“马上要失败了吗”预警时灵敏度明显较低；这说明 **Takeover 更像慢变量，Opposition 更像临界方向变化**。

因此最有用的工程解释不是挑一个冠军，而是联合监控：

- Takeover：自身历史是否正在接管；
- Opposition：接管以后是否开始反向；
- External Anchor Control：prompt + question 还有多少未来控制权。

这一轮不是说表面监视完全没信息，而是：

> **source-specific future causal control 能更早告诉我们“为什么快要漂”，而不仅是“已经开始看起来漂”。**

## 7. 一个新的工程定义：Overthinking 不是“想太久”

本轮支持的更精确工作定义：

**Overthinking onset = external constraint control has already matured, but self-generated history begins to gain opposing future control faster than it contributes useful rule formation.**

中文：

> **推理过度的起点，不一定是文字已经重复或答案已经错误，而可能是：原始提示与用户问题已经充分塑形后，自生成历史开始获得与它们相反的未来控制权。**

因此合理思考区间不是固定 token 数，而是一段因果平衡带。

## 8. GCM 如何替代单纯 CoT monitoring

建议在线监视四条曲线：

1. Prompt FCI
2. User-question FCI
3. Self-history FCI
4. Opposing-self FCI

同时保留：
- Future-State Readout：模型准备生成什么；
- Influence Horizon：这些影响在几步后显现；
- Control Gain：如果要纠偏，哪里仍有杠杆。

一个非常直观的 overthinking dashboard 可以显示：

**External Anchor Control**
= Prompt FCI + Question FCI

**Self Takeover**
= Self-history FCI / total FCI

**Self Opposition**
= 与 external-anchor direction 相反的 self FCI

**Balance Band**
= external control 已成熟 + opposing self control 仍低

## 9. 与现有外部研究的关系

这套方法与“读 CoT 内容”不同，也与单纯 activation decoding 不同。

它不问：
- hidden state 像什么概念；
- 模型在 CoT 里有没有承认某个 hint；
- 哪个 attention weight 最大。

它问的是可干预问题：

> 如果移除/改变 prompt、question 或 self-history 的某一部分，未来 continuation 会如何改变？

因此它天然对应 counterfactual behavior，而不是语言化解释。

## 10. 当前边界

这是 synthetic proof-of-mechanism。

它建立了：
- 三源 future-control 曲线足以在构造世界中恢复 near-optimal reasoning band；
- 同一固定 causal-balance rule 在 9 个相邻动力学设置中仍能追踪区间；
- self-history 对 external constraints 的反向未来影响可以在明显输出失败之前提供早期预警。

它尚未证明：
- 真实开放 LLM 的最佳阈值也是 95% / 5%；
- 自然语言中 prompt/question/self-history 能像本玩具一样完全干净地拆分；
- 所有 overthinking 都属于 self-history takeover。

下一步真实 LLM 实验应该直接把 prompt、user question、不同 CoT span 做 source ablation / counterfactual edit，并计算 short-horizon FCI 和 Influence Horizon，再看这些曲线是否在 harmful overthinking 前发生同样的控制权换手。
