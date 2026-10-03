# EXP036 MyGait 双足 IMU 数据产品来源报告

研究 ID `STAT-PSYMOE-EXP036-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`。EXP035 未找到 GaitPDB 牛顿双足力模型的直接独立来源。本轮另问 [Zenodo MyGait](https://zenodo.org/records/15672744) 的双足 IMU、临床组别和舒适速度步行是否可形成**新的**真实数据产品；不使用来源声明不可靠的压力列，也不复用 EXP033 的模型。

Zenodo API 返回明确 `CC BY 4.0` 与公开 497,749,531字节 ZIP。一次 HTTP Range 仅取 ZIP 末尾4 MiB，解析了1,482个文件路径，无本地原始 ZIP/CSV 副本。冻结 `10mSlow` 任务在中央目录中各有 PD44、健康45个不同参与者文件，各一份。初版解析漏掉 PD 前10个带 `-RTSOCS` 的文件名，误报34；失败派生与修订保留，正式更正后为44。

中央目录只能看到**每人一份CSV**，无法从文件路径确认内部 `foot` 列在每人都包含左右足。按本实验冻结的“左右足文件可辨”门，记 `STOP_FILE_INTERSECTION_UNKNOWN`，不把44/45人头通过写成双足源已通过。公开描述提示可能将两足放在同一文件中，这需要另立问题直接读原件检验；不是本实验已完成的数值审计。没有训练、科学性能或 Shared Ganglion 结果。

原件索引、许可、失败解析、更正与门见 工作日志 (source asset outside this public snapshot)、路径表 (source asset outside this public snapshot)、[门](GATE_RESULT.md)。后继将用新 ID 对“**同一个 CSV 内左右足观测是否齐全且同步**”作真实数值来源审计，避免改写本轮路径门。
