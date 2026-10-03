# EXP053 30天单截距适应门

四城2014-11校准完整配对各678–716、2015评价各7,653–8,526，支持门通过；未重新读取UCI原件。四个截距参数只由2014-11的本城真实结果与EXP051原预测计算，最晚校准目标2014-12-01 23；2015逐行B0/B1/B2用EXP051/052原位文件匹配。EXP051北京B1本身拟合到2015年底，本实验**仅回顾性诊断，不是2014可部署历史状态**。

| 城市2015 | 30天截距模型较持续值MAE改善 | 完整本地模型收益恢复比例 | 两门均过？ |
| --- | ---: | ---: | --- |
| 成都 | −0.09% | −0.8% | 否 |
| 广州 | 8.74% | 70.8% | 否 |
| 上海 | 15.49% | 80.3% | 是 |
| 沈阳 | 12.44% | 65.3% | 否 |

四城共同的≥5%改善和≥80%恢复门未通过，`ONE_INTERCEPT_30D_INSUFFICIENT_EXPLORATORY`。上海单城达到，但成都反而略差于持续值，不足以将单截距当作通用适应器。2015测试已暴露，本次不能称新确认；不改月份或阈值救门。

证据：支持 (source asset outside this public snapshot)、四个唯一标量状态 (source asset outside this public snapshot)、[完整指标](METRICS.json)、B3逐行预测 (source asset outside this public snapshot)、[局部复算](LOCAL_VALIDATION.json)、原命令返回 (source asset outside this public snapshot)。
