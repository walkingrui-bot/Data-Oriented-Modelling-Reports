# EXP030 — GaitPDB 认知双任务同人配对来源门

研究 ID `STAT-PSYMOE-EXP030-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP029](../EXP029/CLOSEOUT.md)。这不是 EXP028 PADS M4 的外部验证。新的科学问题：在官方 [PhysioNet Gait in Parkinson's Disease v1.0.0](https://physionet.org/content/gaitpdb/1.0.0/) 的 PD 与健康组真实步行数据里，是否存在足够多**同一人**的普通步行与 serial-sevens 认知负荷步行原始记录，并能从官方原件明确识别任务、组别、传感器、时间和主体？若是，可另立模型实验比较人级认知双任务响应；若否，不推断任务效应或以不同人伪配对。

官方首页称总共 93 PD、73 HC 来自三项研究，且**部分**人有做 serial sevens 的第二任务。总人头不是配对人头。H1：至少 20 个不同 PD 人和 20 个不同 HC 人具有清楚标识的一人两任务配对、可原位读取的足底力 100Hz 记录和可核的组别；H0：配对支持不足或任务/ID语义无法识别，使双任务差异不可检验。20/组仅是继续到谨慎的探索性配对统计设计的最小数据门，不表示正式效能充分，更不能支撑临床泛化。

## 冻结审计

1. 只读官方 v1.0.0 目录/文件清单、页面所链元数据或格式说明。逐源建立 `subject_id`、PD/HC、普通步行文件、serial-sevens 文件、任务定义、研究来源、文件可达状态；同人的重复 visit 不算新 subject。只要任务映射依赖文件后缀猜测而无官方解释，标 `UNRESOLVED_TASK_SEMANTICS`，不计合格配对。
2. 抽固定排序前 2 个有候选配对的人，每人两文件只读首/末少量行或 HTTP range，验证时间单调、至少 16 足底力通道和实际 100Hz 附近；不保存原始记录。若目录/网页不支持范围读取且完整文件总量超预算，保留未验证，不私自放大下载预算。
3. 资格门 PD≥20/HC≥20 个不同人同人两任务、官方组别与任务意义可定位、至少固定两人四文件局部数值可达。任一失败即停止 `PAIRED_DUAL_TASK_COHORT_NOT_IDENTIFIED`，不以总数93/73或多 visit 凑门。通过只称 `PAIRED_DUAL_TASK_SOURCE_READY_FOR_MODEL_DESIGN`；本轮不训练、没有效应或验证结果。

来源预算 ≤20 URL 请求、≤5 MiB 内存读取；只保存派生索引与 URL，不下载整个288MB数据包/复制源文件。不计算非必要哈希、不跑全仓门。预期输出 `SOURCE_INDEX.md`、`PAIR_AUDIT.csv`、`WORKLOG.md`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`；每尝试先登记，异常保留。若通过，后继新 ID 冻结配对统计模型、人级分割、对照和止损；若未通过，按用户自治授权再选信息增益更大的真实问题。
