# EXP025 PADS 真实个体多通道资格报告

研究 ID `STAT-PSYMOE-EXP025-20261002-001`；2026-10-02；`EXPLORATORY`。**人级来源资格通过**：在官方 [PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 原件中，469 名独立参与者全部可按 ID 连接诊断、30 项非运动症状问卷和 11 项左右腕动作引用；PD 276、鉴别诊断 114、健康 79，均超过预设每组 50 人。固定 25 人的诊断与 file list 25/25 一致；额外固定 25 人×左右腕的一个真实 `Relaxed` 时序 50/50 有 2048×7 数值、无空值或非有限值。`REAL_MULTICHANNEL_COHORT_READY_FOR_BASELINE_DESIGN` 只表示数据可用于设计基线，不表示模型或临床能力。

本选择来自 EXP023/024 的 FDA 当次适应症来源识别停止。PADS 的多个通道和 469 个真实独立人能区分传统统计、source-specific 模型与共享层是否必要。它是 2018–2021 门诊**横断面**数据，不能回答 Parkinson 病程进展；病人时序记录的相对时间归零，不是长期随访。另一候选 UCI Parkinsons Telemonitoring 虽有密集语音记录，但只有 42 人且官方说明每次 recording 的 UPDRS 是插值，不足以把记录数当真实独立 outcome。

来源来自 URL 原件：`patients/patient_###.json`、`movement/observation_###.json`、`questionnaire/questionnaire_response_###.json` 和 `preprocessed/file_list.csv`；每个人的三类 JSON 和 file list 条目均直接检查。全文原件不另存；只保留 URL、状态、派生人级计数、组别和局部原始时序形状。实际读取 cohort 元数据 8,116,344 bytes、50 时序 9,666,412 bytes，均在预设 50 MiB 和请求上限内。进一步读取所有动作信号并训练模型在本轮**未做**。

诊断由官方说明的神经科医生确认，但本轮未证明医生对问卷/手表观测盲法。原件 `condition` 与预处理 `label` 是 outcome，不得入 predictor；`disease_comment` 和 `age_at_diagnosis` 也是直接或诊断后信息，已进 [LEAKAGE_LEDGER.md](LEAKAGE_LEDGER.md)。每人 11 项任务不是 11 个独立样本。后续必须人级划分、train-only 标准化，比较运动单通道、问卷单通道、传统联合基线，再按验证收益决定 Stat-MoE/Shared Ganglion；不因架构预期直接训练。该公开数据的官方许可证为 CC BY-NC-SA 4.0；本轮没有公开发布或上传原数据。
