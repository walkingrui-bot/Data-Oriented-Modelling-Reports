# EXP022 来源语义数据字典

所有数据位于本研究目录；官方 ZIP/XLSX/HTML 原件按 URL 和源行键引用，没有本地复制。每个 Parquet/CSV 是本轮不同语义或阶段的唯一状态；旧 EXP021 文件只读。`source_snapshot` 是 HTTP Last-Modified/长度或页面实际读取时刻的记录，不等于历史首次公开版本。字段缺失使用 NULL 或空字符串，必须按列说明理解；空白不是零或失败。

## 核心表与单位

| 文件 | 行单位 | 关键解释 |
| --- | --- | --- |
| `derived/SOURCE_SEMANTIC_CANDIDATES.parquet` | Orange NDA `(application, product)` 8,209；Purple August 月表 `(BLA, product, Original submission)` 1,488 | 独立产品源行，`quality_tier=PENDING_MANUAL_GATES` 是建设阶段原状态。Purple 行不等于 BLA 原始许可。 |
| `derived/FDA_APPLICATION_ACTION.parquet` | Drugs@FDA NDA/BLA submission action 87,291 | `event_type=FDA_APPLICATION_ACTION`；status、class、ORIG/SUPPL 分列；`approved_status_code` 只反映 `AP`，不变成产品/许可日。 |
| `derived/REGULATORY_DOCUMENT.parquet` | Drugs@FDA document metadata 74,005 | `verified_document_role=UNKNOWN` 全部；文件日期不是 event date，Letter 类型不自动成为原批准信。具体 URL/ID 在本表。 |
| `derived/BLA_ORIGINAL_LICENSURE_CANDIDATES.parquet` | 官方 Purple BLA 详情页一 BLA 一行 750 | BLA 级 `Original Approval Date`；4 与月表产品日期关系异常保留。网页 `retrieved_at` 不作 first-public。 |
| `derived/REGULATORY_EVENT_HIGH_CONFIDENCE.parquet` | 8,209 NDA 产品 + 746 BLA 级原始许可，唯一 `event_id` | 全部 TIER_A；4 BLA 异常不入表。产品事件与许可事件并列而不合成统一药物获批日。 |
| `derived/NDA_FIRST_OBSERVED_PRODUCT_APPROVAL.parquet` | 有精确 Orange 产品日的 NDA 一行 4,099 | TIER_B，当前快照的产品最小日；`is_derived=true`，不是 FDA 原始 application approval truth。 |
| `derived/NDA_APPLICATION_TIMELINE.parquet` | Orange 产品与 Drugs action 的 NDA 并集一行 5,620 | 4,099 有 exact Orange 产品日，1,521 无；首日/后续产品日期、ORIG/SUPPL action 和 document ID 各自分列。 |
| `derived/BLA_LICENSE_TIMELINE.parquet` | August 2026 的 750 个 351(a) BLA 一行 | 页级原始日期、月表产品日期、名称、Drugs action 与 document 索引独立；746 TIER_A，4 TIER_C。 |
| `EVENT_SCOPE_AUDIT.csv` | EXP021 原 crosswalk 的每一行，10,998 | 旧日期结果只作历史列；新 `exp022_scope_class` 显式区分产品 vs application action。 |
| `TRUE_DATE_CONFLICTS.csv` | 具同 application + product + event class 的日期差异队列 | 当前 0 个**合格比较对**，故只有表头；真冲突率 NULL，不能解释为零错误。 |

## 高置信事件字段

`event_id` 为本轮源行/页面范围唯一键，不是药物 ID。`drug_regulatory_id` 是 `NDA:<6位申请号>` 或 `BLA:<6位号>`，仅监管身份，不等于 ChEMBL drug。`application_no` 与 `product_no` 保留官方编号；BLA 级许可的 `product_no` 为 NULL。`event_type` 限 `NDA_PRODUCT_APPROVAL` 或 `BLA_ORIGINAL_LICENSURE`，`event_scope` 分别为产品强度/剂型途径或 BLA license。`event_date` 是相应官方结构化产品日或 BLA 详情页标示的 Original Approval Date。

`document_date`、`document_signature_date`、`public_first_date` 在高置信表均为 NULL；不能把 `event_date`、HTTP `source_release_date` 或 `retrieved_at` 偷换为这些日期。`source`、`source_url`、`source_file`（如该表有）、`source_row_key`、`source_snapshot`、`retrieved_at`、`transformation_script` 提供来源定位。Orange 行的 `ingredient`、`trade_name`、`dosage_route`、`strength` 是源字段原义；BLA 级许可行不从当前产品名字反向填当时名称。`quality_tier=TIER_A` 意味本轮来源语义/ETL 门通过，不意味着历史时锁、适应症或模型资格。

## 日期差异分类

`DIFFERENT_SCOPE_EXPECTED` 仅表示产品日晚于全部已连接 Drugs 原申请 action 日，产品和 application 本属不同单位；**没有**据此确认具体 supplement。`UNRESOLVED_SCOPE` 包括同日、产品较早及夹在多个 action 日之间，因为日期相等也不能证明是同一产品事件。`SOURCE_ONLY` 表示没有连接的另一类来源 action。当前旧 audit 没有可支持 `SAME_SCOPE_MATCH` 或 `SAME_SCOPE_DATE_DIFFERENCE` 的精确同范围配对。四个 Purple 页与月表产品日期的异常是 BLA license vs product scope，留 TIER_C，不算自动判源错误。
