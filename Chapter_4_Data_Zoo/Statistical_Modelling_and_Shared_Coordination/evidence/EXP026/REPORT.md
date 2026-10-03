# EXP026 PADS 问卷与双腕静息动作统计基线报告

研究 ID `STAT-PSYMOE-EXP026-20261002-001`；2026-10-02；`EXPLORATORY`。EXP025 通过真实人级多通道来源门后，本轮问一个最小的可决策问题：在同一批横断面真实个体上，单项双腕静息动作是否使简单统计模型在 30 项非运动问卷之外获得稳定组别信息？依据用户后续自治授权，EXP023/024 的 FDA 当次适应症识别失败保持原样，药物适应症分支暂停；转向 PADS 不等于替它补出监管时锁。

## 实际执行

469 位独立人：PD276、鉴别诊断114、健康79。只读取官方 PADS v1.0.0 原位 469 份问卷、469 份动作 observation 元数据和 938 份 `Relaxed` 双腕原始时序，累计 1,876 HTTP、189,123,765 bytes，全部可读、无重试、所选字段无缺失。按事先 seed 20261002 分层成 train280 / validation92 / test97，各人只在一组。原件不另存；`FEATURES.csv` 是唯一一份 30 问卷二元特征、每腕 10 个统计特征及 10 个左右绝对差的派生数据产品，`SOURCE_AUDIT.csv` 和 `SPLIT_MANIFEST.csv` 记录来源与独立性。诊断、诊断注释、年龄诊断日、文件路径与 subject ID 不进特征；年龄/性别也不进本轮模型。

M1 问卷、M2 双腕动作、M3 联合使用同一 class-weighted、L2 正则三类 logistic regression；M0 为类别先验。λ={0.01,0.1,1,10} 只依据 validation macro log loss 选择，之后 train+validation 重拟合并一次评价 test。train-only 插补/缩放；本轮没有观测缺失。原计划 M0 validation 先验文字存在潜在泄漏，模型运行前以 [Amendment 001](AMENDMENT_001.md) 更正为 train-only 先验，保留修订过程。所有 15 个实际拟合收敛。该内部 test 不具有独立中心或前瞻时序资格。

| 模型 | validation macro loss | validation balanced accuracy | test macro loss | test balanced accuracy |
| --- | ---: | ---: | ---: | ---: |
| M0 类别先验 | 1.242923 | 0.333333 | 1.245370 | 0.333333 |
| M1 问卷 | 0.767094 | 0.629293 | 0.855639 | 0.655229 |
| M2 静息双腕 | 1.019016 | 0.436364 | 1.164297 | 0.455299 |
| M3 联合 | 0.700544 | 0.694949 | 0.807638 | 0.637605 |

M3 对 M1 的 validation loss 改善 +0.066549、balanced accuracy +0.065657；test loss 改善 +0.048002，但 balanced accuracy **下降 0.017624**。预设四条件中的 test balanced accuracy 没过，故 [冻结门](GATE_RESULT.md) 失败。test 的 DD 召回从 0.4583 到 0.5000，而 HC 从 0.8824 到 0.8235、PD 从 0.6250 到 0.5893；这种混合变化不能压缩成“联合更好”。动作单通道弱于问卷；联合使概率得分改善但未使三类离散决策稳定改善。

## 解释与未识别项

当前可说：这一个静息任务包含能改善内部宏平均概率得分的信号，但**不满足事先的联合通道增益资格**；没有训练 Stat-MoE、Ganglion 或 precision branch 的证据基础。测试为同一门诊的 97 人且组别不均衡，未取得外部 cohort，未证明临床诊断、病程进展、治疗结果或新主体泛化。问卷可能与临床判定同次采集，评估者盲法未识别。未读取/建模其余十项动作，不推断它们没有价值。训练前未查看 test 成绩；看过本轮 test 后不得把它当下一实验 confirmation。

WORKLOG.md (source asset outside this public snapshot) 保留 split、来源、数值拟合和局部验算全部尝试；`PREDICTIONS.csv` 保留 validation/test 人级概率与真值用于复核，`OPTIMIZATION.json` 保留 15 个拟合状态。局部验算 11/11，含从保存预测重算结果；未运行全仓测试、外部确认或无关哈希。[CLOSEOUT.md](CLOSEOUT.md) 指向新的稳定性诊断，不覆盖本轮失败。
