# EXP082 — 多年真实交通量与天气共同小时来源语义门

研究 ID `STAT-PSYMOE-EXP082-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_TRAFFIC_WEATHER_SOURCE_AUDIT`；父=[EXP081](../EXP081/CLOSEOUT.md)。EXP081同城三区天气增量分化、整体留出门失败且无PEER增量；下一重要未知是环境通道是否在**不同实际需求系统**有可识别价值。先用真实多年的交通流量/天气共同时间轴建立另一任务来源，而不是在已看Tetouan test继续调路由。不同结局与地点只提供另一科学问题，不叫原电力模型外部确认。

## 官方输入与冻结来源语义

[UCI492官方数据页](https://archive.ics.uci.edu/dataset/492/metro%2Binterstate%2Btraffic%2Bvolume)描述2012–2018美国I-94西行某计数站的小时交通量与天气，CC BY 4.0。仅官方ZIP `https://archive.ics.uci.edu/static/public/492/metro%2Binterstate%2Btraffic%2Bvolume.zip`内`Metro_Interstate_Traffic_Volume.csv.gz`，内存解压读取，不另存ZIP/GZ/CSV。固定需要date_time、traffic_volume、temp、rain_1h、snow_1h、clouds_all；holiday与weather_main/description只记录列存在，不作为本来源门模型输入。源页称本地CST，不以网页声明替代原日期核验。

逐行解析源日历小时，原交通量必须有限非负，四数值天气必须有限；`?`/空/NaN是真缺测，不填0。先按`date_time`分组：同一小时重复行只有在交通量**完全相等**时才可形成唯一本小时真实outcome；天气数值若重复但不同，预先用**同小时中位数**形成单一回顾性天气向量，并记录各字段冲突小时数量及最大极差；字符串天气类别不参与数值模型。任一重复小时交通量冲突则`STOP_DUPLICATE_OUTCOME_SEMANTICS`，0模型。源时区/DST实际序列可能有空洞或重复，不能只按行号构造未来小时。所有分组仅派生内存统计，不存原始记录副本。

来源门：官方预期唯一GZ成员、指定列与≥45,000原行；≥40,000唯一源日历小时，≥95%行交通量和四天气都有限，0负交通量；所有重复时刻outcome一致；按唯一本小时真实`t→t+1小时`形成起点天气完整且目标交通量有效的配对，目标年2013–2016训练≥20,000且≥800不同目标日、2017验证≥5,000且≥250日、2018测试≥5,000且≥250日。2012部分只供历史记录，不作独立模型目标。只要任一门失败`STOP_TRAFFIC_WEATHER_SOURCE_SUPPORT`，不训练；通过仅`TRAFFIC_WEATHER_HOURLY_SOURCE_READY_FOR_DESIGN`。本ID不检验天气预测增量，不评价模型或留出性能。未来建模必须只用起点或更早天气；原`rain_1h`等为小时汇总，拟再滞后一小时避免把当小时未完成汇总冒充起点实时可用，仍限回顾性。

## 尝试、预算与局部核验

预登记`EXP082-SOURCE-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python audit_traffic_source.py`，网络≤2MiB、内存≤200MiB、CPU≤3分钟。输出派生`SOURCE_MATRIX.json`、原`RUN_OUTPUT_001.txt`、门/报告/关账；原件URL和成员路径为恢复依赖，不保存原件副本。局部只核计数/年份/重复语义/门，不跑全仓或非必要哈希。通过后新ID再冻结时间外传统统计基线与天气滞后；若不通过，按失败层级换来源或修复可证的解析错误，不降低冻结门。
