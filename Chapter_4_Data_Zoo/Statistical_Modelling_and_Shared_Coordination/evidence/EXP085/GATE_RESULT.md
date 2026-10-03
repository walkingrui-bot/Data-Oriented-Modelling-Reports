# EXP085 统计门裁决

来源重核 (source asset outside this public snapshot)六门、试验级支持 (source asset outside this public snapshot)五门全过：24非零第二气源配置各4训练/1验证/1条件留出，96/24/24个独立**试验**；验证/test各CO12、甲烷12。train内固定四折从八路选第4路为最强单路，32候选CV拟合与两最终固定模型，无validation/test模型选择。[train选择](TRAIN_CV_SELECTION.json)。

| 阶段 | SINGLE logloss | MULTI logloss | 多路改善 | 差的95%成对试验bootstrap区间 | 平衡准确率单/多 | 冻结三门 |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 验证24试验 | 0.556765 | 0.355475 | 0.201290 | [−0.275128,−0.131581] | 0.625000/0.791667 | 3/3通过 |
| 留出24试验 | 0.931620 | 0.605626 | 0.325994 | [−0.489321,−0.179871] | 0.541667/0.541667 | 2/3通过 |

验证三门全过，按冻结规则评分留出一次。留出概率logloss改善≥0.05且区间上界<0，但**平衡准确率增益=0，未达≥0.05**；最终`NO_TEST_MULTISENSOR_GAIN`。验证逐试验 (source asset outside this public snapshot) · 留出逐试验 (source asset outside this public snapshot) · [派生指标](VALIDATION_METRICS.json)/[留出指标](TEST_METRICS.json) · [局部验证](LOCAL_VALIDATION.json)14/14。

概率改善是观察事实，不是预冻的整体通过，也不证明共享Ganglion。试验来自同一风洞与同一24配置，文件ID非实际时间；每阶段仅24试验，不能推及新浓度/装置/场地。不能看test后改阈值、特征、C或门再声称合格，也不能从该结果诊断模型/矩阵容量不足。
