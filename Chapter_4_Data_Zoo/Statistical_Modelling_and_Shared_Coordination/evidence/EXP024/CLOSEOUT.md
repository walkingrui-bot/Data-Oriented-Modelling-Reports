# EXP024 关账

研究 ID `STAT-PSYMOE-EXP024-20261002-001`；2026-10-02；`EXPLORATORY`。执行状态：**固定文书类型门停止**。工程有效性：**来源元数据与 40 份 PDF 读取为局部有效；38 份未完成语义人工裁决**。科学结论：**当前 2010–2024 NDA/BLA 混合 cohort 未达预设统一处方 I&U 来源资格；indication-specific event 未识别**。

尝试清单及原始失败见 WORKLOG.md (source asset outside this public snapshot)。`SUPPORT-001` 四子层支持充分，`SAMPLE-001` 固定 40 application 且同-key URL 40/40，`DOC-001` 40/40 PDF 可取，`ADJUDICATE-001` 定向核两份真实 OTC 文书，令 ORIG NDA 合格上限 13/15 < 14/15，立即停止后续人工裁决。没有补抽、改门或删除已读但未判的 38 份证据。源 URL 与逐条机器结果在 DOCUMENT_AUDIT.csv (source asset outside this public snapshot)，两份人工失败与其余未判状态在 DOCUMENT_ADJUDICATION.csv (source asset outside this public snapshot)，关门见 [GATE_RESULT.md](GATE_RESULT.md)。

**DRUG_TRANSLATION LINE PAUSED — INDICATION EVENT IDENTIFIABILITY NOT QUALIFIED IN CURRENT COHORTS.** 这不是宣称所有 FDA Rx 子集无解，而是当前公开源/当前设计未支持把 indication event 送去训练。后继建议以独立 Experiment ID 审核 PhysioNet PADS：真实个体诊断、左右腕传感器和问卷的匹配/泄漏边界是否足以让传统统计与多通道模型有可区分的决策。新问题不借 EXP024 的旧样本或门槛当确认。EXP022 的 FDA 监管事件层仍保存并可单独使用。
