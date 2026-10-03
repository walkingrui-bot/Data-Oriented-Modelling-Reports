# EXP030 同人认知双任务来源门

研究 ID `STAT-PSYMOE-EXP030-20261002-001`；2026-10-02。事前 [PLAN.md](PLAN.md) 要求 PD≥20 且 HC≥20 位不同人，每人有官方语义明确的普通 `_01` 与 serial-sevens `_10` 配对，并在支持门过后做固定2人的四文件局部数值 QA。

官方 [format.txt](https://physionet.org/files/gaitpdb/1.0.0/format.txt) 确认 `Ga`、`Pt`/`Co`、`_01`/`_10` 含义；原位目录和 [demographics.txt](https://physionet.org/files/gaitpdb/1.0.0/demographics.txt) 一对一审核 47 个 Ga 主体。`PAIR_AUDIT.csv` 逐人记录：**PD21 配对通过，HC6 配对低于20**。总库 PD93/HC73 跨三个不同研究，不能算作认知双任务交集。

判定：`PAIRED_DUAL_TASK_COHORT_NOT_IDENTIFIED`，在样本支持门停止。预设的两人四文件数值 QA 因上游样本门不可能通过而**未执行**；原始 force 记录未读，不能声称原始数值已验证，也不能推断是否存在认知双任务效应。没有训练或改门。请求 6/20，读取小文本低于 5 MiB。
