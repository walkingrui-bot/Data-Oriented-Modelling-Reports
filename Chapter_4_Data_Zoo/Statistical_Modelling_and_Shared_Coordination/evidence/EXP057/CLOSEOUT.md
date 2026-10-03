# EXP057 关账

- 原问题：用户提出模型/共享矩阵可能太小，要求直接扩容实践并及时止损。事前[计划](PLAN.md)只问原六路真实开发数据上32D能否带来达到预定幅度的验证改善。
- 唯一训练尝试：`EXP057-CAPACITY-001`，完成B16/C32/F32各三seed，九个新检查点/训练trace及验证预测见[指标](METRICS.json)和`MODEL_STATES/`、`TRACES/`；原终端输出见RUN_OUTPUT_001.txt (source asset outside this public snapshot)。C64/F64按门**未运行**，不能写成失败模型。
- 执行 / 工程 / 科学三轴：`COMPLETE / VALID_SCOPED_WITH_DOCUMENTED_PLAN_DEVIATION / NO_PRACTICAL_32D_VALIDATION_GAIN + OPTIMIZATION_LIMIT_REMAINS`。
- 触发门：C32对B16三seed均更差；F32中位仅−0.000239且达到单seed幅度仅1/3，均未过预定双条件。64维止损，不改门。[门结果](GATE_RESULT.md)。
- 已知：在相同真实train/validation、相同2000轮规则下，扩核心16→32未获实用收益；整个latent扩至32有小点估计改善但未过门；延长16维预算本身改善了旧1000轮验证成绩。
- 未知：更长训练下的各宽度结果、真正未见来源/时间泛化、历史药物转化能力；16维是否理论上足够未识别。
- 记录偏差：读含test行的原cohort整表后过滤dev，未用test标签/预测/结果选型；计划“不读取test标签”的字面要求未完全符合，保留[更正](AMENDMENT_001.md)。旧test此前已暴露，本实验只是回顾性开发。
- 下一实验依据：最大未解混杂是B16仍触预算上限。最小真实实验应固定16维与同一数据/指标，检查继续训练是否优于扩容收益；无论结果如何都决定是否继续优化容量或转向数据问题。须新ID，不把本轮门追改。
- 实际局部核验：8/8见[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)；未运行全仓门、旧test重打分或非必要哈希。
