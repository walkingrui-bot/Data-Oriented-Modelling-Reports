# EXP078 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_YEAR_HOLDOUT_MULTICHANNEL_STATISTICAL_TEST`；执行`COMPLETE` / 工程`VALID_SCOPED` / 科学`SMALL_SUBMETER_DEV_SIGNAL_BELOW_PRACTICAL_GATE`。
- 原问题/计划：单栋总表下一小时kW，三分表/其它电学量是否在自回归历史之外提供足够年份时间外增量？[冻结计划](PLAN.md)，单模型尝试`EXP078-STAT-001`；0模型配置修订或重试。原输出 (source asset outside this public snapshot)。
- 全部尝试：主分析`EXP078-STAT-001`完成；局部复算`EXP078-QA-001`因`numpy.bool_` JSON写入错误无效、无核验文件，`EXP078-QA-002`仅修输出类型完成[11/11](LOCAL_VALIDATION.json)，未重训。详工作日志 (source asset outside this public snapshot)。
- 已知：完整lag后的样本门通过；2009年SUB较AR日MAE改善0.5400%、区间上界<0，但198/355天改善；5%幅度和60%日期门失败，[门](GATE_RESULT.md)。PERSIST对照较差仅为2009验证描述。
- 未知：2010模型性能、跨家庭效应、不同事件结局、在线可用性。2010仅核来源/样本支持，绝不称独立预测确认；容量原因不可识别。
- 停止层级/后继：统计实用幅度和稳定日数失败；平均功率预测附加channel暂停。新ID可针对真实高负荷事件检验尾部信息，无论结果均改变是否建任务特定通道的决定。
- 本次验证：原件来源重核、四臂拟合与2009逐日指标、局部11/11；未评分test，未运行全仓门或非必要哈希。
- 原ZIP/TXT没有复制，本地仅脚本/派生支持、逐日误差、原输出和关账，未声明异地备份。
