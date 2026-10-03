# EXP063 关账

- 原问题：北京原 N1 能否不拟合地理运输到独立 UK-AIR 伦敦区域同定义真实缺测 24 小时任务，并稳定胜过无拟合 B0？
- 唯一尝试 `EXP063-TEST-001`：按[原计划](PLAN.md)及[环境补充](AMENDMENT_001.md)执行。十站原年度文件再次内存读取 16,285,763 字节，来源计数/状态/单位与 EXP062 相同，667对逐站相同；模型参数只引用 EXP060 原件。输出 SOURCE_RECHECK.json (source asset outside this public snapshot)、[METRICS.json](METRICS.json)、PREDICTIONS.csv (source asset outside this public snapshot)、原终端 (source asset outside this public snapshot)。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_FROZEN_EXTERNAL_SCORE / ZERO_SHOT_N1_TRANSPORT_NOT_SUPPORTED`。B0 MAE 5.578，N1 14.386；日区块差+8.808、区间[+6.673,+11.100]；0/10站改善。四门全失败，不改门、不调外部数据。
- 已知：直接北京参数运输在该十站 2024 任务明显劣于最小基线；N1 预测水平均值23.424、真实9.275。这个实验是实际模型检验，已看的 2024 不能再叫未见确认。
- 未知：最小本地校准或完整本地同形式统计在独立未来年份是否可用；水平偏差的具体归因；自然缺失机制、实时历史状态、仪器差异。不能由此诊断共享宽度因果原因或宣称其它模型必胜。
- 决策：停止该零样本参数运输，保留 B0；下一新 ID 先审 2025 同定义事件和时间语义，若可行再开独立训练/未来评价。不给 Ganglion 任何新增资格。
- 局部复算[12/12](LOCAL_VALIDATION.json)；不训练、无全仓门、无非必要哈希。
