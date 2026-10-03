# EXP041 临床结果 crosswalk 门

按事前优先级审同一原 ZIP `Participants Data.xlsx` 的 `Parkinson Disease` 工作表，固定44名PD在该表均有匿名 ID 行。结果：派生列/状态审计 (source asset outside this public snapshot)。

| 候选 | 明确列 | 当前日期/值规则下合格人 | 不同结果值 | 判定 |
| --- | --- | ---: | ---: | --- |
| UPDRS III运动总分 | 未找到 | 0 | 0 | 不可用 |
| Mini-BESTest总分 | 未找到 | 0 | 0 | 不可用 |
| 过去一月跌倒次数 | 第14列 | 10 | 3 | <30人且<5值 |

月跌倒列余34人中33个工作簿日期为**当前解析器未识别的字符串**，1个距离记录日期>7天；不能把33人说成临床字段缺失或结果为0。按本轮冻结分析与门记 **`STOP_CLINICAL_OUTCOME_SUPPORT`**，不训练。由于日期格式未知，该停止不能证明修复日期语义后依然不足；新ID可做具名格式审计，不能追改本轮已看结果。
