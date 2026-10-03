# EXP020 terminal outcome chronology 审计

研究 ID `STAT-PSYMOE-EXP020-20261002-001`；审计日 2026-10-02。结论：**本轮已核验来源不足以恢复“决策日之后获批”的 drug–target–indication 事件时间线，触发 `STOP_A`。** 这只限定本轮审计范围，不断言所有公开来源永远无法拼出该时间线。原始聚合与来源见 outcome_chronology_audit.json (source asset outside this public snapshot)，运行和中断见 WORKLOG.md (source asset outside this public snapshot)。

## 原终端标签的可用范围

EXP017 使用的[固定 Git blob 原件](https://api.github.com/repos/vi-c-ky/Human-genetic-evidence-associated-with-drug-approval/git/blobs/d7102b1357aaeb780c73d286318fea297d0dbcb4)有 26,278 行，桥接后为 26,235 个当前 target–disease pair。实际列只有 target、disease、现时 `phase`、二元 `label` 和若干现时关联分数；**没有 drug ID、试验 ID、首次到达各 phase 的日期、获批日或来源版本日**。旧 `phase=4` 标签只能保留为 EXP017–019 的回顾性开发标签；不能在 EXP020 中赋予事件日。`overall_score`、`clinical`、`phase`、`label` 均禁止作为预测证据。

## 26.06 官方临床表的只读诊断

本轮直接读取 [clinical report](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/clinical_report/clinical_report.parquet)、[clinical indication](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/clinical_indication/clinical_indication.parquet) 和 [clinical target](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/clinical_target/clinical_target.parquet) 的 aggregate；原行未复制。三表分别有 289,955、86,468、13,307 行。把**当前** drug–target–disease 映射与旧 pair 相交，18,458 个旧 pair 连接到 40,607 个 drug–target–disease 三元组，涉及 3,041 个 drug；连接到 166,646 个报告关系、37,516 个不同 report ID。一个 pair 可有多药轨迹；这个诊断不能当历史 eligible cohort。精确多药 pair 分布未完成，记未知。

26.06 `clinical_report` 的审批类来源 ATC、DailyMed、EMA、EMA Human Drugs、FDA、PMDA、TTD 合计 29,315 条 `APPROVAL` report，**`trialStartDate` 与 `year` 在这组中均为 0 条非空**。另有 AACT `APPROVAL` 206 条，其中 18 条有 `trialStartDate`，但试验开始日不是获批日。当前 `clinical_indication.maxClinicalStage`、`clinical_target.maxClinicalStage` 同样没有首次发生日期，不能反推。Open Targets 的[临床报告说明](https://platform-docs.opentargets.org/drug/clinical-report)明确区分试验、药品批准与其他报告，且 26.06 的 AACT 药物/疾病抽取使用当版完整试验文本；[临床靶点说明](https://platform-docs.opentargets.org/target/drugs)显示 drug–disease 报告再与 drug–target 作用机制连接，最大阶段是聚合量。

AACT 一至三期和四期报告常有 `trialStartDate`：Early Phase 1 为 4,919/4,922，Phase 1 为 43,862/44,420，Phase 1/2 为 14,453/14,525，Phase 2 为 57,746/58,316，Phase 2/3 为 5,937/5,969，Phase 3 为 36,181/36,556，Phase 4 为 30,254/30,446。这些是**试验开始字段覆盖，不是获批事件覆盖，也不是已核实首次进入 phase 的时间线**。部分 `trialStartDate` 晚于审计日，按阶段观察到的最大值可至 2050；直接当已发生事件会错误。上游 ClinicalTrials.gov 区分[实际与预计开始日](https://clinicaltrials.gov/study/NCT05906823)，还提供[首次公开日字段](https://clinicaltrials.gov/data-about-studies/csv-download)；26.06 临床报告 schema 未带实际/预计标志和首次公开日，不能证明历史时点已经公开。停止/撤回描述也未构成可靠、有日期的 drug–indication terminal event。

## 时间线资格裁决

| 必要链段 | 已核到 | 本轮资格 |
| --- | --- | --- |
| 旧标签到 drug ID | 旧 CSV 无 drug ID；26.06 可以做现时多药映射 | 历史身份未锁定 |
| drug–target–disease–clinical report | 26.06 三表可连接，当前旧 pair 覆盖 18,458 | 只能作现时诊断 |
| Phase 1/2/3 首次发生日 | AACT 多数有 trial start；实际/预计与 first posting、历史版本未核对 | `OUTCOME_DATE_UNAVAILABLE` 对正式事件定义 |
| Phase 4／批准日 | 29,315 条审批类 report 无该两日期字段 | `OUTCOME_DATE_UNAVAILABLE` |
| 某个 `t0` 的 eligible universe | 25.12 [官方历史目录](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/25.12/output/)未列 `clinical_report`/`clinical_target`；26.06 映射含事后信息 | 未构建 |

因此没有选择 decision dates 或 horizon，也没有逐 cutoff eligible pair、future event、确认标签。这个空缺不是零事件。若未来另立具名研究，可考察 ClinicalTrials.gov 的版本化 NCT 记录和 [Drugs@FDA submissions 日期字段](https://open.fda.gov/apis/drug/drugsfda/understanding-the-api-results/)，先建立并人工核验 application/NCT→drug→indication→target 跨源身份链、实际事件日及历史公开日；本轮未完成这条链，不能以其存在为本轮 PASS。
