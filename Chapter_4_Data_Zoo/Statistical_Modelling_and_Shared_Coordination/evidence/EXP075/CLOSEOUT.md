# EXP075 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_TEMPORAL_SOURCE_AUDIT`；执行`COMPLETE` / 工程`VALID_SCOPED_SOURCE_AUDIT` / 科学`TEMPORAL_SOURCE_SUPPORT_ESTABLISHED_ONLY`。
- 原问题：真实住宅设备用电是否支持固定下一小时Wh结局、完整共同时间轴和足量时间外分段？唯一尝试`EXP075-SOURCE-001`按[计划](PLAN.md)官方ZIP只内存读取，0修订/重试。原输出 (source asset outside this public snapshot)。
- 已知：19,735行源10分钟全连续、字段全有限，19,729个真60分钟后目标，train/val/test=13,808/2,960/2,961，97/22/21目标日期。[门](GATE_RESULT.md) · 来源摘要 (source asset outside this public snapshot)。
- 未知：原日期时区、当时天气/室内列精确可用时刻、跨住宅适用性；小时天气有插值，不能将当前表状态冒充当年实时可得。无模型成绩。
- 后继：新ID冻结只用起点及更早值的自回归与新增室内/天气传统模型，采用日期块验证；若没稳定增量即止损，不启动Ganglion。
- 本次实际验证：官方原件解析及派生一致性[7/7](LOCAL_VALIDATION.json)。仅静态查官方许可和列说明；未训练、未评分test、未跑全仓。
- 本目录计划/脚本/派生JSON/原输出/门/报告/关账均本地未跟踪；原ZIP/CSV不复制，官方URL/成员路径为恢复依赖，无异地备份/哈希保证。入口/登记册同步。
