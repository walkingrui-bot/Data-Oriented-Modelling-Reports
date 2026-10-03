# EXP027 — PADS 双通道增益的开发集划分稳定性

研究 ID：`STAT-PSYMOE-EXP027-20261002-001`；2026-10-02；`EXPLORATORY` / `RETROSPECTIVE_DEVELOPMENT_DIAGNOSTIC`；父阶段 [EXP026](../EXP026/CLOSEOUT.md)。EXP026 锁定 test 已看，且其 balanced accuracy 增益门失败，不改原门，不把新分析称 confirmation。当前问题是：M3 联合问卷+单项双腕 `Relaxed` 在原开发人群内的增量是否对人级划分稳定，还是一次 validation 划分波动？独立观测单位仍是人；五次重复不是五倍人数。

## 来源和竞争解释

仅引用 EXP026 唯一派生 FEATURES.csv (source asset outside this public snapshot) 与 SPLIT_MANIFEST.csv (source asset outside this public snapshot)。排除原 `test` 97 人，开发集 `train+validation` 372 人（HC62、PD220、DD90）。不重新下载 PADS 原件、不复制原始问卷/时序、不另存特征副本。若 M3 的相对增益在多个重新划分中稳定，单次 EXP026 test 的三类召回反转可能与小组样本阈值敏感有关，工程下一步是寻找新的外部人员/中心资格，而非调旧 test；若不稳定，则停止为一个静息任务开发共享架构，优先检查更有生理意义的其他真实任务或独立数据。两种结果都会改变下一投入。

H1：联合特征在开发人群多数分割下同时改善宏平均概率损失与三类平均召回。H0：增益主要在概率校准或特定分割出现，三类硬决策不稳定。只有开发集内部的探索性证据，不能推翻 EXP026 test 失败或支撑临床能力。

## 冻结方法、预算与门

- 固定五次重复 seed `20261003` 至 `20261007`，每次按三组人级分层：每组排序 ID 后用 Python `random.Random(seed).shuffle`，按顺序循环分配 fold 0–4。每人每次只在一个 fold 的 out-of-fold 验证侧；腕和任务不另计样本。记录 `FOLD_MANIFEST.csv` 的 372×5 派生划分。
- 只比较 EXP026 事前模型 M1 问卷与 M3 联合，完全沿用 EXP026 30 问卷、30 静息动作、缺失标志、fold-train 内插补/标准化和 class-weighted L2 multinomial logistic。两臂 λ **固定 0.1**，取自 EXP026 在未看其 test 前的 validation 选择；不在 EXP027 再选参。每臂每折拟合一次，共 50 fits。达到 `gradient_inf<1e-6` 或最多 5,000 步；未收敛完整记录并视为 `STOP_ENGINEERING`，不能为结果补调。
- 每次重复汇总其 372 人 out-of-fold 概率，算 macro log loss、三类 balanced accuracy。五次重复分别比较 M3−M1；另记 25 个 fold 配对差，但 fold 并非独立验证样本。冻结稳定性门：**至少 4/5 次**重复同时满足 loss 改善 ≥0.02 和 BAcc 改善 ≥0.03，并且剩余重复的两指标都不得为负。若不过门，不推进该静息任务的 Stat-MoE/Ganglion；即使过门，仍只能说开发集划分稳定，应另找未见人群/中心，EXP026 test 不能重用为 confirmation。
- 不读取已见 test 的特征值或预测以作模型优化；程序仅从 split manifest 选原 train+validation。可保留参考 EXP026 已公开的失败数值作为研究动机，不以它选本轮 seed、lambda 或阈值。M0/M2 不重训；问题只诊断 M3 相对 M1。

输出 `FOLD_MANIFEST.csv`、`FOLD_METRICS.csv`、`REPEAT_METRICS.csv`、`OOF_PREDICTIONS.csv`、`OPTIMIZATION.json`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`。`OOF_PREDICTIONS.csv` 保存派生人级概率而非原始传感器。预算 50 小模型，单机 CPU ≤10 分钟；超时/异常保留现场，不能静默缩减重复数。只做本研究行数、fold 唯一性、结果重算局部检查；无全仓门/哈希。
