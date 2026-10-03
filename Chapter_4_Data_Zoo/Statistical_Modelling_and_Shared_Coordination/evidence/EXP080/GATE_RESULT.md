# EXP080 三区真实来源门

前两尝试分别为官方下载504、原CSV内部双空格表头未规范化；均不作来源裁决。错误/修订 (source asset outside this public snapshot) · [修订001](AMENDMENT_001.md)。有效第三次读取[UCI849原件](https://archive.ics.uci.edu/dataset/849/power%2Bconsumption%2Bof%2Btetouan%2Bcity)，派生证据见来源矩阵 (source asset outside this public snapshot)。

| 冻结来源门 | 有效观察 | 裁决 |
| --- | ---: | --- |
| 唯一CSV/九列/≥50,000行 | 1 CSV、九列、52,416行 | PASS |
| 唯一可释日历、≥99%十分钟、无重复逆序 | `%m/%d/%Y %H:%M`唯一、52,415/52,415步 | PASS |
| 九列同刻完整有限≥95%、三区无负值 | 52,416/52,416；0负值 | PASS |
| 各区每季度≥100不同正读数 | 最少Zone3第四季4,829种 | PASS |
| 真+60分钟配对，训练≥30,000且≥50天 | 34,986/243天 | PASS |
| 验证≥8,000且≥50天 | 8,784/61天 | PASS |
| 测试≥8,000且≥50天 | 8,640/60天 | PASS |

**`THREE_ZONE_TEMPORAL_SOURCE_READY_FOR_DESIGN`**；这只是可建模来源支持，0模型/性能。原始时间覆盖2017-01-01至12-30，**不含12-31**。源时区与功率单位未由官方页面明确证明，后继只用原始单位、源日历回顾性评价；三区共属一城，不能当三城市独立验证。
