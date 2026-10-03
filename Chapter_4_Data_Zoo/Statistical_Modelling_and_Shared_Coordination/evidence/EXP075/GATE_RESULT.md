# EXP075 来源/时间门

官方UCI374原ZIP内CSV只在内存读，19,735条单建筑真实记录，2016-01-11至2016-05-27，原时区未知。来源矩阵 (source asset outside this public snapshot)。

| 冻结门 | 观察 | 裁决 |
| --- | ---: | --- |
| 必需列、≥19,000行、日期唯一升序 | 全列齐、19,735、严格升序 | PASS |
| 10分钟相邻步≥99%、所需字段完整≥95% | 均100% | PASS |
| 非负Appliances，i+6真实目标恰60分钟≥99% | 0负值；19,729/19,729 | PASS |
| 目标时间划分train≥10,000且≥60天 | 13,808；97天 | PASS |
| validation/test各≥2,000且≥20天 | 2,960/2,961；22/21天 | PASS |

**`REAL_ENERGY_TEMPORAL_SOURCE_READY_FOR_STAT_DESIGN`**，来源资格而非性能资格。原天气小时值存在插值，日期时区及每列历史可用时刻未明；后继只能称回顾性时间外建模，不称实时运营预测。0模型、0test成绩。原输出 (source asset outside this public snapshot)。
