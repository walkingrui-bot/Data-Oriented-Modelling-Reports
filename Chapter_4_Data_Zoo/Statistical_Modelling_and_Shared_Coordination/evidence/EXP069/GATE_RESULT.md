# EXP069 冻结开发门裁决

来源结构重核与 EXP068 完全匹配；固定21名官方训练受试者的5折人级OOF，每人等权统计。[OOF_METRICS.json](OOF_METRICS.json) · 逐人派生成绩 (source asset outside this public snapshot)。

| 指标 | ACC | GYR | JOINT |
| --- | ---: | ---: | ---: |
| 人等权 logloss（越低越好） | 0.394391 | 0.737366 | 0.370522 |
| 人等权六类平衡准确率 | 0.874835 | 0.721905 | 0.907312 |

| 冻结 JOINT 对 ACC 门 | 实测 | 裁决 |
| --- | ---: | --- |
| logloss 差≤−0.03 | −0.023868 | FAIL |
| 平衡准确率差≥+0.02 | +0.032477 | PASS |
| 按人 bootstrap logloss 差95%区间上界<0 | [−0.096754,+0.076312] | FAIL |
| logloss 改善人数≥14/21 | 16/21 | PASS |

**`STOP_JOINT_DEV_GATE`**。这是开发受试者上的混合观察：分类点成绩改善，但预先要求的概率损失幅度与稳定性没有通过。依原计划0次官方test性能评分，无`TEST_METRICS.json`；不能称独立人保持的增量，不能因此接入Ganglion或断言模型容量不足。
