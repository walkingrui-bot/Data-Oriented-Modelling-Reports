# EXP057 — 真实六路数据上的共享核心扩容止损实验

研究 ID `STAT-PSYMOE-EXP057-20261002-001`；2026-10-02；`EXPLORATORY_RETROSPECTIVE_DEVELOPMENT_CAPACITY_TEST`；父阶段[EXP056](../EXP056/CLOSEOUT.md)。用户明确要求实践检验“模型或共享矩阵太小”并及时止损。此新实验直接比较大小，不改EXP056原只读门，也不把旧test重新叫确认。

## 问题、数据和边界

在[EXP017](../EXP017/REPORT.md)同一真实26.06六路原生管线、同一target-disjoint train/validation和源内五折OOF导出状态上，扩大共享核心输出或扩大六接口与共享核心的共同维度，是否在验证log-loss给出有实用幅度、跨seed一致的增益？结果无论怎样都决定是否继续花资源做64D：若32D未达门立即停；若达门才做64D。终端pair是target×disease，validation独立单位为212个target/4132 pair；train为990个target/17702 pair。现有test 232个target在EXP017及之后已暴露，**本实验不读取原test预测、标签、模型结果，不对test打分**。原来源当前整理状态没有历史decision-date锁，结果只限回顾性开发工程选择，不能称drug translation确认。

以EXP017原位`train_channel_oof.parquet`重建训练的四维源状态，用原位`routing_weights.json`及仅训练组重拟合专家生成验证状态；须用原EXP017检查点和已有验证预测核对重建误差≤2e-6，否则停止。不能复制原始来源、旧状态或旧检查点；只保存本实验必要的新模型状态、trace与派生验证预测。

## 固定模型和判据

- B16：六接口各`Linear(4,16)+Tanh`，共享`Linear(16,16)+Tanh`，输出`Linear(16,1)`，即原结构但从头训练到新共同预算。
- C32：六接口仍4→16，共享16→32，输出32→1。只扩大共享矩阵的输出宽度，独立于接口瓶颈。
- F32：六接口4→32，共享32→32，输出32→1。扩大全模型latent；不更改源内统计路由。
- 第二阶段仅在对应32D过门时运行：C32过门才做C64（接口4→16，共享16→64，输出64→1）；F32过门才做F64（接口4→64，共享64→64，输出64→1）。两个支线各自按同规则与其32D父臂比较；不做64D的test评价。
- 所有臂种子101/202/303；原拆分与源状态；全批Adam lr=.002，BCE-with-logits，`max_epochs=2000`、validation patience200、改善容差1e-7；同硬件、float32、每epoch记录train/validation loss。按每seed最低validation loss保存唯一新模型；最大epoch/早停、训练秒数和参数数都留档。宽度导致参数数和计算不同，比较按相同epoch/优化规则，并报告实际资源，不伪称相同FLOPs。原EXP017 1000轮成绩只作历史参照，不作当前共同预算对照。
- 对每个32D臂，以同seed B16验证log-loss为对照。过实用门需：三seed**中位**差 `wide - B16 ≤ −0.0010`，且至少2/3 seed差 `≤ −0.0005`。若均未过，停止为`NO_PRACTICAL_32D_VALIDATION_GAIN`，不运行64D。若任一过门，其对应64D臂按同一规则与对应32D臂比较；64D不达门则在32D止损。所有结果还与原位Stat-MoE validation log-loss作描述性比较。
- 若任何候选最优epoch=2000且验证曲线仍明显下降，只能报告固定预算的结果，不把未见更长训练的效果归因于容量；标`OPTIMIZATION_LIMIT_REMAINS`。验证集已在旧实验被看过，扩大即使过门也只支持当前开发候选，不支持新确认或泛化。

不调门、种子、学习率或特征。若重建验证失败、NaN、资源异常，保留失败原件并停止相应run；不得拿已看test救模型。最长本地训练预算90分钟，不使用付费计算。核心宽度和总参数数会由实际实例静态核对，非必要哈希禁止。只跑当前脚本的局部数据/数值/保存点重建检查，不跑全仓门。

## 输出与尝试

登记 `EXP057-CAPACITY-001`，实际命令 `/Users/rui/.cache/stat_psymoe_exp017_env/bin/python run_capacity.py`，原位输入为EXP017 native pair派生特征、cohort、route、训练OOF、旧验证预测与原检查点；输出`STATE_RECONSTRUCTION.json`、`MODEL_STATES/`各新状态唯一文件、`TRACES/`、`VALIDATION_PREDICTIONS.parquet`、`METRICS.json`、`LOCAL_VALIDATION.json`、工作日志、门、报告、关账。失败另存`FAILURE.json`/原终端输出，不覆盖。不同宽度新模型是不同训练状态，不是同一检查点副本。
