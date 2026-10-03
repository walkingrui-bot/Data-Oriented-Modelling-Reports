# EXP046 路径解析失败更正说明（2026-10-02）

`EXP046-NUMERIC-001` 下载官方原ZIP一次并在内存审12 CSV，原始逐站行/有限值计数保留于原派生表 (source asset outside this public snapshot)。程序用 `re.search("PRSA_Data_(.+)_20130301...", info.filename)` 对**包含父目录**的ZIP成员路径匹配，贪婪捕获成 `20130301-20170228/PRSA_Data_站名`，不等于 CSV 内真实 `station` 值。于是12站 `station_label_agrees=False`、合格站0、门停止，这是**实现错误**，不是数据中站名错或来源不够。

本实验事前原ZIP请求预算为1次，已经用尽；不得在本ID静默重读原件、把错误门输出覆写为通过，也不能凭同样行数推断12站共同时间网格。另立 EXP047，固定同一数值门、按成员**basename**解析并实际计算共同小时交集。EXP046 来源许可/真实观测描述仍有效，科学数值门未有效裁决。
