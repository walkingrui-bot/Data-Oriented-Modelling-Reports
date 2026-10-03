# EXP021 EVENT_A 人工核查门冻结

冻结时间：2026-10-02，`EVENT-A-005` 自动分布已看、人工样本和任何审批信 PDF 尚未选择/核查。性质：`EXPLORATORY` 的事前人工抽样门，不回写为 EXP020 或历史确认判据。

已看分布：5,784 Drugs@FDA NDA/BLA ORIG/AP application event、8,209 Orange NDA product event、1,488 Purple 351(a) Original product event；unique application NDA 5,458 / BLA 774。跨 application 与 product 的 exact application number 日期比较：MATCH 7,019、1-day difference 5、CONFLICT 1,622、SOURCE_ONLY 2,434。`CONFLICT` 在此尚不表示 FDA 数据错误；产品增补规格晚于申请初批可能是正当差异。FDA 批量源仅证明 occurrence date，尚无可靠 `public_date`。

## 固定抽样及判定

- seed `20261002`。从有独立 approval letter 的 Drugs@FDA accepted ORIG/AP 申请中无放回取 NDA 30、BLA 10；从 Purple 351(a) original product 中取 10 个不同 BLA，优先 Drugs 不在的来源独有 BLA，官网产品详情页核原始批准日。此是分层且有原件可达条件的样本；报告该偏倚，不外推为全 universe 错误率。若某链接失效，原样记该条不可核，不补选以使结果好看。
- 另从 1,622 个 `CONFLICT` 中以同 seed 无放回抽 20，独立检查 Orange 产品记录、Drugs ORIG 申请记录和与产品日期相符的 supplement/doc（若存在），逐条分类 `LATER_PRODUCT`, `TRUE_DATE_DISAGREEMENT`, `INDETERMINATE`。不将 application 日强塞为 product 日。若链接不可达，记录证据缺口。
- 每条记录检查 application/BLA number、product number（适用时）、ORIG/351(a) action、日期、来源 URL、证据文本/位置。A 主样本若 50 中关键身份/approval 日期/原始 action 错误超过 1，或独立原件验证成功少于 45，`MANUAL_A` 不通过。冲突样本必须 20/20 有明确证据状态；不能裁决的条目留 `INDETERMINATE` 并从任何可用时间链排除，不以猜测填充。所有主/冲突样本写 `MANUAL_VALIDATION.csv`。
- 对符合上述局部门的 A 候选，才可开始 EVENT_B 探索；后续 `CHRONOLOGY_READY_FOR_MODELLING` 仍必须独立满足用户十项总门。人工样本无法证明未抽样行的历史公示日、适应症或靶点。

停止／预算：主样本与冲突样本官方原件若明显不可达或系统性 OCR 无法识别，原结果和失败保留，必要时 STOP_1/5；本轮 PDF/页面合计网络读取不超 4 GiB，单链接重试最多一次。若原件日期与汇总表有实质冲突，不以页面最新版覆盖历史原行，记录双边值。
