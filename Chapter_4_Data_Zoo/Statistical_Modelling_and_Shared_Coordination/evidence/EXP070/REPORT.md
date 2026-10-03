# EXP070 报告：独立WISDM人群双手机传感器来源合格

官方 [UCI507 WISDM](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata) 原件的包内活动键确认 A=Walking、D=Sitting、E=Standing。51/51个不同人的手机加速度与陀螺仪，在三项活动每一路均有至少3,568有效行；两传感器时间跨度的最低交叠率0.999253，超过冻结的40人、1000行、0.5交叠率门。[来源门](GATE_RESULT.md) · 逐人原件成员索引及计数 (source asset outside this public snapshot)。

第一次下载后的活动键解析器只懂代码在前，错误把空映射归为样本不支持；失败原件保留 (source asset outside this public snapshot)，修订仅扩大键文本解析格式，不改活动和科学门。修订与重试 (source asset outside this public snapshot)。有效002扫描仍发现三个活动各两个相邻时间倒序步，后继必须排序、确立同步与窗口密度规则。跨度高度重叠本身不产生配对样本，更不产生模型结果。

这个独立51人群比继续改UCI240的21人开发集更能分辨第二传感器收益是否稳健；但活动集合从六类变成三类、手机位置从腰部变成口袋、采样/预处理不同。即使后继成功，也不把它当EXP069同一模型的直接外部确认。[关账](CLOSEOUT.md)。实际局部派生一致性8/8；无训练或旧测试评分。
