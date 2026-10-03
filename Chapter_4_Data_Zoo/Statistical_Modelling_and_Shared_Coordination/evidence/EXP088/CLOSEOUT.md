# EXP088 关账

- 执行：`EXP088-STAT-001`一次完成；工程局部有效，源/1300事件/7-3-3日支持核验均过，60个train-CV+两最终模型拟合。局部派生复算13/13，无全仓门/哈希，原ZIP/txt未复制。
- 科学：开发平均MAE改善12.530%、9/10浓度水平改善，但仅2/3日改善，冻结三门2/3，`STOP_CO_MULTISENSOR_DEV_GATE`；后三日性能未评分。不能把平均改善升格为稳定模型或因失败猜容量。EXP086的两项旧失败原封保留，本ID也非独立确认。
- 证据：[计划](PLAN.md) · 日志 (source asset outside this public snapshot) · 原输出 (source asset outside this public snapshot) · 来源重核 (source asset outside this public snapshot) · 模型支持 (source asset outside this public snapshot) · 事件特征唯一派生 (source asset outside this public snapshot) · [train选择](TRAIN_CV_SELECTION.json) · 开发逐事件预测 (source asset outside this public snapshot) · [指标](VALIDATION_METRICS.json) · [局部复算](LOCAL_VALIDATION.json) · [门](GATE_RESULT.md) · [报告](REPORT.md)。
- 下一决策：不从同源已看开发与未评分后三日绕过停止。综合多真实任务的统计门，另立决策审计明确哪些通道有可留证据、哪些架构保持冻结；新科学任务需独立条件。
