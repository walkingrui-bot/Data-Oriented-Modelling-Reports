# EXP042 — MyGait PD 问卷日期格式识别与固定月跌倒结果支持

研究 ID `STAT-PSYMOE-EXP042-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP041](../EXP041/CLOSEOUT.md)。EXP041 按其固定解析得到月跌倒数仅10人/3值，另33个日期文本无法解析。本实验新问：这些日期字符串能否通过明确格式和同人步态记录日被**无歧义**解析，进而使同一个已预定的“过去一月跌倒次数”成为足够支持的真实 PD 组内结果？不更换结果、不改 EXP041 门或其10/3记录。

## 固定输入、格式规则、独立单位

原件为 [Zenodo MyGait v1](https://zenodo.org/records/15672744) ZIP 中 `Parkinson Dataset/Questionary data/Participants Data.xlsx` 的 `Parkinson Disease` 工作表；固定 EXP036 `1_10mSlow` 44 PD 匿名 ID与 README确认的原始记录日。每人一个结果，不复制工作簿或逐人原始值。候选列只有 EXP041 锁定的 `Number of falls in the last month`，不扫描其他 outcome 选结果。

日期解析只接受 Excel 日期、ISO/年月日、日月年或月日年的显式斜线/点/连字符格式，可带 `00:00:00` 类时间尾缀；两位年份按2000–2099。为每个字符串枚举所有合法候选日：只有**唯一**候选与该人记录日相差≤7天，才视为无歧义时序匹配；零候选/多个不同候选或>7天均不计。记录日期格式模式分布及不可识别原因，不猜缺失日期。

## 冻结门与决策

若 ID 一对一且至少30名不同 PD 的月跌倒数在无歧义±7天内有有限非负整数值，并有至少5个不同数值，记 `FALLS_OUTCOME_SOURCE_READY`。否则 `STOP_FALLS_OUTCOME_SUPPORT`。真实0可以是观测值，missing不能当0；重复冲突不计人。通过也只是 outcome 来源资格，后继必须另立模型ID并先核数量分布/时间批次/传统统计对照；不直接称步态预测跌倒。

最多1次4 MiB ZIP尾部 Range+1次≤1 MiB问卷成员Range，共≤2源请求/≤5 MiB响应。输出派生格式模式计数、逐人日期/结果资格状态、门/报告/关账；不保存原始工作簿、原始个人结果或同一材料副本。无训练/随机种子。局部验证仅核固定44ID、格式候选、时间门和支持数；禁全仓门及非必要哈希。
