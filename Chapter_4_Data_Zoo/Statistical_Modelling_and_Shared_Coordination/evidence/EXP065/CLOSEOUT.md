# EXP065 关账

- 原问题：只用伦敦区域2024真缺测配对拟合简单统计，2025同定义时间外能否稳定胜无拟合B0？单截距、单特征与八特征谁提供额外价值？
- 唯一尝试 `EXP065-STAT-001`：按[PLAN.md](PLAN.md)固定公式与门；官方两年原CSV20文件内存读取37,144,253字节、来源/配对与 EXP062/064 精确复现；2024 667对拟合 C0/M1/L1，2025 589对只评分。新状态唯一MODEL_STATES.json (source asset outside this public snapshot)，旧北京N1仅原路径引用；逐对派生预测 (source asset outside this public snapshot)、原输出 (source asset outside this public snapshot)。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_REAL_TEMPORAL_EVALUATION / NO_LOCAL_STAT_CANDIDATE_QUALIFIED_FOR_2025_MAE`。2025 B0/C0/M1/L1 MAE4.094/4.159/4.028/4.112；C0/M1/L1固定门全失败，L1对M1额外门失败。[门](GATE_RESULT.md)。
- 已知：2024训练内拟合三候选皆胜B0，但2025没有一条保持预定幅度、区间与逐站稳定性；M1点收益1.62%不够。本任务 B0 默认，不启Stat-MoE或Ganglion。
- 未知：增量不稳定的具体机制，独立第三年份是否改变结论，其他损失/任务的价值。2025已看，不能再作为新模型的未见确认；回顾性档案不能冒充历史实时状态。
- 决策：停止这条自然缺测24h MAE任务的模型升级，保持原结果和失败。若继续，用新 ID 先审2026来源或转向新的真实科学问题；不要继续在已看2025上调模型。后续优先寻找能真正改变工程决定的未见域；不为了证明架构而改门。
- 局部复算[12/12](LOCAL_VALIDATION.json)；无全仓测试、非必要哈希。
