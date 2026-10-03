# EXP047 — 北京多站原件站名和共同小时网格修正审计

研究 ID `STAT-PSYMOE-EXP047-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP046](../EXP046/CLOSEOUT.md)。EXP046官方来源/许可门通过，但其唯一数值尝试因ZIP成员路径正则吞入父目录、所有站被误判而工程无效。本独立实验问：在**同一官方原 ZIP**中，按成员 basename 正确核站名和完整小时网格后，真实多站PM2.5/气象数据是否通过原先的数值门？EXP046的失败结果保持原样。

## 固定数据、方法和门

来源 UCI ID501 [官方原件](https://archive.ics.uci.edu/dataset/501/beijing%2Bmulti%2Bsite%2Bair%2Bquality%2Bdata)；许可已由EXP046官方页面确认 CC BY4.0。一次官方原ZIP网络读取到内存，逐个原始CSV `Path(member_path).name` 严格匹配 `PRSA_Data_<station>_20130301-20170228.csv`，并与该文件 `station` 列唯一值精确核对。不能以目录文字当站名，不使用UCI页附带的 `data.csv/test.csv` 替代原始站文件。

延续 EXP046 已冻结的最低支持：≥10个独立站各有≥30,000唯一合法小时且无站内重复冲突，≥10站每站 PM2.5 有限非负小时≥25,000、`TEMP/PRES/WSPM`同时有限小时≥25,000；合格站的原始小时网格实际交集≥20,000。另明确检查每站最早/最晚时间为官方2013-03-01 00:00至2017-02-28 23:00；若不一致作为日期失败。missing 保留为missing，负PM不计有效值，不修改门追求通过。过门 `REAL_MULTISITE_SOURCE_READY`，否则 `STOP_NUMERIC_SOURCE_SUPPORT`；本实验仍不训练。

≤1次≤20MiB官方ZIP原件请求，只在内存解压/解析，原ZIP/CSV不落盘。输出逐站派生审计、总门/报告/关账及运行失败原状。无模型/种子。最小验证仅本站名、时间网格、计数、门；无全仓门/非必要哈希。通过后另立真实预测问题，先统计基线、未来时间锁与整站留出。
