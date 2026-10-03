# EXP031 关账

研究 ID `STAT-PSYMOE-EXP031-20261002-001`；2026-10-02；`EXPLORATORY`。执行状态：**在数值来源门停止**；工程有效性：**元数据、人级派生和门复算局部有效，模型未执行**；科学结论：**当前冻结的三研究来源层不足以测试跨研究预测增量**。这不是“没有观察到模型效果”，因为没有拟合、没有真实预测。

完整尝试：`EXP031-COHORT-001/002` 为解析错误，原输出移入 `derived/failed_COHORT_001/002/` 留存；`EXP031-COHORT-003` 校正后支持门通过；`EXP031-SOURCE-001` 165 人159份数值合格，Ju PD 25/29<90%，停止；`EXP031-VERIFY-001` 派生表4/4一致性通过，并记录重试元数据更正。见 工作日志 (source asset outside this public snapshot)、[来源门](GATE_RESULT.md)、[报告](REPORT.md)、[更正](CORRECTION_001.md)。没有 `EXP031-MODEL-001` 真实尝试，也无 Stat-MoE、Ganglion 结果。官方源只保存 URL 与原件索引，无原始日志/源码/力信号副本。

后继 [EXP032](../EXP032/PLAN.md) 另问 Si 单来源内部是否有真实统计信号；不把 EXP031 失败门改写为通过，不将内部 CV 叫外部确认。
