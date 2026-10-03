# EXP079 — 下一小时真实高负荷事件是否需要分表通道

研究 ID `STAT-PSYMOE-EXP079-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_YEAR_HOLDOUT_EVENT_CLASSIFICATION`；父=[EXP078](../EXP078/CLOSEOUT.md)。这是**新结局**而非EXP078的门槛修订：总表连续功率平均MAE上三分表仅0.54%开发改善，未达实用门。当前重要未知是附加回路是否在*高负荷事件*而非平均误差上有足够价值；结果过门会支持任务特定事件channel，未过门则暂停单栋电力新增通道，不继续换小门槛或扩容。2009连续MAE已看，本ID只能作具名探索，不能追认原ID或称独立确认。

## 真实结局、时间与样本

仅官方[UCI235](https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption)原ZIP/TXT流式读取，不落地原件。复用EXP078已冻结的源整点、真+60分钟目标、0/1/2/24/168小时完整lag、四臂同一完整样本、目标年2007–08训练/2009开发/2010条件式test和日期≥18小时评价日；其脚本函数直接引用，保留同源恢复依赖。来源重核与样本门仍须通过：训练≥10,000配对/≥500天、2009≥6,000配对/≥250评价日、2010≥5,000配对/≥250评价日，否则零模型。

新事件阈值只从**2007–08合格训练目标**求第90百分位，`numpy.quantile(method="linear")`，严格冻结事件定义为未来目标`Global_active_power ≥ threshold`；训练/验证/测试阈值相同，不用后年分位或当前总表生成标签。它只表示本住宅训练期上十分位负荷，**不称危险或电网过载**。训练事件≥1,000且2009验证事件≥400才拟合；不为开发门查看2010事件数或模型分数。真实缺测仍剔除，不填零；所有特征≤起点。

## 固定统计与门

`AR`五个总表lag+六日历、`SUB=AR+三分表各五lag`、`ELECTRICAL=AR+反应功率/电压/电流各五lag`、`JOINT=AR+两组`，与EXP078同特征合同。四臂同规格`HistGradientBoostingClassifier(max_iter=200,max_leaf_nodes=15,min_samples_leaf=50,learning_rate=0.05,l2_regularization=10,early_stopping=False,random_state=20261002)`，仅训练年拟合，不调参。只供描述的常数对照为训练事件率。主指标：各评价目标日先算二元log loss，再日等权；模型概率统一裁到[1e−6,1−1e−6]。辅指标：完整评价日所有小时的average precision（PR-AUC）。按2009日等权logloss选`ELECTRICAL→SUB→JOINT`中最低者（精确同分按此顺序），2000日期成对bootstrap seed20261002求候选−AR logloss差95%区间。

2009开发四门同时通过才评分2010：相对AR日logloss改善**≥5%**；差区间上界<0；**≥60%评价日期**改善；候选PR-AUC较AR提高**≥0.02绝对值**。失败即`STOP_EVENT_CHANNEL_DEV_GATE`，2010不评分。通过后只对AR/常数/选中候选一次评分2010，同四门都过才`EVENT_CHANNEL_YEAR_HOLDOUT_GAIN_SUPPORTED_WITHIN_ONE_HOUSE`；任意失败为`NO_2010_EVENT_CHANNEL_GAIN`，不看test重选或调参。即使过门也只表示这栋房子的任务特定预测信息，不证明Stat-MoE/Ganglion或其他住户普适性。

## 预算、尝试与关账

预登记`EXP079-EVENT-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_power_events.py`；网络≤30MiB、内存≤1GiB、CPU≤20分钟、最多四次固定拟合。输出`SOURCE_RECHECK.json`、`MODEL_SUPPORT.json`、`EVENT_SUPPORT.json`、验证逐日派生误差与指标、条件式test文件、原`RUN_OUTPUT_001.txt`及门/报告/关账。只做局部派生指标/门复核；不跑全仓门或非必要哈希。若开发门失败，**该单栋家庭电力附加channel路线暂停**，下一新ID应换有不同真实观测单位或结局机制的数据，不再用本2009期反复选任务。
