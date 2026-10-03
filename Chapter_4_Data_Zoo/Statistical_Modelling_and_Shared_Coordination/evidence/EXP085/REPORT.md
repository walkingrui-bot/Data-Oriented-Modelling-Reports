# EXP085 报告：八路概率质量改善，硬判别留出门未保持

**真实问题。** [UCI309](https://archive.ics.uci.edu/dataset/309/gas%2Bsensor%2Barray%2Bexposed%2Bto%2Bturbulent%2Bgas%2Bmixtures.)每次非零CO或甲烷气源真实施加设定，在共同温湿度之外，八路气敏响应相对train内最佳单路是否有跨独立重复试验的合格判别增量？观测单位是一次风洞试验；所谓label是施加设定，非逐时GCMS浓度。

**方法。** 24施加配置各6次、按同配置ID固定4训练/1验证/1留出。每路用0–60秒基线和60–240秒释放中位数差；共同温湿度各两特征；`StandardScaler`+C0.1 logistic，train内四折选最强单路第4路，再与全部八路同规格对比。开发三门同时要求logloss绝对改善≥0.05、试验级差bootstrap上界<0、平衡准确率增益≥0.05；仅通过才评分留出。原值与完整配置见[计划](PLAN.md)、特征 (source asset outside this public snapshot)、[选择](TRAIN_CV_SELECTION.json)。

**结果与裁决。** 验证24次，八路相对单路logloss改善0.201290，区间全<0，BAcc增0.166667，三门全过。留出24次，logloss进一步改善0.325994，区间全<0，但两臂BAcc同为0.541667，三门只过2项。实验执行完成、工程局部有效；科学裁决`NO_TEST_MULTISENSOR_GAIN`，没有达到冻结的整体判别收益门。[门](GATE_RESULT.md) · 原输出 (source asset outside this public snapshot) · 逐试验留出 (source asset outside this public snapshot)。

**解释限度。** 在同场地同配置新试验中，八路模型给出更好的概率损失，但0.5固定判别没有更多正确的两类平衡判断。不能把概率收益等同架构获批，更不能因为BAcc未增推测共享矩阵/模型太小。24次留出独立于train/验证试验，但浓度配置/场地相同，文件ID非时间先后。概率/决策差异值得在一个**新数据任务**研究；已看这24次test不能改称新确认。

**后继。** 优先找明确许可、真实连续参考浓度与多传感器同期测量、可识别独立暴露事件或时间段的来源，先审来源，再决定是否适合概率或连续结果问题。此实验不启Stat-MoE/Ganglion。
