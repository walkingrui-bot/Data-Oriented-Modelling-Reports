# EXP081 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_MULTI_ZONE_TEMPORAL_STATISTICAL_TEST`；执行`COMPLETE_AFTER_TWO_TRANSPORT_RETRIES` / 工程`VALID_SCOPED` / 科学`WEATHER_ZONE_HETEROGENEITY_AND_NO_GLOBAL_HOLDOUT_GAIN`。
- 原问题/冻结计划：其他分区或环境量能否相对三区各自OWN历史带来跨后续月段保持的实用增量？[PLAN](PLAN.md)，无门/模型修订。
- 全部尝试：`EXP081-STAT-001/002 INVALID_SOURCE_TRANSPORT`各为官方504、0模型/分数、原错误1 (source asset outside this public snapshot)/原错误2 (source asset outside this public snapshot)；`EXP081-STAT-003 COMPLETE`同配置第三次成功，12个固定传统模型，原输出3 (source asset outside this public snapshot)；工作日志保留全部。
- 已知：来源/模型支持通过。开发整体2/3合格而放行test；留出Zone1/2 WEATHER仍改善，Zone3恶化10.561%触发整体门失败，[门](GATE_RESULT.md)。合格区无PEER/JOINT选型，跨区共享未观察增量。Zone3 PERSIST优于HGB。
- 未知：跨城市/后续年份保持、真实在线天气可用性、任何zone路由在独立条件是否安全；不能看过本test后把其重称确认，也不能诊断模型/共享矩阵容量小。
- 停止层级/转向：整体generalisation失败且基线适配随区变化；不启动全三区天气channel或Ganglion。新ID优先找另一个真实长期需求系统，识别环境通道价值及原始时间语义。
- 本次实际验证：第三轮官方原件重核、12模型固定拟合、条件式test一次、逐日/CI/门派生复核[11/11](LOCAL_VALIDATION.json)；未跑全仓门/非必要哈希。
- 原ZIP/CSV未复制，官方URL是恢复依赖；本地保存脚本、派生逐日指标、三次原输出/关账，无异地备份保证。
