# EXP028 认知负荷静息任务开发集门

研究 ID `STAT-PSYMOE-EXP028-20261002-001`；2026-10-02。判据见事前 [PLAN.md](PLAN.md)。官方 [PADS v1.0.0](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) 旧开发 372 人的 `RelaxedTask` 双腕原件 372/372 可读；脚本 1,116 次请求另 1 次来源 preflight、148,530,961 bytes，未超冻结预算，0 缺失/语义错误。原 EXP026 已看 test97 人未下载该任务、未进入模型。25/25 M4 拟合收敛；M1/M3 对照引用 EXP027 同 fold 保存的 OOF 概率。

| 重复 | M4 对 M1 macro loss 改善 | M4 对 M1 balanced accuracy 改善 | 冻结双指标门 |
| ---: | ---: | ---: | --- |
| 1 | +0.065517 | +0.048946 | 通过 |
| 2 | +0.061673 | +0.037868 | 通过 |
| 3 | +0.069658 | +0.034333 | 通过 |
| 4 | +0.067725 | +0.054469 | 通过 |
| 5 | +0.064643 | +0.059058 | 通过 |

**开发集资格门 5/5 ≥4/5，且无负重复：`COGNITIVE_TASK_DEVELOPMENT_SIGNAL_OBSERVED`。**这个门只判旧开发372人在重新划分下的观察，不是五个独立队列，也不能修复 EXP026 旧 test 上另一个任务的失败。M4 对原 `Relaxed` M3 的 macro loss 五次改善 +0.02199～+0.03967；balanced accuracy 三次较高、两次较低。它提示预设的任务差异可能重要，但不证明心算任务在外部受试者保持，也不支持直接训练或推广 Shared Ganglion。局部保存输出核对 7/7，详见 `LOCAL_VALIDATION.json`。
