# EXP060 关账

- 原问题：在目标站真实当前PM缺测的24小时预测中，本站气象与邻站污染联合是否提供超过仅邻站的稳定增量？
- 唯一尝试`EXP060-STAT-001`：官方UCI501原ZIP一次8,192,212字节，内存解析；B0/N1/W1/J1按计划固定训练、评价；三ridge参数仅存一份MODEL_STATES.json (source asset outside this public snapshot)，1664留出行派生PREDICTIONS.csv (source asset outside this public snapshot)，原输出RUN_OUTPUT_001.txt (source asset outside this public snapshot)。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_REAL_PREDICTION / NO_STABLE_JOINT_WEATHER_GAIN`。
- 门未过原因：2016同站J1相对N1改善3.80%且日区块区间上界<0；2016两整站J1退化0.42%、区间跨零，2项预定条件失败；不调门。[冻结门](GATE_RESULT.md)。
- 已知：邻站统计N1相对原邻站中位在本源有数值收益，联合气象的新增收益不稳定跨整站；2017未来×整站仅16行。
- 未知：缺失选择机制、独立城市/新时期的N1泛化、其他空间结构。不得把同站改善写成共享核心价值。
- 决策：此固定任务不启动Ganglion；保留N1传统统计基线。下一最有信息增益问题是能否找到**独立、多站、真实缺测及未来PM的外部来源**来挑战N1；没有这种数据就暂缓任务外部资格，而非在已见测试上继续调模型。新问题另立ID。
- 局部验证8/8见[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)；未运行NN、全仓门或哈希。
