# EXP032 Si 内部足底力统计信号报告

研究 ID `STAT-PSYMOE-EXP032-20261002-001`；2026-10-02；`EXPLORATORY_RETROSPECTIVE_DEVELOPMENT`。EXP031 的三研究来源门因 Ju PD 可读率不足而停止，故本轮另立较窄科学问题：一个完全满足原数值规则的 Si 研究中，**事前固定**的12个双足力统计量是否比训练人群的类先验有稳定区分价值？Si 来源原件来自 [PhysioNet GaitPDB v1.0.0](https://physionet.org/content/gaitpdb/1.0.0/)，官方 [format.txt](https://physionet.org/files/gaitpdb/1.0.0/format.txt) 将 `Si`、`_01` 和双足总力列分开定义。本研究只引用 EXP031 派生特征原件，没有复制原始力或重读大文件。

64 人（PD35/健康29）全数进入五次分层人级5折。每折仅训练其他人，固定 class-weighted L2 logistic λ0.1；训练折的类比例常数为对照。25/25次拟合收敛。宏观对数损失的模型相对先验改善分别是 +0.03776、+0.05323、+0.05962、+0.02707、**−0.01632**；相应 balanced accuracy 为0.69064、0.71084、0.65320、0.70788、0.64187。事前至少4/5同时过两幅度门，本轮恰为4/5，故看到 **Si 内部开发信号**，同时第五次的损失变差提示分折敏感性。

这不是独立确认：五次只是同64人的不同折分配，且 Si 研究本身是单中心/单任务来源。研究未解决 Ga 或 Ju 的协议差异、潜在跨研究个人重叠，也未评估跨研究 holdout。传统统计模型已给出可观察的内部信号，没有理由此时用 Stat-MoE/Ganglion 替代它。下一项新 ID 的最大信息增益是固定该模型对已合格且**从未用于本轮拟合**的 Ga 研究做一次来源留出压力测试；若增量不保持，应调查来源可比性，而不是从 Ga 结果调阈值或网络。

人级 OOF、折、拟合状态和六项局部复算分别见 PREDICTIONS.csv (source asset outside this public snapshot)、SPLITS.json (source asset outside this public snapshot)、[OPTIMIZATION.json](OPTIMIZATION.json)、[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)。无全仓门或哈希。
