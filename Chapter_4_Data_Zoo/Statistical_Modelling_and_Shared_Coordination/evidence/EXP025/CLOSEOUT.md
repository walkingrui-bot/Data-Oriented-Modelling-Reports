# EXP025 关账

研究 ID `STAT-PSYMOE-EXP025-20261002-001`；2026-10-02；`EXPLORATORY`。执行状态：**完成来源资格审计**。工程有效性：**本轮 469 人元数据全数 ID/通道审计与固定50源时序局部 QA 有效**。科学结论：**真实横断面多通道 person cohort 支持下一阶段传统统计基线设计；模型价值与临床有效性未检验**。

全部尝试及失败范围在 WORKLOG.md (source asset outside this public snapshot)：初始四原件 schema 预检，469 人三类原件与 file list 全数连接，固定 25 人独立核及固定 50 条 Relaxed 左右腕原始数值读取均完成。无失败重试、无模型运行。源 URL/版本/许可证和恢复依赖见 SOURCE_INDEX.json (source asset outside this public snapshot)，人级审计在 `SUBJECT_AUDIT.csv`，组别/通道计数在 `CHANNEL_DIAGNOSTICS.json`，门判在 [GATE_RESULT.md](GATE_RESULT.md)。原始 JSON/CSV/时序仍在官方 PhysioNet URL；本地未复制。

未做所有任务时序文件验证、特征构造、个人级 split、统计或神经模型拟合、外部 validation。横断面组别不等于未来 outcome，训练前必须排诊断与后诊断字段。此研究通过后应另立 EXP026，先锁人级 train/validation/test 与传统统计基线，再据真实增益和稳定性决定 Stat-MoE 或 Shared Ganglion，不能在 EXP025 偷换科学问题。
