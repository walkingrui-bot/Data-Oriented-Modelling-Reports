# EXP080 — 城市三配电分区与天气真实共同时间轴来源门

研究 ID `STAT-PSYMOE-EXP080-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_MULTI_ZONE_SOURCE_AUDIT`；父=[EXP079](../EXP079/CLOSEOUT.md)暂停单栋家庭电力新增通道。新科学问题：北非Tetouan真实城市的三条配电区负荷与环境测量，是否有同刻、足量且可按后续月份隔离的原始记录，足以设计“目标分区自身历史之外，其他分区/天气是否有价值”的任务？该任务有**三区域**共同时间轴，区别于同一家庭总表与分表的物理组成；但仍是一个城市、单年，不称跨城市验证。若源门失败先止损，不训练。

## 来源选择与约束

用[UCI849官方页](https://archive.ics.uci.edu/dataset/849/power%2Bconsumption%2Bof%2Btetouan%2Bcity)所列CC BY 4.0源，官方ZIP `https://archive.ics.uci.edu/static/public/849/power%2Bconsumption%2Bof%2Btetouan%2Bcity.zip`内`Tetuan City power consumption.csv`，ZIP/CSV仅内存读取，不保存副本。官方列语义：DateTime、Temperature、Humidity、Wind Speed、general diffuse flows、diffuse flows、Zone 1/2/3 Power Consumption；实际表头/日期格式以原件审出，不凭来源网页的“无缺失”声明补0。天气/功率单位和源时区页面未充分定义，结果仅称原始单位及回顾性源日历。

只审真实源；对全部日期、九列、有限值、非负区功率、步长与每区变化进行计数。DateTime格式官方页未明确：在读原件前固定候选ISO年-月-日、日/月/年、月/日/年（各可带或不带秒）；仅接受**唯一**全行可解析、严格升序且≥99%十分钟相邻的候选，否则`STOP_AMBIGUOUS_SOURCE_CALENDAR`。该步骤只用时间字符串，不看负荷值挑格式；不猜时区。将下一小时候选目标定义为源日历恰+60分钟的另一行三区域实际功率（每区同一目标时刻），不把行号代替真实时间。以**目标日期**定义2017年1–8月训练来源、9–10月验证来源、11–12月测试来源；出该年范围只审记录不评分。源门：唯一预期CSV成员、九列齐且≥50,000行；无重复/逆序源日历，至少99%相邻记录恰10分钟；九列同刻完整有限≥95%且三区域功率无负值；三区域各在四个自然季度有≥100种不同正读数；真+60分钟配对在1–8月≥30,000、9–10月≥8,000、11–12月≥8,000且每段各≥50不同目标日期。任意失败`STOP_MULTI_ZONE_SOURCE_SUPPORT`，不建模。全部通过仅`THREE_ZONE_TEMPORAL_SOURCE_READY_FOR_DESIGN`，不是预测或独立通道增益。

为何选此来源：EXP078/079说明单栋内部电学增量很小，尚不知更高观测单位的跨区共同信息；UCI849体量和明确许可允许以最小真实审计区分“多区同步源存在”与“无可建模共同时间轴”。UCI321把尚未创建客户的负荷编码成0，不能把零直接当观测；BDG2的数据/许可遵循另需更大集成成本，先用源语义清楚的三分区检查问题。若来源过门，另ID用传统统计先测，且日期/区为真实分层，不能直接上Ganglion。

## 尝试与局部预算

配对计数进一步固定为起点九列同刻有限且三区域起点负荷非负、未来恰+60分钟三区域目标均有限非负；三分区共用同一真实目标时刻，不能把三区域配对数相加成独立日期数。

预登记`EXP080-SOURCE-001`：`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python audit_tetouan_source.py`；网络≤5MiB、内存≤300MiB、CPU≤3分钟。输出`SOURCE_MATRIX.json`派生计数/门、`RUN_OUTPUT_001.txt`、门/报告/关账；原ZIP/CSV不落地。局部复核门算术与时间划分；不做全仓门、非必要哈希。来源通过后新ID再冻结模型/样本/验证门，不在本ID看性能。
