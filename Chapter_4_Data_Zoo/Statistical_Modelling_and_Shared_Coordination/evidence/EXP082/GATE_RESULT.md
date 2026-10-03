# EXP082 交通量/天气唯一小时来源门

[UCI492官方原件](https://archive.ics.uci.edu/dataset/492/metro%2Binterstate%2Btraffic%2Bvolume)有效第二次读取，首次504无数据、原错误 (source asset outside this public snapshot)。有效派生矩阵 (source asset outside this public snapshot)与原输出 (source asset outside this public snapshot)保留；成功重试JSON的run_id误标001已只校正元数据为002，数值/门未动。

| 冻结门 | 观察 | 裁决 |
| --- | ---: | --- |
| 唯一官方GZ/所需列/≥45,000原行 | 1个GZ、所需列齐、48,204行 | PASS |
| ≥40,000唯一小时、全日历可解析 | 40,575、0失败 | PASS |
| ≥95%原行交通与四天气有限、0负交通 | 48,204/48,204，0负 | PASS |
| 重复小时交通量完全一致 | 5,445重复小时，0交通量冲突 | PASS |
| 目标年2013–16真+1h配对≥20,000/≥800日 | 20,715/1,099日 | PASS |
| 2017验证≥5,000/≥250日 | 8,692/365日 | PASS |
| 2018测试≥5,000/≥250日 | 6,521/273日 | PASS |

**`TRAFFIC_WEATHER_HOURLY_SOURCE_READY_FOR_DESIGN`**，仅来源资格。5,445重复小时多7,629原行；相同时刻气温/降雨/云量冲突分别78/9/32小时，最大极差20.433 K/0.76 mm/75个百分点，后继按预定同小时中位数并需报告该数据质量界限。2018只至9月30日。`rain_1h`为小时累计，源天气在线可用时刻未证，后继必须用滞后值且只称回顾性。0模型、0性能分数。
