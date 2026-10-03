# EXP059 关账

- 原问题：目标站当前PM原始自然缺测时，真实24小时未来标签、本站气象和同刻邻站观测是否有足够交集？它用于判断是否值得建立新多源任务，非原药物模型的外部确认。
- 唯一尝试`EXP059-SOURCE-001`：官方ZIP一次在内存读取；12站/420,768原行，五域合格数3,185/1,286/85/277/16。聚合见SOURCE_SUPPORT.json (source asset outside this public snapshot)和站年计数 (source asset outside this public snapshot)；无原件副本。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_REAL_SOURCE_AUDIT / NATURAL_OUTAGE_SOURCE_READY_FOR_DESIGN`；五域和逐站最低来源门通过。[门](GATE_RESULT.md)。
- 已知：真实自然NA与真24h标签有交集，10训练站和验证站均有支持；2017两整站极小，缺失选择机制未知。
- 未知：邻站/气象哪个通道有独立预测增量、时序相关下收益是否稳定、共享神经核心是否额外有用、外部城市泛化。
- 不可做的结论：来源门通过=模型通过，或把16条未来×整站pair当独立外部确认。旧EXP048域已看，同源后继均须标探索。
- 下一问题：在同一真实自然缺测pair上冻结邻站简明基线、本站气象单通道、两者联合的传统统计；先检验互补信息是否足以改变架构决策。另立ID，不为启动NN而降低门。
- 局部验证6/6见[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)；未训练、未运行全仓门/哈希。
