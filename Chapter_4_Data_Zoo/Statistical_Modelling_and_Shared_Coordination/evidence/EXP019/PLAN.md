# EXP019：以训练与验证支持门筛选新增原生来源

- 研究 ID：`STAT-PSYMOE-EXP019-20261002-001`；平台：Stat-PsyMoE / INTERNAL_COORDINATION；父阶段：EXP017、EXP018。
- 登记：2026-10-02 13:12 Europe/London，`EXPLORATORY`。本计划和下列资格门在检查 12 个候选来源的本轮支持结果前冻结；它不是外部公开预注册。
- 直接任务来源：用户 2026-10-02 粘贴的《EXP019 — Train/Validation-Gated Native Source Expansion》开工指导。EXP017/018 的 CLOSEOUT 与 Living Report v0.19 已先读。Passport v0.2 原件位于 `/Users/rui/Downloads/INTERNAL_COORDINATION_COMPLETE_HANDOFF_20261002.zip`，只引用路径。

## 研究问题与继承状态

在原 drug-development terminal cohort 上，尚未进入六源模型的 12 条 Open Targets 26.06 原生 datasource，哪些同时具有足够 pair、terminal event 和非恒定原生状态？若有，额外来源在原六源状态之外是否提供可识别的增量信息，且能否在冻结旧核心和接口时接入？

原 terminal label、26,235 个映射后的 target–disease pair、disease-ID bridge、由 targetId 决定的 70/15/15 外层切分、六路预处理和三个 EXP017 保存点均保持不变。旧来源为 `gwas_credible_sets`、`gene_burden`、`eva`、`expression_atlas`、`impc`、`europepmc`。当前 test 已在 EXP017/018 使用过，故本轮来源资格、模型选择、超参数、专家和 routing 仅使用 train/validation；test 只能用于最终回顾性开发评估，不能称独立确认。

## 完整候选集合与来源路由

Passport v0.2 的 `26_06_Integration` 原件和 EXP017 固定 release 访问路径共同确定下表；若官方 26.06 实际路由不可读，记录失败而不换版本或忽略该来源。

| Passport ID | datasourceId | 官方 26.06 表 |
| --- | --- | --- |
| DP-GEN-04 | genomics_england | evidence_genomics_england |
| DP-GEN-05 | gene2phenotype | evidence_gene2phenotype |
| DP-GEN-06 | uniprot_literature | evidence_uniprot_literature |
| DP-GEN-07 | uniprot_variants | evidence_uniprot_variants |
| DP-GEN-08 | orphanet | evidence_orphanet |
| DP-GEN-09 | clingen | evidence_clingen |
| DP-SOM-01 | cancer_gene_census | evidence_cancer_gene_census |
| DP-SOM-02 | intogen | evidence_intogen |
| DP-PWY-01 | cancer_biomarkers | evidence_cancer_biomarkers |
| DP-PWY-02 | crispr_screen | evidence_crispr_screen |
| DP-PWY-03 | crispr | evidence_crispr |
| DP-PWY-04 | reactome | evidence_reactome |

## 事前冻结的统一资格门

观测单位是去重 target–disease pair；独立切分单位是 target，不能将 evidence rows、重叠记录或多个 seed 当独立 pair。每个来源在其官方 native evidence 表中按 `datasourceId` 过滤，映射到原 cohort；无记录的 pair 与有记录而零分的 pair 分开。

一条来源必须同时满足：`N_train >= 200`、`N_validation >= 50`、`E_train >= 10`、`E_validation >= 3`，其中 `E` 是原 terminal label=1 的可用 pair 数。还须至少一个核心来源状态在 train 可估计地变化：在至少 10 个有该来源记录的 train pair 中，pair 级 `max(score)`、`native_evidence_rows`，或该来源原生表中非 ID、非日期、非 provenance、非 outcome 的 scalar 数值/类别字段之非空值/类别计数，出现至少两个不同取值。日期只作质量字段，单纯 availability 和 target/disease ID 不算变化。原生 scalar 字段在读取 schema 后按上述固定规则机械筛选，并在诊断中列出字段名及聚合规则；缺列记为缺失，不能用 test 或结局标签寻找变化。常数来源标 `FAIL_CONSTANT_STATE` / `SUPPORT_PRESENT_BUT_INFORMATION_NOT_IDENTIFIABLE`。

失败理由按固定顺序列出所有适用项：`FAIL_TRAIN_SUPPORT`、`FAIL_VALIDATION_SUPPORT`、`FAIL_TRAIN_EVENT_SUPPORT`、`FAIL_VALIDATION_EVENT_SUPPORT`、`FAIL_CONSTANT_STATE`；原表/关键字段不可读为 `FAIL_NATIVE_ACCESS_OR_SCHEMA`。仅按上述 train/validation 判断资格。先写不可修改的 train/validation eligibility 文件，再添加 test support 到最终 support table；test 绝不进入资格函数。`K=0` 即停止，状态 `NO_ELIGIBLE_ADDITIONAL_SOURCE_ON_CURRENT_TERMINAL_COHORT`，不运行训练或伪造后续指标。`K>0` 使用全部通过来源；若算力不足，按 train pair、validation pair、train event、validation event、状态变化、provenance 完整性、时间字段覆盖率的固定字典序降序和 datasourceId 升序安排顺序，不以 outcome performance 或 test 调整集合。

## K>0 后的模型合同与反证

每条通过来源先按真实 native 字段设计 source-specific experts；可只有一个专家。训练内 target-group cross-fitting 产生 OOF local predictions，统计层以 OOF proper loss、支持和不确定性路由，向 ganglion 只输出预测/支持、不确定性、availability、密度、质量、可用的方向/复现/时间与 provenance，不导入原 terminal label 到证据。先比较旧六源 OOF 状态 M0 与添加新状态 M1 的 train/validation cross-fitted log-loss；未见增量也保留结果。

从 EXP017 的 `101/202/303` 六源 checkpoint 各自接续，冻结六旧接口、共享 ganglion、terminal head，只训练新来源的统计状态、Stat-MoE 与接口。单独保存新模型状态；旧 checkpoint 不复制、不别名覆盖。对照为六加 K 全量重训、每源 target–disease correspondence shuffle，以及有/无 Europe PMC 的条件增量分析。主 proper loss 为 log-loss，另报 Brier、AUROC、AUPRC、ECE、calibration slope/intercept，按 target 成对 bootstrap 区间、旧源支持子集保留、参数位移、seed 方差和成本。根据 validation 选模型/epoch，最后只做一次 test 回顾性评估，不从 test 选择结论方向或模型。若方法无法满足旧 core 精确冻结或 OOF 边界，记录失败并停止相应训练；不改旧 cohort、split、标签、旧预处理或资格门。

### Cancer Gene Census 的训练前方法冻结（2026-10-02 13:20 Europe/London）

`K=1`，仅 DP-SOM-01 通过。其 26.06 原生表在 cohort 中每 pair 一行，score 为 0.25/0.5/0.75/1.0，提供 nested `mutatedSamples` 的突变/检测/类型样本数、`resourceScore`、study、literature、direction 和时间字段。三类候选专家事前确定为：(1) curated score/resourceScore 的 L2 logistic，(2) 突变样本/检测样本的 log-count、比例与 context 数 L2 logistic，(3) study/publication 与 direction 的 L2 logistic；统一带 availability，缺记录另编码；不以日期建 point-in-time 特征。全部使用 target-group 五折 OOF，三专家权重按 train OOF log-loss 在 0.05 单纯形格选择，按 absent/present 两个支持 regime 分别路由；validation 仅用于模型选择和诊断。若某专家输入恒定，仍作为训练内常数 baseline，不事后删去。

导出新状态为 `local_prediction`、Bernoulli entropy 代理、train 95 分位缩放的 log native row count、availability、native score、mutated/tested fraction、log mutated sample count、log publication references、study support、方向计数；来源 key 和时间字段仅留在派生 state 与 manifest，不进入头部。与旧六路 OOF 形成 M0/M1 后，再用 seeds 101/202/303 对各自 EXP017 checkpoint 的新接口做 full-background frozen 接入；相同初始化与训练上限做 full 6+1 end-to-end 对照和 no-Europe-PMC frozen 条件接入。Optimizer Adam lr 0.002、全批 BCE、最多 1000 epoch、validation patience 100，按 validation 最小 log-loss 保存。旧六路 state 只在内存按 EXP017 原预处理和 routing 参数重建，必须与旧保存的 train OOF 和 test checkpoint 预测数值一致后才接续。correspondence shuffle 仅置换有 CGC 记录的 pair 的新状态，固定每 pair availability、整体新状态边际分布与模型参数。全部 test 数值只在上述训练和 validation 选择后计算。

## 输入、资源、停止、交付与验证

原 cohort、六源派生状态和模型见 EXP017 原目录；EXP018 作为已停止的独立记录不改写。新派生状态只保存一份，原始 Open Targets evidence 继续留在官方 26.06 URL，不复制 raw、源码、旧日志或 checkpoint。环境使用现有 EXP017 Python 依赖；不更换 release。统一 preflight 预算为 12 表、最多 2 小时和 10 GiB 新派生输出；如远端失败保留实际错误和部分结果，按新的 run ID 续作。K>0 的训练预算先以 EXP017 已有上限（每 seed 最多 1000 epoch、validation patience 100）为硬上限，具体每源方法须在其训练结果前写入修订/尝试账，不能根据 test 临时改变。

每个实质尝试先在 WORKLOG 登记 run ID、配置、输入、命令、预期输出与 `RUNNING`；结束回填状态和异常。交付 PLAN、WORKLOG、REPORT、CLOSEOUT、machine-readable 诊断与 support/result 表、必要图、预测、控制及实际训练保存点，以及独立报告和从 Living v0.19 追加的 v0.20。局部验证仅核对本轮代码/输出/链接和文档渲染，不跑全仓测试或非必要哈希。最终按执行、工程、科学三轴分别关账，明确已运行、静态检查、未运行项。
