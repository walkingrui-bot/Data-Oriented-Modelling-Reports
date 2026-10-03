# EXP076 报告：下一小时用电的附加来源未通过开发门

真实单住宅[UCI374](https://archive.ics.uci.edu/dataset/374/appliances-energy-prediction)的下一小时设备用电任务中，用目标时间划分，起点已知的能耗滞后与日历构成AR，室内和天气值额外滞后一小时。固定四臂同规格传统HGB在训练时段拟合后，验证20个完整目标日期的等权MAE为AR **34.964 Wh**、INDOOR **34.966 Wh**、WEATHER **35.183 Wh**、JOINT **35.000 Wh**，无拟合PERSIST **51.146 Wh**。

按预定规则最优附加臂INDOOR仍比AR差0.001882 Wh；日期成对bootstrap的差区间跨零，20天中只10天改善。三项冻结开发门全部失败，因此停在开发阶段，**test未评分**。[冻结裁决](GATE_RESULT.md) · 原输出 (source asset outside this public snapshot) · [局部核验](LOCAL_VALIDATION.json)。这属于固定模型、特征、单住宅和一小时视窗下的统计增量未观察到；不能归因于容量，也不能推广为室内/天气永远无用。数据日期时区和各字段当年实时可用性仍未知，结果只属回顾性时间外验证。

下一实验可改变科学问题到更长预测时距，必须另立ID并先冻结目标、来源、门及止损；不得改写本ID结果或使用此test选型。
