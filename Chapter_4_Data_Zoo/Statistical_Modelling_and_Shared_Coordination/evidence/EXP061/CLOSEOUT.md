# EXP061 关账

- 原问题：伦敦 UK-AIR 2024 预选 12 站能否提供与北京 N1 同定义的 ≥8 邻站、目标站真缺测、24 小时真目标外部评价样本？
- 来源/方法：[PLAN.md](PLAN.md)、[AMENDMENT_001.md](AMENDMENT_001.md)；官方年度 CSV 原位网络读取，不存源文件副本；状态 `R`、GMT 小时结束、空字段与无行分开。
- 尝试：`EXP061-SOURCE-001` 因 15 分钟同名链接未区分而部分无效，失败输出 (source asset outside this public snapshot)及派生状态 (source asset outside this public snapshot)保留；`EXP061-SOURCE-002` 修复链接过滤完成十二站，输出 (source asset outside this public snapshot)、最终来源矩阵 (source asset outside this public snapshot)、配对支持 (source asset outside this public snapshot)。无训练尝试。
- 执行 / 工程 / 科学：`COMPLETE / VALID_SCOPED_SOURCE_AUDIT / STOP_EXTERNAL_NATURAL_OUTAGE_SUPPORT`。八站过 6,000 小时门，少于需要的九站；同定义合格配对为零，第二配对门也未过。没有修改任何门。
- 已知：当前 12 站子网的 2024 已核定时钟与数值语义；581 个真缺测且 24 小时后实测起点最多七个合格邻站。
- 未知：完整伦敦站点目录是否能补足同定义网络、N1 跨城表现、不同仪器严格可比性、缺测机制及后续被修订的历史记录。不能将当前数据库状态写成 2024 年当时状态。
- 决策：停止本 ID，不评模型。下一 ID 先审核**官方完整伦敦 2024 站点目录**，仍保持 ≥8 邻站与 ≥6,000 小时门；若补足再另立外部冻结模型检验，若不能则关此同定义任务。此转向是补足真实来源边界，结果无论有无新增站都会改变工程决策。
- 只运行本轮 11 项局部派生一致性检查，见[LOCAL_VALIDATION.json](LOCAL_VALIDATION.json)；未运行全仓门、模型预测或非必要哈希。
