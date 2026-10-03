# EXP070 冻结来源门

有效尝试为 `EXP070-SOURCE-002`；001活动键解析失败并[更正](AMENDMENT_001.md)，原样保留，不计科学来源失败。派生来源矩阵 (source asset outside this public snapshot)。

| 冻结门 | 原件观察 | 裁决 |
| --- | --- | --- |
| 包内A/D/E活动名匹配 | Walking/Sitting/Standing | PASS |
| ≥40个同人三活动×手机acc/gyro | 51/51人 | PASS |
| 每人每类每路≥1000有效xyz/timestamp行 | 最低acc3572、gyro3568 | PASS |
| 每类两路非零时间跨度且交叠≥0.5 | 最小交叠率0.999253 | PASS |

**`WISDM_THREE_ACTIVITY_PAIRED_SOURCE_READY_FOR_DESIGN`**。只选三类 A/D/E；51人中每人均有三类、两传感器。源行0无效/0错ID，三个活动各出现2个相邻时间倒序步，需下个配窗协议显式排序与核密度。时间跨度高度交叠仅是必要来源条件，尚未逐窗同步。0模型、0旧测试评分。第一次脚本“STOP”属无效解析输出，失败证据 (source asset outside this public snapshot)不能当冻结数据门裁决。
