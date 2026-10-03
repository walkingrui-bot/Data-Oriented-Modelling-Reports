# INTERNAL_COORDINATION_017：六条原生来源首次实训

研究 ID：`STAT-PSYMOE-EXP017-20261002-001`  
日期：2026-10-02（Europe/London）  
性质：`EXPLORATORY`；父阶段：`INTERNAL_COORDINATION_016`  
执行／工程／科学：`COMPLETE / VALID_SCOPED / MIXED_UNCONFIRMED`

## 结论

在固定 Open Targets `26.06` 的六条真实原生证据表上，本轮完成 cohort 限定的 source-specific 状态、每条管线三专家统计路由、共享 16D ganglion、传统基线、三种初始化与局部破坏对照。验证集选出的 native ganglion seed 101 在相同 4,401 个 test pair 上的 Bernoulli log-loss 为 **0.194880**；native Stat-MoE 为 **0.196240**。按 test target 成组的 1,000 次成对 bootstrap，差值为 **−0.001361，95% CI [−0.004207, +0.001225]**，跨零。因而这是回顾性探索的数值优势，不是确认的优越性。

本轮同时保留阴性首跑：最初的 source-level 250 epoch ganglion 三 seed 都不及 Stat-MoE；看过结果后的独立长预算尝试才出现小幅数值优势。Native 相对 association-only 输入的成对比较也跨零。Europe PMC 来源移除损失显著升高；Gene Burden 训练集仅 13 个可用 pair。26.06 快照没有按历史决策日锁定，不能据此称前瞻预测、临床有效性或共享机制已被证明。

## 数据、独立单位与输入边界

终端标签来自原交接指向的固定 Git blob `d7102b1357aaeb780c73d286318fea297d0dbcb4`，原始 26,278 行，经官方 26.06 disease 表桥接得到 26,235 个唯一 target–disease pair。一个桥接 pair 的 phase 为 1/2，但二元标签均为 0；两种 phase 和原 ID 一并保留。没有将不同标签强行合并。26.06 association 的 18 条 datasource 在 cohort 内均非空，六条本轮来源的 native pair 数如下。

| 原生管线 | Cohort 内 pair | Native evidence 行 | Train / validation / test pair |
| --- | ---: | ---: | ---: |
| GWAS credible sets | 540 | 2,261 | 349 / 87 / 104 |
| Gene Burden | 26 | 139 | 13 / 6 / 7 |
| EVA / ClinVar | 797 | 7,389 | 556 / 129 / 112 |
| Expression Atlas | 647 | 1,241 | 437 / 112 / 98 |
| IMPC | 408 | 2,102 | 299 / 61 / 48 |
| Europe PMC | 11,942 | 1,869,896 | 8,308 / 1,772 / 1,862 |

独立切分单位是 Ensembl target：train / validation / test 为 990 / 212 / 232 target、17,702 / 4,132 / 4,401 pair、916 / 220 / 228 阳性。同一 target 无跨切分。五折训练内 OOF 按 target 分组，选本地和全局统计权重；多个 pair、多个 seed 不构成独立生物样本。`clinical`、`overall_score` 与终端标签/phase 不作为证据输入；原始 native 行没有复制到本记录。

EVA 原生表有 638 个 association 表未显示的零分 pair、1,182 行，其中 `[evidence only]` 1,176 行；“有证据记录但零正向支持”与“来源缺失”分开编码。Gene Burden 26 pair 中 20 个没有 beta；IMPC 408 pair 中 6 个没有 human phenotype count。Europe PMC 的最大 publicationYear 为 2120，故日期字段本轮不入模，也不用于伪造 point-in-time 资格。

## 方法与实测

六源分别构造 source-specific native geometry：GWAS locus/resource score、Gene Burden p-value/beta/cohort、EVA 变异与临床类别、Expression Atlas study/contrast/fold-change、IMPC model/phenotype、Europe PMC publication/resource score。每条源内的 native score、native geometry、三状态 EB 收缩专家以训练内 OOF log-loss 选权重，输出 local prediction、熵代理、训练分位缩放的 native evidence 数和 availability。全局 Stat-MoE 对 additive / pairwise / EB 权重为 0.65 / 0.25 / 0.10。共享 ganglion 接收六条导出状态，用 seeds 101/202/303、最多 1,000 epoch、验证 patience 100；所有原始预测和检查点保存。

### Native 六路 test 指标

| 模型 | Log-loss ↓ | Brier ↓ | AUROC | AUPRC |
| --- | ---: | ---: | ---: | ---: |
| Prevalence | 0.203800 | 0.049123 | 0.5000 | 0.0518 |
| Evidence count | 0.198182 | 0.048700 | 0.6421 | 0.0981 |
| Calibration only | 0.200394 | 0.048849 | 0.6371 | 0.0840 |
| Additive logistic | 0.198386 | 0.048080 | 0.6443 | 0.1130 |
| Pairwise logistic | 0.201023 | 0.048001 | 0.6393 | 0.1187 |
| Empirical Bayes | 0.198708 | 0.048633 | 0.6198 | 0.0690 |
| Native Stat-MoE | 0.196240 | 0.047993 | 0.6462 | 0.1145 |
| Ganglion seed 101 | **0.194880** | **0.047771** | 0.6482 | 0.1209 |
| Ganglion seed 202 | 0.195006 | 0.047831 | 0.6486 | 0.1196 |
| Ganglion seed 303 | 0.195098 | 0.047865 | 0.6483 | 0.1176 |

Seed 101 的 validation log-loss 0.199506，为三 seed 最低；三者最佳验证 epoch 均为预算上限 1,000，不能宣称训练已收敛。Seed 101 test ECE(10) 0.0081、校准 slope 0.8788；Stat-MoE 的 ECE(10) 0.0066 较低。完整 validation、test 和各模型 target-group bootstrap 区间见 [metrics.json](results/native_six/EXP017-NATIVE-TRAIN-001/metrics.json)，不以单一排序代替多指标判读。

### 前置 source-level 尝试和比较

首次 association-only 六源运行中，Stat-MoE test log-loss 0.196175；250 epoch ganglion seeds 101/202/303 为 0.206666/0.218476/0.201880，全部更差。三条验证曲线在预算末仍下降。`EXP017-AMEND-002` 在看过 test 后另立长预算尝试，保留原首跑；原检查点的预测重建最大误差为 0，新尝试三 seed test 为 0.195742/0.195433/0.195539。按 validation 选 seed 202，相对原 Stat-MoE 的成对差 −0.000742，95% CI [−0.003617, +0.001787]。这些后验修订不能追认为初始确认。

Native Stat-MoE 减 source-level Stat-MoE 的 log-loss 差 +0.000065，95% CI [−0.001423, +0.001430]；native seed 101 减 source-level 长预算 seed 202 的差 −0.000553，CI [−0.001895, +0.001000]。同一 test 曾用于 source-level 诊断，因此 native 对比只作描述性分析。

## 破坏对照与可识别边界

- Native ganglion pipeline shuffle 将 seeds 101/202/303 的 test log-loss 从 0.194880/0.195006/0.195098 增至 0.214187/0.216594/0.217816，说明导出状态与来源的对应关系对当前预测有用。
- 单源移除 Europe PMC 后分别为 0.206741/0.206668/0.206908，是最大依赖；移除 EVA 也小幅变差，而部分稀疏来源移除略改善。不能把整体数值优势均分给六条来源。
- 移除学习 core 的首个方向后为 0.202136/0.212281/0.219765；每 seed 仅一次等范数随机扰动为 0.195374/0.196812/0.203874。只说明当前模型对所选方向敏感；未用多随机对照、独立样本或保存无关状态的因果控制证明机制。
- Core 权重增量的有效秩约 3.36/3.33/3.47，但可读性和数值损伤不能代替最终行为可控性的独立验证。

## 关账与后续

本阶段问的是“六条真实原生管线能否完成训练、评价与归档，以及相对基线的结果如何”，此工程问题已回答。科学证据为 **mixed / unconfirmed**：数值优势小且 CI 跨零，强烈依赖文学来源，缺少时锁与独立确认。EXP018 的六路→九路冻结接入、EXP019–021 的其它 Passport 扩展、EXP022 的历史时锁及独立来源 holdout 在本阶段均未执行；在新计划中登记时不得沿用本次 test 作为未看过的确认集。

本次实际验证：官方固定 26.06 原表 schema/限定 cohort 读取、桥接唯一性与标签冲突守卫、缓存复读、target 不交叉、六源特征范围/缺失、训练与保存结果、分组 bootstrap 和本报告对应的局部数值读取。仅静态检查：016 原 harness 与原报告边界。未验证：全量原表、全 18 路训练、历史决策日时锁、前瞻/临床效果、独立来源 holdout、完整收敛、因果机制、全仓回归。证据路径与全部失败尝试见 [CLOSEOUT.md](CLOSEOUT.md) 和 WORKLOG.md (source asset outside this public snapshot)。
