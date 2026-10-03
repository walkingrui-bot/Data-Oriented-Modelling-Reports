# EXP073 — WISDM 18活动四路身体传感器真实来源门

研究 ID `STAT-PSYMOE-EXP073-20261002-001`；2026-10-02 BST；`EXPLORATORY_REAL_FOUR_SENSOR_SOURCE_AUDIT`；父阶段 [EXP072](../EXP072/CLOSEOUT.md)。EXP069/071在两个真实人级开发任务上，手机加陀螺仪未过原定稳定/实用门；EXP072核实1629重复行数值无冲突。新科学问题：WISDM 的**18类活动、手机与手表四路传感器**是否具备足够同人同活动、交叠时段，能真正测试跨身体部位的信息互补？手表在手腕、手机在口袋，活动包含手部动作，比继续三类姿态/移动任务更能区分跨通道信息与重复测量。来源过门也不承诺Ganglion价值。

## 官方数据和冻结来源门

[UCI507数据页](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)及其[原始说明PDF](https://archive.ics.uci.edu/ml/machine-learning-databases/00507/WISDM-dataset-description.pdf)：51人，每人约18活动×3分钟，手机/手表各acc与gyro，原件含ID、活动码、timestamp、xyz。许可网页为CC BY 4.0；保留Weiss 2019、DOI `10.24432/C5HK59`。固定18码 A–M、O–S（无N），活动名以原件 `activity_key.txt` 与官方PDF对应；任何缺码/错义停止，不把标签改成易成功子集。独立单位是人，同人四设备记录、时间点及窗口不重复计独立人。

从同一官方ZIP仅内存读取 `raw/{phone,watch}/{accel,gyro}/data_<id>_<sensor>_<device>.txt` 的204个原件成员；不保存源ZIP/PDF/原始行副本。逐人/类/路核文件存在、行ID与类码、timestamp可解析、xyz有限、有效行数、时间最小最大与原顺序倒序；对同人同类四路计算**跨度交叠率** `max(0,min(四路max)-max(四路min))/min(四路时间跨度)`，比值不依赖timestamp绝对纪元。每人每类四路各≥500合法行、非零跨度、四路交叠率≥0.5；至少**40个不同人对所有18类**都达门，才 `WISDM_18_ACTIVITY_FOUR_SENSOR_SOURCE_READY`；否则`STOP_FOUR_SENSOR_18_CLASS_SUPPORT`，不训练。不把跨度交叠称同步窗，不把缺行当0。完整逐人逐类支持、缺失与无效行都留派生计数。

只做来源资格；若过门，新ID再冻结四路实际配窗、按人开发/测试、手机传统基线、手表传统基线和联合传统基线，先回答统计增量，再决定Stat-MoE/Ganglion是否有额外问题。UCI240及WISDM旧三类test均不评分。与前实验共享WISDM人群，此任务是新标签集/跨身体科学问题，不是EXP071未过门的“补考确认”。

预登记尝试`EXP073-SOURCE-001`，命令`python3 audit_wisdm_four_sensor_source.py`；网络≤330MiB、内存≤2GiB、CPU≤25分钟；原件不落地。输出`SOURCE_MATRIX.json`、`RUN_OUTPUT_001.txt`、门/报告/关账，仅局部派生核验，无全仓门与非必要哈希。
