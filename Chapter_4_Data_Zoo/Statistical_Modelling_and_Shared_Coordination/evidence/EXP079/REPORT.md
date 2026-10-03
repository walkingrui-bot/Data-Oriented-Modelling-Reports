# EXP079 报告：真实高负荷事件的联合附加量仍未过实用门

在[UCI235原件](https://archive.ics.uci.edu/dataset/235/individual%2Bhousehold%2Belectric%2Bpower%2Bconsumption)的另一栋家庭中，沿用真下一小时整点与完整历史样本，改为预测训练期第90百分位 **2.64 kW** 以上的实际负荷事件。阈值只从2007–08训练目标决定；2009验证有626事件，评价355个完整日期。固定四臂传统分类器的日等权logloss：AR **0.208400**、SUB **0.203902**、ELECTRICAL **0.206500**、JOINT **0.203506**；常数训练事件率对照0.266736。

按冻结选择的JOINT较AR改善**2.348%**，日期bootstrap差区间低于零；但只200/355日期改善，PR-AUC只从0.327005到0.335514。四项开发门仅区间一项通过，故**2010未评分**。[门](GATE_RESULT.md) · 原失败504 (source asset outside this public snapshot) · 有效原输出 (source asset outside this public snapshot)。下载504的首尝试无模型/结果，原样保留；同一协议重试成功。

连续功率平均误差与该高负荷事件两个不同科学结局，都观察到少量附加来源开发信号，但都没有达到预定的实用幅度及日期稳定性。**单栋家庭电力新增channel路线暂停**；保留简单AR统计基线和失败档案，转向具有不同真实观测单位的来源。当前不能诊断容量，也不能把同一家庭的三回路当独立复制。局部派生[12/12](LOCAL_VALIDATION.json)复核了日损失、bootstrap、选型与停止；PR-AUC只核算报告字段关系，未保留逐小时概率供独立复算；未跑全仓。
