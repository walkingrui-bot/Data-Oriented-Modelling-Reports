# EXP088 报告：十四路CO校准有平均增量，开发日稳定门失败

**新真实问题。** [UCI487](https://archive.ics.uci.edu/dataset/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation)独立15分钟CO施加事件的同期十四路气敏能否在后续实验日，比训练内选出的最强传统单路/环境对照更准确地回归施加浓度？这是同装置、CO由流量控制器生成的回顾性校准；EXP087已审过各日来源目标，不是新未见标签确认。EXP086的原来源结构门失败不变。

**实做。** 所有13日×100预定事件原样入样，传感器/温湿度/流量/加热电压输入取每窗口中心段中位数及传感器IQR，不靠真实CO筛样本；标签是同中心CO中位数。7训练/3开发/3条件后续日，传统固定HGB；训练日四折按日CV从ENV及14单路选第11路，再和十四路比较。主指标日期等权MAE，三开发门为≥5%改善、三个日期全改善、≥7/10浓度水平改善。[计划](PLAN.md) · 事件派生 (source asset outside this public snapshot) · [选择](TRAIN_CV_SELECTION.json)。

**观察。** 1,300事件完全可算。开发日期MAE第11路0.327732ppm、十四路0.286666ppm，平均改善12.530%；9/10浓度水平改善。三天中两天改善，2016-10-08十四路0.213857ppm比单路0.211870ppm略差；因此冻结三门只通过2项，后续三日**没有评分**。[门](GATE_RESULT.md) · [派生指标](VALIDATION_METRICS.json) · 原输出 (source asset outside this public snapshot)。

**结论与路线。** 实验完成且局部工程有效，科学裁决`STOP_CO_MULTISENSOR_DEV_GATE`。在此受控腔室中有多路平均校准信息，但没有达到预设跨日稳定性，当前保持传感器11传统统计对照，不启Stat-MoE/Ganglion，也不归因于模型太小。要判断共享架构，必须另有独立、未用于此次源审与选择的数据条件；旧开发/条件留出不被重命名确认。
