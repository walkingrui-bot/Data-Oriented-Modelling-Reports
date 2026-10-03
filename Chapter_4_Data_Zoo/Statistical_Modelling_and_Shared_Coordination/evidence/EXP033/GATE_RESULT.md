# EXP033 Si→Ga 来源转移点估计门

研究 ID `STAT-PSYMOE-EXP033-20261002-001`；2026-10-02。事前 [计划](PLAN.md) 限定 Si 64人一次训练、Ga 47人整研究一次留出，固定12双足统计、λ0.1、训练先验对照。Ga 点估计须同时 balanced accuracy≥0.55、macro log loss 相对 Si 先验改善≥0.02。

| 项目 | 观察 | 预设要求/判断 |
| --- | ---: | --- |
| Si 训练 / Ga 留出 | PD35/健康29；PD29/健康18 | 原位111人全数数值合格 |
| 固定 logistic | 1/1拟合收敛 | 必须收敛 |
| Ga macro log loss | 模型0.519710；Si先验0.697561 | 改善 **+0.177852**，≥0.02 |
| Ga balanced accuracy | **0.761494** | ≥0.55 |
| Ga confusion（行真HC/PD，列预测HC/PD） | `[[15,3],[9,20]]` | HC召回15/18，PD召回20/29 |

双指标点估计门 **通过**，标记 `GA_SOURCE_TRANSFER_OBSERVED`。Ga 47个结果只看一次；未在 Ga 调阈值、调 λ 或重训，未用 Ju 来源失败组。局部状态/逐人预测/指标重算初次因验证器权重维数断言错误而无效，原失败保留；更正后6/6通过，见 [AMENDMENT_001.md](AMENDMENT_001.md)、[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)。研究样本少，官方未提供本轮可核的跨研究同人链接，故**不能称独立人外部确认或临床用途**。
