# EXP067 关账

- 原问题：起报时可知的目标站连续停测年龄是否能为B0形成跨2024/2025稳定的高误差拒用候选？
- 唯一尝试 `EXP067-RISK-001`：两年20官方CSV原位内存重读37,144,253字节，与原预测和来源逐站一致；计算到`t`为止的明确空字段连长，保留左删失/中间组。SOURCE_RECHECK.json (source asset outside this public snapshot)、RISK_ROWS.csv (source asset outside this public snapshot)、原输出 (source asset outside this public snapshot)。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_RETROSPECTIVE_RISK_AUDIT / NO_REPEATED_LONG_OUTAGE_RISK`。两年分组支持门过，但2024长/短MAE比1.182区间跨零；2025比0.579且方向相反；冻结风险门失败。[门](GATE_RESULT.md)。
- 已知：不能依据简单≥6h年龄规则自动拒用B0；两年组间目标水平不同，当前分析不能识别停测因果机制。
- 未知：其它已知质量信号、实时源状态、独立年份的B0边界。不能因回顾性分层否定或确认普遍部署安全。
- 决策：关停此阈值路线，B0仅作为当前真实任务的简明基线，不加后验年龄规则。若继续系统研究，新 ID 应转向真正未反复使用的真实 outcome/来源和预定对照，不为Ganglion造题；前述失败保持。[报告](REPORT.md)。
- 本区域局部核验[11/11](LOCAL_VALIDATION.json)；无新训练、全仓门或非必要哈希。
- Living Report 已以新版本0.24 (source asset outside this public snapshot)追加 EXP023–067 路线与当前决策，渲染核验 (source asset outside this public snapshot)独立留档；旧v0.23保留。
