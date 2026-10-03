# EXP076 冻结开发门裁决

官方来源结构重核通过。验证集按目标日期等权，20个完整日期；选中附加候选为INDOOR。指标来自[VALIDATION_METRICS.json](VALIDATION_METRICS.json)，20日派生误差见[VALIDATION_DAILY_ERRORS.csv](VALIDATION_DAILY_ERRORS.csv)。

| 冻结门 | 观察 | 裁决 |
| --- | ---: | --- |
| 候选较AR日MAE改善≥5% | −0.00538%（34.965655对34.963773 Wh） | FAIL |
| 成对日期bootstrap差95%区间上界<0 | [−0.534896,+0.553436] Wh | FAIL |
| ≥60%日期改善 | 10/20=50% | FAIL |

**`STOP_ADDITIONAL_CHANNEL_DEV_GATE`**。按计划没有执行test预测或评分；不建立室内、天气或联合channel，不启动Stat-MoE/Ganglion，不以扩大容量追逐此开发集。该裁决只适用于这栋建筑、下一小时Wh、固定滞后特征与HGB；它不证明传感器普遍无信息。AR相对PERSIST的验证MAE较低，但尚无test资格结论。
