# EXP088 — 真实CO施加事件的跨实验日最强单路对十四路校准增量

研究ID `STAT-PSYMOE-EXP088-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_EPISODE_LATER_DAY_MULTISENSOR_CALIBRATION`；父=[EXP087事件级来源门](../EXP087/CLOSEOUT.md)。科学问题：在UCI487已识别的每次真实15分钟CO施加事件上，同步14路气敏响应相对训练日内选择的最强单路或共同环境信息，能否改善**后续实验日**CO设定浓度的回顾性校准误差？这是连续CO施加/流量控制目标，非独立化学分析仪真值或实时预报；一事件一个样本，绝不以百万行当n。

## 资格、先验已看数据与限定

EXP086原件行数/一次回退两门失败不变；EXP087另证实13日×100个稳定时钟窗口，回退仍在同一窗口。本ID重新从[UCI487官方ZIP](https://archive.ics.uci.edu/dataset/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation)按同900秒清洗+100个900秒窗口提取所有1,300事件，不按真实CO/IQR筛样本；逐日原完整行数/时钟窗口与EXP087对照。输入取每窗口相对[300,840)秒的温度、湿度、流量、加热电压四共同变量中位数，14传感器各中位数与IQR（28特征）；标签同中心的CO中位数。须每事件≥1,400完整中心行、所有四共同+十四路特征与目标有限、1,300/1,300可算、每日期100事件，否则`STOP_CO_MODEL_EVENT_SUPPORT`、0模型。传感器值不从目标构造，所有臂相同事件。

EXP087已为来源审计列出全部日/窗口的CO中位数，故这些日的目标**已被看过**；本ID明确只作探索性后续日评价，不称新确认、独立外部验证或未见标签测试。仍固定不据后续日性能调模型，保持工程决策纪律。

## 固定日期分割与模型

按原13日期升序，前7日训练（700事件）、中3日开发（300）、末3日条件式后续日（300）。传统统计HGB回归`loss='absolute_error',max_iter=200,max_leaf_nodes=15,min_samples_leaf=25,learning_rate=0.05,l2_regularization=10,early_stopping=False,random_state=20261002`，输出截断[0,20]ppm。共同环境四特征为ENV；14个单路候选各=ENV+该路两特征；MULTI=ENV+全部14路。用训练7日的`GroupKFold(n_splits=4)`，按日分组，每候选只在训练内做四折，选日等权MAE最低的ENV或一个单路为`BEST_BASE`（同分ENV先、再低路号）。对BEST_BASE与MULTI在7日完整训练各拟合一次；不让开发或后续日选择传感器、超参或窗口。ENV可能成为最佳是对传感器价值的有效反证。

主指标每事件绝对ppm误差先按实验日均值，再日期等权；同日十浓度水平从源CO设定对应中心值按0.1ppm舍入，仅作分层稳定性，不作为输入。MULTI开发门同时要求相对BEST_BASE日期MAE改善≥5%、三个开发日各改善、在合并开发日十个浓度水平中至少7个MAE改善；若失败`STOP_CO_MULTISENSOR_DEV_GATE`，不评分后续3日。开发全过才评分后续3日同三门一次；都过也只称`EXPLORATORY_CO_MULTISENSOR_LATER_DAY_GAIN_WITHIN_ONE_RIG`，否则`NO_CO_LATER_DAY_MULTISENSOR_GAIN`。不对已看来源标签宣称确认。无需Stat-MoE/Ganglion，除非传统多路实有持久增量且之后独立数据能改变架构决策。

## 尝试、预算和档案

预登记`EXP088-STAT-001`，命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_co_calibration.py`；网络≤210MiB、内存≤850MiB、CPU≤10分钟，0付费计算。官方原ZIP/txt不另存；唯一派生`EVENT_FEATURES.csv`、来源/支持核验、train CV选择、开发逐事件误差/指标、条件式后续日误差/指标、原`RUN_OUTPUT_001.txt`原位保存。局部核日期/事件分割、派生指标/门、后续日文件是否按门存在；不跑全仓门/非必要哈希。
