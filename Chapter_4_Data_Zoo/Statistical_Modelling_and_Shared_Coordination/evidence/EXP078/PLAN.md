# EXP078 — 四年家庭电力分表能否超越总表历史预测下一小时功率

研究 ID `STAT-PSYMOE-EXP078-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_YEAR_HOLDOUT_MULTICHANNEL_STATISTICAL_TEST`；父=[EXP077真实来源门](../EXP077/CLOSEOUT.md)。用户授权真实研究自治并要求实践止损。科学问题：单栋家庭的**三回路分表**及其它电学读数，在过去总表和日历之外，是否改善下一小时总表有功功率预测，并跨整年时间外条件保持？它决定是否值得为该类任务建立额外channel state；先比较适当传统统计，绝不为架构制造增量。

## 数据、观察单位、时间锁

仅官方[UCI235原ZIP](https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption)内原TXT，内存流式读取，不保存原件副本。复核EXP077的成员名、九列、总行数及首末源日历；不匹配`STOP_SOURCE_VERSION_DRIFT`，不建模。只选源日历整点`:00:00`记录为起点，目标恰+60源日历分钟的`Global_active_power`，单位kW。一个评价日期最多24个相关小时，**日期**而非分钟是主独立评价块；不把小时数当独立家庭。目标年的2007–2008训练、2009开发验证、2010条件式测试，2006只供应历史lag；源时区未证，结论仅回顾性按源日历时间外。

起点的总表和六附加电学通道在`0,1,2,24,168`小时以前记录必须全部存在、解析有限且非负；目标总表也必须存在、有限、非负。缺失一律剔除该配对，不填0/插值。各历史时间用真实datetime键精确匹配，不用行偏移冒充时间；所有臂使用**同一完整样本**。目标时刻已知日历：时刻小时、星期、年内日的sin/cos各一对。基线`AR`为五个总表lag+六日历特征；`SUB=AR+三分表×五lag`（分表是分钟Wh，不和目标kW相加）；`ELECTRICAL=AR+反应功率/电压/电流×五lag`；`JOINT=AR+全部30额外lag`。PERSIST为总表起点值，无拟合只供描述。所有输入≤起点，不使用目标时刻测量。来源缺测模式可能选择样本，报告年度剔除数。

先审可建模支持：训练≥10,000配对及≥500目标日期；2009验证≥6,000配对及≥250日期；2010测试≥5,000配对及≥250日期；每个年份评价只纳入有≥18合法目标小时的完整目标日期。任何一项不符`STOP_HOURLY_MODEL_SUPPORT`，0拟合、0评分。此门不观察性能。

## 固定统计、选择与终止

四臂同规格`HistGradientBoostingRegressor(loss=absolute_error,max_iter=200,max_leaf_nodes=15,min_samples_leaf=50,learning_rate=0.05,l2_regularization=10,early_stopping=False,random_state=20261002)`，仅训练年拟合，输出截断到≥0。预算最多四次固定拟合，不调参。2009年各目标日期先算MAE kW再等权平均，附加候选在`ELECTRICAL,SUB,JOINT`中选日MAE最低，精确同分按此顺序；2000次日期成对bootstrap seed20261002给候选−AR MAE差95%区间。开发门：候选相对AR日MAE改善**≥5%**、差区间上界<0、至少**60%评价日期**改善。未全过即`STOP_ADDITIONAL_CHANNEL_DEV_GATE`，不评分2010模型表现。全过仅把AR/PERSIST和选中候选在2010一次评分，同三门全过才`ADDITIONAL_CHANNEL_YEAR_HOLDOUT_GAIN_SUPPORTED_WITHIN_ONE_HOUSE`，否则`NO_2010_CHANNEL_GAIN`，不得看test调参或换臂。

物理上总表含各回路分表，观察到增量不等于三条独立家庭样本或因果作用；即使通过，也只证明固定年份/住宅/任务的预测增量，不直接证明Stat-MoE或Ganglion。未过门不诊断容量大小，也不把EXP076同任务失败改写。

## 尝试与验证预算

预登记`EXP078-STAT-001`：`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_household_stats.py`；网络≤30MiB、内存≤1GiB、CPU≤20分钟、四个固定模型。输出`SOURCE_RECHECK.json`、`MODEL_SUPPORT.json`、条件式验证/测试逐日派生误差与指标JSON、`RUN_OUTPUT_001.txt`及关账，禁止原ZIP/TXT副本。局部只核来源、支持、候选选择/门及不当test评分；不跑全仓门、非必要哈希。若失败，关账并重新选择信息增益最高的真实问题。
