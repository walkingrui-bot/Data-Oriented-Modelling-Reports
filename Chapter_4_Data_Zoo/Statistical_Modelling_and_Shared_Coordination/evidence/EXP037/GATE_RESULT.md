# EXP037 结构预检门

固定 PD01、健康01 两份 `1_10mSlow` 原件 CSV，直接来自 [Zenodo 原 ZIP](https://zenodo.org/records/15672744) 的 HTTP Range；派生审计 (source asset outside this public snapshot) 与[程序](audit_two_members.py)原位保存。

| 条件 | PD01 | 健康01 |
| --- | ---: | ---: |
| 左/右 `foot` 行 | 3318 / 3265 | 2657 / 2626 |
| 六轴 `acx/acy/acz/gyrx/gyry/gyrz` | 6583行全有限 | 5283行全有限 |
| `timestamp` 逐足有限且严格递增 | 通过 / 通过 | 通过 / 通过 |
| 逐足 ≥100 行 | 通过 | 通过 |

**`STRUCTURE_PASS`。** 两份固定样本证实双足位于单 CSV 的行中；本门不推出其余87人的覆盖率、50 Hz 实际采样一致性、临床变量联结或疾病建模效果。`p_...` 压力字段未用。
