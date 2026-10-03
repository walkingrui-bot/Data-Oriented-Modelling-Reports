# EXP026 关账

研究 ID `STAT-PSYMOE-EXP026-20261002-001`；2026-10-02；`EXPLORATORY`。执行状态：**完成**。工程有效性：**局部有效**（469 人源及 15 个拟合、11/11 输出核对）。科学结论：**冻结联合通道增益门未通过，当前证据不足以推进 Stat-MoE 或 Shared Ganglion**；并非证明所有 PADS 运动任务无效。

全部尝试在 WORKLOG.md (source asset outside this public snapshot)：`EXP026-SPLIT-001`、`SOURCE-001`、`MODEL-001`、`VERIFY-001` 全部完成；无失败重试。源门、预算、人级 split、冻结门与实际成绩分别见 `SOURCE_SUMMARY.json`、`SPLIT_AUDIT.json`、[GATE_RESULT.md](GATE_RESULT.md)、[REPORT.md](REPORT.md)。M0 validation 先验修订有独立 [AMENDMENT_001.md](AMENDMENT_001.md)；原计划不回写。原件均保留官方 URL；不复制原时序/问卷。唯一派生特征表、模型选择、15 拟合状态、一次测试预测和聚合指标保存在本目录。

停止原因：validation 两指标改善，但锁定 test 的 balanced accuracy M3=0.637605 低于 M1=0.655229，触发事前 gate；测试中 HC/PD 召回下降而 DD 上升。已知同中心概率质量改善，未知该动作的增益是否可在新个体/不同任务/外部中心保持。不能说模型 clinically useful、能预测 longitudinal progression 或共享架构有额外作用。下一研究可用新 ID 在原开发人群内做**回顾性稳定性诊断**，不重新命名已看 test 为确认，也不在 EXP026 内修改模型门。若以后要确认，需另找未见个体/中心。
