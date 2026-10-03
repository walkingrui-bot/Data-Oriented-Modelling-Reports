# EXP023 当次 Label 来源人工样本冻结

2026-10-02；抽样前记录。已看全表 source support 但尚未查看或选取本轮任何 application/document ID。来源是 EXP022 固定 Drugs@FDA snapshot 和高置信产品/许可应用号。`SOURCE_SUPPORT.json` 已显示 ORIG 4,354 个应用，其中 2,682 有同-key Label URL；efficacy SUPPL 1,793 个应用，其中 1,473 有 URL。这个分布不用于事后更换失败样本。

- `ORIG_APPROVED`：`submission_type=ORIG`、`approved_status_code=true`、精确 action 日，应用在 EXP022 TIER_A NDA 产品/BLA 许可范围内。一个应用如有多个 ORIG action，选最早 `event_date`，再按数字 `submission_no` 升序、`event_id` 升序。
- `EFFICACY_SUPPL_APPROVED`：`submission_type=SUPPL`、`submission_class=EFFICACY`、批准且精确日，应用同上。一个应用的多个合格 supplement 也选最早日，再按 `submission_no`、`event_id`。这是历史首个可见 efficacy action 的固定规则，不按 Label 可用性选。
- 排除 EXP021 两个已看人工 CSV 的所有 application，以及 EXP022 Gate A、Gate B、BLA 页补抽、五个定向 BLA、四个异常 BLA 的 application。EXP022 全表程序处理和 750 页级批量来源读取不等于逐条 indication 人工核验，故不排全体 BLA。
- 从剩余 ORIG 应用按 `(application_type, application_no)` 排序后用 Python `random.Random(20261025).sample` 取 20。随后 efficacy 池排这 20 个 application，以同种子新 `Random(20261025+1).sample` 取 20。若不足 20 记 `STOP_SUPPORT`，不修改规则。
- 无 Label URL 也保留在样本。exact key 是 `(application_type, application_no, submission_type, submission_no)`；多个 Label 候选按 `document_date` 升序、`document_id` 数字升序取一。文档日未知排在已知日期后。URL 不作为随机抽样依据。
- 人工门维持 PLAN 所写每层 ≥18/20 可读、同-key且完整 `INDICATIONS AND USAGE`；0 严重 scope/date 错误。HTTP 403/404、PDF 不可读、无该段或仅当前页面均记其原始状况，不能补抽。最多 40 URL 首次读取，失败各一次重试；512 MiB 总网络、20 MiB 单文件。
