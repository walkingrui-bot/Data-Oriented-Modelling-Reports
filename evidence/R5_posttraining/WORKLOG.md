# 工作日志

## R-READ-001 — 来源阅读与实验操作化

- 2026-09-25；COMPLETED；无模型加载、无训练。
- 输入：用户指定任务 MD、机制 DOCX；完整文本和四幅图读完，来源复制到 sources/。
- 第三/四轮 RTG 原始包在有限指定区域未定位，云端数值仅作为材料引用。
- 研究入口、正式登记册、最新工作区状态已查；独立新目录，不继承旧主体。
- 保留两个事前问题：联合预算与最小方程的差异；静态组合可能被无写回迭代基线完全解决。取舍见 correction_log / PLAN。
- 工程/科学状态：未运行 / 未检验。下一步：局部实现与合同测试，再固定 5-seed 离线运行。

## A-PREFLIGHT-001 — 当前模块合同与一次更新 smoke

- 2026-09-25；启动前状态 **RUNNING**。
- 配置：合成 N=10、种子 731，非正式训练/验证/测试数据；随机 reader，不训练能力。
- 命令：`.venv-neural/bin/python -m RTG_POSTTRAIN_V01.tests.test_contracts`。
- 目的：精确规则分区、标签约定、后代行写回与预算、无写回等价、行重排、继承通路、等参数/冻结 base、诊断输出。
- 预期输出：`attempts/A-PREFLIGHT-001/stdout.log`、`stderr.log`、`completion.json`。
- 不使用任何正式 OOD 得分，不承担科学验收。

### A-PREFLIGHT-001 结果

8/8 合同通过，实际测试 0.613 秒，退出 0；完成时间 2026-09-25T07:06:50Z。基线冻结、两臂同参数和单次真实前向均通过。没有科学能力结果。

## A-SMOKE-001 — 完整管线的小规模独立执行

- 启动前 RUNNING；种子 731；base/RTG/recurrent 各 2 updates、batch=8、validation/test 各 4 rules；长度仅 1/2/4。
- 目的：验证数据保存、固定 training→selection→evaluation→trace→surface→completion 出口可运行；随机未学好模型分数不用于科学推断或正式选参。
- 配置与输出都在 `attempts/A-SMOKE-001/`；不继承到正式五种子。
- 命令：`python -m RTG_POSTTRAIN_V01.src.campaign --config RTG_POSTTRAIN_V01/attempts/A-SMOKE-001/config.json --run-id SMOKE-PIPELINE-001 --output-root RTG_POSTTRAIN_V01/attempts/A-SMOKE-001/output`。

### A-SMOKE-001 结果：FAILED

07:07:48Z 退出 1。base 做了 2 更新，RTG 的 L=1 无 grad_fn，未完成 post-training。原始 traceback / source snapshot / 输入 / step0 检查点均保留。R-001 修复两臂的一步梯度边界和真实更新计数；不作为机制科学失败。

## A-PREFLIGHT-002 / A-SMOKE-002 — R-001 后局部重验

启动前 RUNNING；父尝试 A-PREFLIGHT-001 / A-SMOKE-001。同样工程 seed 和微型数据预算；唯一改动 R-001。分别输出到新的 attempts 目录，不覆盖失败。正式五种子尚未启动。

### A-PREFLIGHT-002 / A-SMOKE-002 结果

9/9 合同通过（0.370 秒）；修正后的完整 smoke 退出 0，全部 240 预测/诊断/重命名输出完成，实际 optimizer updates=4。07:09:38Z 结束。只验证接口，不作为能力证据。

## A-CAMPAIGN-001 — 固定五种子正式 Phase A

- 启动前 **RUNNING**；2026-09-25，输入 sources/ 两文件、PLAN、`configs/phaseA_v1.json` 和 R-001 后源码。
- 种子 101/202/303/404/505；每种子 base 800 batches、RTG/recurrent 各 1200 batches，batch128；只给最终答案。
- 预期输出：根 data/checkpoints/results/traces 和 `attempts/A-CAMPAIGN-001/` 的原始日志、source_snapshot、config、分阶段事件及终态回执。
- 命令：`.venv-neural/bin/python -m RTG_POSTTRAIN_V01.src.campaign --config RTG_POSTTRAIN_V01/configs/phaseA_v1.json --run-id A-CAMPAIGN-001`。
- 固定代码和课表一次执行到底。训练命令无中间控制台进度；agent 不查询进程、不抽读日志或成绩，只等待整批命令结束后读取结果。

### A-CAMPAIGN-001 完成回执

2026-09-25T07:11:41Z，整批退出 0，59.43 秒；5/5 seeds 完成，真实 optimizer updates=12970，正式最终预测 563200，执行 errors=[]。此后才开始 agent 结果读取与冻结审计。

## A-ANALYSIS-001 / A-AUDIT-001 — 训练退出后的统计、局部恢复与证据检查

- 启动前 RUNNING；无追加训练、无改参、无新模型选择。
- A-ANALYSIS-001：读取既定 CSV/NPZ/trace，按冻结 Gate A 判断，rule 聚类配对 bootstrap、surface、周期基线和写入诊断，生成图表；`analyze.py`。
- A-AUDIT-001：只检查本轮所有训练标签/规则分区、原始输出与聚合一致、每 seed selected/step0 新进程各 16 个 episode×4/12 步恢复、基础 reader 全 test 状态读取和有限 trace 合同；`audit_completed.py`。
- 输出 `results/` 和 `figures/`，原始材料不改；对应 attempt 保存 stdout/stderr/完成状态。没有全仓门或哈希。

### A-ANALYSIS-001 / A-AUDIT-001 结果

两项均退出 0。全部 563200 正式输出、3600 trace steps、30 组新进程恢复检查通过；全部 25600 个 test rule-state 查询的一步 reader 正确。五种子的完整 RTG、等参数 recurrent、iterated base 和全部机制消融在 1–20 步均 100%；step0 RTG 长程有错误。Gate A 的绝对项通过、相对优势项失败。保持冻结 gate，不启动 B/C。

## A-DIAG-001 — 既有 trace 的事后方向诊断与失败示例索引

- 启动前 RUNNING；纯读取已保存输出，无模型调用、无参数更新；本项明确是看到 A 对照持平后的探索诊断。
- 问题：后训练是在把写入幅度关掉，还是让写回方向与静态规则相容？用已保存 L_before/L_after 和对应 retention 重建实际写入，测写入最大项是否对准目的节点的正确下一状态。这个真值只用于诊断，未进入训练。
- 输入：formal test.npz、既定 trace 和 selected 系数、全部 final predictions。输出：`results/rewrite_alignment_diagnostic.csv`、`traces/control_failure_examples.jsonl`、`results/diagnostic_receipt.json`。
- 只取事前固定的四个 episode/seed；不因该诊断选 checkpoint 或修改 gate。

### A-DIAG-001 结果

07:19:52Z COMPLETED，模型调用0。full写入保持近1而未关闭，预定20步轨迹的400条transition中最大写入方向100%对准正确后代，step0为4%；仅10个规则的小样本描述。全局test不同规则2553个；80控制错误例另存。旧raw保留base-only41120错、step0 RTG2726错；full无错。

## 交付源码与文档

新增 `reproduce.py` 只负责向新目录复跑、采用唯一run ID，补充独立训练/绘图依赖清单。分析/恢复CLI增加显式run-id参数，默认值与本轮相同；不改已运行训练源码、原始结果或gate。REPORT逐项回答原任务12问，CLOSEOUT区分三轴和未运行阶段。

## A-PACKAGE-001 — 局部文档检查与完整工件包

- 启动前 RUNNING；无训练/模型推理。
- 输入：本项目全部非缓存文件和本研究ID的四份记录索引；不纳入其它研究、旧模型或外部venv。
- 只检查本轮Markdown本地链接、末尾新增工具语法和必需工件；压缩包用ZIP CRC读取核对，不计算SHA/树哈希。
- 预期输出：仓库根 `RTG_POSTTRAIN_V01_20260925.zip`；`attempts/A-PACKAGE-001/completion.json`、外部最终 `PACKAGE_RECEIPT.json`。最终回执在归档完成后生成，不被冒称提前存在于包内。
