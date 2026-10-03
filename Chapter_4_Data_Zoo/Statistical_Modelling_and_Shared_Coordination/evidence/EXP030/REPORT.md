# EXP030 GaitPDB 同人双任务来源审计报告

研究 ID `STAT-PSYMOE-EXP030-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`。EXP029 没有找到 PADS M4 直接同构外部 cohort，因此本轮另立科学问题：PhysioNet GaitPDB 是否有足够 PD 与健康**同一人**普通步行/serial-sevens 步行配对，可研究认知负荷对足底力动力学的作用？它与 PADS 的腕部组三分类模型不同，不是那个模型的外部确认。

官方语义文件明确 `Ga` 是双任务研究、`Pt` 与 `Co` 是 PD/健康、`_01` 是普通步行、`_10` 是 serial-7 心算步行。目录 113 个 Ga 文件与人口表 47 名 Ga 受试者对齐。真实 `_01`+`_10` 配对 **PD21、HC6**；健康支持小于事前20人门。总数据页写 PD93/HC73，但含另外两项研究，不能拿来补这个任务的健康配对。门在元数据层已不可能通过，所以固定两人四文件原始数值 QA、建模与效应评估均未运行；没有把未读强行说成数值有效。

来源原件 URL 与派生人级清单见 [SOURCE_INDEX.md](SOURCE_INDEX.md)、`PAIR_AUDIT.csv`，判据见 [GATE_RESULT.md](GATE_RESULT.md)。这属于**任务交集样本支持不足**，不是统计模型没有效果。下一个更有价值的问题应舍弃 serial-sevens 配对，在 GaitPDB 三研究的普通步行原件上核独立人、组别和来源差异，研究能否建立真实 source-level holdout 的 PD/健康统计基线；须新 ID，不能把它追认为本轮双任务结果。若跨研究人身份无法核或任务协议不可比，应在其门停止。
