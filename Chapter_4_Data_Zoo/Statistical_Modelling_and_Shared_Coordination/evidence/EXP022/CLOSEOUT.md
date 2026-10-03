# EXP022 关账

研究 ID `STAT-PSYMOE-EXP022-20261002-001`；`EXPLORATORY`；2026-10-02。执行状态：**完成**。工程有效性：**本轮局部验证有效**。科学结论：**当前 FDA 来源语义监管事件层通过已冻结门，适用域受限**。没有做 drug–indication、历史预测或架构效果检验。

## 原问题与范围

EXP021 的统一 EVENT_A 人工资格门停止后，本轮另立问题：Orange 产品日、Purple 产品和 BLA 级原始许可日、Drugs 提交动作日及文件日期能否按各自官方语义形成可追溯监管事件层。原计划、冻结判据和修订见 [PLAN.md](PLAN.md)、[GATE_FREEZE.md](GATE_FREEZE.md)、[AMENDMENT_001.md](AMENDMENT_001.md)、[BLA_PAGE_QA_FREEZE.md](BLA_PAGE_QA_FREEZE.md)。EXP021 的 STOP_5、样本与历史失败未修改。

## 全部尝试及结果

完整 run_id、输入、命令/分析方法、预期位置和结果见 WORKLOG.md (source asset outside this public snapshot)。`EXP022-BUILD-001` 因 JSON 序列化失败而无效，其五个初始产物保留在 `derived/failed_BUILD_001/`；`BUILD-002` 用新运行修正。来源诊断、两个人工主门、BLA 串行页面访问、独立页级补抽、聚合及局部验证都单独记账。旧 EXP021 的 703 个 HTTP 403 不因本轮 750/750 页可读而改写。

## 门与交付

- Gate A：75/75 新来源行 ETL exact，PASS。
- Gate B：50/50 新行事件语义正确，灾难性 scope 错误 0，PASS。
- 补充 BLA 页重读：25/25 exact；4 个页级/月表异常 TIER_C 隔离。
- 旧 10,998 条 crosswalk 全部重分类；同范围独立可比对数 0，真正日期冲突率不可估，不声称 0%。
- 主事件 TIER_A 8,955 条：NDA 产品 8,209、BLA 原始许可 746。NDA 派生首可见产品日 4,099 条为 TIER_B。STOP_A–E 均未触发，`REGULATORY_EVENT_LAYER_READY` 仅限此来源语义层。

核心表、键、空日期及证据入口见 [DATA_DICTIONARY.md](DATA_DICTIONARY.md)，统计、限制与官方链接见 [REPORT.md](REPORT.md)，门判定见 [GATE_RESULT.md](GATE_RESULT.md)。官方原件只通过其 URL、source row/page key、snapshot 元数据引用；不保存官方 ZIP/XLSX/HTML 副本。

## 结论边界与后继

本轮没有 indication、target、disease、NCT、historical first-public、follow-up 或 censoring。`REGULATORY_EVENT_LAYER_READY` 不能写成 `CHRONOLOGY_READY_FOR_MODELLING`，也不是 drug–indication 监管终点。没有训练或评估 Stat-MoE、Ganglion 或统计预测模型。

下一条信息增益最高的问题是：能否把**当次** FDA label 和监管 action 中的适应症文本，与具体产品或 BLA 许可事件建立可审计且有时间界限的联系；如果无法识别，暂停 drug translation 线而不制造代理终点。按用户最新路线自治授权，另立 EXP023；其候选来源、数据支持与门槛须在该研究内预先登记，不能回填本轮。
