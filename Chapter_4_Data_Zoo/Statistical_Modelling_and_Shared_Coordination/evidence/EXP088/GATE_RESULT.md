# EXP088 开发门裁决

UCI487原件与EXP087全部13日×100窗口的行数和CO中心中位数逐项重核；源/模型支持门全过。训练前7日700事件，开发中3日300，后续3日300仅审支持。train-only 15候选（ENV+14单路）四折按日CV共60拟合选传感器11，再按冻结同规格HGB各拟合最强单路与十四路。来源 (source asset outside this public snapshot) · 支持 (source asset outside this public snapshot) · [train选择](TRAIN_CV_SELECTION.json)。

开发三日日期等权MAE：`SENSOR_11` **0.327732ppm**，十四路 **0.286666ppm**，点改善12.530%。十个浓度水平中9个改善；但只有2/3日改善，2016-10-08十四路0.213857ppm劣于单路0.211870ppm。预冻三个开发门中幅度与浓度层通过、**逐日全过失败**，裁决`STOP_CO_MULTISENSOR_DEV_GATE`；后续2016-10-13/14/16没有模型性能分数。逐事件预测 (source asset outside this public snapshot) · [验证指标](VALIDATION_METRICS.json) · 原输出 (source asset outside this public snapshot)。

这只是探索性按后续日任务；EXP087源审已列出全部CO标签，不能称独立未见标签确认。EXP086两源门失败仍保留。不能把平均12.53%改善写成稳定通过，不能因为一日轻微恶化调整已冻结门、阈值、模型容量或共享矩阵。13项局部复算通过。[局部验证](LOCAL_VALIDATION.json)。
