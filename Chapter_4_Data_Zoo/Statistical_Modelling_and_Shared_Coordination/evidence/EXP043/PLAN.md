# EXP043 — MyGait 英文月名日期的月跌倒结果最终来源裁定

研究 ID `STAT-PSYMOE-EXP043-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP042](../EXP042/CLOSEOUT.md)。EXP042 按固定数字日期格式得到32人/4种月跌倒值而停止，同时原表另有8个 `November DD, YYYY`/`December DD, YYYY` 月名日期。本实验新问：严格解析这8个**已观测格式**，合并同一44人同一跌倒列，是否改变真实结果支持和后续决策？不追改EXP041/042门或结果。

## 冻结来源、方法与门

- 同一 [Zenodo v1](https://zenodo.org/records/15672744) ZIP 原件 `Participants Data.xlsx`；固定 EXP036 44个 PD 匿名人级路径与录制日。沿用 EXP042 数字日期枚举及唯一±7天规则，只扩展 `EnglishMonth DD, YYYY` 明确格式；英文月名按常规12个月逐字匹配，不从跌倒值决定日期。若日期有零个/多个近邻仍不计。
- 唯一结果仍是第14列 `Number of falls in the last month`，有限非负整数才有效；真实0与20均保留，缺失不作0。重复冲突不计人。输出日期格式状态、逐人资格而不保存逐人结果值。
- 完整结果来源资格门仍要求 ≥30名不同 PD 人及 ≥5种不同观测计数。通过记 `FALLS_OUTCOME_SOURCE_READY_FOR_DESIGN`；未过记 `STOP_FALLS_OUTCOME_SUPPORT`，并根据计数分布决定是否值得新建模型设计。通过只表示来源支持，不保证可预测；训练须新ID和冻结统计/对照。

≤2次源Range（ZIP尾部4 MiB、问卷成员≤1 MiB）、≤5 MiB响应；原件内存读，不复制原工作簿。无模型/种子。局部验证仅核44ID、日期候选、不同结果值、门判；禁全仓门和非必要哈希。
