# EXP029 — PADS 心算双通道候选的外部来源兼容性

研究 ID `STAT-PSYMOE-EXP029-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP028](../EXP028/CLOSEOUT.md)。开始前已做两组广义官方来源检索，只看到 PADS 本身、PPMI、Monipar、BIOCLITE、ALAMEDA、UCI/PhysioNet 步态等候选名称和部分摘要；这些为**初始 scoping，已观察，不伪称对候选名单盲审**。详细源语义/许可/样本门在本计划之后才核。

问题：是否存在一份**独立于 PADS**、公开可合法本机读取、真实人级的 cohort，可在不改变原组三分类与 30 项问卷+双腕心算任务定义的情况下，对 EXP028 M4 作直接外部验证？H1：存在可定位原件、person ID、由临床确认的 PD/DD/HC（PD≥30、DD≥20、HC≥20），与 PADS NMS30 实质同构的问卷、同步双腕 accel+gyro、认知负荷静息任务、明确采样/任务协议和允许的非商业研究访问。H0：审到的公开来源只有部分可比，或存在访问/许可障碍；此时 `DIRECT_EXTERNAL_VALIDATION_SOURCE_NOT_IDENTIFIED_IN_AUDITED_SET`，不迁就成二分类、换设备/任务、填补缺失问卷或以同一 PADS 人重复分割自称外部确认。

审计集合事前固定为六类官方原件或托管记录：PADS 作为接口基准（不算外部）、PPMI 官方数据访问和数字传感说明、[Monipar Zenodo](https://zenodo.org/records/8104853)、[BIOCLITE Zenodo](https://zenodo.org/records/20644246)、[ALAMEDA Zenodo](https://zenodo.org/records/15769959)、UCI Daphnet/PhysioNet Gait in Parkinson's Disease。可追加一项直接指向相同 NMS+双腕认知任务的官方记录，但须在日志注明发现时间和来源；不声称穷尽全球数据。每个候选审：独立人和三组样本数、诊断依据、问卷、两腕 accel+gyro、心算任务、格式/采样、许可/访问。未知写 UNKNOWN，不能根据论文标题或片段猜具体数据列。

判据：任一**非 PADS**候选在官方资料/原位元数据同时满足全部字段和人数/访问门，才可登记 `DIRECT_EXTERNAL_SOURCE_READY_FOR_NEXT_PROTOCOL`；否则停止**直接 M4 外部确认路线**，保留 EXP028 开发候选，下一独立实验选择更可识别的真实问题或建立新 outcome/通道 crosswalk，不能在本 ID 偷改。若需个人凭据、受控访问申请或许可不明，不擅自越权获取；记阻断。此次只读，不训练、下载原件或修改模型。

预算至多 10 个官方页面/记录与 2 个官方说明文档，输出 `SOURCE_MATRIX.md`、`WORKLOG.md`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`，引用原 URL；不复制源文件。局部核来源引用与矩阵字段，不做全仓门/哈希。
