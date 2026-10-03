# EXP074 — WISDM 跨设备活动片段的无标签边界来源门

研究 ID `STAT-PSYMOE-EXP074-20261002-001`；2026-10-02 BST；`EXPLORATORY_LABEL_INDEPENDENT_EPISODE_SOURCE_AUDIT`；父阶段 [EXP073](../EXP073/CLOSEOUT.md)四路同刻与全18类支持门失败。新科学问题：对手部/物体动作，是否存在**不用目标活动码即可从每设备原始时间轴切出片段**的来源证据，使手机/手表虽不同钟仍可按同人同次任务比较统计摘要？若必须先读活动标签才能切样本，活动识别建模会包含目标指导的分段，故先停止，不做漂亮但无效的融合结果。

## 固定活动与审计输入

按 [UCI507官方说明](https://archive.ics.uci.edu/ml/machine-learning-databases/00507/WISDM-dataset-description.pdf)预选十二码 `F,G,H,I,J,K,L,O,P,Q,R,S`：打字、刷牙、吃/喝、接球、运球、书写、拍手、叠衣等手部/物体动作；排除A–E移动姿势、M踢球。这是新的 episode 级任务，不修改EXP073全18类失败。仅引用EXP073已保存逐人逐类四路来源派生矩阵 (source asset outside this public snapshot)，不复制原始ZIP、行或矩阵；该矩阵与本任务同次官方快照，允许先审必要条件。独立单位仍为人，片段×设备不是独立人。

## 事前来源门

在固定12类中，对每人四传感器的每类均要求≥500合法行、时间跨度在150–220×10^9 tick内；范围来自官方每活动约3分钟，仅检来源完整性，不把绝对timestamp当共同时钟。对每一路所有有时间范围的官方18类，按其**最小timestamp**排序；四路对选定12类的相对先后顺序必须完全相同，保证同人同次任务序位可关联，但不因此声称毫秒同步。

为核“可不看标签切片段”的**必要证据**：对每个选定活动，在每一路原时间轴中，它与紧邻上一个活动区间的间隔、与紧邻下一个活动区间的间隔都须≥5×10^9 tick；如果它是原序列首/尾，缺少的那侧由文件边界代替。若任一相邻类时间区间重叠或间隙不足，该设备无法仅凭这个固定时间空隙规则证明片段边界；不得改用标签去切、不得事后降低5秒。至少**40个不同人对全部12类、全部四路**通过行数/时长、同序和双侧可见边界门，才`LABEL_INDEPENDENT_12_EPISODE_SOURCE_READY_FOR_MODEL_DESIGN`；否则`STOP_LABEL_INDEPENDENT_EPISODE_SUPPORT`。这只是必要条件：即使通过，还需下一ID在原始未标记时间序列上实测分段准确率，不能直接训练模型。

预登记尝试`EXP074-EPISODE-SOURCE-001`，命令`python3 audit_episode_boundaries.py`；输入仅EXP073派生JSON，CPU≤2分钟、无新网络/原始数据副本。输出`SOURCE_GATE.json`、`RUN_OUTPUT_001.txt`、门/报告/关账，只留逐人结果和失败原因计数，不复制前一矩阵。0模型、0test性能、局部校验，不做全仓或哈希。
