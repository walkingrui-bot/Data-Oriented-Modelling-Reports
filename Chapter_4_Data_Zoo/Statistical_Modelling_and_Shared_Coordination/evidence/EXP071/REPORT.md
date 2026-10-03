# EXP071 报告：真实配窗充分，手机陀螺仪统计增量未过门

从 [WISDM官方原始手机时序](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)依冻结时间交集、密度、排序、同刻均值规则形成51人×三活动×17个非重叠10秒双路窗，共 **2601** 个真实配窗，无拒窗；40人开发、11人保留不评分。原来源行数与EXP070完全匹配，配窗门通过。逐人窗数 (source asset outside this public snapshot)。

传统L2统计在40人五折OOF中，单加速度计ACC的人等权logloss **0.2352**、平衡准确率 **0.8966**；联合陀螺仪JOINT为 **0.2585**、**0.9039**。联合概率损失变差0.0232，分类增幅0.0074，成对人级区间跨零，改善人数21/40。四个预定实用/稳定性门全部失败，**`STOP_JOINT_DEV_GATE`**；按协议官方11人测试性能未评分，不训练Stat-MoE或Ganglion。[门](GATE_RESULT.md) · 逐人成绩 (source asset outside this public snapshot)。

六处原始相邻时间倒序按冻结规则排序；21,424条重复timestamp折叠全部集中在受试者1629的六个所选组。计算按协议有效，但目前不知道这些同刻行是完全重复还是冲突记录；不能把它忽略为噪声，也不能事后删人重训冒充原实验。下一独立ID应只读核异常语义，再决定是否需要新的数据资格或新问题。即使无异常，本实验也只限三活动、手机口袋、WISDM内部受试者开发交叉验证；UCI240旧测试与本任务新测试均未看性能。[关账](CLOSEOUT.md)。
