# EXP065 — 2024 本地传统统计适应到 2025 自然缺测

研究 ID `STAT-PSYMOE-EXP065-20261002-001`；2026-10-02；`EXPLORATORY_REAL_TEMPORAL_HOLDOUT_STATISTICAL_ADAPTATION`；父阶段 [EXP064](../EXP064/CLOSEOUT.md)未来来源通过。EXP063 北京 N1 在伦敦区域零样本明显不如无拟合 B0。新科学问题：在**同一区域仅用 2024 真实自然缺测配对训练**的普通统计，能否在尚未评分的 2025 同定义任务稳定优于 B0？更具体地，单一水平校准是否足够，还是本地单特征或八特征关系有额外价值？结果决定是否保留本地传统模型，或回退 B0；不能把北京失败归因于模型尺寸。

## 数据与不可变边界

2024 训练样本精确引用 EXP062 (source asset outside this public snapshot)十站 **667** 真缺测配对，2025 时间外评价精确引用 EXP064 (source asset outside this public snapshot)同十站 **589** 对。逐站 counts/单位/状态必须复现原来源记录，否则 `STOP_SOURCE_VERSION_DRIFT`，不拟合、不评分。两年度官方原 CSV 仅内存读取，不复制；GMT 小时结束时钟、明确空 PM(t)、真 t+24h 目标、≥8邻站同刻已核定 PM 语义不变。2024已看过原北京 N1/B0 零样本成绩，是训练/开发数据；2025尚未见任何模型成绩，但已看过来源支持数，因此本实验仍称探索性时间外评价，不称无条件确认或当年实时预测。站×小时相关。

## 固定模型与门，2025评分前

- B0：同刻可见邻站 PM 中位数，**无拟合**；必须在 2024 与 2025 同定义。
- C0：只用 2024 训练真实目标，把原北京 N1 (source asset outside this public snapshot) 的 `log1p` 预测整体加**一个均值残差截距**；原八系数/标准化不变，`max(0,expm1)`输出。它检验简单水平校准，但不代表从2024实时出发。
- M1：本地 `Ridge(alpha=1.0, fit_intercept=True)` 对 `log1p(neighbor_median_t)` 单一特征，以2024 `log1p(PM(t+24h))` 训练；2024 StandardScaler 参数固定到2025，逆变换同上。
- L1：本地同样 ridge/目标，使用 EXP060 原 N1 八特征顺序：邻站 p25/median/p75 的 `log1p`、邻站数、小时 sin/cos、年相位 sin/cos；只从2024 fit StandardScaler 与系数，2025不拟合。特征公式沿 EXP060，闰年也固定分母365.25，不为英国调 alpha。没有站 ID、未来协变量、人工 mask。
- 只将 2024 全部667对用于三个模型拟合，不能用2025选 alpha/特征或调 C0；无需内层模型选择，因为四个候选分别按预定假设报告，若多个通过只报告多个，后续选择需新未见年份。

主指标 2025 原单位 MAE；次指标 RMSE、预测/目标均值、十站逐站 MAE、2024拟合内指标（只描述）。为免多站同日伪独立，以2025**预测起点 GMT 日**为共同区块，1000次 bootstrap（seed20261002），对每候选与 B0 比较绝对误差差均值区间。每个 C0/M1/L1 **分别**达到：总体 MAE 比B0改善≥5%、区块95%区间上界<0、2025至少**6个有≥10对目标的站**逐站MAE较B0改善、任一此类站退化不超过20%，才称 `LOCAL_STAT_CANDIDATE_SUPPORTED`。M1/L1之间另设额外特征价值门：L1相对M1总体MAE改善≥3%、日区块 L1−M1 区间上界<0、≥6/9站 L1优于M1；未过则不能说八特征必要。若任何候选不过门，保留其原始成绩并明确不支持；若全不过，B0是当前任务默认。不得把C0/M1/L1中某个2025赢家再拿同年调优。

尝试 `EXP065-STAT-001` 事前登记，命令 `/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_local_temporal.py`，20官方CSV请求总≤50MiB、CPU≤20分钟；输出 `SOURCE_RECHECK.json`、`MODEL_STATES.json`（仅新拟合状态及原N1路径引用）、`PREDICTIONS.csv`、`METRICS.json`、原输出、局部核验、门/报告/关账。新本地模型状态各仅一份；不复制源文件/旧模型/旧日志，不启 NN/Stat-MoE/Ganglion、全仓门或非必要哈希。

用户在 EXP022 后授权研究自主转向，并要求容量/收益用真实实验及时止损；当前比较可以直接区分简单校准、单变量统计和更多邻站/时间特征是否有可重复的时间外价值，比再调共享矩阵更有决策信息。
