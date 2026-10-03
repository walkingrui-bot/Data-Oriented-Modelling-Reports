# EXP020 关账与原件索引

研究 ID `STAT-PSYMOE-EXP020-20261002-001`，父 EXP017/018/019；2026-10-02。执行 `STOPPED_AFTER_HISTORICAL_DATA_AUDIT`，工程 `VALID_SCOPED_AUDIT`，科学 `NOT_IDENTIFIABLE_IN_AUDITED_DATA`。预设 `STOP_A` 生效，模型未训练，旧 test 未作为确认使用。结论和 15 问见 [REPORT.md](REPORT.md)，数据门原件为 [OUTCOME_CHRONOLOGY.md](OUTCOME_CHRONOLOGY.md)、[LEAKAGE_LEDGER.md](LEAKAGE_LEDGER.md)。

## 全部尝试

| run_id | 终态 | 原件／失败 |
| --- | --- | --- |
| `EXP020-AUDIT-001` | `PARTIAL_INTERRUPTED` | 26.06 临床三表成功聚合后，重复远程查询耗时中断，进程退出 1；返回摘要与异常见 WORKLOG.md (source asset outside this public snapshot)。 |
| `EXP020-AUDIT-002` | `COMPLETE / VALID_FEASIBILITY_DIAGNOSTIC` | 结局聚合 JSON (source asset outside this public snapshot)及 [chronology](OUTCOME_CHRONOLOGY.md)；数值取成功原工具返回，未伪称重复完成。 |
| `EXP020-LEAK-001` | `PARTIAL_FAILED_NETWORK` | GWAS/Gene Burden 各唯一 JSON 已保存；取 EVA 目录时连接拒绝。 |
| `EXP020-LEAK-002` | `COMPLETE / VALID_DATE_INVENTORY_ONLY` | 复用前两源原件，五源从旧官方 URL 索引接续；七份 `leakage_audit_*.json`、JSON (source asset outside this public snapshot)、CSV (source asset outside this public snapshot)和 [ledger](LEAKAGE_LEDGER.md)。 |
| `EXP020-REPORT-001` | `COMPLETE / DOCUMENTED_STOP` | 本关账、[主报告](REPORT.md)、独立 DOCX (source asset outside this public snapshot)与 Living v0.21 (source asset outside this public snapshot)；文档局部验证见 WORKLOG。 |

## 来源与恢复依赖

- 用户粘贴的 2026-10-02 EXP020 开工指导在 `/Users/rui/.codex/attachments/7b4c1980-1c06-4d52-9e3f-1a32c5dbf1b0/已粘贴的文本.txt`；它是本轮直接任务来源。EXP017/019 原始 URL 清单分别在 六源 manifest (source asset outside this public snapshot)与 CGC support (source asset outside this public snapshot)。本轮 JSON 只保存原件 URL 和聚合数，不复制原始源码、语料、日志、检查点或官方 Parquet。
- 26.06 官方临床三表、七条 `evidence_*` 的准确 URL 在本轮 JSON 中；25.12 官方历史目录已核对存在七来源同名表，临床 `clinical_report`/`clinical_target` 不在其目录。存在 URL 不能当作已备份或已完成逐行历史重建。
- 原六路/七路训练状态仍在 EXP017/019 唯一原件目录，本轮未加载、复制或别名保存。用户交接 ZIP 原位保留，不重包。

## 未执行与后继边界

没有合法 terminal event date 和历史 eligible universe，因此不创建 `SPLIT_LOCK.json`、`TRAINING_LOCK.json`、确认标签、M0–M7、`results/`、`figures/`、`checkpoints/` 或成熟曲线；不把未运行写为零效应。时间锁后的 CGC 增量、Europe PMC 贡献、post-cutoff 污染放大和一开确认均未检验。后继仅见 REPORT 建议，不自动执行。
