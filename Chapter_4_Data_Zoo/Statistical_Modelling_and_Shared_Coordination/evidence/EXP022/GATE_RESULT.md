# EXP022 人工门与监管事件层判定

冻结依据：[GATE_FREEZE.md](GATE_FREEZE.md)，两组新样本选取前记录；BLA 页级补充抽检另见 [BLA_PAGE_QA_FREEZE.md](BLA_PAGE_QA_FREEZE.md)。本轮是 `EXPLORATORY` 的局部门评估，EXP021 的 STOP_5 不追改。

| 门 | 冻结判据 | 本轮结果 | 判定 |
| --- | --- | --- | --- |
| Gate A ETL fidelity | Orange 25 + Purple 25 + Drugs 25，75/75 全字段 exact | 75/75；源物理行、官方字段、派生值与逐条 agent 裁决见 `GATE_A_SAMPLE.csv`、`GATE_A_REVIEW.csv` | PASS |
| Gate B event semantics | 50 新样本 NDA 30/BLA 20，≥47/50 正确且灾难性 scope 错误 0 | 50/50、灾难性 0；Orange 是产品、Purple 月表是产品提交、Drugs 是 application action，`SUPPL` 不冒充原申请 | PASS_FOR_ENCODED_TYPES |
| BLA 页级补抽 | 25 个新 BLA 页号与 `Original Approval Date` 独立重读一致 | 25/25；另 4 已看异常全数重读，页级值再现但跨 scope 关系未裁决 | PASS_SUPPLEMENTARY_QA；4 异常 TIER_C |
| STOP_C 真正同范围冲突 | ≥100 合格同范围对时，未裁决差异须 ≤1%；少于 100 不报 0% | EXP021 10,998 比较均缺同产品/同 event class 双来源关系；合格对 0、真冲突率 NULL；真正冲突队列无 eligible 行 | STOP_C 未触发；冲突率未估 |
| STOP_D NDA/BLA 主类型 | 官方行/字段明确，BLA 级原批准至少 100 个 | NDA 8,209 产品行；Purple 官方 BLA 详情页 750/750 可读，746 进入 TIER_A，4 隔离 | 未触发 |
| STOP_E 规模 | NDA ≥1,000 产品事件、BLA ≥100 原始许可 | NDA 8,209 / BLA 746 | 未触发 |

结论：`REGULATORY_EVENT_LAYER_READY` **限于本轮的来源语义监管事件层**。`REGULATORY_EVENT_HIGH_CONFIDENCE.parquet` 包含 8,955 个来源事件 ID，不是 8,955 个独立药物或 drug–indication 成功。TIER_A 不要求 Drugs action、Orange/Purple 和文件签署日相等；官方单源字段定义加当前 ETL/语义抽检是本轮资格依据。`TRUE_DATE_CONFLICTS.csv` 只有表头表示旧比较中没有合格同范围配对，**不是 0% 冲突率**；如将来得到产品级独立来源，须另做真正同范围核验。

本结论不能写成 `CHRONOLOGY_READY_FOR_MODELLING`：indication、target、disease、历史 first-public、follow-up/censoring 均未建。没有训练预测模型，亦没有回头修改 EXP021 的 39/50 STOP_5。人工抽样在不同应用号上无放回，并排除 EXP021 两批已看记录；125 条 A/B 样本均不同应用号。样本准确率不能自动外推成全体零错误。
