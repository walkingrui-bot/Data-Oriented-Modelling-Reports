# EXP077 冻结真实来源门裁决

[UCI235官方原件](https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption)流式读取；原始ZIP/TXT未落地。首轮固定宽度解析无效，保留原输出 (source asset outside this public snapshot)及无效派生矩阵 (source asset outside this public snapshot)，不用于以下门。有效第二轮证据见来源矩阵 (source asset outside this public snapshot)、原输出 (source asset outside this public snapshot)、[修订](AMENDMENT_001.md)。

| 冻结门 | 有效观察 | 裁决 |
| --- | ---: | --- |
| 官方成员/九列、≥2,000,000行、日历/行宽全可解析 | 唯一TXT；2,075,259行；0无效 | PASS |
| 2007–2010各≥250不同日期 | 365/366/365/330 | PASS |
| 各年四路共同完整≥95% | 99.252%/99.974%/99.186%/96.289% | PASS |
| 三分表各年分别≥1,000严格正值 | 最低为2010分表1的36,537 | PASS |
| 目标年train 2007–08真+60分钟配对≥300,000 | 1,048,251 | PASS |
| 2009验证真+60分钟配对≥100,000 | 521,116 | PASS |
| 2010测试真+60分钟配对≥100,000 | 457,144 | PASS |

**`FOUR_CHANNEL_YEAR_SPLIT_SOURCE_READY_FOR_DESIGN`**，只表示来源/时间轴足以设计后继模型。原生缺测25,979行（七列同时缺），不填0；2010完整率降低，后继须按实际配对筛选并核样本/日期数。日期无时区，时钟含义及当时实时可用性未证；总表与分表存在物理组成关系，绝不当作独立人群。未训练/评分任何年份。
