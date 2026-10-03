# EXP070 关账

- 登记/状态：2026-10-02 BST；`EXPLORATORY_EXTERNAL_COHORT_SOURCE_AUDIT`；执行 `COMPLETE` / 工程 `VALID_SCOPED_SOURCE_AUDIT_AFTER_PARSER_CORRECTION` / 科学 `PAIRED_SOURCE_SUPPORT_ESTABLISHED_ONLY`。
- 原问题：独立人群是否有足够同人、同活动的真实手机加速度/陀螺仪来源支持？[事前计划](PLAN.md)及来源/预算门未改。
- 全部尝试：`EXP070-SOURCE-001`下载成功但活动键解析空映射，**无效解析**，其自动`STOP`不作科学裁决，失败派生状态 (source asset outside this public snapshot)、原输出 (source asset outside this public snapshot)保留；[AMENDMENT_001](AMENDMENT_001.md)只改格式解析；`EXP070-SOURCE-002`重新下载/全51人原位审计通过，原输出 (source asset outside this public snapshot)。
- 已知：51/51人三类×两路满足各≥1000有效行及跨度交叠≥0.5；实际每路最少3568行，最小比0.999253；0目标无效/错ID，三个活动各2个邻行时间倒序。活动键确证三类。[门](GATE_RESULT.md) · 逐人派生矩阵 (source asset outside this public snapshot)。
- 未知：精确时间配准、10秒双路合格窗数、传感器是否提供独立预测信息、任何模型稳定性与跨场景泛化。跨度交叠不能冒充配准。与UCI240标签/设备/预处理不完全同构。
- 决策：来源门通过；下一新ID冻结排序/时间交集/窗密度、按人开发及传统统计对照。失败层级001为解析，002来源已通过；未训练NN或扩共享矩阵。
- 本次实际验证：脚本语法、来源全51人抽取、派生逻辑[8/8](LOCAL_VALIDATION.json)。仅静态检查官方许可/说明。未验证配窗、模型、全仓门。
- 工件：本目录计划、脚本、失败与有效派生输出、原终端输出、修订、门/报告/关账均本地未跟踪；官方原件URL保留，未建ZIP/原始行副本或异地备份。重做依赖官方URL当前可访问且内容不变；无哈希版控。入口/登记册同步。
