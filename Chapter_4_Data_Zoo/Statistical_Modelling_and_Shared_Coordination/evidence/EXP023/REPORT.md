# EXP023 当次 FDA Label 适应症事件可识别性报告

研究 ID `STAT-PSYMOE-EXP023-20261002-001`，2026-10-02，`EXPLORATORY`。本轮按冻结的 20+20 第一阶段来源门停止：原申请仅 12/20、efficacy supplement 仅 17/20 具有同一 application/submission key 的 FDA Label URL，低于每层 ≥18/20 可读完整标签的必要上限。**当前抽样范围的数据支持不足；适应症事件仍未识别。**

问题是同一次已批准 action 能否找到当次标签及 `INDICATIONS AND USAGE` 文本。使用 EXP022 原位监管表与 [FDA Drugs@FDA 官方 12 表定义](https://www.fda.gov/drugs/drug-approvals-and-databases/drugsfda-data-files)，再次在内存中读取同一来源版本的 class/document lookup；`EFFICACY=2`、`Label=2`。全表中符合 EXP022 高置信监管应用范围的 ORIG 已批准 action 有 4,398（4,354 application），efficacy SUPPL 已批准 action 有 5,185（1,793 application）。同一 key 有 Label URL 的应用分别为 2,682、1,473。URL 是文件候选，不是文档角色或可用日期的确认。

样本在 [SAMPLE_FREEZE.md](SAMPLE_FREEZE.md) 中先冻结，40 个 application 无交集并排除先前人工已看记录，按最早合格 action 的确定规则和固定 seed 选出；SAMPLE.csv (source asset outside this public snapshot) 保留全部包括无 URL 的记录。原申请样本跨 1959–2024 年，较早 action 多无 Label URL；本轮未按年份重新筛选或补抽。因来源链接上限已经低于冻结门，没有发起样本文档下载，不能声称正文是否可读或是否包含新适应症。

失败层级是 **data availability / sample support**，不是统计模型失败。结论只适用于本轮跨全年份的 cohort 和预设门。下一最有信息增益的独立问题是较近批准年份能否形成同时具 action 与当次 Label 的真实队列；需另立 EXP024 并预先冻结年份、抽样和停止规则，不在本轮改 gate。EXP022 的 `REGULATORY_EVENT_LAYER_READY` 仍限原来源事件层；EXP020/021 的停止也保持原样。
