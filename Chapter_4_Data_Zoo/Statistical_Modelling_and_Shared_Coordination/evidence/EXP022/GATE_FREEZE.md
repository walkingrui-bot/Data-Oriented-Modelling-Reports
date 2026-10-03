# EXP022 人工门与停止判据冻结

冻结时刻：2026-10-02 15:27 UTC；已看官方源结构、EXP021 历史人工记录和 EXP022 全表**自动分布**，尚未选择/查看 EXP022 Gate A 或 Gate B 的样本 ID。登记性质 `EXPLORATORY` 中前瞻冻结的两个新人工门；不追认 EXP021。

已看分布：Orange NDA 产品 8,209 行/4,099 NDA；Purple 351(a) Original 产品 1,488 行/750 BLA；Drugs NDA/BLA application action 87,291 行；文档元数据 74,005 行。EXP021 10,998 crosswalk 中按 scope 重新分类：`DIFFERENT_SCOPE_EXPECTED 1,615`、`UNRESOLVED_SCOPE 7,031`、`SOURCE_ONLY 2,352`；旧 1,622 个 CONFLICT 变成 1,612 个产品较晚的不同范围与 10 个未解范围。当前可比较的精确同范围跨来源对数 0，真实同范围冲突率**不可估计**。Purple 750 BLA 中 5 个有多个月表 `Approval Date`，已见五个详情页实例；这些五个 BLA 以及 EXP021 全部已看应用号不得进入新人工门。

## 抽样池和锁

- 先从 EXP021 当前与失败人工 CSV 的所有 `application_number` 构成旧已看 application 排除集，另排本轮五个定向诊断 BLA。所有本轮样本只从其余原位官方 snapshot 派生记录选；同一个应用号不跨门重用。
- Gate A 随机 seed `20261022`，无放回、固定顺序的分层抽样：Orange 25、Purple 25、Drugs 25（NDA ORIG 10、NDA SUPPL 10、BLA ORIG 3、BLA SUPPL 2）。样本键是来源物理行号+application+product/submission。抽中后不可因核对困难而换样。
- Gate B 独立 seed `20261023`，排旧样本与 Gate A 全部 application；Orange NDA 产品 15、Drugs NDA action 15（ORIG 7、SUPPL 8）、Purple BLA 产品 15、Drugs BLA action 5（ORIG 2、SUPPL 3），共 NDA 30/BLA 20。不得后看后重抽。
- 工具可辅助固定抽样、打开原件行、生成逐字段比对，但逐行 source 值与解释要由 agent 检查后写裁决；自动脚本 PASS 字样不等于人工审查。

## Gate A ETL fidelity

按官方同 snapshot 原始行逐条核 derived 的原始与标准化字段。Orange 核 application type/no、product no、ingredient、trade name、剂型/途径、强度、完整日；Purple 核 BLA/product、proper/proprietary name、351(a)、Original、剂型/途径、强度、完整日；Drugs 核应用类型/号、submission type/no/status/class/date。标准化只允许预定义补零与日期格式转换，不接受语义猜测。**75/75 全字段 exact** 才通过；否则 `STOP_A`，保留逐条差异并修 ETL，旧样本不可重新命名为通过。原件可读而导出表不一致是 ETL 失败；外部详情页 403 不算这个门，因为本门核下载的官方行。

## Gate B event semantics

对独立 50 行复核来源类型、事件单位与日期意义：Orange 只能是 NDA 产品批准；Purple 月表只能是 351(a) Original 产品提交批准，不自动是 BLA 级原始许可；Drugs 只能是 application/submission action，SUPPL 不当 ORIG，AP 状态不覆盖产品/许可日。最低 **47/50 分类正确且灾难性 scope 错误 0**。灾难性包括 ANDA 当 NDA、MEDGAS 当常规 therapeutic NDA、supplement 当 original、351(k) 当 351(a) 原始许可、文档类型 Letter 当获批事件、产品日直接冒充 BLA 级 Original Approval Date。若未达，`STOP_B`。可达官方月表/ZIP 原件为语义依据；外部 PDF/页面不可达留 `EXTERNAL_DOCUMENT_UNAVAILABLE`，不自动判错。

## 其它停止/通过规则

- `STOP_C`：若有不少于 100 个真正同一 application+product+event class 的独立来源对，未裁决日期差异超过 1%，则停止；少于 100 对时仅记冲突率不充分可估，不把 0 对说成 0% 冲突。
- `STOP_D`：若 NDA 产品批准或 BLA **原始许可** 主要事件缺少可直接定位的官方 source field/row，且无法形成至少 100 个独立、明确日期的 BLA 级 `Original Approval Date`，事件层不通过。月报产品行不能填补这个数。
- `STOP_E`：高置信产品/许可层少于 1,000 个 NDA 产品事件或少于 100 个 BLA 原始许可事件时，不足以继续下一轮 indication 重建。这是探索期、看过上列自动分布后、人工抽样前冻结的最低规模，不是事前确认样本量计算。
- 只有 Orange、Purple、Drugs 的 scope 均正确分开、两个新人工门通过、真正同范围日期问题没有未解决的实质队列、TIER_A 产品/许可表成立且未触发 STOP_C/D/E 时，才可宣称 `REGULATORY_EVENT_LAYER_READY`。即使通过也没有 indication/target/public-first/censoring，绝不称可建模。
