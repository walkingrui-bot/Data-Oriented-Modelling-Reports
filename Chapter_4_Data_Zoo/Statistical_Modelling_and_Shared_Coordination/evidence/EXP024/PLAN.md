# EXP024 近年 FDA 当次标签与适应症证据门

研究 ID `STAT-PSYMOE-EXP024-20261002-001`；2026-10-02；`EXPLORATORY`；父 EXP023 / EXP022。EXP023 跨全年份固定样本中 ORIG 12/20、efficacy SUPPL 17/20 有同-key Label URL，低于原门，已原样停止。缺失集中在其抽中的较早年份，值得用**新 ID、新 cohort、新样本**回答近年文件是否支持当次 indication。用户路线自治授权允许此选择，不修改 EXP023 门。

## 研究问题与改变的决策

2010-01-01 至 2024-12-31 有精确 FDA approved action 日的 NDA 与 351(a) BLA，能否在同 application/submission 下取得当次 FDA Label 原件并确认可读的完整 `INDICATIONS AND USAGE`？若可，用它作为下一阶段 indication 差分审计的真实来源；若不可，暂停 Drug Translation 线的数据识别工作，转向其他真实可识别的 longitudinal 或多模态任务。本题无论结果均改变来源选择，不做 Stat-MoE/Ganglion/模型训练。

选择该时间范围是因为 EXP023 缺 URL 的抽中原申请均为 1994 年及以前，efficacy 缺 URL 的三条为 2001 年及以前；2010–2024 提供较近且已结束的批准年份。此观察是探索性选 cohort，不能把新门称作 EXP023 的确认或独立历史预测。当前 FDA snapshot 仍不是 2010–2024 当时的可见状态。

## 来源、单位和候选

沿用 EXP022 官方同 snapshot 原位 action、document、Tier A application 及 EXP023 官方 lookup。`approved_status_code=true`、`event_date` 完整且落在上列范围；ORIG 一层，`submission_class=EFFICACY` 的 SUPPL 一层。NDA 需 EXP022 Tier A Orange 产品，BLA 需 Tier A 351(a) 原始许可。action 仍是 application/submission 事件，不将其日自动广播给产品或 indication。原始 FDA Label PDF 只从 `REGULATORY_DOCUMENT` 中 exact key 的 URL 内存读取，不本地另存。

## 抽样和冻结门

- 先对两层及 NDA/BLA 子层报告完整 action/application 和同-key Label URL 数。四个子层每层若不足 5 个 application，则 `STOP_SUPPORT`，不补别的类。
- 抽样前写 `SAMPLE_FREEZE.md`。每层 15 NDA+5 BLA，合计 ORIG 20、efficacy SUPPL 20；同一 application 不跨层，排除 EXP021/022 手工已看与 EXP023 40 个新样本。每应用选最早符合年份窗的 action，再按 submission no、event ID 排序；对排序后的 application 用种子 `20261027`、`20261028`、`20261029`、`20261030` 分子层抽样。无同-key Label URL 者不替换。
- 样本 40 个当次 label 候选最多各读一个 PDF。多候选选最早 `document_date`，再最小 document ID。记录 HTTP、bytes、文件类型、PDF 文本可读性、自身 application/submission/产品线索、`INDICATIONS AND USAGE` 定位、label 内日期线索、标签与 action 的时间关系。文件角色由正文裁决；元数据 type=Label 不是充分证据。
- 主门：ORIG 与 efficacy 各 ≥18/20 有同-key且可读完整 I&U 的官方当次 Label；各子层 NDA ≥14/15、BLA ≥4/5；严重 scope/date 错误 0。若 URL 元数据上限不足任一门，直接停止而不下载正文。可读性未过、I&U 缺失、文件错配都保留原始结果，不补抽、不放宽。
- 即使此门通过，也只称 `CONTEMPORANEOUS_LABEL_SOURCE_READY`。真正 indication event 还需区别原始标签已有适应症与 efficacy supplement 新增适应症，独立审读或确定性差分、产品范围核对和另冻门；本轮不把 I&U 全文每一行都称新增批准。

## 预算、证据和边界

最多 40 个样本 URL 首次读取，失败每 URL 最多一次重试；总网络 ≤512 MiB、单文件 ≤20 MiB。不使用付费计算、个人凭据或私有上传。保存源 URL、原行键、短的有界证据摘录、裁决和失败；不复制完整 PDF/HTML/源码、旧日志或检查点。预期输出 `SOURCE_SUPPORT.json`、`SAMPLE_FREEZE.md`、`SAMPLE.csv`、`DOCUMENT_AUDIT.csv`、`GATE_RESULT.md`、`WORKLOG.md`、`REPORT.md`、`CLOSEOUT.md`。运行前记 run_id/RUNNING，失败也关账。只做本区域局部验证，不跑全仓门/无关哈希。

仍然没有历史 first-public、独立 target/disease crosswalk、NCT、follow-up/censoring，故无论来源门结果如何都不得称 `CHRONOLOGY_READY_FOR_MODELLING`。若本 cohort 也失败，下一 ID 应检验替代真实数据问题，不继续在同一 drug source 上改门凑成功。
