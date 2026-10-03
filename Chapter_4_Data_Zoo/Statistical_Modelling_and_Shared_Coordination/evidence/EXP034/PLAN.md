# EXP034 — GaitPDB Ga/Si 人员独立性与协议来源审计

研究 ID `STAT-PSYMOE-EXP034-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP033](../EXP033/CLOSEOUT.md)。EXP033 的 Si→Ga 固定统计模型点估计门通过，但一个阻断科学主张的未知仍在：Ga/Si 是否可被证实为不同受试者，且入组/采集协议是否足以把该评估称为外部人群验证？本轮只审**来源身份和协议证据**，不查看新模型结果、不训练、不用人口值推测同人。

## 资料和判据

来源以 [PhysioNet GaitPDB v1.0.0](https://physionet.org/content/gaitpdb/1.0.0/) 的数据页、[format.txt](https://physionet.org/files/gaitpdb/1.0.0/format.txt)、[demographics.txt](https://physionet.org/files/gaitpdb/1.0.0/demographics.txt) 及源页列明的 Ga/Si 原研究方法/原始论文为限；最多10个网页/PDF页面族，不下载或复制原始足底力/完整论文，只记录可定位 URL、具体声明和缺口。来源是公开开放资料，若遇付费/访问限制就记未能核实，不用二手摘要填空。

身份门：只有明确的跨研究受试者排重声明、能一对一确认不重叠的原始匿名跨研究 linkage，或原研究样本关系的原始记录，才记 `CROSS_STUDY_PERSON_DISJOINTNESS_ESTABLISHED`；仅有不同研究名前缀、相同/不同年龄、总人数、不同发表年份或“subjects”措辞均不够。协议门：原始资料需说明 Ga/Si `_01` 的任务、装置/采样、入组/诊断和关键运动状态（如药物状态/速度/步行环境）是否可比；未知就逐字段标未知，不能自动归为相同。

若双门都可证实，EXP033 的解释仍只是既有同一资料库的研究留出，独立外部有效性还需独立来源。若任一门不通过，记 `INDEPENDENT_PERSON_OR_PROTOCOL_NOT_ESTABLISHED`，保留 EXP033 来源压力测试说法，不升级为独立确认。结果无论方向都会决定下一步是搜独立同构力数据还是先解来源/identity 问题。不修改 EXP033 的模型门、点估计或输出。

记录原始来源索引/证据矩阵、尝试、报告、关账；只验证本目录链接和字段，无全仓门、哈希或原始数据重读。
