# EXP078 年份时间外开发门裁决

来源重核 (source asset outside this public snapshot)及完整lag样本门 (source asset outside this public snapshot)通过：2007–08训练17,359配对，2009验证8,565配对/355评价日，2010仅核来源支持7,228配对/298评价日；2010模型性能**未评分**。2009逐日等权结果来自[VALIDATION_METRICS.json](VALIDATION_METRICS.json)。

| 冻结门 | 2009观察 | 裁决 |
| --- | ---: | --- |
| 最佳附加臂较AR日MAE改善≥5% | SUB改善0.5400%；0.477555对0.480148 kW | FAIL |
| 候选−AR日期bootstrap差95%区间上界<0 | [−0.004775,−0.000484] kW | PASS |
| ≥60%日期改善 | 198/355=55.77% | FAIL |

**`STOP_ADDITIONAL_CHANNEL_DEV_GATE`**。观察到很小的分表方向性改善，但未满足冻结实用幅度与日期稳定性；2010不评分。其它电学/联合臂MAE分别0.483354/0.479306 kW，都未胜过SUB。这一单栋总表连续功率任务不建立新增channel state，不运行Stat-MoE/Ganglion，不以加大模型替代未达标的统计门。结果不能推广到异常高负荷等不同结局，也不证明模型容量原因。
