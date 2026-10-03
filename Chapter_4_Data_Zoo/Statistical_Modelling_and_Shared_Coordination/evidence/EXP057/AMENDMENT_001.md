# EXP057 执行后事实更正 001

登记时间：2026-10-02，在 `EXP057-CAPACITY-001` 运行结果已保存后。此更正**不回改原计划、不改门、不更改模型或评价**。

原[PLAN](PLAN.md)写“本实验不读取原test预测、标签、模型结果”。实际[代码](run_capacity.py)通过 `pd.read_parquet(cohort_mapped.parquet)` 将包含train/validation/test的原cohort全表读入内存，然后立即按`split∈{train,validation}`过滤，才建立`dev`、`y`、源状态和模型输入；各原生派生来源表也整表读取但仅按dev键连接。原旧test预测文件、旧test成绩和test检查点性能**未读取或计算**，test标签未用作训练、验证、选型或报告指标。

因此“完全没有读取test标签”这句计划文字没有被字面满足。正确执行事实是：**test标签随原cohort文件进入内存，但在模型数据集形成前被过滤，未参与任何性能计算或决策。** 原test本就已在EXP017及后续暴露，本实验仍只有回顾性开发资格；此偏差不升级为新确认，也不能抹去。`METRICS.json`里的“test not accessed”限定为未用作评价，不能理解为原文件从未包含test行。
