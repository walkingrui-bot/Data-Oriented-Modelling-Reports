# EXP069 — 独立受试者上的陀螺仪增量：先测传统统计

研究 ID `STAT-PSYMOE-EXP069-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_PERSON_HOLDOUT_STATISTICAL_TEST`；父阶段 [EXP068](../EXP068/CLOSEOUT.md)来源门已通过。用户在 EXP022 后授权自治研究，并要求用实际结果及时止损。科学问题：在真实受控活动识别中，**陀螺仪**是否在加速度计之外提供跨受试者、可保持且足以抵偿第二传感器成本的预测增量？这个结果决定是否有理由进一步比较 Stat-MoE / Shared Ganglion；不因神经结构存在就跳过统计。

## 固定原件、单位和特征

官方 [UCI240 数据](https://archive.ics.uci.edu/dataset/240/human%2Bactivity%2Brecognition%2B)：30人、六类；官方 train21人7352个重叠128点窗、test9人2947窗。每窗六个已预处理三轴信号：`total_acc`三轴、`body_gyro`三轴。仅从这六个信号按确定公式各抽11个窗内特征：mean、std、10/50/90百分位、RMS、max−min、平均相邻绝对差、lag-1 Pearson相关（零方差时定0）、去均值实FFT在[0.4,3)Hz和[3,10)Hz的频谱能量占总非零频能量比例（分母零时定0）。共每模态33、联合66维；不使用561个发布衍生特征、subject ID作预测因子或前后窗口上下文。特征是发布预处理窗的统计摘要，不冒充连续原始信号。

**人**是独立评价单位，窗口只是一个人内相关测量。训练/测试必须保持官方人级不相交；训练21人的ID升序依次分配到5个fold（index modulo 5），得到人级OOF。每个模型各fold只在其训练人上拟合 `StandardScaler` 和 `LogisticRegression(C=1, penalty=L2, solver=lbfgs, max_iter=500, random_state=20261002)`；不调C或特征。三个固定模型：ACC加速度33维（主基线）；GYR角速度33维（辅助）；JOINT拼接66维（候选）。另报训练先验常数概率作为无传感器参照。拟合失败或未收敛报告失败，不事后换优化器。

## 先开发门、后一次独立test

主指标为每人六类多分类负对数似然的窗均值，再对人等权平均。第二主指标为每人六类平衡准确率，再对人等权平均；所有人应具六类，否则停止。定义差值 `JOINT−ACC`（logloss越负越好，BAcc越正越好）。按受试者成对重抽2000次、seed20261002，报告 logloss 差95%百分位区间。先在21人OOF算门：Δlogloss≤−0.03、ΔBAcc≥+0.02、logloss区间上界<0、至少14/21人 logloss改善。未全过即 `STOP_JOINT_DEV_GATE`，不在本ID评分官方test，不测试Ganglion。全部过后，在全train拟合固定三模型，并**仅一次**读取test性能：test9人须 Δlogloss≤−0.03、ΔBAcc≥+0.02、logloss区间上界<0、至少6/9人logloss改善；全部过才称 `REAL_HAR_GYRO_INCREMENT_SUPPORTED_WITHIN_PROTOCOL`。否则 `NO_INDEPENDENT_PERSON_HOLDOUT_INCREMENT`；旧开发现象仍留档。test后不调模型、特征或门槛；若新结构问题再另ID。

来源版本门在任何拟合前：重新读取官方原件且train/test人、窗、六信号宽度、逐类人/窗、测试人不交叉与 EXP068 `SOURCE_MATRIX.json`完全一致；不一致 `STOP_SOURCE_VERSION_DRIFT`。EXP068 已看test类别支持但未看性能。当前test性能尚未计算；本实验是探索性外部人留出，不是独立实验室/设备确认。

## 运行与预算

唯一预登记尝试 `EXP069-STAT-001`，命令 `/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_har_stats.py`；原件内存读取不落地ZIP/信号副本。≤70MiB下载、≤1GiB内存、≤30分钟CPU、OOF三模型各5拟合、若过开发门追加3拟合，0随机参数搜索。保存派生 `SOURCE_RECHECK.json`、`OOF_METRICS.json`、`OOF_PERSON_ROWS.csv`、若开发过门则 `TEST_METRICS.json`/`TEST_PERSON_ROWS.csv`；不保存原始窗口副本。仅局部脚本/结果验算；不运行全仓测试或非必要哈希。若所有门失败，转向更有信息增益的新科学问题，当前传统 ACC 留作已测基线，不能以“模型小”为未经验证的原因。
