# EXP026 — PADS 人级双通道统计基线

研究 ID：`STAT-PSYMOE-EXP026-20261002-001`；2026-10-02；`EXPLORATORY`；父阶段 [EXP025](../EXP025/CLOSEOUT.md)。本计划在任何 EXP026 模型特征/性能计算前冻结。EXP022 的 FDA 来源语义层保留，EXP023/024 的适应症来源停止不改；当前 drug indication 分支暂停，因为两个固定同次标签门没有获得合格来源。PADS 人级来源门通过，使一次真实多通道统计比较比继续寻找牵强药物代理更能决定架构工作。

## 问题、假设与可反证结果

在 [PhysioNet PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 的 469 位真实受试者中，问卷与**单个双腕静息任务 `Relaxed`** 是否提供可互补的横断面 PD / differential diagnosis / healthy control 组别区分信息？独立单位是人，三类定义沿用 EXP025。H1：简单的问卷+双腕联合统计模型在锁定验证集比问卷单独模型改善，且一次锁定测试不逆转。H0：该动作任务没有提供稳定额外价值；此时不启动 Stat-MoE 或 Shared Ganglion。一个任务的无增益不证明其余 10 个任务无用；即使改善也不证明临床诊断或外部可迁移。

本实验比较 M0 训练集类别先验常数、M1 30 项非运动问卷、M2 双腕 `Relaxed` 摘要、M3 问卷+双腕摘要。M1–M3 用同一类带 L2 正则的 class-weighted multinomial logistic regression，不以神经网络代替统计基线。所有模型均真实数据、真实缺失、无合成科学样本。后续是否建立多任务 motion branch 或共享层依结果另立 ID，不能在此轮看过 test 后再改特征/模型。

## 来源、泄漏与特征锁

- Outcome 沿用 EXP025 官方患者原件 `condition` 的映射：Healthy→HC(0)，Parkinson's→PD(1)，四类其他诊断→DD(2)。`SUBJECT_AUDIT.csv` 仅供人级索引与 split；问卷及 `Relaxed` 左右腕时序直接在官方 URL 内存读取，原始响应不另存或打包。冻结版本 1.0.0、URL pattern 与每次 HTTP/形状账。
- 30 个问卷问题仅按固定 `link_id=01..30` 编码：False=0，True=1，缺失=NaN，缺失标志另列。只在训练集计算每项中位数并填充；保留真实缺失数量。不得将问题文本、ID、文件名、组别、病名、诊断备注、`age_at_diagnosis` 或预处理 label 当 predictor。年龄/性别只在结果中描述，不进入本轮模型。
- 仅 `movement/timeseries/{id}_Relaxed_{Left|Right}Wrist.txt`，按原件 `observation_###.json` 验证引用、sampling_rate=100、通道顺序为 Accel XYZ / Gyro XYZ。每份 CSV 首列时间、后六列数值；不用时间值、源路径或 subject ID 作特征。各腕对 3D accel/gyro 的模长各算均值、标准差、5–95%跨度、相邻差平方根均值，以及中心化六轴在 3–7 Hz 相对 0.5–15 Hz 功率的 accel/gyro 均值。共每腕 10 个特征，另加对应左右绝对差 10 项，共 30 项。没有参数从 test 拟合。若原件列语义不符，先停止并记失败，不能按性能改解释。
- 原始时序若 HTTP/shape 错误或包含 NaN/非有限，保留人级真实缺失并记录；运动模型在同一 469 人上使用训练集中位数插补+缺失标志，不能静默剔除测试人。若任一组运动源可读率 <90% 或整体 <95%，`STOP_SOURCE`，不拟合模型；阈值在读取前冻结。

## 划分、模型与冻结判据

- 从 EXP025 469 人审计表按三组分层，组内先按 ID 排序，再用 Python `random.Random(20261002).shuffle`；每组 train=`floor(0.60*n)`、validation=`floor(0.20*n)`、test=余数。一次写出 `SPLIT_MANIFEST.csv`，其中 ID 只作连接键。各人最多一行，任何腕/任务都不能跨 split。
- M1/M2/M3 按同一流程：train-only 中位数插补、train-only 均值/标准差缩放；类别权重为训练人数除以 `3*n_class`；正则 λ ∈ {0.01, 0.1, 1, 10}，仅通过 validation **macro log loss** 最小选择，平局选较大 λ。数值优化用确定性全批 softmax 梯度下降与 backtracking，目标收敛 `gradient_inf <1e-6` 或 5,000 步，未收敛报告而非伪装成功。选 λ 后以 train+validation 重拟合一次，锁定 test 只评估一次。M0 用 train+validation 类别先验。
- 主要报告 validation 与 test 的 macro log loss、macro balanced accuracy（3 类召回平均）、各类召回、confusion matrix；M0 同列。主要增量 M3−M1：loss 改善=`loss(M1)-loss(M3)`，balanced accuracy 改善=`BAcc(M3)-BAcc(M1)`。事先决策：validation 两指标须分别 ≥0.02、≥0.03，且 test 两指标均 >0，才称**观察到联合通道额外价值，值得新实验探更完整 motion 与共享结构**。否则本任务不支持添加复杂架构。由于样本量与单中心同次采集，test 仍只是一次内部保留集，不能称外部确认。
- 解释竞争方案：若 M2 优于 M1 而 M3 不改善，说明简单联合/小样本可能不足，下一实验可研究多任务或非线性，但不能在本 ID 改模型。若 M3 改善，下一实验先研究多任务稳定性与 source-specific 统计，再评估 Stat-MoE，只有跨通道剩余共同信息才考虑 Ganglion。

## 预算、尝试与停止

最多读取 469 问卷 JSON、469 observation JSON、938 个 `Relaxed` 腕文件；原位响应累计 ≤250 MiB，≤2,000 请求，并发 ≤12；不复制原始信号或完整问卷。新目录保存唯一一份派生 `FEATURES.csv`、`SOURCE_AUDIT.csv`、`SPLIT_MANIFEST.csv`、程序、数值结果及必要人级预测（不含原始源内容）。开发/数值单元测试仅用小合成数组，不作科学证据。运行前 WORKLOG 登记 run_id、配置、输入、预期输出和 RUNNING，异常/失败保留。局部验证限本轮 split、字段、泄漏、输出数值、可重现性；不运行全仓门或无关哈希。
