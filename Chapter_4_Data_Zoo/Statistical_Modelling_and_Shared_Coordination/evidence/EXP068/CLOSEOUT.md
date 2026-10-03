# EXP068 关账

- 登记与状态：2026-10-02 BST `EXPLORATORY_REAL_SOURCE_AUDIT`；执行 `COMPLETE` / 工程 `VALID_SCOPED_SOURCE_AUDIT` / 科学 `SOURCE_SUPPORT_ESTABLISHED_ONLY`。
- 原问题：独立真实活动数据是否支持按受试者隔离的加速度计/陀螺仪互补测试？唯一尝试 `EXP068-SOURCE-001` 按[计划](PLAN.md)读取官方 UCI240 压缩包，原件不落盘。未修订来源门；无失败重试。
- 已知：10,299个有效窗、30个人、官方 train/test 21/9人且不重合；每类 train/test 人数21/9；六通道128点全有限与对齐；0跨域完整六信号精确重复。所有冻结门通过，原输出 (source asset outside this public snapshot)、派生矩阵 (source asset outside this public snapshot)、[裁决](GATE_RESULT.md)。
- 未知：任何活动分类性能、第二传感器增量、Stat-MoE/Ganglion价值、跨硬件/自由生活迁移。官方50%重叠窗不能当独立样本；测试标签仅看预定来源计数，未看性能。
- 下一步：另立新 ID，冻结只在train内做的受试者级开发选择、传统单/双传感器基线及一次 test 评价；若传统结构无显著增量即止损，不因架构偏好扩模型。
- 本次实际验证：原件结构检查，派生一致性[8/8](LOCAL_VALIDATION.json)。仅静态检查：官方来源与 CC BY4.0 许可文字。未验证：模型、全仓门、外部场景。
- 工件：本目录的计划、脚本、日志、派生 JSON、门、报告、关账均为本地未跟踪新文件；原件仍在官方 URL，未建数据副本或异地备份。重做依赖官方 URL 保持可访问且内容不变；未用哈希做版本保证。登记册和研究入口同步。
