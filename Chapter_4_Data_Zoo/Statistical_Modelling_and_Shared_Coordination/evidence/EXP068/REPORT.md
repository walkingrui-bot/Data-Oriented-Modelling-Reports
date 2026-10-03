# EXP068 报告：双惯性传感器真实跨人任务来源合格

UCI240 [官方数据页](https://archive.ics.uci.edu/dataset/240/human%2Bactivity%2Brecognition%2B)所列30名受试者、六类活动与预处理128点重叠窗口，在官方原件上可复核：train 21人/7352窗，test 9人/2947窗；六类在两组每人均有记录。六个加速度/角速度通道完整有限、逐窗对齐，0人交集、0跨组完整六通道精确重复。所有冻结来源门通过，结果为 **`REAL_HAR_PERSON_SPLIT_SOURCE_READY_FOR_STAT_DESIGN`**。[门](GATE_RESULT.md) · 来源派生矩阵 (source asset outside this public snapshot)。

这比前条空气质量缺测任务更适合现在的系统问题：它有明确的第二传感器和按人的独立留出，能区分“单传感器统计已足够”与“双传感器提供可保持的增量”。仍需新实验用传统统计先测，只有额外结构需求才研究 Stat-MoE 或 Shared Ganglion。本数据是受控实验室条件、腰部手机、预处理重叠窗；不等于临床、自由生活或连续原始传感器流。气体传感器漂移候选因官方页面许可描述冲突被暂存，未读取数据。[选择及原门](PLAN.md)。

本次实际验证为原件12个信号文件、两个人/标签文件与8项局部派生一致性；未做模型训练、性能测试、跨硬件或全仓验证。终端输出 (source asset outside this public snapshot) · [局部验证](LOCAL_VALIDATION.json)。
