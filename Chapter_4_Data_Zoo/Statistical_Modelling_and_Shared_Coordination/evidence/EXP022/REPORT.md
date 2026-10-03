# EXP022 来源语义监管时间线报告

研究 ID `STAT-PSYMOE-EXP022-20261002-001`；2026-10-02；`EXPLORATORY`。本轮结论为 **`REGULATORY_EVENT_LAYER_READY`，仅限监管来源事件层**。EXP021 的统一 EVENT_A 构建及人工门仍是 `STOPPED_AFTER_EVENT_A_MANUAL_GATE / CHRONOLOGY_NOT_QUALIFIED`；EXP022 另立问题、来源语义和人工样本，没有重判旧门。没有训练预测模型，仍不能写 `CHRONOLOGY_READY_FOR_MODELLING`。

## 为什么拆分后可以成立

[FDA Orange Book](https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files)的 `Approval_Date` 属于 NDA 产品行；[Drugs@FDA](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)的 `SubmissionStatusDate` 属于申请/提交动作；[Purple Book](https://purplebooksearch.fda.gov/index.cfm?event=downloads)月表的产品 `Approval Date` 与详情页 BLA 级 `Original Approval Date` 也不能无条件合并。EXP022 实际读了与 EXP021 索引 Last-Modified 和长度相同的四个官方端点，原 raw 只在内存中。五个 BLA 的月表 Original 产品行有不止一个日期；其中 [BLA 125789 详情页](https://purplebooksearch.fda.gov/index.cfm?blaNo=125789&event=productdetails)写 2024-08-01，月表另有 2026-06-17；[BLA 102219 详情页](https://purplebooksearch.fda.gov/index.cfm?blaNo=102219&event=productdetails)写 1974-03-12，月表另有 1930-06-14。因此简单复制或取产品最小日都不是安全的 BLA 原始许可规则。原意图和更正见 [AMENDMENT_001.md](AMENDMENT_001.md)。

采用明确的 [事件 ontology](EVENT_ONTOLOGY.md)：Orange NDA 产品批准、Purple 月表产品提交批准、Purple 详情页 BLA 原始许可、Drugs 申请动作和 FDA 文件证据分开。文件类型名 `Letter` 的角色默认 UNKNOWN；签署日、结构化事件日、源修改时间、检索时间、最早公开日分列。Orange 产品可派生 `NDA_FIRST_OBSERVED_PRODUCT_APPROVAL`，但只表示当前快照中最早可见的产品日。没有把申请日广播给产品或适应症。

## 实际规模与旧冲突重分类

| 指标 | 实际结果及单位 |
| --- | --- |
| Orange NDA 产品日期 | 8,209 行、8,209 不同 application/product 键，4,099 NDA；日期 1982-01-05 至 2026-08-28，早年 Orange 无精确日行不补日。 |
| Purple 月表 351(a) Original 产品 | 1,488 行、750 BLA；这是产品范围，不能逐行称 BLA 原始许可。 |
| Purple 官方详情页 BLA 原始许可 | 串行读取 750/750 唯一 BLA 页均得全年份原始日期；746 进入 TIER_A，4 个与月表日期范围异常留 TIER_C。 |
| 高置信来源事件 | `REGULATORY_EVENT_HIGH_CONFIDENCE.parquet` 8,955 唯一事件 ID：NDA 产品 8,209、BLA 原始许可 746。BLA TIER_A 日期 1924-03-13 至 2026-08-19；2010 年以来 NDA 产品 3,293、BLA 许可 389。不是独立药物数量。 |
| NDA 当前快照派生首产品日 | TIER_B 4,099 NDA；不叫 FDA 原申请获批日。NDA timeline 5,620 应用，1,521 无精确 Orange 产品日；688 个 NDA 有晚于首日的后续产品日期。 |
| 申请动作／文件元数据 | Drugs NDA/BLA actions 87,291 行，文件记录 74,005 行；全部 document role 保持 UNKNOWN。BLA timeline 750 行，其中 366 有 Drugs 原申请已批准 action，仍不把动作日覆盖页级许可日。 |
| EXP021 全部旧 audit | 10,998 行重分类：`UNRESOLVED_SCOPE 7,031`、`DIFFERENT_SCOPE_EXPECTED 1,615`、`SOURCE_ONLY 2,352`。旧 1,622 个 `CONFLICT` 中 1,612 是产品较晚的不同范围，10 个仍未解范围；没有继承为已证实 FDA 日期错误。 |

旧 audit 没有 application + product + event class 均相同的两个独立日期来源，所以真正同范围可比较对数是 0，`TRUE_DATE_CONFLICTS.csv` 为 header-only，**冲突率未识别而非 0%**。四个 BLA 页级/月表异常为 `019640`、`103352`、`125164`、`125422`，两侧值与定向复核见 `BLA_ANOMALY_REVIEW.csv`，未进高置信层。Purple 页级日期在 746 个 BLA 与至少一个月表产品日相同；这只是跨层一致性观察，不把月表产品行重新称许可事件。

## 人工门、失败和版本边界

固定种子与抽样规则先于本轮新样本写入 [GATE_FREEZE.md](GATE_FREEZE.md)。Gate A 从未看应用中抽 Orange 25/Purple 25/Drugs 25，逐字段对官方同 snapshot 原行：**75/75 exact**。Gate B 另抽 NDA 30/BLA 20 检查产品、许可、申请动作的事件语义：**50/50 正确、0 灾难性 scope 错误**。另对 25 个新 BLA 详情页使用不同 HTML 解析重读，**25/25** BLA 号与页级原始日期一致。样本均不与 EXP021 两批人工及本轮另一门重叠。此为样本核验，不能把全体未抽行的错误率声称为零。[门结果](GATE_RESULT.md)逐项列出。

串行逐页访问恢复了 EXP021 并发请求中 703 个 HTTP 403 的来源可达性，但旧 47/750 成功与 703 失败现场仍原样保留；新的 750/750 是本轮新访问证据。`BUILD-001` 在诊断 JSON tuple key 序列化时失败，且静态检查发现文档日期覆盖，五个失败产物留 `derived/failed_BUILD_001/`；`BUILD-002` 修正后新运行产出当前候选。没有删旧失败或以最终通过倒改旧尝试。

## 资格和下一科学边界

两个冻结主门、补充页级抽检与 NDA/BLA 最低规模均通过；STOP_A–E 未触发。`REGULATORY_EVENT_LAYER_READY` 表示在**当前源 snapshot 与上述 ontology**下可分别引用 8,955 条 NDA 产品/BLA 许可监管事件。这个数据层还没有 indication 文本、drug→target、疾病 ontology、NCT、first-public 历史锁、follow-up 或 censoring；这些缺项不由 TIER_A 标签弥补。下一科学问题是监管 action/当次 label 到 indication-specific 事件的可追溯连接，应另立实验 ID；本轮不自动把当前产品/许可日复制给任何适应症。详情及恢复路径见 [CLOSEOUT.md](CLOSEOUT.md)。
