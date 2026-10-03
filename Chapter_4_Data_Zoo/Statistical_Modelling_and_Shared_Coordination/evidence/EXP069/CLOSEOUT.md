# EXP069 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_PERSON_HOLDOUT_STATISTICAL_TEST`；执行 `COMPLETE` / 工程 `VALID_SCOPED_OOF_ANALYSIS` / 科学 `JOINT_INCREMENT_NOT_QUALIFIED_AT_DEV_GATE`。
- 原问题：加入真实陀螺仪能否在加速度计之外提供跨受试者、值得成本的增量？唯一尝试 `EXP069-STAT-001`按[冻结计划](PLAN.md)完成官方训练21人的固定5折人级OOF。原件来源结构对EXP068重核一致；无门槛/特征/超参修订或重试。来源 (source asset outside this public snapshot) · 运行日志 (source asset outside this public snapshot)。
- 正观察：ACC分类能力相对先验明显；JOINT对ACC的平衡准确率点差+0.032477，16/21人的logloss较低。
- 未过门：JOINT的logloss差−0.023868未达−0.03；按人95%区间[−0.096754,+0.076312]上界未<0。GYR单独低于ACC。四个预门只过两个，`STOP_JOINT_DEV_GATE`。[详细门](GATE_RESULT.md)。
- 按原条件，**官方test9人没有性能评分**；无`TEST_METRICS.json`或`TEST_PERSON_ROWS.csv`。本结果不证明第二传感器无效，也不证明其独立保持的收益，更不能归因为模型/共享矩阵容量。Stat-MoE与Ganglion均未运行。
- 本次实际验证：脚本语法、来源结构、OOF逐人指标重算及不触碰test评分[7/7](LOCAL_VALIDATION.json)。仅静态检查：训练定义与官方来源语义。未验证：官方test性能、不同硬件/环境、NN容量、全仓回归。
- 工件与恢复依赖：本目录计划、脚本、原终端输出、结构重核、OOF派生行/指标、门、报告、关账均为本地未跟踪新文件；依赖EXP068原件索引 (source asset outside this public snapshot)、官方URL与本地venv。原ZIP/信号无副本；无异地备份或哈希版本声明。
- 路线决策：此统计定义下不支付第二传感器/共享模型复杂度成本。将“是否有其他真实较大独立人群可以区分传感器冗余与当前样本不稳”移到新ID，先审来源、许可与人级支持。失败记录保留，登记册与入口已同步。
