# EXP021 时间线候选数据字典

版本：`EVENT-A-007`，2026-10-02；仅来源级原申请/产品批准候选，**未通过人工门**。所有原始 FDA ZIP/CSV/XLSX、批准信与网页只按官方 URL 读取，未存副本。本目录只保留派生状态、来源索引和失败见证。完整源版本、URL、Last-Modified、读取时间、表列和行数见 SOURCE_INDEX.json (source asset outside this public snapshot)。

## 来源与转换

| 来源 | 本轮字段与单位 | 转换与边界 |
| --- | --- | --- |
| FDA Drugs@FDA ZIP `Submissions.txt` + `Applications.txt` | `ApplNo`, `SubmissionType`, `SubmissionNo`, `SubmissionStatus`, `SubmissionStatusDate`, `ApplType`；application–submission | 仅 NDA/BLA `ORIG` + `AP` + 精确日；排除 ANDA、非批准、Purple 精确 BLA 号标 351(k)、MEDGAS。application 日不能自动分配给同申请下的后来规格。`ApplicationDocs` type 1 `Letter` 仅是链接候选。 |
| FDA Orange Book ZIP `products.txt` | `Appl_Type`, `Appl_No`, `Product_No`, `Approval_Date`, `Ingredient`, `Trade_Name`；product | 仅 `N` NDA 和可解析四位年日；`A` ANDA 与 `Approved prior to Jan 1, 1982` 精确日缺失项排除；MEDGAS 申请排除。`Approval_Date` 是该产品批准日，不代表所有适应症获批日。 |
| FDA Purple Book August 2026 CSV + 同月 XLSX | BLA、Product Number、License Type、Submission Type、XLSX `Approval Date`；product | CSV 只核 section/行数与许可类别；XLSX 显示完整四位年份，选 351(a) + Original；351(k) biosimilar 排除。先前 CSV 两位年解析失败见证保留于 `derived/failed_EVENT_A_005/`。 |

转换脚本：`derived/source_probe.py`、`derived/build_event_a.py`、`derived/repair_event_a_metadata.py`。最终 A-007 从 A-006 仅修正 metadata 语义，事件 ID、日期、行数和跨来源 audit 未更动。诊断与排除计数见 `derived/EVENT_A_DIAGNOSTICS.json`。`crosswalk_audit.csv` 从同一版本 A-006 来源事实生成，适用于 A-007。

## `derived/REGULATORY_EVENT_A.parquet`

一行是**一个来源级候选**，并非独立 drug–indication event。15,399 行，13,517 NDA、1,882 BLA；5,702 application scope、9,697 product scope；事件 ID 唯一。三源行数分别 5,702 Drugs@FDA、8,209 Orange、1,488 Purple。可见 5,376 个 NDA 与 774 个 BLA application number；不同来源/规格/提交不得相加为独立转译成功。

| 字段 | 语义 |
| --- | --- |
| `event_id` | `FDA:ORIG`, `FDA:ORANGE` 或 `FDA:PURPLE` 加来源原键和日构成的本地候选 ID；仅本轮版本内稳定。 |
| `application_number`, `application_type`, `product_number` | FDA 6 位 application / NDA 或 BLA / 3 位 product；application 行 product 留空。 |
| `drug_name`, `active_ingredient` | Orange/Purple 源原药名/成分；Drugs application 行留空，不跨产品推断。 |
| `fda_event_type`, `event_scope` | 原申请 AP、NDA 产品批准、351(a) biologic 产品许可；`APPLICATION` 与 `PRODUCT` 不可混同。 |
| `approval_date`, `occurrence_date`, `date_precision` | FDA 源给的事件日期与现实发生日候选；均 ISO YYYY-MM-DD，精度 `DAY`。不是 indication-specific date。 |
| `public_date` | 公众首次可知日；当前无可靠证据，全部空。 |
| `database_ingest_date` | FDA 内部数据库实际收录日；当前未知，全部空。 |
| `retrieved_at` | 本轮 agent 读取源的 UTC 时间；与发生、公示和 FDA ingest 均不同。 |
| `approval_source`, `source_record_id`, `source_url`, `source_file`, `source_release_last_modified`, `transformation_script` | 来源类型、原键、原 URL、文件、HTTP Last-Modified 与转换代码，可追到原件；Last-Modified 不是每条事件的公示日。 |
| `submission_type`, `submission_number`, `submission_status`, `submission_class`, `license_type` | Drugs ORIG/AP 的原字段、Purple 351(a)，未知 BLA 许可类别标 `UNKNOWN`；目前 24 条 Drugs-only BLA application 的许可类别未知。 |
| `linked_letter_url`, `linked_letter_record_date`, `linked_letter_role` | `ApplicationDocs` 中同 submission 的 type-1 Letter 链接候选及该表记载的文档日；统一标 `UNVERIFIED_TYPE_1_LETTER`。可含更正信/Medication Guide 信，不等于 original approval letter/public date。 |
| `identity_rule`, `exclusion_reason` | 本轮 exact FDA number/product join 与许可不明标记；入表行 `exclusion_reason` 留空，排除类别计数在诊断 JSON。没有 fuzzy auto-match。 |

## `crosswalk_audit.csv`

10,998 行以 product 候选与同 application Drugs ORIG/AP 日期比较，再记录 Drugs-only app。状态 `MATCH`、`DAY_LEVEL_DIFFERENCE`、`CONFLICT`、`SOURCE_ONLY`。最终诊断 JSON 分别为 7,019、5、1,622、2,352。`left_scope=PRODUCT` 对 `right_scope=APPLICATION` 的 `CONFLICT` 只表示日期不一致，晚批准规格可能合规；不能自动判谁错误。保留 `left_date` 与 `right_dates` 原值、多值、差日、source record ID、人工状态。审计中的 exact 是 FDA application number exact，非 ChEMBL 药物身份 exact。

## `MANUAL_VALIDATION.csv`

固定 `MANUAL-A-003` seed 20261003 的 70 条审查：`review_type`、`record_id`、automated/source 值、FDA URL、`verified_value`、`source_excerpt`、`match`、`issue_type`、`note`、HTTP/retry、reviewer。`MATCH` 只表示该条原件核对支持；`UNVERIFIED` 是证据不可达/不可读；`INDETERMINATE` 是有双边证据但无法裁定。39/50 原始样本匹配，11/50 未裁定；20 冲突没有产品级裁决。首次失败样本在 `derived/failed_MANUAL_A_002/`。该 CSV 不存 FDA PDF 或 HTML 全文，只存核查所需短摘录与原 URL。

## 条件性输出未创建

`drug_identity.parquet`、`drug_target_map.parquet`、`drug_indication_map.parquet`、`regulatory_events.parquet`、`trial_events.parquet`、`drug_indication_timeline.parquet` 均未运行、未创建。不能从其缺席推断真实数据零条。旧 26,235 target–disease cohort 也未作为本轮 FDA universe 的纳入条件。
