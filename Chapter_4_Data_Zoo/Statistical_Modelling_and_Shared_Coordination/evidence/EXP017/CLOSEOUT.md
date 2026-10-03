# EXP017 关账与原件索引

研究 ID：`STAT-PSYMOE-EXP017-20261002-001`；父阶段：`INTERNAL_COORDINATION_016`；2026-10-02 关账。计划为 [PLAN.md](PLAN.md)，完整时间顺序为 WORKLOG.md (source asset outside this public snapshot)，本轮结论为 [REPORT.md](REPORT.md)。

## 三轴状态

| 轴 | 状态 | 依据与限制 |
| --- | --- | --- |
| 执行 | `COMPLETE` | EXP017 六条 native/source-specific 训练、三 seed、传统统计、对照与档案完成；EXP018+ 未开始。 |
| 工程 | `VALID_SCOPED` | 固定 26.06 官方原件、label bridge、cohort 限定单份派生状态、target-disjoint split、训练内 OOF、原预测/检查点与局部复读核对完成；不代表全 18 路或全仓验收。 |
| 科学 | `MIXED / UNCONFIRMED` | Native ganglion 相对 native Stat-MoE 的 test log-loss −0.001361，target-group 95% CI [−0.004207, +0.001225]；Europe PMC 强依赖、无历史时间锁、无独立确认。 |

## 全部实质尝试与修订

| ID | 最终状态 | 主要证据 |
| --- | --- | --- |
| `EXP017-PREFLIGHT-001` | `PARTIAL_PREPARATION` | 原 016 ZIP 静态核对；发现原脚本 release 过滤/18 路默认启动/验收范围不足。 |
| `EXP017-ACCESS-001` | `COMPLETE_WITH_ROUTE_CORRECTION` | access_probe.json (source asset outside this public snapshot)；Bedrock 当前表无可用 26.06 行，改走官方固定历史 FTP；未改用 26.09。 |
| `EXP017-CACHE-001` | `FAILED_VALID_GUARD` | cache_failure.json (source asset outside this public snapshot)；桥接 pair 的 phase 不一致；未产生不完整缓存。 |
| `EXP017-BRIDGE-DIAG-001` | `COMPLETE` | bridge_conflicts.json (source asset outside this public snapshot)；唯一 phase 冲突的二元 label 均为 0。 |
| `EXP017-AMEND-001` | 训练结果前修订 | 同 label 不同 phase 合并为一 pair，保留 phase/source ID 集合；不同 label 仍硬停；原失败留存。 |
| `EXP017-CACHE-002` | `COMPLETE` | cache_manifest.json (source asset outside this public snapshot)、cohort_mapped.parquet (source asset outside this public snapshot)、association_cohort_18.parquet (source asset outside this public snapshot)；26,235 pair、18/18 来源非空。 |
| `EXP017-SOURCE-TRAIN-001` | `COMPLETE`，ganglion 阴性 | [原运行目录](results/source_level_six/EXP017-SOURCE-TRAIN-001)；三 seed 250 epoch 均不及 Stat-MoE。 |
| `EXP017-ANALYSIS-001` | `COMPLETE` | [paired_analysis.json](results/source_level_six/EXP017-SOURCE-TRAIN-001/paired_analysis.json)；成对 CI 与下降中验证轨迹。 |
| `EXP017-AMEND-002` | 已看 test 后的探索修订 | 另立 1,000 epoch/100 patience 尝试，不覆盖初跑。 |
| `EXP017-GANGLION-LONG-001` | `COMPLETE` | [长预算运行目录](results/source_level_six/EXP017-GANGLION-LONG-001)；旧预测精确重建，新数值优势 CI 跨零。 |
| `EXP017-NATIVE-PREFLIGHT-001` | `COMPLETE` | native_probe.json (source asset outside this public snapshot)；六条原生表实际 schema/footer。 |
| `EXP017-NATIVE-CACHE-001` | `COMPLETE` | native_cache_manifest.json (source asset outside this public snapshot)；六份 `native_<datasource>_pair_features.parquet` 为单一新 pair 状态，原 raw 未复制。 |
| `EXP017-NATIVE-DIAG-001` | `COMPLETE` | native_diagnostics.json (source asset outside this public snapshot)；EVA 零分、缺字段、Europe PMC 异常年份。 |
| `EXP017-EVA-CATEGORY-001` | `COMPLETE` | 类别定义 (source asset outside this public snapshot)、类别状态 (source asset outside this public snapshot)；797 pair 的类别保真派生统计。 |
| `EXP017-NATIVE-TRAIN-001` | `COMPLETE` | [原生训练运行目录](results/native_six/EXP017-NATIVE-TRAIN-001)；十模型、三 seed、预测、对照、轨迹、图、检查点。 |
| `EXP017-REPORT-001` | `COMPLETE` | 本关账、独立报告和 Living Report 新版；历史文档不改写。 |

## 唯一新状态与报告

- 统计数据：本目录 cohort_mapped.parquet (source asset outside this public snapshot)、association_cohort_18.parquet (source asset outside this public snapshot)、六份 `native_<datasource>_pair_features.parquet`、native_eva_category_features.parquet (source asset outside this public snapshot)，各只保存一次；含输入路由和口径的 cache_manifest.json (source asset outside this public snapshot)、native_cache_manifest.json (source asset outside this public snapshot)。派生 pair 状态是本轮新结果，不是远端 raw evidence 的复制。
- Source-level 首跑：[metrics](results/source_level_six/EXP017-SOURCE-TRAIN-001/metrics.json)、[controls](results/source_level_six/EXP017-SOURCE-TRAIN-001/controls.json)、predictions (source asset outside this public snapshot)、OOF (source asset outside this public snapshot)、[诊断](results/source_level_six/EXP017-SOURCE-TRAIN-001/ganglion_diagnostics.json)、三 seed checkpoint/trace 与 [图](results/source_level_six/EXP017-SOURCE-TRAIN-001/baseline_logloss.png) 均在同一原运行目录。
- Source-level 长预算：[重建核对](results/source_level_six/EXP017-GANGLION-LONG-001/reconstruction_check.json)、[metrics](results/source_level_six/EXP017-GANGLION-LONG-001/metrics.json)、[成对分析](results/source_level_six/EXP017-GANGLION-LONG-001/paired_vs_stat_moe.json)、原预测/控制/三 seed checkpoint 与 trace 在原运行目录。
- Native 六路：[metrics](results/native_six/EXP017-NATIVE-TRAIN-001/metrics.json)、[paired comparisons](results/native_six/EXP017-NATIVE-TRAIN-001/paired_comparisons.json)、[controls](results/native_six/EXP017-NATIVE-TRAIN-001/controls.json)、[split](results/native_six/EXP017-NATIVE-TRAIN-001/split_summary.json)、[routing weights](results/native_six/EXP017-NATIVE-TRAIN-001/routing_weights.json)、[environment](results/native_six/EXP017-NATIVE-TRAIN-001/protocol_and_environment.json)、test predictions (source asset outside this public snapshot)、OOF (source asset outside this public snapshot)、[图](results/native_six/EXP017-NATIVE-TRAIN-001/native_test_logloss.png)、三 seed checkpoint 与 trace 在原运行目录。
- 人类阅读：017 独立 DOCX (source asset outside this public snapshot)；Living Report v0.18 (source asset outside this public snapshot) 从交接包 v0.17 追加 017 章节，属于下一阶段新状态，原 v0.17 仍在原 ZIP。

## 原件与恢复依赖

- 用户提供的完整交接包原件：`/Users/rui/Downloads/INTERNAL_COORDINATION_COMPLETE_HANDOFF_20261002.zip`；包含 016 报告、Living Report v0.17、Passport v0.2、002–016 evidence ZIP 与训练包。001 单独 evidence ZIP 在交接包中未定位；不能写为已归档。
- 另供训练包原件：`/Users/rui/Downloads/INTERNAL_COORDINATION_LOCAL_TRAINING_016.zip`。本轮逐字节比较其与完整交接包内训练 ZIP 相同；未计算哈希。
- 公开原始数据：Open Targets [官方固定 26.06 历史目录](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/) 的 `disease/`、`association_by_datasource_direct/` 与六条 `evidence_*` 表；终端标签 [固定 Git blob](https://api.github.com/repos/vi-c-ky/Human-genetic-evidence-associated-with-drug-approval/git/blobs/d7102b1357aaeb780c73d286318fea297d0dbcb4)。外部 URL 可读取时不是本地备份；将来恢复仍依赖远端可用性、此目录内派生状态、运行依赖与原交接 ZIP。
- 运行环境：`/Users/rui/.cache/stat_psymoe_exp017_env` 的 Python 3.12.14、NumPy 2.5.3、Pandas 3.0.6、scikit-learn 1.9.1、SciPy 1.18.1、PyTorch 2.14.1、DuckDB 1.5.6、PyArrow 25.0.1；模型使用 MPS。环境路径只是本机当前依赖，不称为异地备份。
- 源码：本目录 `access_probe.py`、`cache_source_level.py`、`bridge_diagnose.py`、`train_source_level_six.py`、`paired_analysis.py`、`long_budget_ganglion.py`、`native_probe.py`、`native_cohort_cache.py`、`native_diagnostics.py`、`eva_categories.py`、`train_native_six.py` 和 `build_documents.py`；旧 016 源码只在原训练 ZIP。

交付按仓库明确的“实验材料禁止副本”规则使用原件索引，不再生成重复证据包、重复检查点别名或非实验必要的 SHA 清单。该选择不删除任何历史副本或失败现场。

## 验证边界与下一步

本轮实际运行过固定 release 数据读取、桥接守卫、局部缓存重读、target split/OOF、六源训练与三 seed 对照、bootstrap；另用 DOCX 渲染器检查交付文档。仅静态检查过旧 016 harness 与交接报告。没有运行全仓门、全量哈希、完整 18 路训练、历史 decision-date 时锁、前瞻/临床检验、独立源级 holdout 或因果机制确认。本次 test 不再是未看过的确认集。EXP018 冻结接入另立研究，EXP019–026 仍为后续路线；本关账不替它们裁决。

原开工指导的 `SMOKE_TEST_OK.json` 没有生成：原 016 smoke 脚本只查表名，本轮虽已实测固定版本、桥接、切分和缓存读取，但“同一命令重复执行不重新下载全部数据”的具体自动验收未作为独立门运行；不能补写无条件 `OK` 回执。上述局部证据保留在本记录各原始结果中。
