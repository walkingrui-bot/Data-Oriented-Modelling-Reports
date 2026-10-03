# EXP071 冻结门结果

官方原件结构与EXP070逐人逐活动两路有效行数一致；全部51人 A/D/E 各17个合格真实非重叠双路10秒窗，共2601、0拒窗；开发40人、条件式test11人，配窗来源门全过。配窗派生账 (source asset outside this public snapshot)。

| 40人开发OOF人等权 | ACC | GYR | JOINT |
| --- | ---: | ---: | ---: |
| logloss（越低越好） | 0.235249 | 0.415529 | 0.258457 |
| 三类平衡准确率 | 0.896569 | 0.815196 | 0.903922 |

| 冻结JOINT对ACC门 | 实测 | 裁决 |
| --- | ---: | --- |
| logloss差≤−0.03 | **+0.023208** | FAIL |
| 平衡准确率差≥+0.02 | +0.007353 | FAIL |
| 按人bootstrap logloss差95%区间上界<0 | [−0.011993,+0.067660] | FAIL |
| ≥2/3开发人logloss改善 | 21/40，需≥27 | FAIL |

**`STOP_JOINT_DEV_GATE`**；依原条件未评分11人test，无TEST结果。原时序中21,424个重复timestamp行全在受试者1629的六个所选组，已按预先规则折叠均值；这项异常的原始语义未在本实验核实，须新ID审来源。开发门失败不自动说明容量小或所有活动任务中陀螺仪无价值。[指标](OOF_METRICS.json) · 逐人派生成绩 (source asset outside this public snapshot)。
