# EXP021 关账与原件索引

研究 ID：`STAT-PSYMOE-EXP021-20261002-001`。状态：执行 `STOPPED_AFTER_EVENT_A_MANUAL_GATE`；工程 `SCOPED_CANDIDATE_BUILT_BUT_MANUAL_GATE_FAILED`；科学 `CHRONOLOGY_NOT_QUALIFIED / MODEL_NOT_TESTED`。停止条件：用户指导 STOP_5，修正后 50 条人工初批核查仅 39 条独立 MATCH，低于冻结的 ≥45 条。

入口：[PLAN.md](PLAN.md) 事前问题/方法/预算；WORKLOG.md (source asset outside this public snapshot) 所有实质尝试、失败和修订；SOURCE_INDEX.json (source asset outside this public snapshot) 四官方源 URL/版本/字段/行数；[CHRONOLOGY_DATA_DICTIONARY.md](CHRONOLOGY_DATA_DICTIONARY.md) 输出语义；[GATE_FREEZE.md](GATE_FREEZE.md) 与 [GATE_RESULT.md](GATE_RESULT.md) 人工门；[REPORT.md](REPORT.md) 结果及十五项回答。

最终派生证据：`derived/REGULATORY_EVENT_A.parquet` 15,399 条来源级候选，`derived/EVENT_A_DIAGNOSTICS.json` 源与排除计数，`crosswalk_audit.csv` 10,998 日期比较，`MANUAL_VALIDATION.csv` 70 条修正后固定样本。原始监管源、PDF 和页面未复制；读者按 `source_url`、`source_record_id`、`retrieved_at` 与 `source_release_last_modified` 反查。此处文件为本地派生状态；不主张它们已 Git 跟踪或异地备份。

交付文档：独立 EXP021 报告 (source asset outside this public snapshot)与Living Report v0.22 (source asset outside this public snapshot)。v0.22 从原 v0.21 直接续写新 Experiment 021 段，首页版本号更新；v0.21 原文件保留。DOCX 渲染检查：独立报告 2 页，Living 60 页；新第 60 页及报告全部页面视觉核对，Living 旧第 2–59 页与原 v0.21 对应页像素一致，首页只作版本变更。QA PNG 在临时目录，不是交付包。

失败与更正保留：`derived/failed_EVENT_A_002/`（Purple 许可状态误读成日期）、`derived/failed_EVENT_A_003/`（未排 351(k)）、`derived/failed_EVENT_A_005/`（CSV 两位年与 MEDGAS）、`derived/failed_EVENT_A_006/`（ingest/document 字段语义）；`derived/failed_MANUAL_A_002/` 是首次失败人工样本；`derived/failed_SOURCE_001/` 和 `derived/superseded_SOURCE_002/` 保留来源版本观察。`derived/PURPLE_FULL_YEAR_APPROVAL_DATES.parquet` 与其诊断记录 47 成功/703 HTTP 403 的受限页面尝试，不作最终日期填充。`EVENT-A-001/004` 与 `MANUAL-A-001` 失败于产出前，原 traceback 和改变见 WORKLOG；未伪造工件。

未运行：EVENT_B、indication label/letter 抽取、ClinicalTrials.gov、ChEMBL/Open Targets target、疾病 ontology、完整 drug × indication × target × event 时间线、后续人工 30 indication/30 target、first-public availability、censoring、预测模型、旧 test 或确认。条件文件不存在正是 STOP 的执行边界。EXP020 旧档、Living v0.21 与已有检查点未改。

本区域局部验证：脚本语法检查、15,399 唯一 `event_id`、10,998 audit、70 人工行/50 主样本/39 MATCH、空 public/ingest 日期、4 源索引、条件输出缺席、两 DOCX 成功渲染；`git diff --check` 对本轮修改的研究入口与登记册通过。未执行全仓测试、预测模型、原始源全量哈希或旧实验重放。该研究目录约 17 MiB，低于既定派生存储预算。
