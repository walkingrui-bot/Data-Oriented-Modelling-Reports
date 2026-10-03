# EXP083 — 真实跨年交通下一小时流量：历史与滞后天气增量

研究 ID `STAT-PSYMOE-EXP083-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_TRAFFIC_YEAR_HOLDOUT_STATISTICAL_TEST`；父=[EXP082来源门](../EXP082/CLOSEOUT.md)。科学问题：真实I-94西向单计数站下一小时车辆数，已完成小时的天气数值在该站历史流量与已知日历之外，是否提供跨后续年份保持且足以建立环境channel的预测增量？这与EXP081电力三区是不同结局/观测单位，不能当作其模型外部验证；用传统统计先检验，不先上Stat-MoE/Ganglion。

## 源语义、时间锁与支持门

仅[UCI492官方ZIP内原GZ](https://archive.ics.uci.edu/dataset/492/metro%2Binterstate%2Btraffic%2Bvolume)内存解压，不另存原件。按EXP082预先冻结的唯一源日历小时分组：重复小时交通量必须全部相等，气温/降雨/降雪/云量各取同小时中位数；原缺失不填零。与EXP082的48,204原行、40,575唯一小时、首末小时、重复/冲突数及目标年配对数重核，不符`STOP_SOURCE_VERSION_DRIFT`，0模型。源网页称本地CST，但DST/实时可用时刻不证。

只用目标时刻`t+1h`有真实交通数的唯一小时。起点`t`及过去`t−1h,t−24h,t−168h`各交通量必须存在、有限、非负；天气四数值统一取**`t−1h`**的历史完整小时中位数，原`t`的雨雪小时汇总不用作实时预测输入。全部臂使用同一完整配对，不把缺失当零，不用未来天气或目标时刻交通。已知目标时刻小时/星期/年内日sin/cos各一对。`BASE=四个交通lag+六日历`，`WEATHER=BASE+四滞后天气`；无拟合PERSIST=`traffic(t)`、WEEK=`traffic(t−168h)`仅作描述。目标年份2013–16训练、2017验证、2018条件式test。按**目标日期**作为主评价块，每日≥18合法小时才入主指标。先要求训练≥12,000配对/≥700目标日，2017验证≥6,000配对/≥250评价日，2018测试≥4,500配对/≥220评价日；否则`STOP_TRAFFIC_MODEL_SUPPORT`、0拟合。不检查测试性能决定源门。

## 固定模型和统计门

BASE/WEATHER同规格`HistGradientBoostingRegressor(loss=absolute_error,max_iter=200,max_leaf_nodes=15,min_samples_leaf=50,learning_rate=0.05,l2_regularization=10,early_stopping=False,random_state=20261002)`，仅训练年拟合，输出截断≥0，不调参。主指标各日交通量MAE先求日均再日等权；WEATHER−BASE日期MAE差2000次成对日期bootstrap seed20261002给95%区间。2017开发门同时要求WEATHER相对BASE日MAE改善**≥5%**、差区间上界<0、**≥60%评价日期**改善；任何失败`STOP_WEATHER_TRAFFIC_DEV_GATE`，不评分2018。全过只把BASE/WEATHER/PERSIST/WEEK一次评分2018，同三门都过才`WEATHER_TRAFFIC_YEAR_HOLDOUT_GAIN_WITHIN_ONE_SITE`，否则`NO_2018_WEATHER_TRAFFIC_GAIN`，不得看test重新调参或缩门。

即使两年过门，也只是单道路/记录合并与回顾性天气滞后的任务特异收益，不能称在线预测、跨地点通用或共享Ganglion价值；若不通过也不诊断容量。环境原件的同小时天气冲突是数据质量界限，报告来源中位数变换和其规模。

## 尝试与预算

预登记`EXP083-STAT-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_traffic_stats.py`；网络≤2MiB、内存≤300MiB、CPU≤8分钟、仅两个固定拟合。输出`SOURCE_RECHECK.json`、`MODEL_SUPPORT.json`、验证逐日派生误差/指标、条件式test文件、原`RUN_OUTPUT_001.txt`及关账。局部只核本ID派生天MAE/bootstrap/门和有无test，不运行全仓门或非必要哈希。若失败，停在现有真实统计基线，后继研究新来源或任务语义，不在同一测试集追逐架构。
