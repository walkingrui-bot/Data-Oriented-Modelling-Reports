# EXP031 来源与模型门

研究 ID `STAT-PSYMOE-EXP031-20261002-001`；2026-10-02。事前计划见 [PLAN.md](PLAN.md)，同名普通步行 `_01` 的 PD/HC 人数门为总数 PD≥80、HC≥60 且各研究 PD≥20、HC≥15；其后六个 study×group 每组至少 90% 原始文件满足 19 列、至少 5,000 行、时间与有限值、每文件≤2 MiB 和总预算。

| 门 | 冻结要求 | 观察 | 判定 |
| --- | --- | --- | --- |
| 官方人口与 `_01` 精确配对 | 总PD≥80/HC≥60，各研究PD≥20/HC≥15 | 165 人 PD93/HC72；Ga29/18、Ju29/25、Si35/29；`Juc010` 不匹配而隔离 | 通过 |
| 原件结构/可读率 | 每个研究组别≥90%；165原件，≤180请求、≤250 MiB | 159/165 满足；Ga29/18、Ju25/23、Si35/29。**Ju PD25/29=86.2%**；其他组达到门。166请求、164,521,028字节 | `STOP_NUMERIC_SOURCE` |
| 三次整研究留出模型 | 前两门通过后才训练、比较 | **未运行**；无真实预测、性能或模型门结果 | 未触发 |

Ju PD 中 `JuPt05/07/08` 分别只有 4,419/4,575/4,363 行，低于事前 5,000；`JuPt18` 超过 2 MiB 单文件读取上限。Ju HC 的 `JuCo02/03` 分别 4,034/4,053 行，但 Ju HC 仍为23/25=92%。具体错误和原始 URL 索引见 SOURCE_AUDIT.csv (source asset outside this public snapshot)。不以延长/缩短门或剔除失败人来追认本实验通过。

派生表局部一致性 4/4 通过，范围见 [LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)；`retries` 字段遗漏的更正见 [CORRECTION_001.md](CORRECTION_001.md)。没有回头读取失败文件，也没有拟合统计模型或训练 Stat-MoE/Ganglion。
