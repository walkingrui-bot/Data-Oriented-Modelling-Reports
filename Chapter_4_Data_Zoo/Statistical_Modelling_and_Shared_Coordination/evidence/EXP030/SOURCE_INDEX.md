# EXP030 官方来源与恢复索引

数据页：[PhysioNet Gait in Parkinson's Disease v1.0.0](https://physionet.org/content/gaitpdb/1.0.0/)；官方原位目录：[files/gaitpdb/1.0.0](https://physionet.org/files/gaitpdb/1.0.0/)；语义原件：[format.txt](https://physionet.org/files/gaitpdb/1.0.0/format.txt)；主体组别原件：[demographics.txt](https://physionet.org/files/gaitpdb/1.0.0/demographics.txt)。本轮只在内存读取这些小文本，均未本地复制。唯一派生 `PAIR_AUDIT.csv` 按官方 `Ga` study / `Pt` PD / `Co` HC、`_01` usual、`_10` serial-7 解析，逐主体记录原文件 URL 是否存在及官方人口表组别一致性；`SOURCE_DIAGNOSTICS.json` 记录统计与预算。原始 19 列力时序未读取、未复制；如将来新问题需要，应从官方 URL 原位取、保持新 ID。

官方 `format.txt` 明列时间（秒）、左右足各8个 vertical ground reaction force (N)、左右总力共19列、100Hz；`Ga` 属 Yogev 双任务研究，`Ju` 与 `Si` 是其它研究。后缀 `_10` 仅 **Ga** 有官方 serial-sevens 语义，不能把 `Ju`/`Si` 同号文件想当然纳入；`_01` 为普通步行。目录 `Ga` 文件 113、人口表 `Ga` 47 人；真正 `_01`+`_10` 配对 27 人，其中 PD21、HC6。无跨研究拼接或不同人配对。
