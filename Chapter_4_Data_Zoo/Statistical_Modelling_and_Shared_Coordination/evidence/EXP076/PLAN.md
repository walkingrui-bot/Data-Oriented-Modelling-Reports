# EXP076 — 下一小时用电：室内与天气相对自回归统计的时间外增量

研究 ID `STAT-PSYMOE-EXP076-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_TEMPORAL_HOLDOUT_STATISTICAL_TEST`；父阶段 [EXP075](../EXP075/CLOSEOUT.md)官方来源与时间门通过。用户授权自治研究、要求真实实践及时止损。科学问题：单栋实际住宅的**九处室内温湿度**或**机场天气**，在历史设备用电与已知日历之外，是否提供跨后续日段保持且足以支付额外来源成本的下一小时用电预测信息？这决定该任务中是否值得建立额外channel state；先测传统统计，不为共享架构造题。

## 真实输入、目标和时间锁

仅官方 [UCI374原件](https://archive.ics.uci.edu/dataset/374/appliances-energy-prediction)，不保存原ZIP/CSV副本。保留EXP075以**目标行位置**定义的train70%/validation15%/test15%切点；目标为`Appliances(i+6)`，要求源日期恰为起点`i`后一小时。构造时只允许起点`i`或更早记录：自回归`Appliances`在`i,i−1,i−3,i−6,i−12,i−144`（当前、10/30/60/120分钟及前一日），目标时刻的小时/星期的sin/cos（提前可知），室内`T1..T9,RH_1..RH_9`及天气`T_out,Press_mm_hg,RH_out,Windspeed,Visibility,Tdewpoint`一律取`i−6`（比预测起点早一小时），排除`lights,rv1,rv2`。因此首144个起点无完整lag则不入模型；不把其缺失填0。天气原小时值被插值，`i−6`滞后一小时仅降低未来值混入风险，仍不能证明当年实时可用；结果限定**回顾性时间外评价**。单建筑的相邻行非独立，主统计按目标日期等权。

来源结构先与EXP075重核：19,735行、首末日期、必需列、i+6真目标/划分行数一致；不一致`STOP_SOURCE_VERSION_DRIFT`，无模型。建模样本的分段仍按目标行位置，不让训练标签跨入验证/测试时期；验证/测试的滞后特征可以使用其起点之前实际已观测的能耗。只从train拟合任何统计参数。

## 传统方法、对照、门槛

无拟合PERSIST：预测值等于`Appliances(i)`。固定非神经非参数统计 `HistGradientBoostingRegressor(loss=absolute_error,max_iter=200,max_leaf_nodes=15,min_samples_leaf=50,learning_rate=0.05,l2_regularization=10,early_stopping=False,random_state=20261002)`，目标直接为Wh，所有模型预测截断到≥0。四臂同配置：`AR`上述lag+日历、`INDOOR=AR+18室内`、`WEATHER=AR+6天气`、`JOINT=AR+全部24附加测量`。不调参，不新增NN；模型成本记录输入列数与拟合秒数，若结构不收敛/异常记录失败。

验证/测试只统计各自**目标日期至少100个合法配对**的日期（边界残缺日期不参加主指标，仍保留计数）；按日MAE先求每天平均再对日期等权平均。三个附加候选在validation按日等权MAE选最小，精确同分优先`WEATHER→INDOOR→JOINT`，不看test选。对所选候选与AR，2000次按日期成对bootstrap（seed20261002）求MAE差95%区间；开发门需候选MAE相对AR改善**≥5%**、差区间上界<0、至少**60%评估日期**改善。未全过则`STOP_ADDITIONAL_CHANNEL_DEV_GATE`，不评分test。全过仅将AR/PERSIST与选中候选在test一次评分，test同三门全过才`ADDITIONAL_CHANNEL_TEMPORAL_GAIN_SUPPORTED_WITHIN_ONE_HOUSE`；否则`NO_TEMPORAL_HOLDOUT_CHANNEL_GAIN`，不得调整test。即使增益过门，也要比较选中通道与单通道/联合信息，不直接认为Ganglion有价值；跨房屋、实时运营、因果效应均不在本ID。

预登记尝试`EXP076-STAT-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_energy_stats.py`，网络≤20MiB、内存≤1GiB、CPU≤20分钟，最多4个固定HGB拟合。输出源重核、`VALIDATION_METRICS.json`/逐日派生误差、条件式test指标/逐日误差、原终端输出和关账，绝不保存原CSV副本。局部仅复算少量指标/门，禁全仓门和非必要哈希。若不通过，不归因于模型容量小、不在旧test上反复调参；自主转向下一真实未知。
