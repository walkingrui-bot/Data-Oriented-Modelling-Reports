# EXP020 历史数据可行性审计报告

研究 ID `STAT-PSYMOE-EXP020-20261002-001`；2026-10-02。**执行结论：`STOPPED_AFTER_HISTORICAL_DATA_AUDIT`。** 本轮当前可核验数据不能把 EXP017–019 的现时 phase 标签变成决策日之后的获批事件；按预设 `STOP_A` 不训练。此结论是数据识别边界，**不是** M0–M7 任何模型的性能结论，也不是对所有未来数据整合可能性的否定。

## 问题、方法与证据

问题是过去已经存在的七条真实来源能否预测之后的人体药物研发 terminal outcome。先查原标签实际列，再直接读取 Open Targets 26.06 `clinical_report`、`clinical_indication`、`clinical_target` 的聚合，审计 drug–target–disease–report 身份与阶段日期；七条原生来源全表扫描日期字段，记录原件 URL、日期未知/晚于审计日与当前策展状态风险。审计尝试、网络中断和接续均见 WORKLOG.md (source asset outside this public snapshot)；方法与停止门见 [PLAN.md](PLAN.md)。没有训练、没有本轮模型性能读取、没有新测试集打开；父阶段已公开的开发指标仅用于了解继承状态。

[结局时间线](OUTCOME_CHRONOLOGY.md)显示：旧 26,278 行没有 drug ID/事件日；26.06 当前三表虽可将 18,458 个旧 pair 接到 40,607 条 drug–target–disease 关系，但 29,315 条审批来源 `APPROVAL` 报告没有 `trialStartDate` 或 `year`。AACT 试验开始日不能代替获批日，且 26.06 抽取与映射不是旧 decision date 的 as-of 状态。原始数量、来源和未完成的多药分布见 聚合诊断 JSON (source asset outside this public snapshot)。

[七源泄漏账](LEAKAGE_LEDGER.md)确认原生日期字段有大量覆盖，但“某 26.06 行标一个旧日期”不等于当年已有同一行、同一临床无关评分和同一 ontology 映射。Europe PMC 26,191,349 行中 65 行日期晚于 2026-10-02；CGC 16,503 行日期未知，IMPC 1,049,082 行未知。完整 支持 JSON (source asset outside this public snapshot) 与 CSV (source asset outside this public snapshot) 中 cutoff 纳入数、eligible pairs、future events 均为 `null`，不是零。

## 预设门与三轴状态

`STOP_A` **触发**：本轮审批型 terminal event 日期不能从原标签或核到的 26.06 官方临床三表恢复。`STOP_B`/`STOP_D` 的完整历史版本资格尚未审定；七源有 25.12 快照候选，但未完成早期 cutoff 的逐行内容/映射重建。`STOP_C` 无法评估，因为没有 horizon 后的合法事件计数。`STOP_E` 无法评估，因为没有历史 cohort 可切分。这些未知不能写成已通过或已失败。停止规则不允许从旧 pair 当前 phase 推测日期，也不允许借旧 test 作确认。

| 轴 | 状态 | 解释 |
| --- | --- | --- |
| 执行 | `STOPPED_AFTER_HISTORICAL_DATA_AUDIT` | 完成 chronology 与七源日期库存，未训练。 |
| 工程 | `VALID_SCOPED_AUDIT` | 原件只读聚合、逐源 JSON/表、来源 URL 与局部一致性核对；一次目录访问失败与一次查询中断按原样留账。 |
| 科学 | `NOT_IDENTIFIABLE_IN_AUDITED_DATA` | 不能定义冻结的未来获批标签、eligible cohort 或确认性能；没有阳性/阴性模型结果。 |

## 按用户开工指导逐项回答

| # | 问题 | 本轮回答 |
| ---: | --- | --- |
| 1 | outcome chronology 是否真实可恢复 | 对本轮审批型终点，**未恢复**；29,315 条审批来源记录无获批日；原标签无 drug/date。 |
| 2 | 使用哪些 decision dates | 未设定；`STOP_A` 在选择 cutoff 前触发。 |
| 3 | 每 cutoff eligible pairs/events | 未构建；不是 0。 |
| 4 | 每源多少真实 historical evidence | 未判定；`LEAKAGE_LEDGER.md` 仅给 26.06 全表日期库存。 |
| 5 | 去掉多少 unknown/future date evidence | 未作 cutoff 纳入/排除；现时全表未知与晚于审计日数量见 ledger。 |
| 6 | Europe PMC 时间污染风险 | 已观察 65 行晚于审计日、84,609 行只有年份粒度；后期论文与当前策展风险未量化为性能偏差。 |
| 7 | cutoff 前 CGC 覆盖 | 未判定；26.06 全表 16,503 行日期未知。 |
| 8 | classical historical performance | 未运行。 |
| 9 | Stat-MoE performance | 未运行。 |
| 10 | ganglion performance | 未运行。 |
| 11 | ganglion 对 Stat-MoE paired interval | 未计算。 |
| 12 | CGC historical increment 保持否 | 未检验。EXP019 现时开发 test 的点估计不能移作本轮证据。 |
| 13 | Europe PMC historical contribution 保持否 | 未检验。 |
| 14 | post-cutoff evidence 虚增多少 | 未注入、未测。 |
| 15 | confirmation 一次性打开且未用于调整否 | **确认集未创建、未打开**；不能称一次确认已完成。 |

## 交付与范围

实际交付：计划、完整尝试账、结局时间线、七源泄漏账及各 JSON、支持 CSV/JSON、报告、关账、独立 DOCX、Living v0.21。由于 STOP_A，`SPLIT_LOCK.json`、`TRAINING_LOCK.json`、`evidence_maturity_curve.csv/png`、`results/`、`figures/`、`checkpoints/`、模型预测、置信区间和 seed 保存点**未创建**。这满足预设“停止就不硬训”，不能把缺文件补为空壳。

局部验证只有本轮脚本语法、七份 JSON/支持表数值一致性、链接与文档渲染；未跑全仓门、旧实验重放、全目录哈希、外部 FDA/ClinicalTrials.gov 身份链或历史快照逐行回算。后继建议只登记：如另立研究，先构建审批 application 与 NCT 到药物/疾病/靶点的版本化映射、区分 actual/estimated 与首次公开时间，核验端点日期和足够未来事件，再冻结新的 cutoff/cohort/split；不自动启动 EXP021。
