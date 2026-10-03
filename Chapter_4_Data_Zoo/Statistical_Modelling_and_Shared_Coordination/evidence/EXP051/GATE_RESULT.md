# EXP051 四外城零样本运输门

北京UCI501十训练站239,479真实配对拟合共同三特征普通ridge；已暴露2016同站开发域84,064配对，相对持续值MAE改善10.54%，通过冻结≥5%模型资格门。模型参数在读取UCI394四城原件前写入唯一状态 (source asset outside this public snapshot)。外城各≥5,000真实精确24h配对的来源门通过（原件一次3,390,122字节响应）；四城仅作一次零样本评价，不用外城数据训练/校准。

| 外部城市 `PM_US Post` 2013–15 | 配对数 | 持续值MAE | 北京ridge MAE | 相对改善 | ≥5%门 |
| --- | ---: | ---: | ---: | ---: | --- |
| 成都 | 23,496 | 32.605 | 33.047 | **−1.36%** | 未通过 |
| 广州 | 24,310 | 22.250 | 19.965 | **10.27%** | 通过 |
| 上海 | 24,899 | 30.310 | 30.229 | **0.27%** | 未通过 |
| 沈阳 | 21,062 | 46.138 | 39.045 | **15.37%** | 通过 |

冻结的四城全过条件为假，判定 `ZERO_SHOT_EXTERNAL_TRANSPORT_NOT_STABLE`。这是**地理/来源泛化失败**，不能以广州/沈阳单城收益宣称通用运输；成都甚至比持续值差。城市仅4个地理域，小时强相关且2013–15与北京训练年份重叠。结果不能单凭此分清“共同统计模型跨城市系数失配”和“各城同模型本来也无预测增量”。EXP052另立探索诊断，不回调本次四城测试。

原位证据：来源支持 (source asset outside this public snapshot)、北京已暴露开发门 (source asset outside this public snapshot)、[四城指标](METRICS.json)、93,767外城逐行预测 (source asset outside this public snapshot)、[局部复算](LOCAL_VALIDATION.json)、原命令返回 (source asset outside this public snapshot)。
