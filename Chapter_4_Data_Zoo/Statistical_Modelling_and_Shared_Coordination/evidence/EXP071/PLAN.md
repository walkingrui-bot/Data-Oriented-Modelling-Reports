# EXP071 — WISDM 实际时间配窗与跨人双传感器统计检验

研究 ID `STAT-PSYMOE-EXP071-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_PAIRED_WINDOW_PERSON_HOLDOUT`；父阶段 [EXP070](../EXP070/CLOSEOUT.md)仅来源跨度合格。用户自治授权与“实践、及时止损”要求继续。科学问题：在独立51人真实手机原始时序的 walking/sitting/standing 三类任务中，陀螺仪能否在加速度计外提供跨人保持、超过第二传感器成本的预测增量？若时间配窗本身不足先停止；若传统联合统计没有增量，不训练 Stat-MoE/Ganglion；若增量稳定，再以新ID研究结构是否超过联合统计。

## 原件、窗口与独立单位

仍用 [UCI507 官方原件](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)的 `raw/phone/{accel,gyro}/data_<person>_<sensor>_phone.txt`，只选包内已确认 A=Walking、D=Sitting、E=Standing。51名不同人是独立单位；一个人多个非重叠窗仍相关。EXP070记录A/D/E各有两处相邻时间倒序，故本实验对每人/活动/传感器按整数timestamp稳定排序；同一timestamp若重复取三轴均值。文件行首ID不符、时间/xyz不可解或非有限按来源漂移停止，不伪作缺失。EXP070每人每类每路有效行数必须逐项复现，否则`STOP_SOURCE_VERSION_DRIFT`，不跑模型。

源时间跨三分钟约180×10^9 tick，和官方每活动三分钟相符；本实验固定 `10^9 tick = 1秒`的**相对时间刻度**，不解释为历法日期。对每人/活动，取两传感器时间范围交集，从其左端连续切 **10×10^9 tick** 半开、不重叠的完整窗；末尾不完整窗丢弃。每窗每路至少100有效原始点，含窗两端边界的最大相邻时间间隙≤1×10^9 tick，才视为配对合格。各路在相同窗内用线性插值到从左边界起每50×10^6 tick一次的200点网格；若网格端位于首末实际点外，只在已通过≤1秒边界间隙的情况下用最近端值。每窗按轴固定11特征：mean、std、p10/p50/p90、RMS、range、相邻绝对差均值、lag-1 Pearson（零方差=0）、去均值实FFT的[0.4,3)与[3,8)Hz能量比例（零总能量=0）。每模态33、联合66；不引入手表或发布的ARFF特征。排序/插值是预处理，不制造目标类别；拒窗及每人类支持均留数。

## 来源配窗门和人级切分

人ID1600–1650预先升序，**位置 index modulo 5 为0者11人 test**，其余40人 development；这个切分在任何配窗数/成绩计算前固定。合格人必须三类各≥10个双路合格10秒窗；需≥32个development人、≥8个test人、总合格窗≥1800，否则`STOP_PAIRED_WINDOW_SUPPORT`，不建模型。仅合格人进入对应集合；test窗数只作预定来源支持审计。人、类、时间窗是实际观测，不能把窗口 bootstrap 当独立人。

## 统计对照与冻结止损

三组固定传统模型 ACC、GYR、JOINT：各自33、33、66特征，同一 `StandardScaler`（只拟合训练人）+ `LogisticRegression(C=1,L2,lbfgs,max_iter=500,random_state=20261002)`，无搜索；训练人类别频率常数概率为PRIOR。development合格人升序 modulo 5 再分5折人级OOF，所有选模和来源判断只在此开发侧。任一拟合未收敛/类缺失则记录工程失败，不事后换模型。每人三类logloss窗均值与三类平衡准确率，再人等权汇总；JOINT−ACC是唯一主比较。对每人logloss差成对有放回重抽2000次（seed20261002）计算95%百分位区间。

开发门全需：JOINT−ACC logloss≤−0.03、平衡准确率≥+0.02、logloss CI上界<0、至少开发合格人数的2/3（向上取整）人的logloss改善。失败`STOP_JOINT_DEV_GATE`，**不评分test性能**。通过后只在全部development人拟合固定三模型，官方新定义test人仅一次评分；test按完全相同四条件（2/3向上取整），全过才 `WISDM_GYRO_INCREMENT_SUPPORTED_WITHIN_PROTOCOL`，否则`NO_INDEPENDENT_PERSON_HOLDOUT_INCREMENT`。test后不改窗口、特征、模型或门；UCI240旧test始终不用。即使成功，也只称同一WISDM协议的独立人留出，不说跨实验室或UCI240模型直接外部确认。

## 运行账、预算与输出

预登记尝试 `EXP071-PAIR-STAT-001`，命令 `/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_wisdm_paired_stats.py`；官方ZIP仅内存读与按成员流式读，不保存原件/原始行副本。网络≤330MiB、内存≤2GiB、CPU≤30分钟；最多三模型×5 OOF=15次拟合，开发过门才额外3次。保存`SOURCE_RECHECK.json`、`WINDOW_COUNTS.json`、条件式`OOF_METRICS.json`/`OOF_PERSON_ROWS.csv`、条件式`TEST_METRICS.json`/`TEST_PERSON_ROWS.csv`、终端原输出、门/报告/关账。局部只核配窗计数与派生结果，禁全仓门、非必要哈希。若门失败明确哪层止损并自主选下一真实问题，不把“模型太小”当未经测试的解释。
