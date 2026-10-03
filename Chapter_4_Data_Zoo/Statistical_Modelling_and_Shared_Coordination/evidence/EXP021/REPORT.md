# EXP021 监管结局时间线重建报告

研究 ID `STAT-PSYMOE-EXP021-20261002-001`；2026-10-02；`EXPLORATORY`。执行结论：`STOPPED_AFTER_EVENT_A_MANUAL_GATE / CHRONOLOGY_NOT_QUALIFIED`。EXP020 的 `STOPPED_AFTER_HISTORICAL_DATA_AUDIT` 原封保留；本轮没有训练任何预测模型。

## 问题、行动与判断

本轮要从真实 FDA 监管事件重建 drug × indication × target × event 的有日期、有来源链，以便将来定义真实 historical cutoff。按用户顺序，先从 [Drugs@FDA 文件](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)、[Orange Book 产品文件](https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files)、[Purple Book 官方月度下载](https://purplebooksearch.fda.gov/index.cfm?event=downloads)建立 `EVENT_A` 原申请/产品批准候选；只有 A 过人工门才允许 EVENT_B 的适应症文本及后续 NCT/靶点/ontology 连接。实际运行停在 A 的人工核查：修正后独立 50 条样本仅 39 条核实，低于冻结的 45 条门。20 条跨来源日期差异也未获产品级裁决。因此不能把 A 候选升格为可靠 regulatory chronology，更不能宣称可建模。

## 真实读取和可复现产物

四个官方端点（Drugs ZIP、Orange ZIP、Purple August CSV、同月 XLSX）均实际读取，raw 未落盘。`SOURCE_INDEX.json` 保存 URL、HTTP 类型、Last-Modified、读取时间、表列与行数；来源原件只按 URL 引用。Drugs ZIP 有 12 张表，其中 `Submissions` 194,004 行，`Applications` 29,377 行；Orange `products.txt` 48,761 行；Purple CSV 和 XLSX 同为 2,277 物理行、全量 section 2,242 条产品记录。Drugs 在线媒体的 Last-Modified 在尝试间变动时，版本锁中止了一次运行并重新建索引，未混合来源快照。

最终 `derived/REGULATORY_EVENT_A.parquet` 是**未经人工门放行的来源级候选**：15,399 行、5,702 application 行和 9,697 product 行；NDA 13,517 行、BLA 1,882 行；对应 5,376 个 NDA 与 774 个 BLA application number，但跨来源和同申请多规格不得相加为独立转译事件。三源行数：Drugs 5,702；Orange 8,209；Purple 1,488。所存 occurrence/approval 日区间为 1924-03-13 至 2026-09-28。Purple 使用官方 XLSX 的四位年份，旧 CSV 的两位年推断（把 1924 错作 2024）在失败目录中留存，未混入当前候选。排除了 37,875 行 Orange ANDA、2,677 行无精确日 Orange NDA、109 行经 Purple 标明 351(k) 的 Drugs BLA ORIG/AP、83 行 Drugs MEDGAS ORIG。计数为源记录过滤，不是临床失败事件。

`crosswalk_audit.csv` 共 10,998 行：`MATCH 7,019`、一日差 `5`、`CONFLICT 1,622`、`SOURCE_ONLY 2,352`。比较的是 Orange/Purple **产品批准日**与 Drugs **申请原批准日**；后来新增规格合法地晚于原申请，故 1,622 仅是人工核查队列，不能叫 FDA 日期错误。审计保留每侧原日期与 FDA number；未自动裁决。A-007 的 `public_date` 和 `database_ingest_date` 全部空白；`retrieved_at` 才是本次读取时刻。2,954 个 Drugs application 候选关联 `ApplicationDocs` type-1 Letter URL，但该类型可能是更正信或用药指南信，**不是**已验证原始批准信。24 条 Drugs-only BLA application 的 351(a)/351(k) 许可类型在当前 Purple 连接中仍未知。

## 人工抽检与失败证据

在查看自动分布后、抽样前冻结 [GATE_FREEZE.md](GATE_FREEZE.md) 的 50 条初批核查、20 条冲突核查与至少 45/50 独立核实门。首次固定样本 `MANUAL-A-002` 为 44 MATCH、3 FAIL、3 UNVERIFIED；其中两条 Purple 年份误读和一条 MEDGAS 更正信暴露 ETL/来源选择错误。保留原失败输出后，另立 `SOURCE-003`、`EVENT-A-006/007`，使用 FDA XLSX 四位日期，排除 MEDGAS，并纠正 ingest/document 字段语义。一次逐 BLA 页面年核尝试在 750 BLA 中仅取得 47 个完整年份、703 个 HTTP 403，未以这 47 条外推全体日期。

修正后独立样本 `MANUAL-A-003` 采用新 seed、排除旧样本 ID。50 主样本：39 MATCH、10 UNVERIFIED、1 INDETERMINATE；后者 BLA 761315 在 Drugs 与 Purple 中为 `2024-12-20`，链接 FDA 批准信签署日为 `2024-12-26`，本轮不能判定哪一天代表实际 action。39/50 达不到 ≥45/50。20 日期差异样本中 15 例打开 FDA application 页面后仍缺产品 action 的决定性文件，另 5 例页面两次 403。新样本没有确证“数据错误 0%”这一统计结论；11/50 的未识别使总体错误率不可计算。具体逐行值、原 URL、短证据和裁决见 MANUAL_VALIDATION.csv (source asset outside this public snapshot) 与 [GATE_RESULT.md](GATE_RESULT.md)。

## 用户要求的十五项结论

| 问题 | 本轮证据界限 |
| --- | --- |
| 1 FDA original approval events | 15,399 来源级 A 候选行；不是唯一 drug–indication 事件。5,376 NDA + 774 BLA 唯一申请号；候选未过人工门。 |
| 2 indication-specific events | 未启动 EVENT_B，未构建；不是“真实零个”。 |
| 3 NDA/BLA 数 | 来源级候选 NDA 13,517 / BLA 1,882 行；唯一申请号 NDA 5,376 / BLA 774。 |
| 4 ChEMBL/Open Targets drug identity | 未启动，数量未知。 |
| 5 target 可映射数 | 未启动，数量未知。 |
| 6 disease 可映射数 | 未启动，数量未知。 |
| 7 exact mapping 比例 | FDA application/product number 的源间连接为 exact；ChEMBL/target/disease exact 比例未测。 |
| 8 fuzzy/ambiguous 比例 | fuzzy 自动连接 0；药物/靶点/适应症 ambiguity 未测。日期 audit `CONFLICT` 1,622 是不同 scope 日期对比，不能代替身份歧义率。 |
| 9 approval date conflict | 日期筛查 1,622 处 product–application 差异；20 抽样未完成产品级裁决；1 例 BLA bulk 与批准信签署日差 6 日。已确认 FDA 原始记录错误数未知。 |
| 10 indication conflict | 未启动，数量未知。 |
| 11 artificial inference | 最终 A-007 日期推断 0；早期失败尝试曾以错误短年份规则推断，已保留并替换。 |
| 12 manual validation error rate | 新样本 39/50 可核实匹配，11/50 未裁定；全体误差率不可识别。旧失败样本 3/50 明确失败不归零。 |
| 13 future historical benchmark usable events | 未建立 indication、target、public availability 与 censoring，数量未知。 |
| 14 follow-up/censoring | 未定义。未批准不能自动作失败标签。 |
| 15 `CHRONOLOGY_READY_FOR_MODELLING` | **未通过**；A 人工门已阻断。 |

## 范围、停止与后继依赖

本轮执行状态为 `STOPPED_AFTER_EVENT_A_MANUAL_GATE`；工程上完成了带审计和失败留档的 A 候选构建，但人工资格失败；科学上没有合格 drug–indication chronology，也没有任何模型性能结论。`EVENT_B`、FDA indication 原文、NCT 轨迹、drug-target/ontology crosswalk、30+30 人工映射样本、全链 NCT→FDA→indication→target 和 final event/censoring 均未执行。没有创建空 Parquet 壳文件。旧 26,235 target–disease pair 仅作父阶段背景，未作为 FDA universe 的过滤器。

后续若要重新开放，应另立具名研究/修订，以产品级 letter/label action lineage 处理日期冲突、建立独立可达的人工样本与 earliest-public definition，再依次做 EVENT_B、target/indication/NCT。此建议不解除当前 STOP_5，也不把已看样本重抽到过门。原脚本、源索引、A 候选、crosswalk audit、两次人工记录、失败阶段目录与关闭判断均在本研究目录，见 [CLOSEOUT.md](CLOSEOUT.md)。
