# EXP028 — PADS 认知负荷静息任务的独立通道信息

研究 ID `STAT-PSYMOE-EXP028-20261002-001`；2026-10-02；`EXPLORATORY_RETROSPECTIVE_DEVELOPMENT`；父阶段 [EXP027](../EXP027/CLOSEOUT.md)。EXP026 内部 test97 已看且冻结增益门失败，EXP027 单项 `Relaxed` 的开发划分稳定性 3/5 未达 4/5。两者原样保留。用户自治授权下，本轮仅问新的生理问题：官方 PADS 第二个双腕任务 `RelaxedTask`（静息姿势加 serial sevens 心算）是否比单纯 `Relaxed` 更稳定地提供问卷之外的横断面 PD/DD/HC 区分信息？官方 [PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 说明认知负荷可能诱发轻微动作病理。这是事先选定的一个真实任务，非 11 项任务的搜索或外部确认。

H1：心算任务的简明双腕统计量相对问卷有稳定增量，提示任务协议而非网络容量是下一阶段优先因素。H0：第二个单任务仍未提供稳定增量，应暂停 PADS 单任务 motion/shared 分支，寻找独立更有识别力的数据问题。两种结果都会改变是否继续为这个场景读取其余九项时序和训练 Stat-MoE/Ganglion。

## 样本与来源门

- 仅 EXP026 原开发 `train+validation` 372 人（HC62、PD220、DD90），使用 EXP027 已冻结的 5 seeds×5fold FOLD_MANIFEST.csv (source asset outside this public snapshot)。已见 test97 的 `RelaxedTask` 原件不下载，特征不使用；不能将其作为新确认。问卷特征只引用 EXP026 唯一 `FEATURES.csv` 的 q01..q30，M1 对照只引用 EXP027 已保存同 fold OOF 概率，不另复制问卷/旧模型输出。
- 新来源逐人从官方 `movement/observation_###.json` 核 `RelaxedTask`、100 Hz、双腕、Time+Accel XYZ+Gyro XYZ 7 列、各来源行数，原位读取 `movement/timeseries/###_RelaxedTask_{Left|Right}Wrist.txt`。原始响应只在内存；本实验保存唯一新派生表 `COGNITIVE_FEATURES.csv`（人 ID 与每腕10统计+对应绝对差10）、`SOURCE_AUDIT.csv`。运动统计公式完全复用 EXP026 `wrist_features`，不根据标签/性能改频带或时序处理。
- 最多 372 observation+744 时序=1,116 请求，≤1,200 请求、≤180 MiB、并发≤10。HTTP/shape/通道错误、缺失和重试按人保留。拟合前来源门：整体双腕可读率 ≥95%，HC/PD/DD 每组 ≥90%，零 schema 语义错误；任何不达即 `STOP_SOURCE`，不替换人或任务。所有人保留缺失，fold-train 内插补+缺失标志；不把 missing 当 zero。

## 统计对照与事前决策

- `M4 = 30项问卷 + RelaxedTask双腕30统计`，同 EXP026/027 class-weighted L2 三类 multinomial logistic，λ 固定 0.1，fold-train 插补/标准化、5,000步或 `gradient_inf<1e-6`。25 fold 各拟合一次。M1 使用 EXP027 同 person/fold 的 OOF 预测，不重新选 λ。M3 单纯静息来自 EXP027 同 fold 预测，仅为**二级任务对照**，不影响资格门或模型配置。
- 每次 372 人 OOF 宏平均 log loss 和三类 balanced accuracy；M4 对 M1 的改善须五次中 ≥4 次同时满足 loss≥0.02、BAcc≥0.03，并且剩余重复两指标都 ≥0。未过则单任务 motion/shared 在当前 PADS 设置暂停，不继续为模型造任务；通过也仅是开发集观察，须寻找真正未见的人群/中心，不能重用 EXP026 test。
- 数值未收敛或预算中断保留失败现场，不以调 λ、换阈值、剔除 DD 类或查看 test 解决。组内 5 次/25 folds 相关，报告不能称独立重复队列。原诊断与问卷同次采集，临床盲法与外部迁移未识别。无未来进展 outcome。

输出一份派生新任务特征、source audit、25 fold 新模型 OOF、fold/repeat 指标与优化状态，以及门、报告、关账。每个实质性尝试运行前登记；局部检查只限本 ID 输出与直接依赖文件，不作全仓门/无关哈希。
