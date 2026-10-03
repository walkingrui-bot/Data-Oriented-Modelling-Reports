# EXP024 近年 FDA 当次标签与适应症证据报告

研究 ID `STAT-PSYMOE-EXP024-20261002-001`，2026-10-02，`EXPLORATORY`。**2010–2024 cohort 的 source URL 门通过，正文类型门未通过**：40/40 随机选出的真实 FDA action 有同-key `Label` URL 且 PDF 可访问，但原申请 NDA 15 份中已确认 2 份为 OTC 包装／消费者资料而无所要求的处方 I&U，因此该子层最多 13/15，低于冻结 ≥14/15。其余 38 份只保留机器原始读取，不推断人工资格。

EXP023 的旧 20+20 跨全年份样本在 metadata URL 上限即停止，EXP024 独立更换为 2010–2024 和 NDA/BLA 各层，不改旧样本。完整来源支持：ORIG NDA 1,410 application，其中 1,384 有同-key URL；ORIG BLA 204/203；efficacy NDA 832/817；efficacy BLA 177/175。样本四层 15/15、5/5、15/15、5/5 有 URL。40 份 PDF 在内存读取，46.3 MB，总量低于预设网络预算，无原件文件副本。PDF 可解析和自动命中 I&U 不等于真正当次标签或新增 indication。

两条停止证据详见 [GATE_RESULT.md](GATE_RESULT.md) 和 DOCUMENT_ADJUDICATION.csv (source asset outside this public snapshot)。NDA205434 的官方源是 FLONASE Allergy Relief OTC 包装与问答册；NDA205352 是 Aleve PM corrected OTC carton/Drug Facts。其类别不是本轮冻结的完整处方 `INDICATIONS AND USAGE`。保留 action 日与 document metadata 日，并未用后者替代前者。因冻结 NDA 子层已数学上无法达到门槛，停止余下 38 条人工审读；这些记录仍有 URL、HTTP、PDF 页数、短片段和未裁决状态。

失败层级为 **document-role / cohort identifiability**。没有适应症差分、product-specific indication、historical first-public、NCT/target/disease、随访删失或模型结果。下一步不继续在本实验排除 OTC 以求通过；按预先写下的路线判断，暂停当前 FDA indication-specific Drug Translation 分支，转向另一个具有独立真实个体与多通道观测的数据问题。EXP020 STOP_A、EXP021 STOP_5、EXP022 `REGULATORY_EVENT_LAYER_READY` 和 EXP023 metadata 门失败均原样保留。
