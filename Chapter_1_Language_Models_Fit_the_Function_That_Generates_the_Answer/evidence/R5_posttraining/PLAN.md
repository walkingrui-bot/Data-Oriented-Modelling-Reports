# RTG 后训练功能验证 v0.1：本地执行计划

## 身份、来源、边界

- `research_id`: **P05-RTG-POSTTRAIN-20260925-001**；平台 P05；父实验：无，新生独立模型。
- 建档：2026-09-25，Europe/London；执行者：本任务 Codex agent。
- 性质：**EXPLORATORY**，固定首轮配置和门槛先于能力结果；不是云端 pilot 的确认性复现。
- 授权：用户“做实验吧”，并提供 `sources/` 内两份具名材料。当前任务说明作为施工规格；机制档案的云端成绩是未独立核验的来源引用。
- 机制档案全部 255 个文本段和四幅图已读。有限目录搜索未定位 RTG 第三/四轮原始实验包；不以附近 CE²G 同名轮次代替。
- 本项目从零实现；不继承 AIA、CE²G 或先前 Transformer 项目的模型、数据、优化器或实验结论。其目录和旧失败保持原状。

## 问题与可反驳假说

仅最终答案监督，能否让 RTG 将一步关系能力扩展到新规则的长程组合，并获得相对普通循环适配器的收益？

H-A1：训练长度 1–4，测试 8、10、12 步平均准确率均至少 90%。
H-A2：长程 RTG 比 base-only 和等参数普通 recurrent adapter 明显更好。
H-A3（诊断，不额外增设晋级门）：收益是否依赖 geometry write / inherited state，是否已经由重复调用一步 reader 获得。

反证/不可识别情形：长程低于目标；与普通适配器持平或更差；零后训练/无写回迭代本已满分。静态 permutation 的精确一步函数可直接迭代，这使 A 的绝对分数不能单独识别写回必要性。这个风险在能力结果产生前登记，不通过削弱基线来规避。

## Phase A 模型和监督

1. N=10，结构化随机顺序的完整有向规则表。符号是任意的 10 个类别；没有文本 LM。
2. 从随机参数训练一步注意力 reader：query/key/value 符号嵌入和线性答案层。没有硬编码的 `f[current]` 查询；正确函数迭代仅在隔离的标签生成器出现。
3. 一步预训练：800 updates ×128，最终一步标签；固定全量执行，末态保存 `BASE_ONE_STEP.ckpt`。新 validation 规则上一步准确率须 ≥98%，否则本轮 A 不具备合格基础。
4. 冻结 reader，用其所有查询的 logits 构造 L_ext；每行去均值除 RMS，固定 geometry_scale=1。这个无标签尺度转换保持 argmax，不把分类置信度的任意大小变成写入单位。
5. RTG 维护独立 L[N,N]、M[N,16]；phi 由冻结 reader 的 source-query、destination-key、source-context、destination-value 经可训练线性层得到。真实前向每步只有一个 argmax transition。反向用 softmax straight-through 近似；不称为精确离散梯度。
6. g=normalize(W_phi phi_ab + gamma W_M M_a)，写入目的节点 b 的整行后代几何；M_b 部分混合再归一化。gamma/eta/rho/retention 可学，interaction/mutation/projection 当前为零。
7. **规格取舍 O-001**：依任务说明的最小方程，预算 B=1 限制每次 ΔL 的 Frobenius 范数；M 单独归一化。机制档案 §9 的 ΔL、ΔM 联合付费版本尚未实现/测试，不称完全等价。
8. RTG 后训练：1200 scheduled batches ×128，batch 长度均匀取 1–4，只有最终答案 CE，无辅助损失，无正确中间状态/轨迹/M/g/谱系输入。base 参数更新比例 0%。**R-001 启动前修正**：一步输出先于写回且 base 冻结，所以两臂 L=1 只记分不反传/不动 Adam，只有 L=2–4 作 optimizer step；真实更新数独立记录。
9. 等参数普通 recurrent adapter 使用完全相同的 phi 编码和三个 16×16 线性映射、四个可学标量；全局 16 维 Elman 型状态，加有界残差读出。每个参数参与计算；没有为配平放置闲置参数。相同 base、初始 trainable tensors、训练 batches、更新次数、长度预算。允许同样反复调用 reader，避免把可重复计算特权只给 RTG。记录各自实际运行时间；参数匹配不等于 FLOPs/状态容量完全匹配。
10. 每 200 updates 自动在固定 validation 规则、长度 1–4 评价；按 accuracy 优先、CE 次优选择 checkpoint，候选包括 step 0。保存初态、selected、final、optimizer/RNG 和更新数。训练不访问 OOD。

## 数据隔离、独立单位与评估

- 规则是 permutation；用精确 Lehmer rank 作可逆整数 ID，`rank % 10` 的 0–7/8/9 划分 train/validation/test。无需哈希，所有阶段实施同一排他分区。
- episode 每次重新采样 rule、start、row order。训练阶段允许同 split 内规则再次采样；记录实际所有训练 rule IDs/start/row order/length/target，监督仍仅最终答案。
- 5 独立种子：101、202、303、404、505。独立复现实验单位是 seed，seed 内统计按 rule 聚类；重复 start、长度与对照不算独立规则。
- validation：128 个不重复规则，2 个不同起点，各长度 1–4；base 选定后不再训练 reader。
- test：每 seed 512 个不重复规则，各 2 个不同起点，长度 1,2,3,4,5,6,8,10,12,16,20；同批 episodes 配对比较所有条件。
- 条件：单次 base-only、iterated frozen base、RTG step0、RTG full、no-write、no-inheritance、reset-M、gamma=0、unbounded-write、selected recurrent adapter。
- 表面诊断：128 个 test 规则额外做行重排和随机符号置换（置换后规则仍须属于 test split），长度 4、12；保存原表/置换和配对输出。它们不能用于模型选择。
- 全部最终预测留档；内部全矩阵 trace 仅预定每种子前 4 个 episode ×长度 4/12/20，以及至多 4 个 RTG 错例。trace 记录 L/M/g/alpha/写入范数/entropy/effective candidates/top share 和算法依赖谱系；谱系指针不当作因果必要性证明。
- 主指标：每 seed/condition/length accuracy、相对于控制的百分点差，5 seed 均值与范围。可补充按 rule 配对 bootstrap CI；不把同一规则的多长度当独立样本。

## 冻结的 Gate A 操作口径

- 全部 seed 基础 validation 一步能力 ≥98%。
- full 在 8、10、12 各长度的 5-seed 均值 ≥90%。
- 平均 8/10/12 准确率比 base-only、等参数 recurrent adapter 都至少高 **5 个百分点**，且每个 seed 差值均 >0；这是对“明显高于”的本地事前量化。
- 20 步只报告；无论是否通过，不用本次 OOD 改参补训后追认同一次 gate。
- A 失败则完成冻结消融及本阶段失败定位，交付条件关账；不跳过 A 进入 B/C/D。
- A 通过才为 B 创建可执行协议；B 通过才 C。B/C 原任务方法、三种机制消融和门槛继承原稿；尚未运行时只作为条件路线。完成 C 必须先交中间报告，D 接线留待后续具体决定。

## 执行预算与存档

- 本轮固定 5×(800 base +1200 RTG +1200 recurrent)=16000 scheduled batches；实际 optimizer updates 扣除两适配器的 L=1 空梯度批次。每 seed 训练完成后才评估 OOD，整个 campaign 不根据中间结果增改课表。
- CPU 单进程，torch threads=1；单次 campaign 正常目标在 30 分钟内，硬预算 90 分钟，由程序在安全保存点记录 TIME_BUDGET 后退出。存储预算 1 GiB，预计显著更低；不清理旧研究数据。
- 开始前做当前包局部合同、梯度/数值和小规模一次更新 smoke；smoke 不提供 OOD 能力结果。失败留档、修正用新 run ID。
- **离线执行规则**：启动后 agent 不读进程/日志/中间成绩/状态，也不更换训练代码；既定 5 seed 全部保存退出后统一验收。程序固有日志、validation、checkpoint 不构成 agent 巡检。
- 正式运行前保存源码快照、config、environment 和 RUNNING 尝试条目；每个 seed 子阶段开始/完成由程序追加 attempt events，异常 traceback 原样保存。
- 命令（仓库根目录）：`.venv-neural/bin/python -m RTG_POSTTRAIN_V01.src.campaign --config RTG_POSTTRAIN_V01/configs/phaseA_v1.json --run-id A-CAMPAIGN-001`。
- 输出：本目录内 source/configs/data/attempts/checkpoints/results/traces/figures；最终 REPORT、关账和独立 ZIP 包。依赖环境仅保存版本/运行说明，不复制整个 venv；本地存在不等于 Git 跟踪或异地备份。
- 最小验收：本模块合同；正式结果计数/边界/分区；selected 检查点新进程小批恢复；本轮 ZIP CRC 和文件清单；无全仓测试、历史重放或 artifact 哈希。

## 当前状态

PREPARING。能力结果尚未产生；本计划应连同追加 WORKLOG / correction_log 阅读。

以上为启动前状态，保留在 `attempts/A-CAMPAIGN-001/PLAN_at_launch.md`。2026-09-25最终状态：COMPLETED_CONDITIONAL；A绝对外推通过、相对优势未过，B/C/D/E未运行。最终事实见 REPORT/CLOSEOUT；原判据不改。
