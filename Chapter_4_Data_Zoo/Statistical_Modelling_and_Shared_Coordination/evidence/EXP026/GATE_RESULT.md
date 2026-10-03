# EXP026 冻结多通道增益门

研究 ID `STAT-PSYMOE-EXP026-20261002-001`；2026-10-02。判据于 [PLAN.md](PLAN.md) 事先冻结；M0 先验泄漏修订在任何 EXP026 模型成绩前另记 [AMENDMENT_001.md](AMENDMENT_001.md)。本轮只用 [PhysioNet PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 的真实 469 人、30 项问卷与一个 `Relaxed` 双腕原始任务。独立单位是人；内部锁定 validation 92、test 97。

| 冻结条件 | 观测 | 判定 |
| --- | --- | --- |
| 来源总体 ≥95%、每组三腕/问卷组合 ≥90%；语义结构正确 | 469/469 问卷、observation、左腕、右腕全部读取；0 缺失答案；1,876 请求、189,123,765 bytes；无 schema error | PASS |
| validation M3 相比 M1 的 macro log loss 改善 ≥0.02 | 0.767094−0.700544=+0.066549 | PASS |
| validation M3 相比 M1 的三类 balanced accuracy 改善 ≥0.03 | 0.694949−0.629293=+0.065657 | PASS |
| test M3 相比 M1 的 macro log loss 改善 >0 | 0.855639−0.807638=+0.048002 | PASS |
| test M3 相比 M1 的三类 balanced accuracy 改善 >0 | 0.637605−0.655229=**−0.017624** | **FAIL** |

**总体：`NO_QUALIFIED_ADDED_VALUE_IN_INTERNAL_SPLIT`。**四项增益要求必须同时满足；测试集 balanced accuracy 下降，因此不能称联合动作通道已经稳定提供额外模型价值，也不能据此进入 Stat-MoE/Shared Ganglion。M2 单独动作模型在 test 的 balanced accuracy 0.455299、macro log loss 1.164297，低于 M1；M0 类别先验的 test balanced accuracy 0.333333。M1/M2/M3 所有 12 个 validation 候选与 3 个最终拟合共 15/15 数值收敛；选定 λ 分别 0.1、0.01、0.1。测试只评一次，未因其结果换特征、split 或 λ。

本门失败属于**泛化/稳定性层**：同一中心的小保留集里，概率质量有改善但 hard-class 三类召回未保持。97 名 test 中 HC17、PD56、DD24；M3 相比 M1 的 test 召回 HC 0.8235 vs 0.8824、PD 0.5893 vs 0.6250、DD 0.5000 vs 0.4583。不能由此推出所有运动任务无效，也不能推出 PADS 适合临床诊断。下一独立问题应先查这个矛盾是否为小组别的分割波动或单任务信号不稳定；已看的 test 不能变成新确认集。
