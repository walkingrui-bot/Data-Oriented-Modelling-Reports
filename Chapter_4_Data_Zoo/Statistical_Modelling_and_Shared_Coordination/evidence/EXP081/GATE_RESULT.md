# EXP081 三区传统统计增量门裁决

来源与完整lag支持通过，训练34,842、验证8,784、test8,640真下一小时配对；各区均按目标日期等权。首次两次官方504均无结果，原错误 (source asset outside this public snapshot)/原错误 (source asset outside this public snapshot)；第三次同协议有效。[验证指标](VALIDATION_METRICS.json) · [test指标](TEST_METRICS.json)。

| 分区 | 9–10月冻结最佳附加臂/对OWN MAE改善 | 开发单区资格 | 11–12月同候选改善 | 留出单区资格 |
| --- | ---: | --- | ---: | --- |
| Zone 1 | WEATHER，7.448%，56/61日改善 | PASS | 11.952%，60/60日改善 | PASS |
| Zone 2 | WEATHER，15.307%，59/61日改善 | PASS | 5.213%，53/60日改善 | PASS |
| Zone 3 | WEATHER，0.511%，33/61日改善，CI跨0 | FAIL | **−10.561%**，2/60日改善 | FAIL |

开发整体门：2/3区过单区三门、其余未恶化>2%，**PASS**，因此对预先选中的候选各作一次后两个月评分。留出整体门：虽2/3区过单区门，但Zone3恶化10.561%超过冻结2%上限，**`NO_LATER_MONTH_CHANNEL_GAIN`**。不能事后关闭Zone3天气再把同一留出称为合格；未来路由需新实验及独立条件。三区没有任何合格区选择PEER或JOINT；当前**无跨区共享增量证据**，不启动Ganglion。

无拟合PERSIST对Zone3在验证/测试MAE=1035.389/950.811，远低于OWN或WEATHER；保留更简单统计基线是合理工程判断。源功率单位/时区及天气原字段在线可用时刻未知，所有结果只指回顾性2017 Tetouan，不称实时部署/跨城市泛化。
