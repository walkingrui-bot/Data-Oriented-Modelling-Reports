# EXP058 — 固定16D共享模型的训练预算止损

研究 ID `STAT-PSYMOE-EXP058-20261002-001`；2026-10-02；`EXPLORATORY_RETROSPECTIVE_DEVELOPMENT_OPTIMIZATION_TEST`；父阶段[EXP057](../EXP057/CLOSEOUT.md)。EXP057的C32/F32未达到预先规定的实用扩容门，但B16两seed最优仍触2000轮边界。新问题：在**不扩大任何参数或改变六路真实数据**的情况下把同一16D训练预算延至4000轮，是否取得比本次32D扩容收益更明确的验证改善？结果决定是否继续花资源优化16D；不改EXP057门与关账。

数据与单位继承EXP057仅train17,702 pair/990 target、validation4,132 pair/212 target，26.06当前原生导出状态，无历史decision-date锁。旧test已暴露，仍不用于模型训练、选择、打分或确认。技术上原cohort Parquet含test行，重建函数整表读入再过滤，仅dev用于数组/损失；这一限制沿用EXP057[执行后更正](../EXP057/AMENDMENT_001.md)，不写成完全未读取test字节。直接复用EXP057原位代码函数，不复制源码/数据/检查点；本次新模型每seed单份状态保存。原验证状态用旧检查点验证预测核对≤2e-6才训练。

## 固定方法与停止

- 结构固定B16：六接口4→16、共享16→16、head16→1，总769参数；种子101/202/303，从相同种子**从头**训练；float32、全批Adam lr=.002、BCE-with-logits，`max_epochs=4000`，validation patience500、改善容差1e-7。只改变预算与耐心，和EXP057同seed B16**已保存的重叠轮次**（最多2000轮；seed202旧训练只到1983轮）轨迹必须在数值容差≤2e-6内吻合，否则停止为不可比较。
- 每seed在train-only拟合、validation选最佳epoch；记录每轮loss、收敛/早停、墙钟、唯一checkpoint、逐pair验证预测。原EXP057 B16 2000轮各seed最佳验证loss和F32中位改善是事前已看开发证据，不作新确认。
- 实用优化门：相对EXP057同seed B16 best，三seed验证loss改善的**中位≥0.0003**，且至少2/3 seed各自改善≥0.0002。若不过即`NO_PRACTICAL_LONG_BUDGET_GAIN`，停止此数据上的继续加epoch；若过，也仅保留16D作为当前开发候选，不把已见验证当新外部证据。若最佳epoch仍在4000轮边界，记录`OPTIMIZATION_LIMIT_REMAINS`；不自动再续训练。
- 本地训练预算≤45分钟；任何重建错、NaN、模型/trace不吻合或资源越限保留失败现场，不换阈值、不重用已看test。

运行 `EXP058-OPTIMIZATION-001`：`/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_longer.py`，输出`STATE_RECONSTRUCTION.json`、三个唯一新状态/trace、`VALIDATION_PREDICTIONS.parquet`、`METRICS.json`、局部核验、门/报告/关账与原终端输出。仅本区域验证，不跑全仓门或哈希。
