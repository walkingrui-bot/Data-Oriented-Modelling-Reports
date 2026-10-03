# EXP020 七源时间泄漏账

研究 ID `STAT-PSYMOE-EXP020-20261002-001`。这是 26.06 原生表的**历史可行性库存**，不是某个 decision date 的已纳入证据，也不是训练输入。七份逐源 JSON 为本表唯一机器统计原件：GWAS (source asset outside this public snapshot)、Gene Burden (source asset outside this public snapshot)、EVA (source asset outside this public snapshot)、Expression Atlas (source asset outside this public snapshot)、IMPC (source asset outside this public snapshot)、Europe PMC (source asset outside this public snapshot)、CGC (source asset outside this public snapshot)。总览为 JSON (source asset outside this public snapshot) 与 CSV (source asset outside this public snapshot)。所有 raw 仍在官方 URL，未复制。

## 原生日期库存

`dated` 表示至少一个 schema 日期/年份字段可解析，**不表示**该行的 26.06 内容在历史 `t0` 已存在。`future` 是晚于本次审计日 2026-10-02，不是晚于尚未选择的决策日；`invalid` 仅指非空字段格式无法解析。计数单位为 native evidence row，源间不相加为独立样本。

| 来源 | 26.06 原行 | 有可解析日期 | 日期未知 | 格式异常 | 晚于审计日 |
| --- | ---: | ---: | ---: | ---: | ---: |
| GWAS credible sets | 3,044,078 | 3,044,078 | 0 | 0 | 0 |
| Gene Burden | 44,555 | 44,555 | 0 | 0 | 0 |
| EVA / ClinVar | 3,998,459 | 3,998,459 | 0 | 0 | 0 |
| Expression Atlas | 238,174 | 193,734 | 44,440 | 0 | 0 |
| IMPC | 7,758,975 | 6,709,893 | 1,049,082 | 0 | 0 |
| Europe PMC | 26,191,349 | 26,191,349 | 0 | 0 | 65 |
| Cancer Gene Census | 91,572 | 75,069 | 16,503 | 0 | 0 |

**Europe PMC**：全表 `publicationYear` 有 26,191,349 条，完整 `publicationDate`/`evidenceDate` 各 26,106,740 条；84,609 条只有年份粒度。62 条 `publicationYear>2026`，7 条完整日期晚于审计日，行级并集 65 条；其中历史 EXP017 已见不可能的 2120 年。本轮未把 65 行归入任何训练。它们与后期 trial/批准论文、当前文本挖掘关系的污染风险同时存在，不能靠一个字段的日期解决。

**EVA**：3,998,459 条有 `releaseDate`/`evidenceDate`，只有 35,948 条有 `publicationDate`。一个过去的 submission/release 日期不能证明 26.06 的 assertion、review、score 当年相同。**CGC**：全表 16,503 条日期未知；EXP019 在旧 train+validation cohort 中 721/865 条有日期，那是现时 cohort 的局部检查，不能移作历史 coverage。**IMPC** 1,049,082 条与 **Expression Atlas** 44,440 条日期未知，strict 规则会排除，但由于未定 `t0`，没有“最终排除数”。GWAS 的 `curationDate` 2,996,433/3,044,078，publication date 3,044,074/3,044,078；日期字段含义需要逐行版本核对。Gene Burden 44,555 条有 publication/evidence date，但项目与统计状态可能随版本变动。

## 历史版本、映射及禁止字段

[Open Targets 25.12 原件目录](https://ftp.ebi.ac.uk/pub/databases/opentargets/platform/25.12/output/)列有七条同名 `evidence_*` 来源；这证明存在一个早于 26.06 的**可定位快照候选**，不证明七条 26.06 行能逐行回溯，更不证明 2015/2020 等任意 cutoff 的覆盖。更早版本的 schema、ID 桥接、记录增删改与 source release 日尚未逐行重建。26.06 [官方数据说明](https://platform-docs.opentargets.org/data-access/datasets)也指出历史下载和当前 Parquet 的访问方式。逐源 JSON 的 `original_directory_url`、首末 Parquet URL、原 EXP017/019 URL 索引与 ontology 状态可追溯原件；`ontology_mapping_version` 目前仍是 26.06，不得回填为历史版本。

所有来源的 `score`、`resourceScore`、`qualityControls` 及来源特有 curation/方向字段，在没有历史版本证明时属于**当前版状态**。明确禁止 `clinical`、`overall_score`、旧 `label`/`phase`、当前最大临床阶段、批准标志、药物成功状态及 cutoff 后文献/指南/策展内容。旧 26.06 cohort 的来源支持 pair 数只记录在机器表的 `legacy_2026_cohort_supported_pairs_reference_only`，不得用于历史样本选择。

## 截止日账与裁决

`included_before_cutoff`、`excluded_after_cutoff`、historical eligible pairs/events 全部为 `null`：`OUTCOME_CHRONOLOGY.md` 已触发 `STOP_A`，无合法 cutoff、horizon 或当时 eligible universe。`null` 不等于 0；七源当前日期覆盖不能关闭时间泄漏门。时间锁后 CGC/Europe PMC 的增量、source ablation、污染注入与成熟曲线均未运行。即使未来定义新结局，也要先锁定当时 snapshot 或版本化记录，严格排除未知日期，核对 source 内容和 ontology 的历史状态，再创建新 split；本轮没有通过这一门。
