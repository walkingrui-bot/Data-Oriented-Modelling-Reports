# EXP031 — 三研究普通步行的来源留出统计基线

研究 ID `STAT-PSYMOE-EXP031-20261002-001`；2026-10-02；`EXPLORATORY`；父阶段 [EXP030](../EXP030/CLOSEOUT.md)。新科学问题：在 [PhysioNet GaitPDB v1.0.0](https://physionet.org/content/gaitpdb/1.0.0/) 三项真实研究 `Ga/Ju/Si` 中，用每位受试者**一次普通步行 `_01`**的两足力信号和一个简单统计模型区分 PD 与健康，模型的增量能否在**留出整项研究**时保持？不同研究采集协议与人群可能不同，正是本轮要测的真实 source incompatibility。不是 PADS 腕部模型外部确认，也不回答 serial-sevens 效应。

H1：不引入 study ID 的简洁双足动力学统计量跨三研究均有高于训练类先验的 PD/健康区分价值；H0：来源协议或群体差异使优势不能稳定保持，不能以更复杂 Shared Ganglion 弥补未识别的来源问题。独立数据单位是 `study + subject`；官方没有在此证明跨研究个人身份绝不重叠，所以整研究留出只是来源转移压力测试，**不称独立人外部确认**。

## 来源与前置门

- 只用官方目录、[format.txt](https://physionet.org/files/gaitpdb/1.0.0/format.txt)、[demographics.txt](https://physionet.org/files/gaitpdb/1.0.0/demographics.txt) 的一人一条 `_01`，`Group=1` PD / `Group=2` 健康；路径/Study/年龄/病程量表/UPDRS 等只用于分组或审计，禁止入特征。`_02..._10` 不入模型、不把同人不同 walk 当新样本。若 `_01`、组别或任务语义不明，停止。
- 首先冻结清单并审三个 study 每组人数：总 PD≥80、HC≥60，且每个 study PD≥20、HC≥15，全部独立键唯一且官方 group 与文件名前缀一致。任一不满足 `STOP_SUPPORT`，不读原始大文件。
- 支持门通过后逐人 HTTP 内存读取一次 `_01`，预算 ≤180 请求、≤250 MiB，并发≤6，每文件≤2 MiB；不另存原始 force 文本。要求至少每组/每 study 的 90% 文件可读、19 数值列、时间严格递增且间隔中位数 0.009–0.011s、至少 5,000 行、全有限。源门未过 `STOP_NUMERIC_SOURCE`，不拟合。缺失保留，不剔除使测试人群偏移。

## 固定特征和模型

每人基于第18/19列左右总足力计算 12 个无标签统计量：用正值 `(L+R)` 的该人中位数作归一化尺度；左右各取均值、标准差、P95−P05、超过尺度10%的接触比例（8项）；左右均值差绝对值、中心化左右零滞后相关、合力0.4–3Hz主频、合力0.4–3Hz相对0.4–10Hz功率（4项）。所有公式/阈值在原始数值读取前锁定；不能因留出表现调整频段或任务。求值时 train 两研究中位数插补/均值标准差，holdout 只套用训练状态。普通 `L2` class-weighted binary logistic，λ 固定0.1；数值全批梯度下降收敛 `gradient_inf<1e-6` 或5,000步，不收敛关账工程失败。对照为训练两研究 PD 比率常数。每个 study 轮流独立留出，测试只评一次。

报告三研究各自 macro log loss、balanced accuracy、各类召回、confusion、与先验差。先验决定“有可迁移简单信号”的门：三项留出均 `balanced_accuracy≥0.55` 且模型 macro log loss 比先验至少改善0.02；少一项即 `SOURCE_TRANSFER_NOT_QUALIFIED`，不进入 Stat-MoE/Ganglion。这个探索门只决定工程下一步，不构成临床有效性或跨研究个人完全独立证据。若通过，新 ID 研究协议/群体差异与真正未见人群；若失败，明确来源/统计层问题而非扩大网络。

记录 `COHORT_AUDIT.csv`、`SOURCE_SUMMARY.json`、一份派生 `FORCE_FEATURES.csv`、`SOURCE_AUDIT.csv`、三项模型状态/人级预测、门、报告、关账。每个实质性尝试先记 run_id、预算、输入和 RUNNING；失败保留。只作本轮局部数值/主键/重算检查，无全仓门/非必要哈希。
