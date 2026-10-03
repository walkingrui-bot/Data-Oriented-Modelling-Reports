# EXP017：六条 Open Targets 管线的首次实际接入

- 研究 ID：`STAT-PSYMOE-EXP017-20261002-001`；平台：Stat-PsyMoE / INTERNAL_COORDINATION；父阶段：`INTERNAL_COORDINATION_016`。
- 建档日期：2026-10-02（Europe/London）；登记性质：`EXPLORATORY`；执行状态：`COMPLETE`（2026-10-02 关账；原始计划与下文事后修订均保留）。本记录不是对历史 001–016 的事前注册。
- 任务来源：用户 2026-10-02 粘贴的《本地训练 Agent 开工指导 v0.1》及随后提供的完整交接包。历史报告、Passport 和代码只作为待核对证据；原件位于 `/Users/rui/Downloads/INTERNAL_COORDINATION_COMPLETE_HANDOFF_20261002.zip` 和 `/Users/rui/Downloads/INTERNAL_COORDINATION_LOCAL_TRAINING_016.zip`，不另复制。

## 问题与继承边界

问题：在 Open Targets 26.06 的六条具名 datasource（`gwas_credible_sets`、`gene_burden`、`eva`、`expression_atlas`、`impc`、`europepmc`）上，能否从实际 source-level 数据产生独立的统计通道状态，再训练一个共享协调器；各步相对于传统统计基线的预测与校准表现如何？

继承 016 的 Passport v0.2、18 路映射及架构分工；保留 011–015 的原始结果，不把旧六个 datatype 汇总结果当作本轮六条 native/source-level 实测。此轮先做 datasource-level plane；只有核对 source-level 版本、标签、映射、split 与缓存复读后，才进入六路训练。Native raw geometry 和 point-in-time 前瞻资格另列阶段，不将 source-level 结果称为 native raw 或 prospective 结果。

## 假设、反证与对照

- 工程假设：六条 source-level 通道可分别映射到 26.06 的 target–disease pair，且 ChEMBL terminal outcome、`clinical`、`overall_score` 不进入输入。若 release 身份不唯一、任一必需 ID 无法可靠映射、标签来源不固定、同一 target 跨 split 或污染字段入模，则停止训练并保留失败现场。
- 科学探索：Stat-MoE 和 ganglion 对 log-loss、Brier、校准、缺通道稳健性可能有收益；传统统计持平或获胜也属有效结果。至少比较 prevalence、count、additive logistic、pairwise interaction logistic、empirical-Bayes、calibration-only、单通道/Stat-MoE 与共享 ganglion。做一项 target–disease 错配或通道 shuffle 结构破坏对照。
- 独立切分单位是 Ensembl target；观测单位是 target–disease pair；按 target 确定性 70/15/15 train/validation/test。训练内 target-group cross-fitting；测试集只作冻结后的最终评估。多条 pair 和多个 seed 不算独立生物样本。

## 输入、方法和判据

- 固定 Open Targets `26.06`；每个来源必须检查实际数据中的版本字段和值，不能仅凭文件名或 README 推断。终端 cohort 要锁定来源修订；继承 011 报告所记 26,278 pair 和 Git blob `d7102b1357aaeb780c73d286318fea297d0dbcb4`，若取不到原样数据则记录缺口并停止正式训练。
- 先对原训练包做只读静态检查，再做远端元数据/小查询；缓存只放本轮新状态一份，记录来源、版本、行数、列、重读结果。远端大表须按 `26.06` 和六 datasource 谓词下推，禁止默认抓取 40M+ raw evidence。
- 六路模型分别输出预测/支持、uncertainty、novelty、availability 与 provenance；缺失与零分分开。Stat-MoE 权重由训练内 OOF proper loss 选择。共享 ganglion 仅接收各通道状态，训练终端 Bernoulli 目标。预定 ganglion 初始化种子 `101, 202, 303`；训练预算最多每 seed 250 epochs，超时或内存/磁盘压力记录失败并止步，不改测试集救结果。
- 指标：test log-loss（主）、Brier、AUROC、AUPRC、ECE、校准 slope/intercept、阳性率及按 target 分组 bootstrap CI；同时记录 train/validation/test target 和 pair 数、标签定义、各通道覆盖、版本与桥接未匹配数。探索性质不预设阳性阈值；不可把测试选择写成确认。
- 时间锁：26.06 当前快照仅能做回顾性 source-level 探索；无 decision-date 之前证据冻结时不宣称前瞻预测或因果机制。

## 资源、停止与交付

本次优先限于元数据和六条 datasource 的 target–disease source-level 面；预计缓存预算不超过 10 GiB，单次查询/训练如需超过 2 小时则先记录进展与原因再决定续作。不能访问固定 release、标签或关键字段时暂停实际训练；不以别的版本静默代替。运行前在 `WORKLOG.md` 记 `run_id`、配置、输入、命令、输出与 `RUNNING`，结束补状态和原始异常。

本目录只放新计划、代码修订、日志、结果及必要新状态；旧源码、数据、报告、检查点只引用原件。交付使用原件索引，不额外复制或打 ZIP。验证限本轮代码/六路数据和直接依赖，不运行全仓门或非必要哈希。报告明确区分当前实测、历史报告引用与未检验项。

## Native 原表局部扩展（source-level 结果之后独立尝试）

若六条原生表在 26.06 历史路径可读，则只对原 cohort target–disease pair 聚合，且每源保存一份新 pair-level 特征状态：GWAS 的 locus 数/score/resourceScore；Gene Burden 的 p-value 指数量级、beta、cohort/project 数；EVA 的 variant、study、临床显著性组合数；Expression Atlas 的 study/contrast 与 log2 fold-change 方向和幅度；IMPC 的 model/phenotype 数；Europe PMC 的 publication 数、year 范围与文本挖掘 score。共同记录 evidence 行数及来源路径。原生原始行、文本句子、变异列表不另复制。每源先核对 target/disease ID、非空覆盖与异常值；没有 decision-date 锁定时仍只作回顾性分析。

### 原生六路探索性训练合同（2026-10-02，训练前写入）

沿用原先的 target 70/15/15 split 和五折 target-group OOF，保持同一 26,235 pair；不修改标签。每源的 local score expert 用 native max/mean score 与可用性，geometry expert 用该源特有的聚合统计及其缺失指示，EB expert 用“无记录／有记录零分／有正分”三状态收缩；权重只以 train OOF Bernoulli log-loss 在 0.05 单纯形网格选出。EVA geometry 还使用另存的类别/复审计数。六个导出状态各含 local OOF/外部预测、预测熵代理、按 train 分位缩放的原生 evidence 行数、availability。日期保留在来源状态但不入本次模型；尤其不使用异常的 Europe PMC publicationYear 作时间锁。

传统基线仍为 prevalence、evidence-count、单分数 calibration、additive、pairwise、EB 及统计路由。共享协调器保留六个独立 interface、16D core 和 Bernoulli 目标；新原生训练在看到任何本轮 test 结果前定最多 1000 epoch、验证 patience 100、seeds 101/202/303（取自 source-level 未收敛诊断，故本轮依旧是探索性续作）。按验证选择 epoch/候选；test 指标与 target-group bootstrap、pipeline shuffle、单源缺失、learned-direction lesion 和同范数随机扰动均保存。强制说明阶段边界：这不是 point-in-time prospective 评估，单次 lesion 不构成机制证明。
