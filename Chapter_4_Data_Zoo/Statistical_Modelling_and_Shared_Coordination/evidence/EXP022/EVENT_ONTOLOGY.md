# EXP022 监管事件语义与分类规则

本文件在 EXP022 新人工样本选择前确立。它不改写 EXP021 的统一 EVENT_A 与 STOP_5，只定义本轮数据产品。来源层级证据是 [Orange Book 字段定义](https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files)、[Drugs@FDA 表定义](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)、[Purple Book 月报说明](https://purplebooksearch.fda.gov/index.cfm?event=downloads)及[用户指南](https://purplebooksearch.fda.gov/index.cfm?event=userguide)。

| 事件／证据类型 | 独立单位和日期字段 | 禁止推断 | 质量层 |
| --- | --- | --- | --- |
| `NDA_PRODUCT_APPROVAL` | Orange Book `Appl_Type=N`，`Appl_No` × `Product_No` × 剂型/途径 × 强度；`Approval_Date` 是该产品记录的 FDA 批准日。重复产品号时保留源行和差异，不静默去重。 | 不叫原始申请或适应症批准。排 ANDA、MEDGAS 与无精确日。 | 原件字段明确且 ETL 门通过后 `TIER_A`。 |
| `NDA_FIRST_OBSERVED_PRODUCT_APPROVAL` | 当前 Orange Book snapshot 中同 NDA 有精确日的产品批准日最小值；一个 NDA 一条，记录贡献产品 ID。 | 不自动叫 FDA original application approval；当前快照不代表历史首发公开。 | `TIER_B` 派生。 |
| `BLA_ORIGINAL_LICENSURE` | Purple Book 产品详情页 BLA 级 `Original Approval Date`，351(a) 且明确原始许可时一个 BLA 一条；记录页面 URL。 | 不从所有月报产品行直接复制；不与 `Date of First Licensure` 法规专用字段混同。 | 详情页实际可定位并核字段后 `TIER_A`；否则不造该行。 |
| `BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL` | Purple Book 月报底部全量区 351(a) + `Submission Type=Original` 的产品行 `Approval Date`；BLA × product × 剂型/途径 × 强度 × 日期。 | 不能逐行称 BLA 原始许可。BLA 102219 的部分月报行早于产品页的 Original Approval Date，是明示反例。 | ETL 与语义门通过后可作产品范围 `TIER_A`，不等于上行。 |
| `FDA_APPLICATION_ACTION` | Drugs@FDA `Submissions` 的 application × submission type/no × status，`SubmissionStatusDate`。`AP` 可附 `FDA_APPROVED_APPLICATION_ACTION` 标记。 | 动作日期不覆盖 Orange 产品日或 Purple 原许可日；`SUPPL` 不叫 original；MEDGAS、ANDA 保留旗标但不进创新市场进入层。 | 辅助来源事件，无自动市场进入资格。 |
| `REGULATORY_DOCUMENT` | Drugs@FDA `ApplicationDocs` 的 document ID、类型、文件日期和 URL；`verified_document_role=UNKNOWN`。实际读原文后才可能为 ORIGINAL_APPROVAL_LETTER / SUPPLEMENT_APPROVAL_LETTER / CORRECTION / LABEL / MEDICATION_GUIDE / OTHER。 | 文件类型名 `Letter` 不产批准事件；签署日不机械等于结构化 action date。 | 文件证据层。 |

日期：`event_date` 是当前官方结构化源行事件日期；`document_date` 只对应文档元数据/签署标记；`source_release_date` 使用官方 HTTP Last-Modified（只作当前端点修改时间，不推断原事件公示日）；`retrieved_at` 是本次读取；`public_first_date` 只有另有首公开证据才填，否则 NULL。

## EXP021 全表 crosswalk 重分类

旧 audit 左侧是 Orange/Purple 产品源行，右侧是 Drugs@FDA 原申请 `ORIG/AP` 动作。只有精确 application number 连接，右侧没有 product number、强度与途径对应关系。因此**同一天也不能升级为 SAME_SCOPE_MATCH**。新标签规则：

1. 无右侧动作：`SOURCE_ONLY`。
2. 有右侧动作且左侧产品日严格晚于所有右侧原申请动作日期：`DIFFERENT_SCOPE_EXPECTED`；产品后增与原申请可共存，标 `PRODUCT_LATER_THAN_APPLICATION_ACTION`，但不声称已查到具体 supplement。
3. 其余连接（同日、早于、夹在多个动作日之间）：`UNRESOLVED_SCOPE`；需产品与 submission 的精确 action 连接，不能从日期相等判同一事件。
4. 只有未来有精确 application + product + event class 的第二独立日期来源时，才允许 `SAME_SCOPE_MATCH` 或 `SAME_SCOPE_DATE_DIFFERENCE`；本旧 audit 不具备该条件。`TRUE_DATE_CONFLICTS.csv` 仅收后者；若可比较同范围对数为 0，则冲突率未识别，不报 0%。

所有旧 `MATCH`、`DAY_LEVEL_DIFFERENCE`、`CONFLICT` 仅保留为历史诊断字段。原日期、来源 ID、identity rule 与差值均保留。无法精确建立 scope 的日期先不 adjudicate 真伪。

高置信市场进入层的 NDA 来源为 Orange 产品行，BLA 原始许可来源为可核的 Purple BLA 详情页。Purple 月报产品行可以作为独立的 BLA 产品批准事件，但不能充当 BLA 原始许可行。TIER_A 不需要三源日期一致。跨来源差异仅作审计。
