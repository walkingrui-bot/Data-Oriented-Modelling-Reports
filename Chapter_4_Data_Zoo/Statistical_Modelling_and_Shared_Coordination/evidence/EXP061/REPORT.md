# EXP061 报告：伦敦预选 2024 子网不能承载原八邻站任务

问题是北京 EXP060 的 N1 邻站统计能否在独立城市的**同定义自然缺测**配对上接受检验。UK-AIR 官方 2024 年度逐小时文件有明确 GMT 小时结束时刻、状态及单位；十二个事前站号都取得了原文件，官方 [年度文件页](https://uk-air.defra.gov.uk/data/flat_files?site_id=HRL) 与 [许可说明](https://uk-air.defra.gov.uk/about-these-pages)可追溯。按已核定 `R`、有限非负 PM2.5、原位明确空字段严格计算，只有八个站具备事前规定的每站至少 6,000 个有效小时。它们彼此最多提供七个邻站，故符合北京原任务 ≥8 邻站的真实缺测配对为 **0**。来源矩阵 (source asset outside this public snapshot) · 配对分解 (source asset outside this public snapshot)。

在 `t` 明确缺测且 `t+24h` 有已核定本站目标的起点中，仍有 581 个真实事件；其中 485 个有七邻站、87 个六邻站、9 个五邻站。它们证明有不同的外部问题可做，但不能被追认成原八邻站外部检验。本 ID 的固定来源门未过，**不运行模型**，不将北京 N1 迁移能力写成已验证。[冻结门](GATE_RESULT.md)。

失败层级是这组预选站的**样本/网络支持**。下一信息增益问题应是用官方完整站点目录审查 2024 伦敦是否还有足够已核定 PM2.5 站，而不是在这 12 站降低邻站数；若完整目录仍不足，则关停同定义伦敦外部任务，另找可识别 endpoint/cohort。时间与来源语义已掌握，测站之间仪器 `Ref.eq` 和 `BAM` 的可比性还未作独立定量校准；本轮受站数门阻断，不据此裁定仪器互换或部署效用。

实际运行：两次来源尝试，第一次路径选择误将年度与 15 分钟同名文件看作歧义，完整保留；第二次明确年度 `/site_data/` 并完成十二站审计。仅核验本区域派生计数与门 11/11；没有外部预测、Ganglion、全仓测试或哈希。原输出首次 (source asset outside this public snapshot) · 原输出重试 (source asset outside this public snapshot) · [关账](CLOSEOUT.md)。
