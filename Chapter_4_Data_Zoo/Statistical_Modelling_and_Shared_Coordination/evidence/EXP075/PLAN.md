# EXP075 — 真实住宅用电未来一小时来源与时间门

研究 ID `STAT-PSYMOE-EXP075-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_TEMPORAL_SOURCE_AUDIT`；父阶段 [EXP074](../EXP074/CLOSEOUT.md)WISDM跨设备无标签片段门未过。新科学问题：一个实际建筑的设备用电、九处室内温湿度与外部天气是否能组成**明确先后顺序、真实未来结局**的时间划分任务，供下一实验检验额外传感器/天气相对惯性统计基线的价值？选此源因为共同日期轴和连续计量结局能避开WISDM跨设备时钟/标签分段阻断；它是单住宅，不能推广到其他建筑。

## 来源、语义与准入规则

[UCI374 Appliances Energy Prediction官方页](https://archive.ics.uci.edu/dataset/374/appliances-energy-prediction)称19,735个10分钟观测、约4.5个月、室内ZigBee传感器与电表、机场天气按时间合并且部分**小时天气先插值**；变量`rv1/rv2`是随机测试变量，永不入特征。原CSV `energydata_complete.csv` 只从官方 `https://archive.ics.uci.edu/static/public/374/appliances%2Benergy%2Bprediction.zip` 内存读取，不保存ZIP/CSV副本。许可页CC BY4.0，保留Candanedo 2017、DOI `10.24432/C5VC8G`及天气分发获许可事实。原日期时区与各列精确可用时刻未给出，不能把此回顾性表格冒充历史实时流；后继即使建模也限回顾性时间外评价，不称运营预测。

目标定义在来源审计阶段先固定：行`i`日期为`t`，只要行`i+6`恰为`t+60min`且其`Appliances`实际非缺/有限，形成真实下一小时 Wh 标签；`i`是起点，`i+6`是真目标。下一实验的基线可用截至起点的历史设备用电，额外来源仅起点及更早室内/天气；不把未来表列、`lights`或随机`rv1/rv2`作特征。数据观测单位是10分钟行/后续结局，评价独立不确定性至少按**日期块**而不是行；单建筑不产生多独立建筑。

以全部有效源行日期升序，**按目标行位置**冻结train前70%、validation接着15%、test最后15%；起点必须早于目标且恰隔60分钟。这样训练标签不跨入验证/测试目标时段；验证/测试可使用其起点之前已观测能耗做lag，等价按时序更新。来源审计只计各域合格目标/不同源日期及字段质量，不计算模型或test误差。

冻结门：原件可解、必需列`date,Appliances,T1..T9,RH_1..RH_9,T_out,Press_mm_hg,RH_out,Windspeed,Visibility,Tdewpoint`存在（来源文字说明把CSV的`T_out`称`To`，按实际CSV表头识别）；日期唯一且严格升序，≥19,000源行、相邻恰10分钟比例≥99%；源值所需字段完整有限行≥95%，`Appliances`不能为负；恰60min真实目标配对占可用起点≥99%；train有效目标≥10,000且不同日期≥60，validation/test各≥2,000且不同日期≥20。任何一项失败 `STOP_ENERGY_CHRONOLOGY_OR_SUPPORT`，不训练。全过 `REAL_ENERGY_TEMPORAL_SOURCE_READY_FOR_STAT_DESIGN`；这仅说明回顾性共同时间轴与样本支持，**不是**历史实时可用性/多建筑确认。

预登记尝试`EXP075-SOURCE-001`，命令`python3 audit_energy_source.py`，网络≤20MiB、内存≤256MiB、CPU≤5分钟；保存`SOURCE_MATRIX.json`、`RUN_OUTPUT_001.txt`、门/报告/关账，原源只路径引用。仅局部派生验证，无全仓门/哈希。若过门，新ID再固定合理自回归/室内/天气统计模型及日期块验证与止损门；不为Ganglion制造增量。
