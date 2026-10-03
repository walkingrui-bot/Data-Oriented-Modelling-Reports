# EXP054 — 30天两参数输出校准与三特征本地拟合

研究 ID `STAT-PSYMOE-EXP054-20261002-001`；2026-10-02；`EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST`；父阶段 [EXP053](../EXP053/CLOSEOUT.md)。新问题：EXP053单截距不足，是还需一个输出斜率，还是必须让PM/TEMP/PRES三输入的响应系数在当地学习？这决定下一步优先简单输出校准、当地统计专家，或更长本地历史；先用传统统计，不启Stat-MoE/Ganglion。

## 原件、窗口和固定模型

UCI394官方原ZIP内RAR一次≤10MiB内存/管道读取；成都、广州、上海、沈阳 `PM_US Post`、TEMP、PRES真实逐小时。仅2014-11-01至11-30起点及实测`t+24h`结果作当地校准，2015-01-01至12-30起点作评价，目标仍在2015；每城校准≥400、评价≥3,000、与EXP051/052/053原位逐行值匹配。缺失/负PM/PRES≤0排除，不能填零。EXP051北京模型训练到2015年底，故仍是**回顾性适应诊断，不是2014历史部署**；2015评价已被看过，只有探索资格。

- B0/B1/B2/B3均引用EXP051/052/053原位预测；B2为2013–14完整本地ridge，作收益参考。
- B4：每城在2014-11用 `log1p(B1)` 一输入训练 `Ridge(alpha=1.0,fit_intercept=True)` 拟合 `log1p(y)`；仅用该月标准化该一输入，预测`max(0,expm1(.))`。两个适应自由度为输出斜率和截距，不看当地天气。
- B5：每城在同月用 `log1p(PM_t),TEMP_t,PRES_t` 三输入训练相同ridge；训练月标准化，目标/逆变换同上。无调参、站/城市ID、未来输入。

逐城在同一2015完整键集算原始单位MAE主/RMSE辅。令`recovery=(MAE_B0−MAE_candidate)/(MAE_B0−MAE_B2)`。先看B4：若四城各改善B0≥5%且recovery≥80%，记 `AFFINE_OUTPUT_30D_SUFFICIENT_EXPLORATORY`；否则看B5，若四城各同样过门记 `THREE_FEATURE_LOCAL_30D_SUFFICIENT_EXPLORATORY`；都不过则 `THIRTY_DAY_ADAPTATION_INSUFFICIENT_EXPLORATORY`。B4/B5均完整报告，不能据2015绩效改训练月/正则/门或升格确认。

## 尝试、预算、存储

先登记 `EXP054-CALIBRATION-001`，CPU≤10分钟，一次外部原ZIP网络读；新八模型状态合存一个`MODEL_STATES.json`，新逐时文件仅B4/B5和匹配键/真值，旧B0–B3原位引用；保存支持、指标、局部复算、原返回、门/报告/关账。不得复制原CSV/ZIP/RAR，且不运行全仓门、非必要哈希。若短历史失败，按新ID研究更长当地历史或新未见外部来源，不为证明架构而加NN。
