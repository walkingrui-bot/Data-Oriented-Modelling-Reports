# EXP087 事件可识别性门裁决

[UCI487官方原件](https://archive.ics.uci.edu/dataset/487/gas%2Bsensor%2Barray%2Btemperature%2Bmodulation)按每文件首时刻900秒清洗、随后100个900秒预定窗口切分。全部13日各100窗口均有≥2,500全有限行及≥1,400中心行，中心CO IQR≤0.25ppm，日内各有10个0.1ppm精度浓度水平，总**1,300/1,300真实预定施加事件**满足本ID稳定门。事件矩阵 (source asset outside this public snapshot)。唯一时间回退6.992秒在2016-10-03窗口5内部、不跨边界，六门全过，裁决`CO_EXPOSURE_EPISODES_IDENTIFIABLE_FOR_NEW_QUESTION`。

这不是EXP086复活：旧原件3,843,160完整行<4,000,000与一次时间回退均继续记为失败；本ID的科学问题改为预定施加事件的观测单位，不给旧门补票。本ID未拟合、未评分。下一新ID才可用**所有预定窗口**（不能按目标CO稳定性筛样本）从传感器计算输入并按日切分比较传统统计；即便成功也仅是该一套腔室/气敏装置的回顾性校准。
