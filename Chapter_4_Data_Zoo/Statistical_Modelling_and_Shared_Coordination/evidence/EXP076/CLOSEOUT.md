# EXP076 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_TEMPORAL_HOLDOUT_STATISTICAL_TEST`；执行`COMPLETE` / 工程`VALID_SCOPED` / 科学`NO_ADDITIONAL_CHANNEL_GAIN_AT_ONE_HOUR_DEV_GATE`。
- 原问题和唯一尝试：固定下一小时Wh，室内/天气是否有足够独立增量；`EXP076-STAT-001`依[计划](PLAN.md)执行，0修订/重试，原始终端RUN_OUTPUT_001 (source asset outside this public snapshot)。
- 已知：源重核通过，20个验证完整日期；INDOOR是固定选出的最佳附加臂但较AR稍差，三门全失败，[门](GATE_RESULT.md)。PERSIST验证更差，但不构成test资格。
- 未知：未评分的test表现、跨住宅保持、实时字段可用性、其他时距的增量；不能诊断共享矩阵或模型容量。
- 停止层级与下一决策：固定统计增量门未过；停止本ID、保留AR为简单开发基线。另立新ID才可研究不同科学时距，不能把本ID test改称确认。
- 本次实际验证：官方原件来源重核与派生日期指标局部8/8。仅静态检查了方法/输出路径；未评分test，未运行全仓门或非必要哈希。
- 本目录计划、脚本、派生指标、原输出与关账为本地原位档案；官方ZIP/CSV只以URL和成员路径引用，未复制。未声明异地备份。
