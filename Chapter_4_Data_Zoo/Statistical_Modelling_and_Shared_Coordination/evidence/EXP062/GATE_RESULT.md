# EXP062 冻结来源门

2026-10-02；官方 [AURN PM2.5 目录](https://uk-air.defra.gov.uk/networks/find-sites?view=advanced)按[计划](PLAN.md)的固定伦敦区域框和 [ID crosswalk 补充](AMENDMENT_001.md)执行。目录返回全国 199 站，区域框内 20 站，全部逐站处理；无不可解析 ID 或网络错误。年度原文件 21,833,755 字节内存读取，未建立原数据副本。来源矩阵与时间/状态见 SOURCE_MATRIX.json (source asset outside this public snapshot)，名单和坐标见 DIRECTORY.json (source asset outside this public snapshot)。

| 事前门 | 实得 | 判定 |
| --- | ---: | --- |
| ≥9 站各有 ≥6,000 个 2024 已核定、有限非负 PM2.5 小时值 | **10 站**：BDMP、CA1、BEX、CLL2、HRL、HIL、HP1、MY1、KC1、THUR | 通过 |
| 本站当前真空 PM、精确24小时后本站真目标、≥8 合格邻站同刻真值的配对 ≥100 | **667** | 通过 |
| ≥5 个目标站各 ≥10 个合格配对 | **10 个站**；最少 BEX 12、最多 MY1 249 | 通过 |

667 对分布在 133 个目标起点日期；同一日/小时和多站强相关，**不能当 667 独立样本**。区域外框包含 Borehamwood Meadow Park 和 Thurrock；这是“伦敦区域”而非行政大伦敦样本。门通过只证明**可做新 ID 外部评价**，不是北京模型泛化成功。2024 年度文件为当前取得的历史观测快照，不保证 2024 实时可用。未读任何模型外部误差。配对支持 (source asset outside this public snapshot) · [局部核验 13/13](LOCAL_VALIDATION.json)。

结论：`AURN_LONDON_REGION_SOURCE_READY_FOR_FROZEN_N1_TEST`。
