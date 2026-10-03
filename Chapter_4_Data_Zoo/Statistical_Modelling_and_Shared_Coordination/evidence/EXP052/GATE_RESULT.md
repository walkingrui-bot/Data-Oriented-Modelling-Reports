# EXP052 四城本地统计诊断门

四城各自2013–14训练配对13,385–16,866；2015评价配对7,653–8,526；来源门全过。原UCI394压缩档一次3,390,122字节网络响应，在内存/管道解析；本地普通ridge四个状态各保存一次。2015逐行B1引用EXP051原预测 (source asset outside this public snapshot)并精确匹配，不复制B1原文件。2015外部测试**已在EXP051看过**，本页为探索诊断而非独立确认。

| 城市2015 | 配对数 | 持续值MAE | 北京ridge MAE | 本地ridge MAE | 本地较持续值改善 | 本地较北京模型改善 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 成都 | 8,526 | 27.462 | 26.952 | 24.327 | 11.41% | 9.74% |
| 广州 | 8,344 | 17.944 | 17.899 | 15.730 | 12.34% | 12.12% |
| 上海 | 8,009 | 28.226 | 28.916 | 22.783 | 19.29% | 21.21% |
| 沈阳 | 7,653 | 48.116 | 41.438 | 38.944 | 19.06% | 6.02% |

冻结的重点成都/上海条件均满足（本地对持续值≥5%，对北京模型≥3%），诊断代码 `LOCAL_FORM_USEFUL_TRANSPORT_COEFFICIENTS_FAIL`。这说明同一简单统计形式在两失败城市的本地历史训练下**观察到**可用增量；北京零样本运输失败更符合系数/分布或测量来源差异，而非必须更换架构。由于2015已暴露，此判断不能升格为独立确认，也不能因本地训练胜出就称因果机制已识别。

证据：来源与切分支持 (source asset outside this public snapshot)、四本地模型唯一参数状态 (source asset outside this public snapshot)、[完整指标](METRICS.json)、B2逐行预测 (source asset outside this public snapshot)、EXP051 B1原位逐行 (source asset outside this public snapshot)、[局部复算](LOCAL_VALIDATION.json)。
