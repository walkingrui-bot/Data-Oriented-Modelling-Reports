# EXP023 当次 Label 第一阶段停止门

冻结依据 [PLAN.md](PLAN.md) 与抽样前 [SAMPLE_FREEZE.md](SAMPLE_FREEZE.md)。本轮 40 个不同 application，ORIG 20、efficacy SUPPL 20，按固定 seed 20261025/20261026 从真实 FDA action 中抽样，缺 URL 不替换。

| 层 | 样本 | 同-key FDA Label URL | 冻结可读完整标签最低值 | 结果 |
| --- | ---: | ---: | ---: | --- |
| ORIG approved | 20 | 12 | 18 | 元数据上限不足，停止 |
| Efficacy SUPPL approved | 20 | 17 | 18 | 元数据上限不足，停止 |

`same-key Label URL` 仅是**可能**能读到当次文件的元数据上限；即使所有 URL 均可读，两个层的 12/20 和 17/20 也不能达到 18/20。故按冻结门停止，不下载 PDF、不执行后续内容审读。`SOURCE_SUPPORT.json` 的总体分母为 ORIG 4,354 application（2,682 有同-key Label URL）、efficacy SUPPL 1,793 application（1,473 有）；这些比例没有使固定样本自动通过。

未确认任何 indication-specific regulatory event、标签完整性、actual document role、historic public-first 或新增适应症。没有把缺 URL 当成标签中无适应症，也没有将当前 label 倒填到旧 action 日。本门失败限于本轮覆盖全部年份的源支持设计；EXP022 的独立监管事件层不因此改判。
