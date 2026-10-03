# EXP025 标签与通道泄漏账

本轮只做源资格，**未训练**。主 outcome 来自官方 `patients/patient_###.json` 的 `condition`，并按官方 `preprocessed/file_list.csv` 的 label 映射核一致性：Healthy→0，Parkinson's→1，Other Movement Disorders/Atypical Parkinsonism/Multiple Sclerosis/Essential Tremor→2。DD 是四个真实诊断类别的预定合并，不把任务片段记为独立患者。文件表中的 `label` 是 outcome 副本，仅审计，不入 predictor。

| 字段/通道 | 本轮边界 | 后续模型决策 |
| --- | --- | --- |
| `patient.condition`, `file_list.condition`, `file_list.label` | 诊断 outcome 或其编码 | 仅 outcome 和分层；严禁 predictor |
| `patient.disease_comment`, ICD/任何诊断描述 | 直接临床结论与同义文字 | 严禁 predictor；本轮未复制原文 |
| `patient.age_at_diagnosis` | 诊断后才可知，469/469 非空并不赋予预测资格 | 严禁 predictor |
| `subject_id`, 文件名路径、记录序号与推荐分割标记 | 身份/来源代码，可能编码组别或采集次序 | 仅连接/分组；严禁数值或 embedding feature |
| 两腕 11 项任务原始加速度/角速度 | 同步观测，任务/腕为 channel；同一人多段相关 | 候选 predictor，须 person-level split 与 train-only 标准化；缺失/时长/首0.5秒振动实测处理 |
| 30 项非运动症状问卷 | 与动作同一次评估，不能当未来证据；临床诊断是否见过答案未证实 | 候选独立 channel；先与 movement-only 对照，缺失保留 |
| 年龄、性别、handedness、家族史、酒精对震颤影响 | 同次调查/元数据；人口混杂和可能直接提示病情 | 后续分层敏感性，不在本轮自动当核心特征 |
| `preprocessed/movement` 和 `file_list` | 官方预处理可能做片段切分且标为样本 | 可作为索引/复核，不能把多任务当独立人或把任何 label 附到原件 feature |

PADS 官方说明诊断由神经科医师确认，但没有在此证明评估者对智能手表或问卷盲法。当前任务因此只可定义横断面**组别区分**，不称新诊断、病程预测或临床有效性。采集日期在源中相对起点归零，不得伪造纵向 follow-up。
