# EXP048 24小时真实预测传统基线门

来源完整配对：原ZIP420,768站×小时行中，404,662有当前PM2.5/气象与精确24小时后实测PM2.5；缺失/无效16,106不补0。切分源门 (source asset outside this public snapshot)训练239,479、同站验证84,064、同站2017未来13,383、2016整站16,796、2017时间×整站2,676，全部超冻结支持下限。10训练站、2整站留出 `Aotizhongxin/Wanshouxigong`。所有输入为`t`时刻或时间相位，`y=t+24h`；训练目标在2015年底前，下一域起点2016年起。

| 域 | 对数 | 持续值 MAE (µg/m³) | 固定ridge MAE (µg/m³) | MAE改善 |
| --- | ---: | ---: | ---: | ---: |
| 2016同站验证 | 84,064 | 51.647 | 46.384 | 10.19% |
| 2017同站未来 | 13,383 | 79.551 | 61.833 | 22.27% |
| 2016整站留出 | 16,796 | 55.164 | 49.627 | 10.04% |
| 2017未来×整站 | 2,676 | 87.589 | 69.720 | 20.40% |

四域均≥冻结5%改善，**`TRADITIONAL_BASELINE_GENERALISES_IN_FROZEN_DOMAINS`**。RMSE、每站结果、唯一ridge参数和116,919条完整评价预测见[指标](METRICS.json)、参数 (source asset outside this public snapshot)、预测 (source asset outside this public snapshot)，[局部重算](LOCAL_VALIDATION.json)通过。这是在同一UCI来源内的时段/测站压力测试；2留出站可能共享北京天气和污染事件，不能称独立城市外部验证、因果或生产资格。还没有测试跨站实时共同信号/Stat-MoE/Ganglion。
