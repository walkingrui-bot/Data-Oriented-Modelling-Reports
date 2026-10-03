# EXP025 PADS 人级多通道来源门

事先判据见 [PLAN.md](PLAN.md)。官方 [PhysioNet PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 原件按 URL 在内存读取，未保存原始 JSON/CSV/时序副本。`SUBJECT_AUDIT.csv` 是只含派生存在性、诊断组与通道计数的人级审计，不是原件复制。

| 冻结条件 | 实测 | 判定 |
| --- | --- | --- |
| ≥300 独立人且 PD/DD/HC 每组 ≥50 | 469 唯一 ID；PD 276、DD 114、HC 79。DD 由官方 label=2 的 Other Movement Disorders 60、Atypical Parkinsonism 15、Multiple Sclerosis 11、Essential Tremor 28 组成。 | PASS |
| ≥300 人有同 ID 问卷及 ≥8 项左右腕源引用 | 469/469 有 30 项问卷与 11 项左右腕动作引用；所有 ID 的 patient、observation、questionnaire 原件 HTTP 可达且 ID 相等。 | PASS |
| 固定 001–025 与 file list 的 ID/诊断相符 | 25/25；全表 `condition` 与 file list condition 469/469 相等；官方 file list label 映射 Healthy=0、PD=1、四 DD 类=2。 | PASS |
| 诊断与诊断后字段列入泄漏排除表 | [LEAKAGE_LEDGER.md](LEAKAGE_LEDGER.md) 明列 `condition`、`label`、`disease_comment`、`age_at_diagnosis`、subject ID/路径等禁止 predictor。 | PASS_DOCUMENTED |

附加局部源真值 QA：固定 25 人的 `Relaxed` 左右腕原始时序共 50/50 可读，各为 2048 行、7 个数值列、无空或非有限值。只验证这 50 个文件，不声称其它 10 项任务的全部 469 人原始数值文件已核。CHANNEL_DIAGNOSTICS.json (source asset outside this public snapshot) 与 TIMESERIES_QA.csv (source asset outside this public snapshot) 是直接证据。

结论：`REAL_MULTICHANNEL_COHORT_READY_FOR_BASELINE_DESIGN`。PADS 是神经科医生确认的**横断面**组三分类与同次多通道观测，按 person 作为唯一独立单位。通过来源门不等于模型性能、外部泛化、临床诊断有效性或真实疾病纵向进展；这些均未测试。公开页显示 CC BY-NC-SA 4.0，本轮只本机研究和路径引用。
