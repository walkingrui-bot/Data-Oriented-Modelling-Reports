# EXP033 — Si→Ga 普通步行来源转移压力测试

研究 ID `STAT-PSYMOE-EXP033-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_TRANSFER`；父阶段 [EXP032](../EXP032/CLOSEOUT.md)。EXP032 在同一 Si 64人的开发折中有4/5达门；关键未识别问题是该简洁统计信号换原始研究后能否保持。本轮用 **全部 Si 作一次训练**，把 Ga 的47个普通步行受试者整研究留出评估一次。此研究不重开 EXP031（其 Ju 原件源门仍失败），不把 Ga 称作已证实独立人的外部临床确认：官方文件只给研究前缀，没有本轮可核实的跨研究身份链接。

## 来源与锁定

引用 EXP031 的同一份特征表 (source asset outside this public snapshot)、数值审计 (source asset outside this public snapshot) 和 [官方 format](https://physionet.org/files/gaitpdb/1.0.0/format.txt)。Si PD35/健康29、Ga PD29/健康18；两研究总111人各自原始 `_01` 全数满足 EXP031 的冻结19列、≥5000行、时间/有限数值规则，直接引用既有派生，不重复原始文件读取。若组别、精确 person 键、12个有限特征或资格任一不符，`STOP_INPUT`。Ju 不入分析；不得按 Ga 标签挑人或按性能调整特征。

预测器仅为事前固定的12个左右足总力统计；不纳入 study、ID、年龄、性别、UPDRS 或后果字段。Si 训练中位数插补、均值/标准差，Ga 只套用。引用 EXP031 原位相同 L2 class-weighted binary logistic 实现，λ=0.1，最多1次拟合/5,000步；梯度无穷范数<1e-6 才视作收敛。对照为 Si 训练 PD 比率常数。一次性在 Ga 47人上报告宏观对数损失、balanced accuracy、每类召回、confusion 与个人预测；不在 Ga 上选阈值、校准或再拟合。

## 预定门与可解释范围

一次 Ga 整来源留出若同时 `balanced_accuracy≥0.55`、宏观对数损失相对 Si 训练先验改善 `≥0.02`，记 `GA_SOURCE_TRANSFER_OBSERVED`；否则 `GA_SOURCE_TRANSFER_NOT_QUALIFIED`。这是有真实研究差异的**来源转移压力测试**，不是多中心模型确认或可用临床工具。样本小，点估计有不确定性；报告各组支持和原始概率，不以门通过自动升级 Stat-MoE/Ganglion。若失败，下一新问题应诊断研究间分布/协议差异而不能在已看的 Ga 上调参；若通过，下一新问题要核跨研究人独立性与另一个未见来源。

保留一份训练状态、优化诊断、Ga 人级预测、指标和局部复算。没有原始源副本、全仓门、非必要哈希。实际启动前登记 run_id，异常/失败仍关账。
