# EXP019 关账与原件索引

研究 ID `STAT-PSYMOE-EXP019-20261002-001`；父阶段 EXP017/018；2026-10-02 关账。完整方法与数值见 [REPORT.md](REPORT.md)，事前门与训练前方法见 [PLAN.md](PLAN.md)，全部尝试及原失败见 WORKLOG.md (source asset outside this public snapshot)。

## 三轴状态

| 轴 | 状态 | 证据界限 |
| --- | --- | --- |
| 执行 | `COMPLETE` | 12 来源统一预检；1 源通过，CGC 原生统计、三 seed 冻结接入、全参数接续重训、shuffle、无 EP 条件、区间、九保存点恢复与报告均完成。 |
| 工程 | `VALID_SCOPED` | 固定 26.06 原件、原 cohort/split、先 train/validation gate 后 test 报表、旧预测重建和冻结参数/恢复校验通过；未跑全仓或从零 7 路训练。 |
| 科学 | `MIXED / UNCONFIRMED_RETROSPECTIVE` | frozen101 较旧 test log-loss −0.000300，target-group 95% CI [−0.000730,+0.000094] 跨零；full validation 改善未在选定 test 保持，Europe PMC 依赖仍强；无独立确认或时间锁。 |

## 尝试账及失败

| Run ID | 最终状态 | 唯一原件 |
| --- | --- | --- |
| `EXP019-SUPPORT-001` | `COMPLETE` | [事前资格](eligibility_train_validation.json)、12 来源诊断 (source asset outside this public snapshot)、支持表 (source asset outside this public snapshot)；11 FAIL、CGC PASS；[代码](support_preflight.py)。 |
| `EXP019-CGC-NATIVE-001` | `FAILED_VALID_GUARD` | 失败异常 (source asset outside this public snapshot)；错误读取资格文件不存在的 test 字段，未写 native state；原失败保留。 |
| `EXP019-CGC-NATIVE-002` | `COMPLETE` | 唯一 CGC native pair state (source asset outside this public snapshot)、来源与诊断 manifest (source asset outside this public snapshot)、[修正代码](cgc_native_state.py)。 |
| `EXP019-CGC-STAT-001` | `COMPLETE` | [原运行目录](results/EXP019-CGC-STAT-001)：旧预测重建、target OOF expert、source routing、CGC 导出状态、M0/M1 train/validation 预测和指标；[代码](cgc_stat_models.py)。 |
| `EXP019-ONBOARD-001` | `COMPLETE` | [原运行目录](results/EXP019-ONBOARD-001)：9 新保存点、逐 epoch 轨迹、validation 选择、validation/test 原预测、所有 test 指标、shuffle/无 EP/旧保留对照、成对区间、图和配置；[代码](onboard.py)。冻结保存点仅存新接口并引用旧 checkpoint。 |
| `EXP019-RESTORE-001` | `COMPLETE / PASS` | [九保存点恢复核对](results/EXP019-ONBOARD-001/restore_verification.json)、[代码](verify_restore.py)，validation 预测最大差 1.8e-7。 |
| `EXP019-REPORT-001` | `COMPLETE` | 本关账、[完整报告](REPORT.md)、[支持图](source_support.png)、[test 图](results/EXP019-ONBOARD-001/test_logloss_comparison.png)、独立 DOCX (source asset outside this public snapshot)、Living v0.20 (source asset outside this public snapshot)。 |

## 原件、恢复依赖和未运行项

- 用户提供的 Passport v0.2、016 原报告与基础 Living v0.17 在 `/Users/rui/Downloads/INTERNAL_COORDINATION_COMPLETE_HANDOFF_20261002.zip` 原件；EXP017/018 的计划、失败、六源派生状态、父 checkpoint、Living v0.18/v0.19 仍在各自原目录，不复制或改写。
- Open Targets 官方固定 [26.06 历史目录](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/) 的 12 条 `evidence_*` 表是 raw 原件；每表精确 URL/实际 schema 见 source_support.json (source asset outside this public snapshot)。外部路径可读取不等于本地或异地备份。
- 终端 cohort 和六源恢复见 [EXP017 关账](../EXP017/CLOSEOUT.md)；本轮 frozen checkpoint 必须配合其各自 seed 原 checkpoint 和本轮 CGC 导出状态 (source asset outside this public snapshot)。本轮新状态仅各存一份，不造重复 raw/evidence ZIP/保存点别名。
- EXP018 的 `STOPPED_AFTER_PREFLIGHT / NOT_IDENTIFIABLE` 不被本轮改写；其 ClinGen/G2P/Orphanet 在本轮统一门中仍未通过，但不能把覆盖不足当成模型性能或来源价值裁决。
- 未运行：其余 11 源统计或神经模型、从零全七路训练、独立 cohort/time-locked confirmation、前瞻/临床验证、因果结论、全仓门和非必要哈希。M0/M1 train OOF 未完整外层嵌套；validation 是更干净的增量比较。已看 test 永远不能倒称 unseen confirmation。

后继只登记为计划：当前 cohort 不再硬扩其余 11 源；若要确认 CGC 小幅增量或评估历史转译，另立新 ID，先固定 decision-date 时间锁或外部/新 cohort，再做独立评估。现阶段无新增自动训练授权。
