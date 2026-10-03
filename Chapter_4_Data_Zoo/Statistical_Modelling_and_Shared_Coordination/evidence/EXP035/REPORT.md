# EXP035 独立双足力来源审计报告

研究 ID `STAT-PSYMOE-EXP035-20261002-001`；2026-10-02；`EXPLORATORY_SOURCE_AUDIT`。EXP033 的 Si→Ga 一次传统统计来源压力测试达预设点估计门，但 EXP034 未能核实跨研究人员排重。为避免把不同传感器/任务硬套成确认，本轮固定八个公开数据候选，对真正独立 PD/健康双足垂直力原件逐项审联合门。

八候选 **0 合格**。PhysioNet GaitNDD 有15 PD/16健康和左右 force-sensitive 信号，但 PD 人数不到事前20；Gait in Aging and Disease 仅5 PD/10健康且公开连续输出是 stride interval。[Daphnet](https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait) 是 PD FoG 加速度事件，[PADS](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 是双腕任务。独立 [MyGait](https://zenodo.org/records/15672744) 虽有44 PD/45健康与双足 IMU，其压力字段官方明确因可靠性而不使用；它不能验证牛顿双足力模型。[GaitRec](https://www.nature.com/articles/s41597-020-0481-z) 有大量真实左右 GRF，却是肌骨损伤与健康，无 PD。另一巴西真实力学库只含26 PD、无健康；Nordic walking 数据中的 control 是另一 PD 干预组，而不是健康。

因此本轮把 `GAITPDB_DIRECT_FORCE_EXTERNAL_CONFIRMATION_PAUSED — SOURCE_IDENTIFIABILITY_LIMIT` 记为路线状态，保留 EXP031/033 的各自范围。不能用“压力字段存在”“两足设备相似”或“control”一词替代来源门。结论仅覆盖固定八项，完全没有新模型性能结论。

下一个信息增益较高的真问题是 [MyGait](https://zenodo.org/records/15672744) 的双足 IMU 与 PD/健康真实分组是否可在**明确许可证、逐人/逐任务文件交集与缺失**下建立新数据产品。这是不同观测模态，不是 EXP033 外部测试；若源许可/交集不可识别即在新 ID 停止，不下载大包或硬训。逐字段判据见 [来源矩阵](SOURCE_MATRIX.md)。
