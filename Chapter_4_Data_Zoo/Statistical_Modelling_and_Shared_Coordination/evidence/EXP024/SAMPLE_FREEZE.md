# EXP024 近年当次 Label 抽样冻结

2026-10-02；已见 `SOURCE_SUPPORT.json` 四个子层全表 metadata 分布，但尚未选择/查看本轮 application 或文件正文。ORIG NDA 1,410 application（1,384 有同-key Label URL）、BLA 204（203 有）；efficacy SUPPL NDA 832（817 有）、BLA 177（175 有）。预设每子层最低 5 个 application 的来源门通过。

从 2010-01-01 至 2024-12-31 exact approved action 中，ORIG 或 efficacy SUPPL 分层；限定 EXP022 Tier A NDA/BLA application。每 application 的当层 action 固定选窗口内最早 `event_date`，再按数字 `submission_no`、`event_id`。排除 EXP021 两批人工、EXP022 两门人工及 BLA 页补审/定向异常、EXP023 固定 40 application。逐子层按 `(application_type, application_no)` 排序，使用 Python `random.Random(seed).sample` 无放回：ORIG NDA seed 20261027 取 15；ORIG BLA seed 20261028 取 5；efficacy NDA seed 20261029 取 15；efficacy BLA seed 20261030 取 5。先前抽中 application 从后续子层排除，四层共 40 个不同应用。

在抽中 action 的 exact `(application_type, application_no, submission_type, submission_no)` 上选 document type `Label` 且 URL 非空的候选；多个时 `document_date` 早者优先、未知排后、再按数字 document ID。**URL 不参与 action/application 抽样**；缺失仍入样本并计门。样本选出后不得根据可达性、标签内容或审批结论换样。

冻结门见 PLAN：ORIG/effect 各 ≥18/20，NDA 各 ≥14/15，BLA 各 ≥4/5，有可读的同-key当次完整 I&U；严重 scope/date 错误 0。某层候选 URL 数低于门即停止，不下载正文。若候选足够，最多读 40 URL，失败每 URL 一次重试；单文件20 MiB，总512 MiB。标签正文、action 日、document 日及最早公开日必须分别记录。
