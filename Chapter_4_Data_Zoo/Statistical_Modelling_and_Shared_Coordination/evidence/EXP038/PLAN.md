# EXP038 — MyGait 10mSlow 全队列双足 IMU 数值资格

研究 ID `STAT-PSYMOE-EXP038-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP037](../EXP037/CLOSEOUT.md)。新科学问题：官方 MyGait `1_10mSlow` 的 PD44/健康45 **全部89名路径参与者**中，实际有多少人能提供人级双足、有限六轴与有效时间序列，从而足以进入真实 PD/健康统计问题？EXP037 两份结构预检不能替代全队列门；EXP036 文件名门仍保持停止。

## 来源、假设与竞争解释

固定原件为 [Zenodo v1](https://zenodo.org/records/15672744) 单 ZIP、其 `cc-by-4.0` 元数据及 EXP036 任务交集路径表 (source asset outside this public snapshot)。EXP037 证实固定两人有 CSV 内两足。可能多数人也合格，或存在单足、短记录、缺轴、无效时间/数值而不支持后续人级模型。两种结果决定是否建立本任务的统计基线。

## 冻结单位、门和分析

- 原始单位为人，目录组别加其原始文件 ID 唯一标识；每人一份 `1_10mSlow` CSV。EXP037 PD01/HC01 已核且以原位审计结果引用；本轮读取剩余87名的原 ZIP 条目，不产生原始副本。压力 `p_...` 全部排除。
- 每人合格要求：原件可读；`foot` 仅清楚的 `left/right` 或 `L/R` 两侧（大小写无关）；左右各≥500行；`timestamp` 每侧全部有限并严格递增；`acx/acy/acz/gyrx/gyry/gyrz` 六轴每行均有限。只审结构/数值资格，时间间隔分布描述但**不据未明单位推断50 Hz达标**。不以有多试次当独立人。
- 队列来源门：PD44中至少36名、健康45中至少36名达到个人规则，即各组至少80%；组别/文件 ID 解析必须覆盖固定89路径且不重复。否则 `STOP_NUMERIC_SOURCE`，不训练。通过记 `COHORT_SOURCE_PASS`，仍不能称临床确认、外部验证或模型效果。
- 先记录每人的失败原因和各组统计，再判门；缺失不记为0，失败不删除。技术网络错误与科学数值失败分开报告，不会把访问异常冒充缺足。若网络错误使门不可裁决则 `SOURCE_ACCESS_INDETERMINATE`。

## 预算、状态与输出

1次4 MiB中央目录 Range，加剩余87人各1次≤1 MiB 条目 Range；**最多88次源请求、≤25 MiB压缩响应**。不下载约500MB整 ZIP，不保存原始 CSV。借用 EXP037 原位读取程序，不另复制源码。无模型、无种子、无状态继承；下一模型问题必须再立新 ID。结果保存在本目录 `SOURCE_ROWS_001.jsonl`（仅新87人的派生诊断）、`GROUP_SUMMARY.json`、`WORKLOG.md`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`；原始数据仅用 Zenodo URL 和成员路径引用。局部验证核固定89路径/分组、派生计数和门逻辑；不做全仓门与非必要哈希。
