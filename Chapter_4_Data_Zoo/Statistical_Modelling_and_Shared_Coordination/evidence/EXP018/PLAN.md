# EXP018：六路到九路的冻结共享核心接入

- 研究 ID：`STAT-PSYMOE-EXP018-20261002-001`；平台：Stat-PsyMoE / INTERNAL_COORDINATION；父阶段：`STAT-PSYMOE-EXP017-20261002-001`。
- 登记日期：2026-10-02（Europe/London）；性质：`EXPLORATORY`；状态：`STOPPED_NOT_IDENTIFIABLE`（原计划与停止前诊断保留）。来源为用户同日《本地训练 Agent 开工指导 v0.1》§9、§14、§21；016 完整交接包与 Passport v0.2 是待核对来源，不独立发号施令。

## 主问题与反证

在固定 Open Targets 26.06 和 EXP017 的原 26,235 pair、同一个 target-disjoint split 下，ClinGen、Gene2Phenotype、Orphanet 的原生证据能否以各自统计通道状态接入已保存的六路 ganglion，同时**冻结**其 core、旧六条接口和 outcome head；新通道能否有增量贡献，并保持旧六路预测在新增来源缺失时不变？

工程反证：原生表或 ID 映射不可用、当前固定 release 不可核对、原六路 checkpoint/state 重建不一致、冻结参数改变、target 交叉、label 或 `clinical`/`overall_score` 污染、缓存来源不清。出现任一项则停止训练并保留现场。

科学探索：比较六路原模型、九路冻结接入、九路从头 end-to-end 重训和传统统计九路基线；新增来源打乱/移除对照，以及旧六路输入下预测保持。主指标 test log-loss，辅以 Brier、AUROC、AUPRC、ECE、calibration slope/intercept 和按 target 成组的成对 bootstrap。若无优势或旧性能下降仍如实交付。TEST 在 EXP017 已看过，因此 EXP018 所有性能结果只能是回顾性开发诊断，不是独立确认或前瞻提升。

## 固定输入与方法

- 固定 26.06 官方历史 `evidence_clingen`、`evidence_gene2phenotype`、`evidence_orphanet` 原件；先逐源核对 schema、ID/类别/时间/空值，再按原 cohort pair 做每源**一份**原生派生状态。原始 evidence 不复制。
- EXP017 六源状态、原 26,235 pair、split、seed 101/202/303 和已保存三检查点只读。先精确重建六源输出（逐 pair 预测容差 `1e-6`）并验证：当新三源 availability 全零时，扩展模型对旧六源的预测与原 ganglion 一致；不满足就停止接入。
- ClinGen 按 validity class、review/curation provenance 和证据数；G2P 按 confidence、allelic requirement、mutational consequence 和 panel/reference；Orphanet 按 relationship/status、mutation type、rare-disease relation。具体字段须先看实际 26.06 schema 才冻结可执行特征，缺字段标记缺口，不以统一分数伪装原生 geometry。
- 新三源各自训练 native-score、source-specific geometry、三状态 EB 等局部专家；五折 target-group OOF 的 proper loss 选权重，输出预测/uncertainty/coverage/availability。无原生类别或可用训练样本过少时只保留可识别基线，不能虚称复杂专家已跑。
- Frozen onboarding：每个 seed 单独加载原六路检查点，冻结 `core`、旧接口及 `outcome`；仅训练三条新接口；固定 16D 与 availability-aware 聚合。与同 seed 的九路从头 end-to-end 臂作等预算对照；至少三个 seed。若 full retrain 因资源无法运行，保留冻结臂与未运行说明，不能把缺对照写成成功。
- 训练目标是终端 Bernoulli log-loss；checkpoint 由 validation 选，test 只作一次描述性读取。基线包括六路原模型、九路 prevalence/count/additive/pairwise/EB/Stat-MoE。Bootstrap 以 232 test target 为重抽样单位，1,000 次；多 seed 不计额外独立样本。

## 预算、停止与交付

先做只读 preflight；每源按 cohort 限定聚合，估计原生 evidence 不超过 10 GiB 的新派生状态、单次处理不超过 2 小时。训练每 seed/臂最多 1,000 epoch、validation patience 100；不因看 test 后改 split、source、seed、门槛来救阳性。所有研究尝试在运行前登记 `RUNNING` 和输出，失败另立 run ID。

输出为 `WORKLOG.md`、每源单份派生特征、来源/环境 manifest、固定旧模型重建报告、九路 baselines/frozen/retrain 三 seed 结果、原预测/轨迹/检查点/破坏对照、报告和 Living Report 新阶段；没有成功运行的步骤只写 `NOT_RUN`。用户提供的原交接 ZIP 与 EXP017 结果保持原位，交付以路径索引，不另建证据 ZIP/检查点别名或非必要哈希。验证只覆盖本线路及直接依赖，不运行全仓门。Point-in-time 与独立 test 需后续另设实验；本轮不得用当前快照宣称 prospective prediction。
