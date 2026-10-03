# EXP025 PADS 真实个体多通道建模资格审计

研究 ID `STAT-PSYMOE-EXP025-20261002-001`；2026-10-02；`EXPLORATORY`；父阶段 EXP024 后的用户授权自主转向。当前 FDA indication-specific drug translation 分支因 EXP023/024 来源识别门停止而暂停；EXP022 的监管事件产品保留原位且资格不改。

## 科学问题与竞争解释

[PhysioNet PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 是 2018–2021 门诊横断面观测：官方说明 469 名参与者，神经科医师确认 PD / differential diagnosis / healthy control，左右腕传感器完成 11 项动作并有非运动症状问卷。本轮问：其公开原件能否按**独立人**将诊断 outcome、左右腕动作通道与问卷通道准确对齐，并在排除诊断/临床结论泄漏字段后建立可复现、具有足够人头支持的建模 cohort？不是 longitudinal progression、治疗反应或临床诊断工具资格。

H1：原件按 subject ID 可唯一连接，三类诊断与左右腕/问卷通道有足够真实个体支持，能继续到传统统计→Stat-MoE→Shared Ganglion 的渐进比较。H0：通道缺失、诊断类别含混、预处理标签泄漏或独立人头不足使该架构问题不可识别。无论结果都会决定是否投入大体积时序源与后续模型。

选择 PADS 而非 [UCI Parkinsons Telemonitoring](https://archive.ics.uci.edu/dataset/189/parkinsons%2B)：PADS 有 469 名独立人、两腕和问卷；UCI 仅 42 人且按其官方说明 UPDRS 在密集语音记录间线性插值，不适合把 5,875 行当独立真实 outcome。PADS 是横断面，不提供真实未来进展/随访；当前研究只探个体级诊断通道。PADS v1.0.0 公开页标 CC BY-NC-SA 4.0；本轮只本机研究、存路径和派生审计，不发布原始文件或训练产物。

## 来源及单位

- 原件固定为 PhysioNet PADS v1.0.0 的 `patients/patient_###.json`、`movement/observation_###.json`、`questionnaire/questionnaire_response_###.json` 和 `preprocessed/file_list.csv`，以及必要的单条原始 sensor 文件。HTTP 内存读取，不保存/复制原始 JSON/CSV/时序、源码或 ZIP；保留官方 URL、版本、状态和派生字段统计。主分析单位 subject ID 001–469，不把动作切片、两腕或同一人的重复任务当独立样本。
- Outcome 只从 patient 原件的 `condition` 和必要的官方组别定义构建；`disease_comment`、`age_at_diagnosis`、ICD/diagnosis、任何以诊断推得的文件名/目录或预处理 target 列不得进入 predictor。问卷 30 项和年龄/性别可作为候选独立通道，运动按任务×腕×传感器分开。预处理 `file_list.csv` 仅作索引/一致性审计，不作盲目训练表。
- 缺失保留为缺失；任务顺序、样本起始振动、时钟归零、部分时长 20.48s 等由来源说明记录。组间人口差异、就诊来源差异与不平衡属于混杂风险，不能用整体准确率自称临床有用。

## 本轮冻结审计与停止门

1. 在任何模型前核公开 license/版本/目录与四类原件可达性。使用目录页或 HTTP 原位数据，审 469 个 subject ID 的 patient、observation、questionnaire 是否一对一；从 observation 统计左右腕和任务记录，不把 missing 充零。预算 ≤50 MiB、≤1,500 小文件 HTTP 请求；遇不可达保留失败并停止扩张。
2. 独立核 `file_list.csv` 的 subject/label 结构并与原件比对至少 25 个固定 ID（001–025，先冻结），发现 label 不一致即 `STOP_IDENTITY`，不以预处理表覆盖患者原件。审计输出派生 `SUBJECT_AUDIT.csv`、`CHANNEL_DIAGNOSTICS.json`；不保留原始健康问卷内容。
3. 资格门：至少 300 个不同人具有明确 PD/DD/HC 组别且每组 ≥50；其中至少 300 人有同 ID 问卷与至少 8 项动作的左右腕源引用；25/25 固定 ID 与 file list 的标签及 ID 关系一致；诊断/治疗后字段全部列入泄漏排除表。任一项不满足即停止，不通过改分母、把任务切片计作新个体或合并 DD 与 HC 凑人头。
4. 若通过，声明 `REAL_MULTICHANNEL_COHORT_READY_FOR_BASELINE_DESIGN`，仅是数据资格。再以新 ID 冻结 person-level train/validation/test、传统统计基线、通道噪声/缺失、group-balanced 指标、是否需要 Stat-MoE、ganglion 增益假设与外部验证。**本轮不训练**，没有模型性能或临床可用性结论。

## 记录、预算和停止

本目录保存 `SOURCE_INDEX.json`、`SUBJECT_AUDIT.csv`（派生存在性/通道计数，不复制原始病人 JSON）、`CHANNEL_DIAGNOSTICS.json`、`LEAKAGE_LEDGER.md`、`WORKLOG.md`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`。每次研究尝试先记 run_id、输入、方法、预算、预期输出和 RUNNING，失败保留。只局部核本研究的行数、主键和固定 25 ID，不全仓门/无关哈希。用户若以后要求发布数据/模型，先处理 CC BY-NC-SA 的具体使用条件；本轮不触发发布。
