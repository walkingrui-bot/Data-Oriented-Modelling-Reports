# EXP038 追加更正 001（2026-10-02）

事前 [计划](PLAN.md) 限制**每条压缩读取≤1 MiB**、整个运行≤25 MiB；没有设置解压后2 MiB排除门。`EXP038-COHORT-001` 的程序却继承EXP037预检实现中的 `file_size > 2 MiB` 条件，让PD02/13/16/23/30五份文件未被读。五份原 ZIP 中央目录的压缩大小均≤435 kB，解压大小2.14–2.74 MB；不应归类为数值失败。保留 逐人原派生行 (source asset outside this public snapshot) 和原运行输出 (source asset outside this public snapshot)，不改写已看结果。

另有门逻辑错误：初版只要出现任何 `ACCESS_ERROR` 就记 `SOURCE_ACCESS_INDETERMINATE`，但计划规定的是访问问题**使门无法裁决时**才如此。已实际合格的PD39≥36、健康45≥36，即使五份全不合格，冻结80%来源门仍通过。故只用同一原始派生记录另立 `EXP038-GATE-002` 做零数据读取重判。更正状态是 `COHORT_SOURCE_PASS_LOWER_BOUND`，并明确五份PD仍未读取、存在选择偏差风险；进入模型前须以新ID核完整五份。没有降低阈值或把未知记作成功。
