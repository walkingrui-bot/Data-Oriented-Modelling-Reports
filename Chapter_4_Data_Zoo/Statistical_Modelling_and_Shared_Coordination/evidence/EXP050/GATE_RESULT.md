# EXP050 外部城市共同特征来源门

UCI官方[数据页](https://archive.ics.uci.edu/dataset/394/pm25dataoffivechinesecitiesUCI)列五城、2010–2015逐小时PM2.5与气象、NA缺失及CC BY4。一次3,390,122字节原ZIP网络响应在内存/管道解出内层RAR五个城市CSV；原件均未落盘。五城各52,584唯一有效小时、0重复，首尾2010-01-01 00至2015-12-31 23。各城市有显式PM监测列、TEMP和PRES；`Iws`为累计风速，**不可代替**EXP048的同小时WSPM。

| 非北京城市 | 固定同名 `PM_US Post` 字段精确24h实测完整配对 | ≥15,000来源门 |
| --- | ---: | --- |
| 成都 | 27,666 | 通过 |
| 广州 | 31,401 | 通过 |
| 上海 | 33,226 | 通过 |
| 沈阳 | 21,062 | 通过 |

四城均达到门槛，判定 `EXTERNAL_COMMON_SCHEMA_SOURCE_READY`。北京自身不计外部城市；其他本地PM列也留在数值审计 (source asset outside this public snapshot)，未依据模型成绩选字段。此门只说明真实观测和共同`PM/TEMP/PRES`特征足以设计独立城市评价，尚无外部模型预测或性能结论。旧EXP048八特征模型**不能**原样转移。

证据：来源与许可 (source asset outside this public snapshot)、压缩原件成员 (source asset outside this public snapshot)、逐城逐列数值支持 (source asset outside this public snapshot)、[局部门复算](LOCAL_VALIDATION.json)、原命令返回 (source asset outside this public snapshot)。
