# EXP027 PADS 单静息任务增益稳定性报告

研究 ID `STAT-PSYMOE-EXP027-20261002-001`；2026-10-02；`EXPLORATORY_RETROSPECTIVE_DEVELOPMENT`。EXP026 在 469 位真实 PADS 受试者上显示联合问卷+双腕静息信号改善 validation 宏平均概率损失和三类平均召回，但在已锁 test 只保持 loss 改善，balanced accuracy 下降。新问题是开发人群中的增益是否对人级重新划分稳定；这不会把已看 test 重新变为确认。

本轮只引用 EXP026 的一份派生特征表与 split 索引，排除 test97，在 train+validation 共372人上用预设五个 seed 各做五折 stratified person OOF。M1/M3 均固定 λ=0.1，沿用 train-fold 内插补/缩放和 class-weighted multinomial logistic。没有重新下载原时序、没有重新挑特征、没有根据旧 test 调参。50 个实际拟合全部收敛；每人每次重复仅有一条每模型 OOF 预测，原 test 97 人未进入输出。详细行级在 `FOLD_MANIFEST.csv`、`FOLD_METRICS.csv`、`OOF_PREDICTIONS.csv` 和 `OPTIMIZATION.json`。

五次 M3−M1 的宏平均 loss 改善依次 +0.037411、+0.022001、+0.035124、+0.045482、+0.042648；balanced accuracy 改善 +0.040067、+0.028429、+0.010470、+0.065108、+0.065950。两指标每次均为正，但**只有 3/5 次**同时超过事前 +0.02 loss/+0.03 BAcc 门，未达到要求 4/5 的 [稳定性门](GATE_RESULT.md)。这与 EXP026 单次 test 的 BAcc 反转共同限制了对单个静息任务的架构解释。不能称 Stat-MoE 或 Ganglion 有额外价值，未运行它们。

下一最有决策价值的问题是**任务诱发信号是否比静息信号更可复现**，而非把单一静息任务失败归咎于模型容量。PADS 官方说明第二个 `RelaxedTask` 在休息姿势中加入 serial sevens 心算，可能诱发被单纯静息遗漏的动作表现；它有同一人的真实双腕观测。应以新 ID 预先固定该任务和比较，只用开发人群，不用已看 test 反复筛任务。若仍无稳定收益，暂停本数据上的单任务 motion/shared 路线；若观察到更稳定收益，后继重点是未见个体/中心和多任务采集兼容性，而非立即部署共享架构。

本研究仍为同一门诊的横断面组别，非 longitudinal progression、非临床诊断工具资格。5 个重新划分相关，不增加有效独立人数；问卷与诊断同次采集、评估者盲法未证明。局部只读核验 6/6，未运行外部验证、全仓门或哈希。
