# EXP021 Regulatory Outcome Chronology Reconstruction

研究 ID：`STAT-PSYMOE-EXP021-20261002-001`；登记日 2026-10-02；`EXPLORATORY`。父阶段 EXP017–020；直接任务为用户当日粘贴的 EXP021 开工指导。EXP020 `STOPPED_AFTER_HISTORICAL_DATA_AUDIT` 原样保留：旧标签无 drug/event date，26.06 当前 Open Targets 审批报告没有获批日。本轮从官方监管事件重建新 universe，旧 26,235 pair 仅交叉参考；本轮禁止预测、统计/神经临床结果模型及旧 test 确认。

## 问题与反证

问题：官方 FDA 原件能否形成带 occurrence/public/ingest 日期与 provenance 的 drug–indication–target–event 链，从而让下一阶段独立历史研究可定义？先做 `EVENT_A` 原始产品/申请获批，后在 A 通过门后做 `EVENT_B` 适应症特异性获批；Phase 1–4 的 NCT 时间线只作临床开发事件。若审批 action 类型/日期、药物身份、适应症文本或靶点身份不能可靠追溯，则链条失败或局部未识别；不能以当前最大 phase、试验开始或无审批当失败替代。

## 官方来源与身份方法

- [FDA Drugs@FDA 数据文件](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)：Applications、Products、Submissions、Join_Submission_ActionType_Lookup、ActionTypes_Lookup、ApplicationDocs 与 class/status；`SubmissionStatusDate` 必须与 `ORIG`/`SUPPL`、`AP` 等状态及 action/context 合读，不能全叫获批。FDA 页面列 12 张 tab 分隔表。
- [FDA Orange Book 产品数据](https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files)：`Approval_Date` 对应 FDA approval letter 的产品批准日；按 Appl_Type/Appl_No/Product_No 核对 NDA/ANDA，ANDA generic 不算新靶点转译。该来源可锚 NDA 产品日期，不替代适应症新增日。
- [FDA Purple Book 下载](https://purplebooksearch.fda.gov/index.cfm?event=downloads)：BLA 产品原始批准/首次许可日期独立处理；核对与 Drugs@FDA 同一 BLA 的差异，不混同 Orange Book。
- [ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api)：NCT、phase、intervention、condition、actual/estimated start/completion、first posted；仅试验时间线。Open Targets 26.06/ChEMBL drug mechanism 只作为身份候选，当前 mapping 若缺历史可用日标 `POST_HOC_IDENTITY_LINK`，不得作 cutoff 前预测特征。

主键维持 `drug_id + indication_id + target_id + event_type + event_date`，允许多个 target 和每药多个 indication；在身份未定时保留 application/product/NCT 原 ID。匹配层级：监管号码精确 join > 标准化成分精确匹配 > 同 application context 的同义名候选 > 模糊文本候选；后两层不自动确认。原始 FDA indication 文本先保留，之后才尝试 EFO/MONDO/MeSH 等 ontology 映射，无法识别不强配。每个派生行保留来源 URL、版本/检索日、源记录键、转换版本、排除理由及冲突原值；原始来源只读，不复制落盘，不造重复包。

## 阶段、抽检与通过门

1. `SOURCE-PREFLIGHT`：核对三官方 FDA 来源的实际下载端点、格式、字段、更新日、许可及可访问性；不以网页介绍代替实际文件。先保留原始返回/失败。输出来源索引与数据字典草案。
2. `EVENT_A`：从 Drugs@FDA `ORIG` 且批准状态、Orange Book NDA 产品批准日、Purple Book BLA 原批准日分别建原始事件候选。按 application/product 明确申请级与产品级；不把 ANDA、supplement、tentative/拒绝/pending 混入。三源比较 `MATCH`、`DAY_LEVEL_DIFFERENCE`、`CONFLICT`、`SOURCE_ONLY`；保存冲突双边原值。只输出一份阶段 A 状态 `REGULATORY_EVENT_A.parquet`；完成阶段 B 才另建包含 B 的 `regulatory_events.parquet`，两者语义不同。
3. `MANUAL_A`：在看自动匹配分布后、人工打开原件之前冻结误差门与固定种子抽样，至少 50 original approval；尽可能 20 冲突样本。逐条打开 FDA 原件/批准信/产品页核对 application、product、action、日期，不靠代码自检。核查分母和不可达来源一并记录。人工误差超门或官方日期冲突不可裁决，按预设停止。
4. 仅 EVENT_A 过门再做 `EVENT_B`：从 approval letter/当次 label/efficacy supplement/官方公告取 `indication_text_raw`、审批 action/date/publication date；药物原批准不分发给所有适应症。其后建 `drug_identity`、`drug_indication_map`、`drug_target_map`、`trial_events` 与最终 trajectory。各连接层保持 exact/candidate/ambiguous/unmatched，人工至少核 30 indication、30 target、20 冲突（若该类不足则全核且标不满足预设样本数）；整链 NCT/drug→FDA→indication→target 单独抽查。
5. 评估可用 event、first-public availability、follow-up/censoring 与新 cohort 独立性；10 项全通过才可标 `CHRONOLOGY_READY_FOR_MODELLING`。任何缺项均记录为具体缺口，不自动转 Phase 3 benchmark，不训练。

数值质量门（coverage/date/identity/manual error/event count）在查看字段与基础分布后、抽检和下游建模前追加 `GATE_FREEZE.md`，连同已看数据登记；不能事后改成确认门。STOP_1–6 依用户指导执行：审批日期不可靠、药物身份失败、靶点仅 post-hoc、适应症错误高、人工核查不通过或可用事件不足均停止。外部服务失败留原件；重试独立 run_id。不将未批准视为失败标签。

## 单位、环境、预算与输出

分析单位为 application–product–event，EVENT_B 为 drug–raw indication–event，target 为多值附加关系；NCT 为试验事件单位，同药/同 target/同 disease 的多记录不累加为独立成功。当前日期 Europe/London；官方源按检索时版本记录，不假设 2026 现时目录等于历史公开状态。固定抽样 seed `20261002`，具体随机样本范围由有效 EVENT_A universe 决定。预算上限：本轮网络读取 4 GiB、派生落盘 1 GiB、单个官方原件访问失败可重试一次且留账；超过这些上限先停止对应 run，不以模糊匹配换覆盖。脚本与派生数据仅在本目录，raw ZIP/TSV/CSV 原件不落盘，按原 URL 读取；每阶段状态只存一份。只对本区域做格式、关键计数、随机样本的局部验证；不跑全仓测试或无关哈希。若需要校验官方 release 完整性，仅以协议明确的最小来源记录证据为准，当前不计算 hash。

预期输出：`WORKLOG.md`、`CHRONOLOGY_DATA_DICTIONARY.md`、`SOURCE_INDEX.json`、`crosswalk_audit.csv`、`MANUAL_VALIDATION.csv`、`derived/REGULATORY_EVENT_A.parquet`、条件性的 `derived/drug_identity.parquet`、`derived/drug_target_map.parquet`、`derived/drug_indication_map.parquet`、`derived/regulatory_events.parquet`、`derived/trial_events.parquet`、`derived/drug_indication_timeline.parquet`、`REPORT.md`、`CLOSEOUT.md`、独立 DOCX 和 Living v0.22。所有清洗脚本及数据位于 `derived/`；条件阶段未运行时文件不创建空壳，报告逐项标明。EXP020 历史档案和 Living v0.21 不改。
