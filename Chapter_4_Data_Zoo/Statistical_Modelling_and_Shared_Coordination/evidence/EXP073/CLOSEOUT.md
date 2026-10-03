# EXP073 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_FOUR_SENSOR_SOURCE_AUDIT`；执行`COMPLETE` / 工程`VALID_SCOPED_SOURCE_AUDIT_AFTER_TWO_PARSER_CORRECTIONS` / 科学`STOP_FOUR_SENSOR_18_CLASS_SUPPORT`。
- 原问题：51人×18活动的四路手机/手表记录是否具备冻结的同人同类时间交叠与≥40人支持？[原计划](PLAN.md)科学门不变。
- 尝试：001活动键仅认8码，失败JSON (source asset outside this public snapshot)/原输出 (source asset outside this public snapshot)；002认17码、缺G，失败JSON (source asset outside this public snapshot)/原输出 (source asset outside this public snapshot)；两次均未扫描原始传感器数据，属解析无效；[AMENDMENT_001](AMENDMENT_001.md)与[AMENDMENT_002](AMENDMENT_002.md)只修键文本解析；003认全18码并完成所有204文件，原输出 (source asset outside this public snapshot)。
- 有效观察：原件四文件×51人存在，918人×活动组中901组四路跨度交叠=0，17不可算；全18类按原四路交叠门合格0人。即忽略跨设备时钟，四路≥500行的全18类人也仅39，仍<40。源派生矩阵 (source asset outside this public snapshot) · [裁决](GATE_RESULT.md)。
- 失败层：跨设备时间轴不兼容及全18类逐人支持不足；不是模型容量/训练失败。不能用强行偏移或删类补本实验，不把缺失记零。
- 未知：是否有官方可识别时钟校准事件、局部同刻同步、跨设备episode级统计是否有增量。没有任何模型成绩或外部确认。
- 后继：新科学问题可以明确以人×活动片段为单位、只比较分设备统计摘要；先审选定活动子任务独立人支持，再设计统计对照。旧门/两解析失败保留。
- 实际验证：官方来源成员/活动行审计与派生一致性[7/7](LOCAL_VALIDATION.json)。仅静态核官方说明/许可。未验证模型、配窗、全仓。
- 本地工件仅本目录的计划、脚本、原输出、失败/有效派生JSON、修订、门/报告/关账，均未跟踪；原ZIP/PDF/时序仅URL和成员路径引用，未复制或异地备份，无哈希保证。入口与登记册同步。
