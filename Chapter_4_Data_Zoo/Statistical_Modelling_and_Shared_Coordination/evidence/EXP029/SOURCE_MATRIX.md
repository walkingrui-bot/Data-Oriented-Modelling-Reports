# EXP029 官方外部来源语义矩阵

2026-10-02；只读官方托管页/官方数据访问页，无源文件下载。`UNKNOWN` 表示本次页面未证明，不代表实际不存在；人数均为页面所述**人**而非测量记录。直接 M4 外部资格要同时有非 PADS 独立人、PD≥30/DD≥20/HC≥20、同构 NMS30、同步双腕 accel+gyro、心算静息任务、明确协议和当前可许可访问。

| 官方来源 | 人级 outcome / 数量 | 问卷、传感器与任务 | 访问/许可状态 | 直接 M4 判定与决定性缺口 |
| --- | --- | --- | --- | --- |
| [PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) | PD276/DD114/HC79；EXP025 原件核过 | NMS30、双腕加速度+角速度、`RelaxedTask` serial sevens | 官方 CC BY-NC-SA 4.0，原位可读 | **REFERENCE_ONLY**；与开发同一人群，不是外部来源 |
| [PPMI 官方访问页](https://bank.ppmi-info.org/access-data-specimens/download-data)、[仪表板](https://www.ppmi-info.org/access-data-specimens/data) | 官方仪表板呈 PD/Prodromal/HC 等总体 enrollments，**非本任务通道交集人数**；与 PADS DD 标签不等价 | 官方称有临床、sensor 和多种信息；NMS30 同构、双腕、同一心算静息任务的逐人交集 **UNKNOWN** | 个体级数据须签 Data Use Agreement、在线申请、审核/登录；本轮无授权、不访问 | **NOT_DIRECT**：受控访问；目标组/协议同构未证实。不能把仪表板总数当符合 M4 的人头 |
| [Monipar Zenodo v1](https://zenodo.org/records/8104853) | 21 PD、7 HC，页面未列 DD | 一只 smartwatch 三轴加速度 50 Hz、8 种运动练习；NMS30/双腕/相同心算任务未由页面证实 | 页面标数据开放，但当前解析出的 Rights/License 栏未给清晰许可证文本，记 UNKNOWN | **FAIL_SAMPLE_AND_PROTOCOL**：PD<30、HC<20、无 DD；不拿周重复次数增加人头 |
| [BIOCLITE Zenodo v2](https://zenodo.org/records/20644246) | 24 PD、16 HC，未列 DD | smartwatch 三轴加速度与陀螺仪 50 Hz、8 练习及监督/非监督日重复；NMS30/双腕心算未证实 | 页面标数据开放；当前解析 Rights/License 具体文本 UNKNOWN | **FAIL_SAMPLE_AND_PROTOCOL**：PD<30、HC<20、无 DD；日重复不是新个体 |
| [ALAMEDA Zenodo v1](https://zenodo.org/records/15769959) | 11 PD，无所需 HC/DD；长达一年重复监测 | 腕部三轴加速度 100 Hz 与临床量表；没有页面支持双腕陀螺仪或相同心算任务 | 页面标数据开放；具体许可证文本 UNKNOWN | **FAIL_SAMPLE_AND_TARGET**：PD<30 且另外两组缺；虽有真实纵向观测，不能拿来外部验证组三分类 |
| [UCI Daphnet Freezing of Gait](https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait) | PD 人群中的 freeze/no-freeze**事件**任务；页面 237 instances 不能读成237独立人 | 传感器在小腿/大腿/躯干，只读三轴加速度；无 PADS 双腕心算/问卷语义 | CC BY 4.0 官方页可见 | **DIFFERENT_OUTCOME**：逐段 freezing label，不是 PD/DD/HC 人级诊断 |
| [PhysioNet Gait in Parkinson's Disease v1.0.0](https://physionet.org/content/gaitpdb/1.0.0/) | 93 PD、73 HC，三项研究；未列 DD | 足底 16 个力传感器 100 Hz，部分人有 serial sevens 步行第二任务；无双腕 accel+gyro，NMS30 未由页面证实 | 官方 Open Data Commons Attribution v1.0，开放访问 | **PARTIAL_SCIENTIFIC_ANALOGUE, NOT_DIRECT**：有独立真实人和认知负荷对照，但传感器/活动、问卷、组三类目标不同；可支持新科学问题，不能确认 M4 |

同一候选的未证实字段不能用推断补齐。`DIRECT` 合格数 **0/6 外部候选**（PPMI、Monipar、BIOCLITE、ALAMEDA、Daphnet、GaitPDB）；本结论限上述官方页面和本轮时间，不宣称全球不存在合格 cohort。未点击下载、未申请 PPMI 凭据/授权、未触及私有数据。若未来有 PPMI 许可与同构 schema 或新独立数据，须新 ID 重新审 gate。
