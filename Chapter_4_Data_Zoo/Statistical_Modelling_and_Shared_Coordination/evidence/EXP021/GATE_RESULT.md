# EXP021 EVENT_A 人工门结果

结论：`STOP_5 / MANUAL_VALIDATION_NOT_PASSED`。2026-10-02 修正来源年份后的独立 holdout `EXP021-MANUAL-A-003` 未达到先于抽样冻结的核实数量门；不启动 EVENT_B，也不声明 `CHRONOLOGY_READY_FOR_MODELLING`。

## 固定样本与结果

- `seed=20261003`；排除第一次 `MANUAL-A-002` 已看过的 ID；30 NDA 与 10 BLA Drugs@FDA ORIG/AP 有 type-1 Letter 候选，10 Purple 351(a) source-only BLA，另抽 20 个跨 application/product 日期 `CONFLICT`。详细行、原值、URL、抽取证据、人工判定见 MANUAL_VALIDATION.csv (source asset outside this public snapshot)。第一次失败样本及判定在 `derived/failed_MANUAL_A_002/MANUAL_VALIDATION.csv` 保留。
- 50 主样本：`MATCH 39`（30 letter、9 Purple page）；`UNVERIFIED 10`（9 letter、1 Purple page）；`INDETERMINATE 1`（BLA 761315，Drugs/Purple 日期 `2024-12-20`、链接批准信签署日 `2024-12-26`）。独立确证数量 39/50，低于预设至少 45/50。0 个新样本被确认日期错误，但 11 个未能裁定，因此不能报“错误率 0%”。
- 20 日期比较冲突：15 个打开 FDA application 页面仍未证明 product action 的具体日期归属；5 个网页两次均 `HTTP 403`。全部保留双边原值，状态为 `INDETERMINATE` 或 `UNVERIFIED`，不自动用申请原批准日覆盖产品批准日。报告中的 1,622 个 `CONFLICT` 是跨 scope 筛查数，不等于 1,622 个 FDA 错误。
- 首次 `MANUAL-A-002` 的 50 主样本为 44 MATCH、3 FAIL、3 UNVERIFIED，亦未过门。3 FAIL 包括 2 个 CSV 两位年份把 1924 错算为 2024，以及一封医用气体后续更正信；`EVENT-A-006/007` 用同月官方 XLSX 四位日期并排除 MEDGAS，旧失败不改写成成功。Purple 详情页的全量年核尝试 750 BLA 中 47 成功、703 次最终 403；该尝试为失败/部分来源证据，未用于补造日期。

## 适用范围与停止影响

`EVENT-A-007` 是有真实 FDA 日期及 source ID 的**来源级候选表**，共 15,399 行，但人工门失败，未升格为验证通过的 regulatory chronology。`public_date` 与 `database_ingest_date` 均未知且留空；`retrieved_at` 只是本次读取时间。Drugs 的泛型 Letter URL 只是候选，不自动证明为原始批准信；BLA 761315 的双日期保留。

按 [PLAN.md](PLAN.md) 的顺序和用户 STOP_5，EVENT_B indication 文本、ClinicalTrials.gov NCT 轨迹、ChEMBL/Open Targets drug-target 映射、ontology disease 映射、30/30 下游人工映射样本、完整链抽检与最终可用事件数均**未启动**。这代表工程停止条件，不代表这些来源不存在真实记录，也不能把“未测”写为零结果。无预测模型训练、AUROC、survival、confirmation 或旧 test 使用。

执行状态 `STOPPED_AFTER_EVENT_A_MANUAL_GATE`；工程状态 `VALID_SCOPED_A_CANDIDATE_WITH_FAILED_MANUAL_GATE`；科学状态 `CHRONOLOGY_NOT_QUALIFIED / MODEL_OUTCOME_NOT_TESTED`。重新打开后续研究须另立具名修订/尝试，保留本次失败样本，不对同一抽样反复重试直至过门。
