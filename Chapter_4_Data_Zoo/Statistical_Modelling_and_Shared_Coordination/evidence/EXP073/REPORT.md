# EXP073 报告：四路绝对时间不能直接配窗，18类支持亦不足

在 [UCI507官方WISDM原件](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)中，活动键18/18可核，51人每人手机/手表各acc/gyro四文件齐全，所选有效行0格式/ID错误。然而同一人的手机与手表使用不同timestamp纪元：918个人×活动组中，901组四路跨度可算且**全部交叠率0**，17组因至少一路无该活动时段而不可算。原定义的四路同步来源门0人合格。即使忽略跨设备时钟，四路全18类每路≥500行也只有39人，低于冻结≥40。按[原门](GATE_RESULT.md) **`STOP_FOUR_SENSOR_18_CLASS_SUPPORT`**，不配窗、不训练。

前两次尝试只因活动键英文复合写法解析失败，均未扫任何原始行；错误自动STOP没有科学资格。失败、修订与有效尝试 (source asset outside this public snapshot)完整保留。不能事后给手表补一个估计偏移或删一个缺类人来追认EXP073通过。新问题可以改观察单位为**人×已知活动片段**：只从每设备各自约三分钟记录取统计量，按人和官方活动标签关联，不要求跨设备同刻；需新ID明确其实际可用性、样本支持与用途，不能称实时融合。[关账](CLOSEOUT.md)。
