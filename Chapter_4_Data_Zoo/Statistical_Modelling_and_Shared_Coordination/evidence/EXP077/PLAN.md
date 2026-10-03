# EXP077 — 四年真实家用总表/分表共同时间轴来源门

研究 ID `STAT-PSYMOE-EXP077-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_MULTICHANNEL_TEMPORAL_SOURCE_AUDIT`；父=[EXP076](../EXP076/CLOSEOUT.md)。用户授权真实数据研究自治，EXP076固定单栋短期下一小时任务附加来源增量门失败。这里改变**数据来源与科学问题**：来自另一栋住宅、2006–2010近四年、总表电功率和三个不同回路分表能否为按年时间外一小时预测提供真实同步样本及可观察的各通道变化？本ID只审来源，不训练、不选模型、不评分留出年。

## 转向理由与可区分的解释

原UCI374仅四个多月、室内/机场天气而无独立分表，附加来源一小时开发无收益。改长预测时距仍只有同一栋楼、相同来源，不能区分“该来源不含增量”与“建筑/时间段偶然”。[UCI235官方页面](https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption)说明另一栋法国住宅有2,075,259条分钟观测、近四年、三回路分表与真实缺测，CC BY 4.0；它能先检验能否形成另一个更长时间轴的真实通道任务。与再次扩模型相比，来源是否共同可观察是更靠前的未知；不把UCI235称为跨房屋泛化验证，因为两栋住宅没有相同特征合同或训练任务。

## 冻结读取与判据（看到原文件统计之前）

仅官方ZIP `https://archive.ics.uci.edu/static/public/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption.zip`中`household_power_consumption.txt`，进内存流式解析，不保存ZIP/TXT副本；引用URL/成员路径和派生统计。预期分号列Date、Time、Global_active_power、Global_reactive_power、Voltage、Global_intensity、Sub_metering_1/2/3。`?`及空字段为真实缺测，不能置零或插值；非有限/无法解析数字另计无效。日期按dd/mm/yyyy+hh:mm:ss解析为**未标时区的源日历值**；不同/重复/逆序分钟均记录，不用行号假定真实60分钟。每行总表及三个分表若同刻可解析有限且非负则共同完整。仅来源审计；`Global_active_power`以kW，分表以分钟Wh，不能直接相加，物理残差只描述不作模型结论。

未来目标候选是源日历恰好+60分钟的另一行`Global_active_power`，起点四路共同完整且目标总表有效。逐行偏移60仅当两日期严格差60分钟才算；年分配以**目标年**。2007–2008作训练来源、2009作验证来源、2010作未看性能的测试来源；2006部分记录只用于跨年候选核对，不单独评分。来源门：官方成员、9列与至少2,000,000行；2007/08/09/10每年≥250不同日期；每年四路共同完整≥95%记录且三个分表各≥1,000个严格正值；可计算的目标年2007–08/2009/2010真实+60分钟配对分别≥300,000/100,000/100,000；以上年份无日期解析失败；异常时刻单独计数，允许剔除异常配对，不能推断缺失目标。若任何门失败，`STOP_MULTICHANNEL_SOURCE_SUPPORT`，不训练。通过只标`FOUR_CHANNEL_YEAR_SPLIT_SOURCE_READY_FOR_DESIGN`，不声称预测增量、源时区或当年可在线获得。

## 尝试、预算与局部验证

预登记唯一尝试`EXP077-SOURCE-001`，脚本`audit_household_source.py`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python audit_household_source.py`；网络≤30MiB、内存≤1GiB、CPU≤10分钟。预期`SOURCE_MATRIX.json`（仅派生计数/日期）、`RUN_OUTPUT_001.txt`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`，不另存原件。局部复核行数、年份分配、门布尔与时间配对计算；禁全仓门和非必要哈希。来源通过后新ID才可预登记模型、特征、按年结果门；失败则另选可识别数据，保留本记录。
