# EXP085 关账

- 状态：`EXP085-STAT-001`一次完成；来源/模型支持通过、固定34次拟合、validation/test各一次评分。局部派生复算14/14通过；未运行全仓门/哈希，也未保存第二份原ZIP/txt。
- 科学：验证三门3/3，留出2/3；logloss改善但BAcc增益0，故`NO_TEST_MULTISENSOR_GAIN`。不能更改已看test的门、不能据此称Stat-MoE/Ganglion有收益。失败层级是预定决策指标的留出保持，不是来源、训练不收敛或容量诊断。
- 原件索引与证据：[计划](PLAN.md) · 日志 (source asset outside this public snapshot) · 原输出 (source asset outside this public snapshot) · 来源 (source asset outside this public snapshot) · 支持 (source asset outside this public snapshot) · 试验派生特征 (source asset outside this public snapshot) · [train选择](TRAIN_CV_SELECTION.json) · 验证预测 (source asset outside this public snapshot)/[指标](VALIDATION_METRICS.json) · 留出预测 (source asset outside this public snapshot)/[指标](TEST_METRICS.json) · [局部验证](LOCAL_VALIDATION.json) · [门](GATE_RESULT.md) · [报告](REPORT.md)。
- 新研究路线：源层寻找独立连续浓度/时间事件任务，区分“概率改善”与“可用硬决策”；新ID、新门，不追认本留出。
