# EXP018 停止关账与原件索引

- 执行：`STOPPED_AFTER_PREFLIGHT`，按 [PLAN.md](PLAN.md) 的样本停止条件关闭当前 cohort 的冻结接入尝试。
- 工程：`VALID_DIAGNOSTIC_ONLY`，固定 release 三原表和旧保存点结构可读，原 cohort 分布被实际计算；九路训练链未建成。
- 科学：`NOT_IDENTIFIABLE`，并集 train 11 / validation 4 pair 全为阴性，不能判别新增三源的正向预测贡献；不推断 frozen onboarding 的性能，也不推断三源医学价值。

## 尝试账

| Run ID | 状态 | 原件 |
| --- | --- | --- |
| `EXP018-PREFLIGHT-001` | `COMPLETE` | preflight.json (source asset outside this public snapshot)、[preflight.py](preflight.py)；三原表 schema/footer，旧三保存点参数结构。 |
| `EXP018-NATIVE-DIAG-001` | `COMPLETE_WITH_SEVERE_SPARSITY` | native_diagnostics.json (source asset outside this public snapshot)、[native_diagnose.py](native_diagnose.py)；只留 cohort 聚合类别与计数，原 raw 不复制。 |
| `EXP018-SUPPORT-001` | `COMPLETE / STOP_TRIGGERED` | cohort_support.json (source asset outside this public snapshot)、[cohort_support.py](cohort_support.py)；三源的原 split 标签分布。 |
| Frozen new-interface / full nine-source retrain / performance controls | `NOT_RUN` | 训练未启动，无模型、曲线、指标或检查点；不得补写为失败性能。 |

用户资料原件为 `/Users/rui/Downloads/INTERNAL_COORDINATION_COMPLETE_HANDOFF_20261002.zip`，其中 Passport v0.2 和 016 报告只作来源。三条原表在 [Open Targets 官方 26.06 历史目录](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/26.06/output/) 的 `evidence_clingen/`、`evidence_gene2phenotype/`、`evidence_orphanet/`；EXP017 原 cohort、split、checkpoint 和结果见[父阶段关账](../EXP017/CLOSEOUT.md)。官方 URL 是原件路径引用，不称本地备份；本阶段未复制原始证据或创建重复交付包。

阅读交付：独立 DOCX 报告 (source asset outside this public snapshot)、Living Report v0.19 (source asset outside this public snapshot)、[诊断图](cohort_support.png)。新 Living Report 追加本次 `NOT_IDENTIFIABLE` 章节；v0.18 仍在 EXP017 原目录，不覆盖。

本轮局部验证了三表 schema/footer、原 cohort 限定计数/词值、三旧保存点参数键和 target split 标签分布。没有运行模型或全仓门、没有计算非必要哈希。后继若修改 terminal cohort/outcome 或改选新增来源，应另立研究 ID 并使用独立切分；不得把 EXP017/018 已看过的 test 写成未见确认。
