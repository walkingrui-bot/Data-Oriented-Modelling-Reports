# EXP085 — 真实风洞混合气体身份：八传感器相对最强单传感器的试验级增量

研究ID `STAT-PSYMOE-EXP085-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_TRIAL_LEVEL_MULTISENSOR_STATISTICAL_TEST`；父=[EXP084有效来源门](../EXP084/CLOSEOUT.md)。科学问题：在UCI309真实风洞实验、第二气源**实际非零施加**且乙烯与第二气源流量级别平衡的条件下，同一次试验的八路气敏响应相比训练内选出的最强单路响应，能否稳定提高第二气源是CO还是甲烷的试验级判别？这是真实实验设定标签而非逐时化学真浓度；一个试验是一个样本，不把读数行当独立样本。

## 冻结观测、分割和特征

官方[UCI309](https://archive.ics.uci.edu/dataset/309/gas%2Bsensor%2Barray%2Bexposed%2Bto%2Bturbulent%2Bgas%2Bmixtures.)ZIP只内存读取下采样原件；须先重核EXP084 180试验、24非零配置各6重复、CO/Me各72、时间不回退及区间支持，否则`STOP_SOURCE_DRIFT`、0模型。CO_n/Me_n未释放排除，不制造分类标签。对每个非零试验，气敏8路与温湿度各取0–60秒基线中位数、60–240秒释放中位数与其差；每路最终两特征=基线中位数/释放减基线中位数，温湿度同法四个共同协变量。原时间相等行保留为仪器读取，不按行分割。试验文件ID仅在**同配置内排序**，4个最低ID作train，第5个validation，第6个条件式test；ID不当实际时间。每组12 CO/12 Me的validation/test，训练48/48。此为同场地同配置新试验重复，不是时间外/浓度外/场地外证据。

## 固定模型、统计门与停点

只使用传统L2 logistic pipeline：`StandardScaler()`仅train拟合，`LogisticRegression(C=0.1,solver='lbfgs',max_iter=2000,random_state=20261002)`。单路候选各包含共同温湿度四特征+该路两特征；在96个train试验上用`StratifiedKFold(4,shuffle=True,random_state=20261002)`按train内logloss选择8路中最优（同分选较小路号），仅在train重拟合。MULTI=共同温湿度四特征+八路16特征，同固定规格只在train拟合。禁止用validation选传感器/调C/选时间窗。

主指标试验等权概率logloss，辅助平衡准确率；MULTI−SINGLE逐试验logloss差，2000次成对试验bootstrap seed20261002给95%区间。开发门须同时：MULTI logloss绝对改善≥0.05 nats、差区间上界<0、balanced accuracy提升≥0.05。开发失败`STOP_MULTISENSOR_DEV_GATE`，test原件仅审支持、不输出预测或性能。开发通过才对冻结单路与MULTI在24个test试验各一次评分，同三门都过才`MULTISENSOR_TRIAL_REPLICATION_GAIN_WITHIN_ONE_RIG`，否则`NO_TEST_MULTISENSOR_GAIN`。无论结果，不依据test改容量、特征、传感器选择或门。

即使双门通过，也只能说本风洞同设置的独立重复试验存在多传感器增量；样本24/阶段且浓度范围固定，不能声称共享Ganglion有收益、在线浓度估计或跨场地泛化。若统计增量不通过，保留较好传统单路，停止此任务的附加传感器模型。若通过，下一新ID才比较更合适的channel state/Stat-MoE，仍以传统多路统计为对照。

## 尝试、来源、预算和输出

预登记`EXP085-STAT-001`；命令`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_gas_statistics.py`；网络≤30MiB、内存≤350MiB、CPU≤5分钟，预期`TRIAL_FEATURES.csv`（唯一派生特征产品，含split）、train-CV选择/验证原试验预测与指标、条件式test文件、`RUN_OUTPUT_001.txt`。无原件ZIP/txt副本。局部核本ID试验ID不交叉、指标从预测复算、门/test缺席；不运行全仓门或哈希。
