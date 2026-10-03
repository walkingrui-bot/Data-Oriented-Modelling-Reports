# EXP023 当次 FDA 标签中的适应症事件可识别性

研究 ID `STAT-PSYMOE-EXP023-20261002-001`；2026-10-02；`EXPLORATORY`；平台 INTERNAL_COORDINATION / Stat-PsyMoE；父阶段 EXP022。用户 2026-10-02 EXP022 指导允许通过后另开 indication-specific 重建，随后路线自治授权要求选择最有信息增益的真实问题并直接执行。EXP020 STOP_A、EXP021 STOP_5 和 EXP022 的来源语义门均保持原样。

## 问题与决策用途

当前最大缺口不是再优化模型，而是 FDA 已核准的 application/submission action 能否找到**同一当次**标签，并从其 `INDICATIONS AND USAGE` 及相关监管文件中识别真正获批的 indication。若能建立足够明确的当次证据，后续才有资格研究 drug–indication、历史时锁与 terminal outcome；若不能，停止此公开数据路线，避免把当前 label 倒填历史。

本轮第一刀为真实来源可用性和识别门，不训练模型、不接 NCT/target/disease ontology。竞争解释：H1，同一 submission 的 FDA 文件足以在可观样本中定位当次 label 与 indication 文本；H0，文件缺失、角色含混或时点不明使此事件不可识别。无论方向都决定是否继续 drug translation。

## 来源、独立单位和原件边界

- 输入为 EXP022 原位 `FDA_APPLICATION_ACTION.parquet`、`REGULATORY_DOCUMENT.parquet`、`REGULATORY_EVENT_HIGH_CONFIDENCE.parquet`；FDA Drugs@FDA 下载表的官方字段定义见 <https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files>。只读取真实官方 URL 的文件，内存解析，不另存 PDF、HTML、ZIP 或原始文本副本。每次保存 URL、application/submission key、HTTP/解析结果与短的证据定位，不保存整份原文。
- 主要审计单位是 `(application_type, application_no, submission_type, submission_no)`，同一 application 的多个 submission 不当独立药物；抽样以 application 无放回。`ApplicationDocsDate` 是文件元数据日，`SubmissionStatusDate` 是 action 日，二者不互替。所有当前 snapshot 信息仅作**回顾性来源审计**，不声称历史 first-public。
- 两层来源分开：ORIG 已批准 action；`SubmissionClass` 经官方 lookup 明示 efficacy 的 SUPPL 已批准 action。其他 supplement 不推断为新增 indication。BLA 只保留 EXP022 351(a) 证实的号；NDA 只保留 EXP022 中 Orange exact 产品号的申请。action 与产品/许可的 scope 仍分离。

## 预先冻结的第一阶段方法和门

1. 使用 EXP022 同 snapshot 元数据以及官方 FDA lookup 读取类别语义，建立 ORIG/EFFICACY-SUPPL 已批准 action 分母。按 application/submission exact key 左连接 `REGULATORY_DOCUMENT`，记录有无 `Label` 型 document 候选、URL、文档数、action 日；不因题名或 URL 就把候选判成当次 label。若任一层去重 application <20，记 `STOP_SUPPORT`。
2. 在从未看过的 eligible application 中按固定 seed `20261025` 抽 ORIG 20 和 efficacy SUPPL 20，层内一 application 一 action、优先按 application 号排序再随机；两层 application 不重叠。抽样前保存 `SAMPLE_FREEZE.md` 和 `SAMPLE.csv`。没有 label URL 的 action 仍可被抽中并记缺失，不能补抽。
3. 最多读取每条 sampled action 的一个同-key label 候选官方文件；若多个，按 `document_date` 最早、`document_id` 最小的固定顺序选。逐条核 app/submission、实际文件角色、可读性、`INDICATIONS AND USAGE` 文本和明确的时间关系。只在 PDF/页面自身证据与同-key metadata 都支持时标 `CONTEMPORANEOUS_LABEL_CANDIDATE`，否则 `UNRESOLVED` 或 `MISSING`。此状态也不是已确认的 indication approval。
4. 第一阶段通过要求每层至少 18/20 有可读且同-key的完整 label `INDICATIONS AND USAGE`，且 0 个把别的 submission、当前标签或文件元数据日期误写为 action/event 日的严重 scope 错误。未过即停止 EXP023 并关账；不放宽、不补抽、不以当前 label 代替。
5. 若通过，另冻结 indication phrase 的原始/补充差分、双人或独立解析复核和产品 scope 规则后才允许建立 indication-specific event table。不能用看过的第一阶段样本当确认样本。若 source 能支持文本却不能识别新增 indication，关账为不可识别，不送模型。

## 记录、预算与停止

预期输出本目录：`SOURCE_SUPPORT.json`、`SAMPLE_FREEZE.md`、`SAMPLE.csv`、`DOCUMENT_AUDIT.csv`、`WORKLOG.md`、`REPORT.md`、`CLOSEOUT.md`，必要时派生 Parquet。运行前每次记 run_id、输入、命令/方法、预期路径和 RUNNING，结束补实际结果。最多 40 sampled 文档首次读取，失败每 URL 最多一次重试；总网络上限 512 MiB，单文件上限 20 MiB；不付费、不用个人凭据。超过任一界限停止且留现场。只做本研究局部验证，不全仓测试/哈希。

如果 `STOP_SUPPORT` 或第一阶段门失败，按用户自治授权关账并独立评估下一最大未知；不可把 EXP023 的失败改成 EXP022 不通过。若通过也不等于 `CHRONOLOGY_READY_FOR_MODELLING`：历史 first-public、未观察到事件的 follow-up/censoring 与独立 drug/indication crosswalk 仍须另证。
