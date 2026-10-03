# EXP063 冻结外部零样本门

2026-10-02；北京 N1 原参数引用 EXP060 MODEL_STATES.json (source asset outside this public snapshot)。伦敦区域来源复核十站已核定计数/状态/单位逐站均与 EXP062 相同，配对逐站合计 667 全部一致；无本地拟合。SOURCE_RECHECK.json (source asset outside this public snapshot)。

| 事前门 | 实得 | 判定 |
| --- | ---: | --- |
| N1 相对 B0 总体 MAE 改善 ≥5% | B0 **5.578**；N1 **14.386** µg/m³，反而恶化 **157.91%** | 未通过 |
| N1−B0 日区块成对 MAE 差 95% 区间上界 <0 | 差 **+8.808**，区间 **[+6.673,+11.100]** | 未通过 |
| 十站 ≥7 站 N1 比 B0 好 | **0/10** | 未通过 |
| 没有站恶化 >20% | **10/10 均恶化 >20%** | 未通过 |

真实目标平均 9.275，B0 预测平均 5.975，北京 N1 零样本预测平均 23.424 µg/m³。N1 的直接地理参数运输发生显著水平偏差；这一**描述**不能单独证明是截距、斜率、特征条件关系或仪器差异哪一项因果原因。逐站 MAE 与派生逐对预测见 [METRICS.json](METRICS.json) 和 PREDICTIONS.csv (source asset outside this public snapshot)。

结论：`ZERO_SHOT_N1_TRANSPORT_NOT_SUPPORTED`。本门不因后续适应实验重写，伦敦 2024 已看，不能改称未见确认。日区块133天仍不解决全部连续/空间相关。局部复算 [12/12](LOCAL_VALIDATION.json)。
