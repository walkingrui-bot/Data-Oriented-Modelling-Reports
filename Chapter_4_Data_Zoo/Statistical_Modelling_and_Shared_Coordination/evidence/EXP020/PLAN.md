# EXP020：Decision-Date Locked Drug Translation Benchmark

研究 ID：`STAT-PSYMOE-EXP020-20261002-001`；登记日期：2026-10-02；性质：`EXPLORATORY`。父阶段为 EXP017/018/019。直接任务来源为用户 2026-10-02 粘贴的《EXP020 — Decision-Date Locked Drug Translation Benchmark》；旧阶段文档及交接包仅作证据，不能替代本轮历史审计。

## 问题与反证

问题：在真实历史决策日 `t0` 已存在的科学证据，能否预测之后固定 horizon 内的人体药物研发 terminal event？先审计这个问题是否能被当前可定位公开数据识别。反证：旧 phase 标签缺 drug、事件日和历史 eligible universe；任一关键时间或身份链断裂时，旧 26.06 cohort 无法升级为历史 benchmark。工程 PASS 或旧 test 分数不能反证该缺口。

## 第一门：历史数据可行性

1. 从原始 terminal cohort 的实际列、生成依据及官方 drug/indication/clinical event 表追溯 `drug_id → target_id → disease_id → event type → event date → release/version`；日期缺失记 `OUTCOME_DATE_UNAVAILABLE`，不从当前最大 phase 回推日期。保留多 drug、多 indication、多事件层级。核对第一阶段各 phase 日期、approval/termination 日期是否有可信原始来源，以及事件时间与数据库记载时间的区别。
2. 七来源仅为 `gwas_credible_sets`、`gene_burden`、`eva`、`expression_atlas`、`impc`、`europepmc`、`cancer_gene_census`。逐源核对 26.06 实际 schema、历史 release/版本、可解释的日期字段、当前行修改风险及 outcome-adjacent 字段。按原始路径索引，不复制 raw、旧 checkpoint 或旧日志。生成逐源 JSON 和总 ledger；缺项显式 `null/UNKNOWN/NOT_AUDITED`，不得以未计算数冒充 0。
3. 历史 snapshot 优先于版本记录，版本记录优先于当前行日期过滤。strict 主分析排除不能证明 `≤t0` 的记录；源层 `publication year` 不等同于其当前 curated score 当年已经存在。Europe PMC 2120 年异常必须纳入 invalid-date 审计。
4. 审计只看 provenance、schema、日期覆盖、候选单位和有限规模计数；不查看 EXP020 的任何模型性能。允许已知 EXP017–019 旧开发分数作为父阶段背景，不能当本轮确认。

## 候选 benchmark 协议，仅在第一门通过后冻结

独立样本单位暂定 drug–target–disease–decision date；若选择 target–disease 聚合，须在训练前另写固定规则，并保留所有 drug 轨迹及同 target 分组。候选 `t1<t2<t3` 在完整历史来源覆盖、terminal date coverage 与事件计数审计后确定，禁止由模型性能选择。每个日期从当时可识别的 target/drug/disease universe 重建 eligible cohort；不能以 2026 cohort 删未来行代替。固定 horizon 从真实事件密度选取并在训练前锁定。确认集需新的 temporal + target-disjoint split，不能复用 EXP017–019 已看 test。

若通过数据门，在读确认性能前建 `SPLIT_LOCK.json`（协议所需 row/target/disease/drug ID、cutoff、horizon、assignment、最小必要 SHA256）和独立确认标签；再用 train/validation 冻结 source/experts、16D 共享架构、seeds、epochs、patience、LR、正则，写 `TRAINING_LOCK.json`。模型顺序 M0 prevalence、M1 additive、M2 interaction、M3 EB/hierarchical、M4 native Stat-MoE、M5 global Stat-MoE、M6 ganglion、条件 M7 precision；主 log-loss，辅 Brier、AUROC、AUPRC、ECE/校准；target-group 成对 bootstrap。确认只开一次。此节是条件路线，**不是已执行训练协议**。

## 停止门、预算与输出

`STOP_A` terminal chronology 无法恢复；`STOP_B` 多数来源无法恢复历史可用性；`STOP_C` 未来事件不足；`STOP_D` current row 与历史快照不可辨且严重泄漏；`STOP_E` 无法建新的独立 split。任一成立立即停止训练，执行状态 `STOPPED_AFTER_HISTORICAL_DATA_AUDIT`。若停止，仍交 `OUTCOME_CHRONOLOGY.md`、`LEAKAGE_LEDGER.md`、七源审计、支持表、报告和关账；`SPLIT_LOCK.json`、`TRAINING_LOCK.json`、模型/预测/成熟曲线不存在须逐项说明，不能生成空壳伪装已做。可形成独立 DOCX 与 Living v0.21，但只记录实际审计结论。

本阶段最多审计原 cohort、一条或少量官方 outcome 来源、七张 26.06 表的 schema 与有界日期聚合，以及可定位的官方历史 release。只做当前区域读取和最小输出检查，不跑全仓门或非必要哈希；不下载/复制大型 raw。尝试和失败写入 WORKLOG，原始工具返回或必要诊断存当前目录一次。输出均在本目录，研究入口和登记册更新为索引。
