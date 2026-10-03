# EXP081 — 城市三区下一小时负荷：他区与天气相对自身历史的真实增量

研究 ID `STAT-PSYMOE-EXP081-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_MULTI_ZONE_TEMPORAL_STATISTICAL_TEST`；父=[EXP080来源门](../EXP080/CLOSEOUT.md)。科学问题：Tetouan的三个真实配电分区，预测各区下一小时原始功率时，**另外两区的已观测负荷**或**源环境量**是否在该区自身历史/日历之外提供足够且跨后续月段保持的增量？先用传统统计决定是否需要新增channel；三分区同城，不当三座独立城市。

## 源、时间、单位、样本门

官方[UCI849 ZIP原CSV](https://archive.ics.uci.edu/dataset/849/power%2Bconsumption%2Bof%2Btetouan%2Bcity)只内存读取，不复制原件；实际双空格表头只折叠空白，日期锁定EXP080证实的`%m/%d/%Y %H:%M`，源时区/功率单位未知。重核唯一CSV、九列、52,416行、首末日期、十分钟严格连续、九列有限和三区非负；不符`STOP_SOURCE_VERSION_DRIFT`、0模型。目标为2017源日历起点`t`后真`t+60分钟`同一行三区功率。起点及真实历史lag精确按时间键取值，不用行偏移代替时间。

全部三区模型共用完整样本：每区自身和两区同刻负荷在`t,t−10min,t−60min,t−24h`必须存在、有限、非负；五环境变量只取`t−60min`（滞后一小时），目标三区`t+60min`均存在且有效。缺失不填0；仅有这些真实lag才入模。目标时间已知日历：小时/星期/年内日各sin/cos一对。所有预测特征≤起点，无目标时刻输入。各区`OWN=本区四lag+六日历`、`PEER=OWN+其他两区在t/t−60min四数`、`WEATHER=OWN+五环境滞后一小时`、`JOINT=OWN+全部上述九数`；PERSIST=本区`t`原功率无拟合。三臂比较用同一目标与样本，模型预测截为≥0，指标只称**原始源功率单位**。目标月1–8训练、9–10验证、11–12条件式test；相邻十分钟高度相关，以**目标日期**为主统计块。先核可建模支持：训练≥33,000配对/≥240日，验证≥8,500/≥60日，测试≥8,400/≥60日；验证/测试主评价日要求各日≥100合法十分钟目标。任一失败`STOP_MULTI_ZONE_MODEL_SUPPORT`，0拟合。

## 固定模型/对照/开发门

三区各四臂同规格`HistGradientBoostingRegressor(loss=absolute_error,max_iter=200,max_leaf_nodes=15,min_samples_leaf=50,learning_rate=0.05,l2_regularization=10,early_stopping=False,random_state=20261002)`；共最多12次训练，仅1–8月拟合，0调参。每区在9–10月对各目标日期先求MAE再等权平均，附加候选从`PEER,WEATHER,JOINT`选最低，精确同分优先PEER→WEATHER→JOINT；各区候选−OWN日期MAE差以相同2000次成对日期bootstrap seed20261002求95%区间。单区资格：相对OWN日MAE改善**≥5%**、差区间上界<0、**≥60%评价日期**改善。整体开发门：至少**2/3区**合格，剩余任何区相对OWN不恶化超过2%。未全过则`STOP_ADDITIONAL_ZONE_CHANNEL_DEV_GATE`，不评分test。

通过时仅用冻结选中候选、OWN、PERSIST在11–12月一次评分；仍要求至少2/3区通过同三项、任一区不恶化超过2%，才`ADDITIONAL_INFORMATION_HOLDOUT_GAIN_WITHIN_ONE_CITY`，否则`NO_LATER_MONTH_CHANNEL_GAIN`；看test后不改模型/门/候选。另记录合格区中多少选择PEER或JOINT：若0，则仅天气信息有任务价值，不能说跨区共享；若≥1也只是他区传统统计增量，尚不证明Ganglion。时间季节外推仍只在同一城市2017剩余月份，不能外推到其他城市或实时部署。任何未达门不诊断容量。

## 尝试、输出、预算

预登记`EXP081-STAT-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_three_zone_stats.py`；网络≤5MiB、内存≤500MiB、CPU≤15分钟、固定最多12拟合。输出`SOURCE_RECHECK.json`、`MODEL_SUPPORT.json`、验证逐日派生误差/指标、条件式test文件、`RUN_OUTPUT_001.txt`及报告/门/关账；原ZIP/CSV不落地。局部只核本ID的样本/选型/日期指标/停止门，不跑全仓或非必要哈希。
