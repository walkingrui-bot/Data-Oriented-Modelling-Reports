# EXP054 30天适应自由度门

2014-11各城678–716真24小时校准对、2015各7,653–8,526评价对，来源门通过；UCI394原压缩档一次3,390,122字节内存/管道响应。B4用北京预测的对数一输入拟合输出斜率+截距；B5用当地PM/TEMP/PRES三输入拟合同样ridge。B0–B3引用EXP051/052/053原位证据，2015已暴露，只作回顾性探索；北京基模型训练到2015年底，不能说2014可部署。

| 城市2015 | B4较持续值MAE改善 | B4恢复完整本地收益 | B5较持续值MAE改善 | B5恢复完整本地收益 |
| --- | ---: | ---: | ---: | ---: |
| 成都 | −9.95% | −87.2% | −1.97% | −17.3% |
| 广州 | 8.80% | 71.3% | 11.82% | 95.7% |
| 上海 | 2.85% | 14.8% | −9.41% | −48.8% |
| 沈阳 | 8.88% | 46.6% | −2.13% | −11.1% |

B4与B5均未在四城达到事前逐城MAE改善≥5%且恢复EXP052完整本地模型收益≥80%的门；`THIRTY_DAY_ADAPTATION_INSUFFICIENT_EXPLORATORY`。B5增加当地输入自由度后在三城比持续值更差，不能把短历史失败直接归因于模型容量太小。仍不知道是季节/污染机制变化、训练窗代表性、系数不稳或其他来源差异，需新问题分辨。

证据：来源支持 (source asset outside this public snapshot)、八个新状态 (source asset outside this public snapshot)、[完整指标](METRICS.json)、B4/B5逐行预测 (source asset outside this public snapshot)、[局部复算](LOCAL_VALIDATION.json)、原命令返回 (source asset outside this public snapshot)。
