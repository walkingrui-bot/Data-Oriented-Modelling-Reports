# EXP064 — 2025 伦敦区域自然缺测未来年份来源门

研究 ID `STAT-PSYMOE-EXP064-20261002-001`；2026-10-02；`EXPLORATORY_FUTURE_YEAR_SOURCE_AUDIT`；父阶段 [EXP063](../EXP063/CLOSEOUT.md) 北京 N1 零样本外部运输失败。新科学问题：在同一 UK-AIR 伦敦区域十个 2024 合格站中，2025 年能否提供**此前未评分**的真缺测 24 小时任务，供 2024 本地传统统计训练后的时间外评价？这先审来源，不训练，不读取 2025 模型误差。

## 固定站与原件

站号固定为 EXP062 PAIR_SUPPORT.json (source asset outside this public snapshot) 原合格十站：`BDMP CA1 BEX CLL2 HRL HIL HP1 MY1 KC1 THUR`；不根据2025数据增删候选。每站从官方 `flat_files?site_id=` 页面选 `/site_data/<ID>_2025.csv`，≤十页面+十 CSV、总≤30MiB、每请求30秒、CPU≤15分钟，内存解析不存原 CSV。年度文件须明确 GMT hour ending、R/P 状态、PM2.5 单位 `ugm-3`；2025 非闰年网格 8,760 个小时结束点，从 2025-01-01 01:00 GMT 至 2026-01-01 00:00 GMT，`24:00` 为次日零时。只计 `R`、有限非负 PM；明确空 PM 字段是自然缺测，整行不存在、临时状态或负值不等价。

配对沿原定义：目标站 `t` PM 字段明确空、`t+24h` 有已核定真值，其他2025合格站 `t` 至少8个已核定真值。资格门先要求原十站中至少**九站**各有≥6,000个 2025有效小时；再要求≥100个配对、≥5个目标站各≥10对、≥30个不同预测起点日期。缺任何一项则 `STOP_2025_NATURAL_OUTAGE_SUPPORT`；来源时钟/状态无法辨识或文件读取不全则 `STOP_2025_SOURCE_SEMANTICS`。通过才 `2025_NATURAL_OUTAGE_SOURCE_READY_FOR_LOCAL_STAT_TEST`；来源PASS不表示模型有效。不能改2025年份、补插缺测、降邻站数来过门。

尝试 `EXP064-SOURCE-001` 执行前登记；命令 `python3 audit_2025_source.py`，输出 `SOURCE_MATRIX.json`、`PAIR_SUPPORT.json`、`RUN_OUTPUT_001.txt`、门/报告/关账及局部检查。EXP063 的 2024 外部评分已暴露，只能作为后续训练/开发事实，不得在看2025模型结果后重选或追认确认资格。2025 文件也是现在取得的回顾性已核定资料，不宣称2025当时数据库状态。用户 EXP022 后研究自治及近期实践止损授权该新问题。若门过，下一实验以2024为本地训练、2025为前瞻时间留出，优先传统统计。
