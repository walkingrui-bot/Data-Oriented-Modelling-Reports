# EXP022 来源语义修订 001

记录时间：2026-10-02，人工门抽样之前。性质：本轮探索中看到源字段分布后，对原指导中“Purple Original 月报行可直接称 BLA_ORIGINAL_LICENSURE”的实际编码边界作保守修订；**EXP021 文件、门与结论均不修改**。

旧意图：Purple Book 351(a) Original 产品记录有 `Approval Date`，看作 BLA 原始许可。新观察：同月 XLSX 的 1,488 条此类产品行属 750 BLA，其中 5 个 BLA 的产品行有不同日期；BLA 125789 官方[产品详情页](https://purplebooksearch.fda.gov/index.cfm?blaNo=125789&event=productdetails)给 `Original Approval Date = 2024-08-01`，而月表同时有 2026-06-17；BLA 103955 官方[详情页](https://purplebooksearch.fda.gov/index.cfm?blaNo=103955&event=productdetails)给 2000-03-17，月表还有 2000-07-17。BLA 102219 的[详情页](https://purplebooksearch.fda.gov/index.cfm?blaNo=102219&event=productdetails)甚至给 1974-03-12，而月表该 BLA 有 1930-06-14，说明简单 `min(Approval Date)` 也不是可靠的 BLA 原始许可规则。`Date of First Licensure` 仅 38 产品行非空，且其法规语义独立。

新约定：月表中的 351(a) Original 行编码为 `BLA_PRODUCT_ORIGINAL_SUBMISSION_APPROVAL`；只有官方详情页 BLA 级 `Original Approval Date` 能编码 `BLA_ORIGINAL_LICENSURE`。未取到详情页时该事件缺失，不用月表日期冒充。月表原行仍可形成产品范围事件。影响：EXP021 的 1,488 行不能自动升格 BLA 级原始许可；本轮高置信 BLA 原许可数量取决于页面可用性和人工语义核验，STOP_D/E 风险增大。已看数据如上；新 Gate A/B 样本未选，后续门不追认到 EXP021。
