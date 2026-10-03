# EXP019：训练与验证门控的原生来源扩展

研究 ID：`STAT-PSYMOE-EXP019-20261002-001`；2026-10-02；`EXPLORATORY`。父阶段：[EXP017](../EXP017/CLOSEOUT.md) 六原生来源、[EXP018](../EXP018/CLOSEOUT.md) 三来源支持不足停止。本轮保留原 Open Targets 26.06、drug-development terminal outcome、26,235 个映射 pair、disease bridge、target-disjoint split、六旧通道预处理、共享 core/head 与 EXP017 保存点。既有 test 在父阶段已被看过，本报告全部 test 数值仅为**回顾性开发评估**。

**结论：12 条剩余 Passport 来源仅 Cancer Gene Census（CGC，DP-SOM-01）通过预先冻结的 train/validation 支持与状态变化门，故实际研究为 6→7。** CGC 的独立统计路由及接入模型均实际训练。validation 上可观察到小幅增量；按 validation 选择的冻结接入 seed 101 在 test 上把 log-loss 由 0.194880 降到 0.194580，但按 target 成对 bootstrap 的差值 95% 区间跨 0，当前证据不足以确认优势。全参数接续重训在 validation 更低、既有 test 反而高于旧 checkpoint；新来源无法可靠替代 Europe PMC。EXP018 保持原 `STOPPED_AFTER_PREFLIGHT / NOT_IDENTIFIABLE`，不被改写。

## 固定资格门及 12 来源实际支持

在读取本轮候选支持结果前，[PLAN](PLAN.md) 固定每源 `train pairs ≥ 200`、`validation pairs ≥ 50`、`train terminal events ≥ 10`、`validation terminal events ≥ 3`，并要求至少 10 个 train 有记录 pair 上有 ≥2 个不同的核心原生状态值。先写 [train/validation 资格文件](eligibility_train_validation.json)，才把 test 数添加到 完整支持表 (source asset outside this public snapshot) 和 CSV (source asset outside this public snapshot)。下表 test 仅供记录，完全不参与来源选择。`Ntr/Nval/Etr/Eval/C` 分别代表 train pair、validation pair、train event、validation event、可估计状态变化未过门；CSV/JSON 保留完整 `FAIL_*` 代码、原生表行数、score 与零分、缺失、日期、schema 和官方原件 URL。

| Passport / datasource | Native rows | Train pair/event | Validation pair/event | Test pair/event，仅记录 | 门结果或未通过项 |
| --- | ---: | ---: | ---: | ---: | --- |
| DP-GEN-04 `genomics_england` | 47,102 | 20 / 0 | 7 / 0 | 7 / 0 | Ntr, Nval, Etr, Eval |
| DP-GEN-05 `gene2phenotype` | 5,050 | 5 / 0 | 1 / 0 | 3 / 0 | Ntr, Nval, Etr, Eval, C |
| DP-GEN-06 `uniprot_literature` | 6,692 | 27 / 5 | 7 / 1 | 6 / 1 | Ntr, Nval, Etr, Eval |
| DP-GEN-07 `uniprot_variants` | 36,722 | 14 / 3 | 5 / 1 | 4 / 1 | Ntr, Nval, Etr, Eval |
| DP-GEN-08 `orphanet` | 7,461 | 4 / 0 | 1 / 0 | 1 / 1 | Ntr, Nval, Etr, Eval, C |
| DP-GEN-09 `clingen` | 4,537 | 4 / 0 | 3 / 0 | 3 / 0 | Ntr, Nval, Etr, Eval, C |
| DP-SOM-01 `cancer_gene_census` | 91,572 | **700 / 53** | **165 / 15** | 107 / 5 | **PASS** |
| DP-SOM-02 `intogen` | 4,223 | 86 / 5 | 8 / 0 | 8 / 0 | Ntr, Nval, Etr, Eval |
| DP-PWY-01 `cancer_biomarkers` | 1,301 | 53 / 10 | 14 / 2 | 6 / 0 | Ntr, Nval, Eval |
| DP-PWY-02 `crispr_screen` | 21,643 | 48 / 4 | 5 / 1 | 9 / 0 | Ntr, Nval, Etr, Eval |
| DP-PWY-03 `crispr` | 517 | 25 / 4 | 5 / 1 | 1 / 0 | Ntr, Nval, Etr, Eval |
| DP-PWY-04 `reactome` | 10,752 | 57 / 9 | 7 / 0 | 5 / 0 | Ntr, Nval, Etr, Eval |

`C` 是预定“至少 10 个 train pair 有可估计变化”门，不表示该原生数据库绝对只有一个状态。例如 G2P 的少量 confidence 值有变化，但仅 5 个 train pair，不能由此开通新专家。CGC 在本 cohort 有 972 pair（700/165/107），均有原生 score，train score 有四级；原表每 pair 一行，但突变/检测样本、文献和 study 统计有 native geometry。其 train/validation 865 行中，publication/evidence date 均有 721 行非空；日期只用于质量诊断，不构成历史决策时锁。支持图见 [source_support.png](source_support.png)。

## CGC 原生统计层与旧六路条件增量

唯一 CGC pair 状态 (source asset outside this public snapshot)从官方 `evidence_cancer_gene_census` 原表在内存中限定原 cohort 后构造，不另存 raw evidence。它保留 score/resourceScore、`mutatedSamples` 内的突变、检测和类型样本数、context 数、study/literature 与方向计数、日期及 provenance key。manifest (source asset outside this public snapshot)列出官方 URL、字段、缺失和 train/validation 分布。旧六路 OOF 状态按 EXP017 原预处理在内存重建；三保存点 test 预测最大差 1.8×10⁻⁷，见[重建核对](results/EXP019-CGC-STAT-001/old_reconstruction.json)。

三种 source-specific 专家为 curated score、mutation context、study/publication support 的 L2 模型，而非对所有来源套同一种通用模板。五折 target-group OOF 后按 absent/present 两支持 regime 的 OOF log-loss 选择统计权重；有记录 regime 的权重为 `(score 0, mutation 0.55, study 0.45)`，无记录 regime 选择 study/support expert。训练 OOF 的 CGC Stat-MoE log-loss 0.202935，三个单专家为 0.203430/0.203113/0.203238；validation 为 **0.207396**，单专家为 0.207740/0.208294/0.207658，均为小幅数值差，见[统计路由](results/EXP019-CGC-STAT-001/native_stat_routing.json)。导出状态含预测、熵代理、专家分歧、availability、密度、score、突变比例、突变数、文献数、study/方向；provenance 和时间留在导出状态原件 (source asset outside this public snapshot)，不作为历史时点预测输入。

M0（旧六源状态）和 M1（六源加 CGC 状态）用 target-group OOF stacker 比较：train OOF log-loss 0.192256→0.191980；validation 0.198989→0.198815，validation 成对差 −0.000174，target bootstrap 95% CI [−0.001294,+0.000991]。所以有很小的条件增量点估计，区间不足以确认稳定改善。训练 OOF stacker 继承了 EXP017 的 OOF 状态和以全 train OOF 选定的 routing 权重，未再做完整外层嵌套；以 validation 作为更干净的增量比较面。[详细结果与预测](results/EXP019-CGC-STAT-001/incremental_train_validation.json)保留此边界。

## 6→7 冻结接入、全参数对照及不确定性

三个 seeds `101/202/303` 从各自 EXP017 六路 checkpoint 出发。冻结接入仅训练新 CGC interface 的 192 参数，六旧接口/core/outcome 均逐参数精确不变；对照从相同旧 checkpoint 初始化、开放全部 961 参数作 end-to-end **接续重训**。这是全参数 fine-tuning 对照，未称从零重建 7 路。各自 validation 选最佳 epoch 与 seed，随后才计算 test。另在 Europe PMC 输入缺席背景下训练三份冻结接口。所有九个新保存点均可与原 EXP017 保存点恢复并复现 validation 预测，最大差 1.8×10⁻⁷，见[恢复验证](results/EXP019-ONBOARD-001/restore_verification.json)。

| 条件（validation 选择） | Validation log-loss | Test log-loss，仅回顾性 | 相对同 seed 旧基线 test 差与 target 95% CI |
| --- | ---: | ---: | --- |
| 旧六源 checkpoint seed 101 | 0.199506 | 0.194880 | 基线 |
| CGC frozen seed 101 | 0.198984 | **0.194580** | −0.000300 [−0.000730,+0.000094] |
| CGC 全参数接续重训 seed 101 | 0.197246 | 0.195134 | +0.000255 [−0.001177,+0.001830] |
| 无 Europe PMC 旧 checkpoint seed 303 | 0.213470 | 0.206908 | 条件基线 |
| 无 Europe PMC + CGC frozen seed 303 | 0.211004 | 0.206770 | −0.000138 [−0.001448,+0.000970] |

冻结接入三 seed 的 test log-loss 为 0.194580/0.194542/0.194856；seed 101 是 validation 选择，不能改用 test 更低的 202。全参数三 seed 为 0.195134/0.194987/0.194378；虽 seed 303 的 test 最低，它也不是 validation 所选。选定 frozen101 的 Brier 0.047759、AUROC 0.6506、AUPRC 0.1199、ECE 0.007995、calibration intercept −0.1750、slope 0.9102；全部模型的同项指标见 [test_metrics.json](results/EXP019-ONBOARD-001/test_metrics.json)。全参数对照在 validation 更好但选定 test 较旧模型高，不能据此认定端到端适应有稳定收益；其旧接口/core/outcome 位移非零，见 [validation_selection.json](results/EXP019-ONBOARD-001/validation_selection.json)。图见 [test_logloss_comparison.png](results/EXP019-ONBOARD-001/test_logloss_comparison.png)。

## 必做对照与旧系统保留

对 validation 选择的 frozen101，只在 test 中 107 个有 CGC 记录的 pair 之间置换完整新状态，保持每 pair 的 availability、边际 score/状态分布和模型参数。log-loss 从 0.194580 变为 0.195000；shuffle − original 的 paired target 差 +0.000420，95% CI [−0.000051,+0.000974]，区间跨零。点估计与具体 pair 对应有关，但单次控制不足以确认该效应；三个 seed 的全部 shuffle 原始值在[controls.json](results/EXP019-ONBOARD-001/controls.json)。

旧六源支持但 CGC 缺席的 1,846 个 test pair 上，冻结接入预测逐值完全相同（max shift 0）；六旧接口/core/head 参数位移为 0。旧六源与 CGC 都有记录的 92 pair/5 events 上，frozen101 log-loss 0.179135→0.160726，但样本和 event 少，不能外推。全参数对照在 1,846 个旧支持、CGC 缺席 pair 上从 0.271878 到 0.272931，max 单 pair prediction shift 0.542；故不能把其 validation 改善解释为旧预测受保护。

在无 Europe PMC 背景，frozen303 的 test 差 −0.000138，CI 跨零，仍远高于完整六源背景的 0.194580。CGC 在这种背景可能有极小条件增量，但本轮没有观察到可靠的 Europe PMC 依赖降低。这些是现有来源集合下的预测条件比较，不是因果证据。所有 frozen 训练到 1,000 epoch 上限或接近上限，validation 仍可能缓慢改善；按冻结预算关账，不依据已看 test 继续加 epoch。

## 用户提出的 14 个完成问题

1. **检查数：**剩余 12 条，全部官方 26.06 native 表可读并纳入统一预检。
2. **通过门：**仅 DP-SOM-01 `cancer_gene_census`。
3. **未过门：**其余 11 条的 pair/event/C 原因见上表与完整 CSV/JSON；当前 cohort 支持不足不能裁决它们在别的任务的价值。
4. **合格来源状态：**CGC 的 score、嵌套突变样本/检测数与比例、study/文献和方向，三专家 OOF 统计路由及 11 维导出状态。
5. **Stat-MoE 对单专家：**CGC validation log-loss 0.207396，低于三单专家 0.207740/0.208294/0.207658；未宣称稳定优势。
6. **六源之外增量：**M1 validation 较 M0 低 0.000174；成对区间跨零，证据不足以确认稳定改善。
7. **冻结接入 proper loss：**选定 frozen101 的 test log-loss 较同 seed 旧 checkpoint 低 0.000300。
8. **成对区间：**[−0.000730,+0.000094]，跨 0，未支持稳定优势判断。
9. **对应置换：**选定 seed 的 shuffle log-loss 升 0.000420，但 shuffle − original 区间跨 0，无法确认对应特异性。
10. **全参数收益：**validation 更低，选定 test 0.195134 高于冻结接入 0.194580；未观察到可确认的额外泛化收益。
11. **旧系统：**frozen 旧参数精确不变、CGC 缺席旧支持 pair 预测精确不变；全参数对照可改写旧预测。
12. **Europe PMC：**无 EP 条件小幅点估计改变但区间跨零，未证实依赖降低。
13. **证据级别：**只有 retrospective development；既有 test 已被使用，无独立确认或历史时锁。
14. **后继：**当前 cohort 的其余 11 源不应硬接；若继续科学评估，优先建立独立时间锁或外部/新 cohort 确认并在新 ID 下冻结，现阶段不自动执行。

## 证据、失败与验证边界

`EXP019-CGC-NATIVE-001` 因校验脚本误从 train/validation 资格文件读取 test 字段而报 `KeyError`，未写派生状态；原失败 (source asset outside this public snapshot)保留。新 run `-002` 仅修正行数核对，972 pair 状态成功。所有尝试、修订、退出状态与原件位置见 WORKLOG (source asset outside this public snapshot) 和 [CLOSEOUT](CLOSEOUT.md)。

**实际局部验证：**12 原表 schema/行数与 cohort 限定原生字段，资格文件在 test support 加入前写出，CGC train/validation native 分布，五折 target 不交叉、旧六源 OOF 与三保存点预测重建、三 seed/三训练臂、九保存点恢复、成对 target bootstrap、source shuffle、Europe PMC 条件控制、本轮输出文件。**仅静态/引用：**Passport 原设计与 EXP001–018 历史结论。**未验证：**从零 7 路训练、完整外层嵌套的 M0/M1 train OOF、decision-date evidence lock、独立新 cohort、source-level holdout、前瞻/临床效用、因果机制、全仓门或全量哈希。新报告和 Living v0.20 只追加 EXP019；原 raw 表、旧结果和 EXP018 原件保持原位。
