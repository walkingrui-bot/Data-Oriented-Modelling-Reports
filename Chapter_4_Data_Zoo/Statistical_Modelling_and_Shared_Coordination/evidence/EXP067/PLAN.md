# EXP067 — 已知停测长度下 B0 的真实误差边界

研究 ID `STAT-PSYMOE-EXP067-20261002-001`；2026-10-02；`RETROSPECTIVE_REAL_MISSINGNESS_RISK_AUDIT`；父阶段 [EXP066](../EXP066/CLOSEOUT.md)2026当前已核定网络不足。EXP065 已停止自然缺测24小时 MAE 模型升级、B0为默认。新科学问题：对**起报时已知**的目标站连续停测年龄，B0 在较长停测时是否有跨 2024/2025 重复的明显误差风险，值得为默认基线建立拒用候选条件？结果能改变“B0是否无条件使用”工程决定；这是已看两年上的回顾性适用边界分析，不声称新外部确认，也不重新训练/调整模型。

## 原件、真实单位和防泄漏定义

只引用 2024 EXP063 派生预测 (source asset outside this public snapshot)及 2025 EXP065 派生预测 (source asset outside this public snapshot)中的 B0/真目标；它们分别是原同十站已核定、目标当前明确空、未来24小时真目标、≥8邻站同刻已核定的667/589个配对。用两年 EXP062 (source asset outside this public snapshot) 与 EXP064 (source asset outside this public snapshot) 原 CSV URL 再次内存读取，仅恢复目标站截至起报时`t`的原 PM 空字段历史；逐站时钟/状态/单位及配对数先精确复现，否则 `STOP_SOURCE_VERSION_DRIFT`。

“停测年龄”定义为目标站从最近一个**明确非空或不同状态的已出现小时行之后**到`t`、连续明确空 PM 字段的小时数，含`t`；只用`t`及更早的源字段，不看后续停测终点或未来目标。若该空段在年度网格首小时开始，或其前一小时行不存在，则其开始时刻不明，该配对列为`LEFT_CENSORED_OR_UNKNOWN_START`，不进入主比较，仍计数。目标日与源文件小时语义按原实验，不把 `P` 或缺整行当实测/明确空。2024/2025 当前回顾性核定记录**不等于当时实时可用的缺测告警流**；仅评可计算的回顾性风险标记。

## 事前对照、门和预算

主比较每年分别：短停测 `age=1–2h` 与长停测 `age≥6h`；中间3–5h另报、不纳入主比较。主指标 B0 原单位绝对误差 MAE；同时报告每组配对数/不同日期/目标站数/真实目标均值，避免把污染水平差异误读为停测因果。先有支持门：**每年短组与长组各≥30配对、各≥3目标站、各≥20个起点 GMT 日期**；缺则 `STOP_OUTAGE_AGE_SUPPORT`，不作风险门。支持通过后，`LONG_OUTAGE_B0_RISK_REPEATS_EXPLORATORY`需两年都满足长组/短组 MAE 比≥1.5，且按预测起点日一起重抽全部站行的1000次 bootstrap（seed20261002）所得长−短 MAE 差95%区间下界>0。任一失败则`NO_REPEATED_LONG_OUTAGE_RISK`。这只是描述性关联；即使过门也只能产生候选拒用条件，不能宣称长停测造成错误或具备实时部署资格。不能看结果后改6小时阈值或过门年份。

尝试`EXP067-RISK-001`事前登记，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python audit_b0_outage_age.py`；二十原CSV≤50MiB、CPU≤20分钟。输出`SOURCE_RECHECK.json`、`RISK_ROWS.csv`（只保存配对派生年龄与原B0误差，不存源数据副本）、`METRICS.json`、原输出、门/报告/关账和局部验算。两年 B0 已看，分析标 `RETROSPECTIVE`，不能把2025称新确认，不在本ID拟合拒用阈值或调用Ganglion。若支持不足或无稳定风险，则本条默认B0继续限定在原来源与评价域，不制造额外复杂规则。
