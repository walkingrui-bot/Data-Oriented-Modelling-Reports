# EXP071 关账

- 登记/状态：2026-10-02 BST，`EXPLORATORY_REAL_PAIRED_WINDOW_PERSON_HOLDOUT`；执行 `COMPLETE` / 工程 `VALID_SCOPED_REGISTERED_PIPELINE_WITH_UNRESOLVED_SOURCE_ANOMALY` / 科学 `NO_JOINT_INCREMENT_UNDER_REGISTERED_DEVELOPMENT_GATE`。
- 原问题：WISDM同人双手机传感器实际配窗后，GYR能否在ACC外提供跨人且实用的增量？唯一尝试`EXP071-PAIR-STAT-001`按[冻结计划](PLAN.md)完成；无科学门、超参或test后修订/重试。
- 来源/配窗：EXP070逐人逐类有效原始行数全部复现；51人各类17个10秒双路非重叠窗、合计2601、0拒窗；40开发/11保留人。原6处时间倒序排序、21,424重复timestamp均在1629，按预先均值规则折叠。源重核 (source asset outside this public snapshot) · 逐窗计数 (source asset outside this public snapshot)。
- 模型：15次固定L2拟合；ACC/GYR/JOINT开发OOF logloss0.235249/0.415529/0.258457，平衡准确率0.896569/0.815196/0.903922。联合对ACC概率损失变差+0.023208，人级95%区间[−0.011993,+0.067660]；四个增量门全失败，[裁决](GATE_RESULT.md)。
- **未做**：官方11人test性能评分、容量实验、Stat-MoE、Ganglion、外部人群模型确认。不能据此宣称“模型太小”或所有传感器融合无用。1629同刻原始行是否相同尚未知；本次处理按注册规则有效，其科学语义保留疑问。
- 下一步：另立只读数据异常ID核1629重复timestamp值是否冲突及跨传感器关系；旧成绩不覆盖、不删人重命名为确认。其后优先考察四设备18活动的真实异质任务是否有独立统计需求，而不是继续在三类上改门。
- 实际验证：脚本语法、逐人配窗/指标重算、test零评分[9/9](LOCAL_VALIDATION.json)。仅静态审冻结方法/来源。未验证test、外部设备及全仓。
- 工件：本目录计划、脚本、原输出、结构/配窗派生JSON、OOF逐人成绩、门/报告/关账均本地未跟踪；原件只存官方URL引用，无ZIP/原始行副本/异地备份。复现依赖官方URL内容稳定和本地venv；无哈希保证。登记册/入口同步。
