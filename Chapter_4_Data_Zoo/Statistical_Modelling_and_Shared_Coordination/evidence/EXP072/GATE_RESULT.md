# EXP072 来源异常语义门

官方原件受试者1629的手机 acc/gyro×A/D/E 六组逐行核：与EXP070/071的有效行数、总21,424折叠行及每组1处原顺序倒序全部相同。派生矩阵 (source asset outside this public snapshot)。

| 冻结检查 | 实测 | 结果 |
| --- | ---: | --- |
| 旧六组行数、折叠量、倒序次数一致 | 7/7版本/异常核对 | PASS |
| 重复时间键两行三轴数值精确相等 | 六组全部21,424额外行 | PASS |
| 不同值重复时间键 | 0 | 无冲突 |
| 最大三轴绝对差 | 0.0 | 无冲突 |

**`IDENTICAL_DUPLICATE_ROWS_NO_MEAN_CHANGE`**。EXP071事前同刻取均值对这些点数值无影响；不改变其OOF结果或`STOP_JOINT_DEV_GATE`。只审1629两个源文件，不推断其他设备或更广来源品质。原输出 (source asset outside this public snapshot)。
