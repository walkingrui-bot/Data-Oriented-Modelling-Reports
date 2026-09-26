# 修正与取舍记录

## O-001：事前规格取舍（2026-09-25）

当前任务说明的最小实现只对 geometry proposal 付费，M 混合后归一化；机制档案 §9 对 geometry 与 M 使用共同预算。首轮按更具体的任务方程实施，明确保留联合预算未测试的缺口。尚未看到能力结果；不是结果后改门槛。

## O-002：事前控制和模型容量（2026-09-25）

加入 iterated frozen reader 和 RTG step0，保留同参数 recurrent adapter 的同长度计算机会。静态组合在理想一步能力下可直接完成，故不能以 full 的高 accuracy 单独宣称 RTG 必要。RTG 的 N×N/N×d 动态状态和普通适配器 d 维状态不等容量；“同参数”仅指训练参数数量。

后续真实实现错误、失败运行和改动在此追加，不覆盖旧结果。

## R-001：冻结 reader 的一步梯度边界（2026-09-25T07:07Z）

- 旧实现：对所有长度调用 loss.backward；L=1 的 RTG 输出只依赖 frozen base，没有 grad_fn，完整管线 smoke 在 post-training 抛 RuntimeError。
- 失败证据：`attempts/A-SMOKE-001/`，保留源码、输入、base 已做 2 次真实更新、step0 检查点、traceback。旧 completion 错把未完成 seed 的更新数记成 0；实际 base 的 2 次在 train_curve 和 BASE 事件中可追溯，此处更正，不追改旧回执。
- 新实现：L=1 对两臂统一仅记分，不反传、无 momentum step；L=2–4 保持唯一最终答案 CE。逐 batch 记录真实 optimizer_step，包含失败 seed 已完成的更新。
- 增加单步输出梯度合同；新 smoke 使用全新输出/ID。无正式能力结果、无 OOD 5–20 结果已见；正式配置和 gate 未改，更新计数口径在 PLAN 中显式更正。
