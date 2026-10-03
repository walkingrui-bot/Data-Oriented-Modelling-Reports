# EXP022 Source Semantic Regulatory Chronology

研究 ID `STAT-PSYMOE-EXP022-20261002-001`；平台 INTERNAL_COORDINATION / Stat-PsyMoE；2026-10-02 登记；`EXPLORATORY`。来源是用户本轮粘贴的《EXP022 — Source-Semantic Regulatory Chronology》以及随后“EXP022 之后的研究自治授权”。父阶段 EXP020 / EXP021。EXP020 的 `STOPPED_AFTER_HISTORICAL_DATA_AUDIT` 与 EXP021 的 `STOPPED_AFTER_EVENT_A_MANUAL_GATE / CHRONOLOGY_NOT_QUALIFIED` 不修改。研究责任为本轮 agent；没有并行 agent。

## 问题、假设与反证

研究问题：将 FDA Orange Book 产品批准、Purple Book 351(a) 原始许可、Drugs@FDA 申请动作和 ApplicationDocs 文件分别按官方语义编码，是否可形成足够可靠的独立监管事件层？核心假设是 EXP021 的大量日期差异来自产品、申请、许可和文件层级混用；分层后可以构建高置信来源事件，而无需三源日期相等。反证包括：原件字段无法稳定映射、相同事件范围仍有大量不可裁决差异、人工 ETL/语义门失败、NDA 或 BLA 主要事件无法可靠定义、或高置信事件量不足。

## 来源、继承状态与严格范围

- 原位只读 EXP021 的 A 候选 15,399 行、`crosswalk_audit.csv` 10,998 行、两轮人工记录、失败状态及 `SOURCE_INDEX.json`。本轮新数据只写本目录。EXP021 不回写，旧候选不是本轮合格事件结论。
- 官方原件：[Drugs@FDA 数据文件](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)、[Orange Book 数据文件](https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files)、[Purple Book 月度下载](https://purplebooksearch.fda.gov/index.cfm?event=downloads)。原 ZIP/CSV/XLSX 只在内存读取，不建立本地副本；每次读取记 URL、HTTP metadata、检索时刻和与 EXP021 来源版本的差异。若 live 源变更，明确本轮 snapshot 边界，不能声称与 EXP021 raw 完全相同。
- 禁止预测模型、EVENT_B、NCT、target/disease/indication 连接、旧 test 或历史公示日推断。结构化事件日期、文件日期、来源修改时间、读取时间、首次公开时间分列；无法证明 first-public 时为 NULL。文档默认 `verified_document_role=UNKNOWN`。

## 方法、单位、门和对照

独立单位分别为 Orange `(N, application, product)` 产品行、Purple `(BLA, product, original submission)` 源行及派生的 BLA license、Drugs `(application, submission type, submission no, status)` 动作行。一个 BLA 多产品不计多次原始许可。`NDA_FIRST_OBSERVED_PRODUCT_APPROVAL` 为当前 Orange snapshot 同 NDA 精确日的最小值，`TIER_B` 派生；源事件 `NDA_PRODUCT_APPROVAL`、`BLA_ORIGINAL_LICENSURE` 在符合字段定义且人工门过后方可 `TIER_A`。Drugs 动作与文件单列，不覆盖产品/许可日期。

先定义事件 ontology；将 EXP021 全部 crosswalk 行重新分为 `SAME_SCOPE_MATCH`、`SAME_SCOPE_DATE_DIFFERENCE`、`DIFFERENT_SCOPE_EXPECTED`、`UNRESOLVED_SCOPE`、`SOURCE_ONLY`，并附 date relation。只有具精确产品/事件类别同一性的行才能进入真正冲突队列。原 `CONFLICT` 文本不继承为结论。以当前 FDA source row 对独立 ETL 逐字段核查作为正对照，ANDA、MEDGAS、supplement、351(k)、更正信作为灾难性语义错误的负控。来源不可达与来源级字段错误分开记录。

人工门在抽样前单独冻结，样本不得与 EXP021 已看记录及另一门重叠。Gate A：Orange 25、Purple 25、Drugs 25，要求 75/75 关键字段完全对应官方源行。Gate B：新 50 条，NDA 30 / BLA 20，覆盖 Orange/Purple/Drugs，要求至少 47/50 语义分类正确且 0 个灾难性范围错误。先记随机种子、排除范围、判定口径、不可达处理、已看自动分布，再抽样；不得补抽以刷门。Gate A 失败即 `STOP_A`，Gate B 失败即 `STOP_B`。`STOP_C/D/E` 依据事前冻结的同范围冲突可判定性和高置信最小规模评估；未有可比对同范围源时只报不可识别，不称冲突率零。只有全部通过才标 `REGULATORY_EVENT_LAYER_READY`，仍不得称 `CHRONOLOGY_READY_FOR_MODELLING`。

预算：FDA 原件总网络读取不超过 4 GiB，单 endpoint 失败最多再试一次；新派生落盘不超过 1 GiB。固定随机种子拟为 ETL `20261022`、语义 `20261023`，具体门在 `GATE_FREEZE.md` 生效。脚本运行前追加 run_id、方法/输入/输出/状态；失败保留原产物，不覆盖。验证仅本研究目录的格式、行数、唯一性、字段与少量人工记录，不跑全仓门、不做无关 hash。训练字段、模型、随机分割均不适用。

预期输出：`SOURCE_INDEX.json`、`EVENT_ONTOLOGY.md`、`EVENT_SCOPE_AUDIT.csv`、`TRUE_DATE_CONFLICTS.csv`、`REGULATORY_DOCUMENT.parquet`、`FDA_APPLICATION_ACTION.parquet`、`REGULATORY_EVENT_HIGH_CONFIDENCE.parquet`、`NDA_APPLICATION_TIMELINE.parquet`、`BLA_LICENSE_TIMELINE.parquet`、两个人工门 CSV、`GATE_FREEZE.md`、`GATE_RESULT.md`、`WORKLOG.md`、`REPORT.md`、`CLOSEOUT.md` 与 Living Report 追加状态。未通过停止门时，后续条件性文件不造空壳。

若本实验停止，先保留门/失败并关账，再按用户最新自治授权另立新 ID、选择信息增益最高的真实数据研究；不降低本轮门。若通过，另立后继研究，不在本 ID 偷做 indication 或模型。
