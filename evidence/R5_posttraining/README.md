# RTG_POSTTRAIN_V01

用户 2026-09-25 两份 RTG 材料的独立本地功能验证。

- [报告](REPORT.md) · [关账](CLOSEOUT.md) · [执行计划](PLAN.md)。
- [原始材料](sources/)；[修正记录](correction_log.md)；[工作日志](WORKLOG.md)。
- 正式研究 ID：P05-RTG-POSTTRAIN-20260925-001，EXPLORATORY。
- Phase A 五种子完成：RTG 1–20 步 100%，等参数循环模型、纯迭代base、no-write 也为100%。绝对外推通过、比较优势未过；B/C/D/E 未运行。

## 证据导航

| 路径 | 内容 |
| --- | --- |
| `configs/phaseA_v1.json` | 唯一正式配置、种子、固定预算与gate |
| `src/models.py` | 一步reader、显式RTG、同参数Elman控制 |
| `src/data.py` | 精确rule实例分区、输入与最终标签 |
| `src/campaign.py` | 固定课表、validation选择、冻结评估与原始保存 |
| `data/seed_*/` | base/post训练输入、validation/test、行重排/重命名输入与映射 |
| `checkpoints/seed_*/` | BASE_ONE_STEP、两臂step0到1200及SELECTED；optimizer/RNG/config齐全 |
| `results/phaseA_accuracy_by_length.csv` | 每seed/condition/length的原始聚合 |
| `results/condition_summary.csv` | 五seed均值、范围和标准差 |
| `results/per_episode_predictions.jsonl` | 全部563200正式输出，episode_index索引同seed的test.npz |
| `results/train_curve.csv` | 所有训练批次，optimizer_step区分L=1空梯度批次 |
| `results/seeds_summary.csv` | seed统计、真实更新数、base更新比例 |
| `results/paired_long_comparisons.csv` | 按规则聚类的长程配对比较 |
| `results/surface_*` | 15360个表面变换输出及汇总 |
| `results/scoped_audit.json` | 本轮数据、预测、trace和新进程恢复核对 |
| `traces/internal_diagnostics/` | 预定episode的完整L/M/g、alpha、熵、写入范数、依赖谱系 |
| `traces/control_failure_examples.jsonl` | 80个带规则表的控制失败例；全部错误保留在主JSONL |
| `attempts/` | 所有成功/失败、源快照、日志和回执 |
| `figures/` | 科学静态图；PNG和accuracy PDF |

`traces/failures.jsonl` 专指后训练full RTG错误，本轮为空。B/C/D/E为未运行，见 `results/phase_status.csv`，没有伪造对应成绩文件。

## 环境与复跑

原机使用 `.venv-neural/bin/python` 训练/恢复、`ce2g_git_workbench_14/plot_runtime/bin/python` 分析；确切版本见 `environment.txt` 和两个 requirements 文件。ZIP 不含这两个外部 venv。

解压后，工作目录设为含 `RTG_POSTTRAIN_V01/` 的父目录。已有 Python/Torch/NumPy 环境时：

```sh
python -m RTG_POSTTRAIN_V01.tests.test_contracts
python -m RTG_POSTTRAIN_V01.reproduce --output-root /tmp/rtg_replay_001 --run-id A-REPLAY-001 --analysis-python /path/to/plotting/python
```

`--output-root` 必须是尚不存在的新目录；每次给新run ID。复跑生成新的实际数据/模型/统计，不覆盖归档。若同一解释器已安装 matplotlib，可省略 `--analysis-python`。新机器可按两个requirements文件分别准备训练、绘图环境；本次未测试全新依赖安装或跨硬件位级一致性。

只复算冻结统计、恢复检查（会重写本包派生结果，建议先复制本包）：

```sh
python -m RTG_POSTTRAIN_V01.audit_completed
MPLCONFIGDIR=/tmp/rtg_plot_cache /path/to/plotting/python RTG_POSTTRAIN_V01/analyze.py
```

正式底层入口仍是 `python -m RTG_POSTTRAIN_V01.src.campaign --config ... --run-id ... --output-root ...`；它拒绝覆盖已有campaign数据。

数据生成器只向模型提供规则表和起点；长度控制统一循环次数，正确中间轨迹不用于训练。训练结束前不人工检查中间日志/成绩；预设validation与checkpoint是程序内部固定流程。
