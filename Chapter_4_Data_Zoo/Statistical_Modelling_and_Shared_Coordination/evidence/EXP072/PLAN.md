# EXP072 — WISDM 1629 同时间戳原始观测语义审计

研究 ID `STAT-PSYMOE-EXP072-20261002-001`；2026-10-02 BST；`EXPLORATORY_READ_ONLY_SOURCE_ANOMALY_AUDIT`；父阶段 [EXP071](../EXP071/CLOSEOUT.md)。EXP071在40人开发真实配窗中，发现所有21,424个重复timestamp行集中在受试者1629的A/D/E×手机acc/gyro六组；原协议已固定“同timestamp三轴均值”并完整关账。本新问题：同刻两行是**值完全相同的重复录入**，还是相同时间键下**不同的观测**？答案决定是否把EXP071的该人信号看成可解释的单次记录，及后继数据资格设计；不改旧成绩。

## 冻结审计范围、判据与预算

仅从 [UCI507官方原件](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)内存读取 `raw/phone/{accel,gyro}/data_1629_<sensor>_phone.txt` 两个原件成员，过滤预定A/D/E。每组按原始行顺序核合法字段、时间倒序位置、timestamp出现次数及所有重复timestamp下三轴值；逐timestamp比较**数值逐轴精确相等**，并统计不等同刻键数、值最大绝对差、同值/异值重复行数。只保存计数、差值摘要和成员路径，不复制原始信号、位置序列或原始行。其它50人由EXP071派生账已知无重复；本ID不重读其原件、不训练/评分。

先核每组六组有效行数与EXP070/071一致，重复timestamp折叠量合计21,424且每组恰有1处倒序；不一致`STOP_SOURCE_VERSION_OR_ANOMALY_MISMATCH`，不做同值安全裁决。通过后：若所有重复timestamp的全部三轴数值**精确相等**，裁决`IDENTICAL_DUPLICATE_ROWS_NO_MEAN_CHANGE`；任一个不同，裁决`CONFLICTING_DUPLICATE_TIMESTAMPS_UNRESOLVED`，列出六组冲突数和最大差。即使完全相等，也只说明EXP071均值对该人这些点数值无改变，不说明来源没有其他未知问题；若冲突，不在本ID删人、拆段、重训或把旧开发结果升级为确认。

预登记尝试`EXP072-ANOMALY-001`，命令`python3 audit_subject1629_duplicates.py`；网络≤330MiB、内存≤2GiB、CPU≤10分钟，原ZIP只驻内存。输出`ANOMALY_MATRIX.json`、`RUN_OUTPUT_001.txt`、门/报告/关账；做本目录少量派生一致性核验，无全仓门/非必要哈希。科学类型为只读来源语义审计，0模型、0新测试性能。
