# EXP062 关账

- 原问题：EXP061 预选 12 站失败是否因为遗漏了官方 AURN 伦敦区域内的全年有效 PM2.5 站？
- 唯一尝试 `EXP062-SOURCE-001`：事前固定经纬度框，从官方 199 站目录选20候选，官方站点详情与年度文件逐一溯源，21,833,755 字节内存读取。原输出 (source asset outside this public snapshot)；目录 (source asset outside this public snapshot)；来源 (source asset outside this public snapshot)；配对 (source asset outside this public snapshot)。ID crosswalk 的执行前细则见[AMENDMENT_001.md](AMENDMENT_001.md)。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_SOURCE_AUDIT / AURN_LONDON_REGION_SOURCE_READY_FOR_FROZEN_N1_TEST`。十站达单站门、667配对、十目标站各≥10；三个事前门全过。
- 已知：增加 BDMP、THUR 两座客观入框站可补足八邻站网络；原预选失败不能推广到完整区域。当前 2024 回顾性文件的时钟与状态可追溯。
- 未知：冻结北京 N1 在此区域的 MAE、仪器校准残差、缺测机制、历史实时可用性。来源 PASS 不构成模型通过或共享架构价值。
- 决策：关账并另立 EXP063，固定 N1 与 B0 的外部模型评分/日区块误差门后才读取该分数。若 N1 不运输，不调伦敦测试；新本地适应问题另立 ID。原 EXP061 和本轮差异都保留。
- 局部验证[13/13](LOCAL_VALIDATION.json)，不运行全仓门、模型或非必要哈希。
