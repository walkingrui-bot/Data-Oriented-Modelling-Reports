# EXP040 — MyGait PD/健康对比的采集批次可识别性

研究 ID `STAT-PSYMOE-EXP040-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`；父阶段 [EXP039](../EXP039/CLOSEOUT.md)。新科学问题：即使89人的双足 IMU 数值原件齐全，MyGait 的 PD/健康标签是否有足够**同采集时期**的个体，使模型可区分疾病信息与时间/流程批次效应？不能仅凭输入信号与标签相关就称疾病信号。

## 来源、假设和决策

固定 EXP036 89人任务路径表 (source asset outside this public snapshot) 的文件名时间字段；从同一 [Zenodo v1](https://zenodo.org/records/15672744) 原 ZIP 按 Range 读 `Parkinson Dataset/README.docx` 与 `Parkinson Dataset/Questionary data/Participants Data.xlsx` 的来源说明/列模式。不能把文件名日期无核验地当作实际采集日期，先查官方随包说明；不保存 DOCX/XLSX 原件副本，也不输出逐人原始问卷。竞争解释是 (a) 疾病组跨同一采集批次有实在对照，或 (b) 组别与文件时间/招募批次紧密绑定，模型结果无法识别疾病机制。两者决定是否开展传统统计 PD/HC 基线。

## 冻结审计与停止门

- 从每条固定路径解析 `YYYY.MM.DD-HH.MM.SS`，形成按组的最早/最晚日期、年/月分布与**同月 PD/HC 交集**；不能从目录组别反推缺失日期，解析失败逐人留档。
- 只把随包 README 或表格明确说明的日期/ID/组别语义记为已确认；未说明则标未知。公开问卷/临床表只留工作表名、字段名与非敏感聚合支持，不复制逐人原始值或把当前表冒充历史字段状态。
- 只有日期语义可确认、并至少有同一日历月 **≥10 PD 与 ≥10健康** 独立人、且两组任务协议相同的明确来源证据时，记 `DATE_PROTOCOL_SUPPORT_FOR_BASELINE`，之后另立模型 ID。若无这样的同期支持，或日期/协议语义不明，记 `STOP_DATE_PROTOCOL_IDENTIFIABILITY`，不训练 PD/健康疾病分类器。该门只为可解释对比资格，不证明因果性。

## 预算与输出

一份原有路径表，最多1次4 MiB ZIP尾部 Range、2次各≤1 MiB成员Range，总≤3次请求/≤5 MiB原始响应。只用内存解析DOCX/XLSX，保存派生 `DATE_SUPPORT.json`、`METADATA_SCHEMA.json`、门/报告/关账；没有模型、随机种子或运行状态。局部验证只检查本轮日期解析、来源字段与门判，禁全仓门与非必要哈希。若停止，根据证据另立最大信息增益问题，可能转 PD 组内真实连续 outcome，须先核临床 crosswalk。
