# EXP053 — 北京模型的30天本地截距校准是否足够

研究 ID `STAT-PSYMOE-EXP053-20261002-001`；2026-10-02；`EXPLORATORY_REUSE_OF_EXPOSED_EXTERNAL_TEST`；父阶段 [EXP052](../EXP052/CLOSEOUT.md)。问题：四城都能在本地历史上训练普通ridge，是否只需**每城一个截距**和30天本地真实回执，就能获得接近完整两年本地模型的2015预测收益？这是检验统计适应自由度，决定是否有理由增加Stat-MoE，不涉及Shared Ganglion。

## 固定数据与时序

只读EXP051外城原位逐时预测 (source asset outside this public snapshot)及EXP052本地模型原位逐时预测 (source asset outside this public snapshot)，不重新读取或复制UCI原件、模型状态和旧预测。四城各用EXP051已保存的北京B1在**2014-11-01至2014-11-30**起点对应的24小时后实测结果估一个标量；2015-01-01至2015-12-30逐小时预测做评价。校准回执最晚到2014-12-01，与2015评价隔开；不给校准器2015**当地**标签、未来气象或其他城状态。注意北京B1本身拟合至2015年底，因此这不是可在2014年真实部署的历史状态，只是已完成模型上的回顾性适应诊断。2015外城已在EXP051/052暴露，本实验只作探索诊断。

## 冻结规则和门

每城30天校准完整实测配对≥400、2015与EXP052的B2键和真值精确匹配≥3,000；否则 `STOP_CALIBRATION_SUPPORT`。B0=当地当时PM持续值；B1=EXP051冻结北京ridge；B2=EXP052冻结各城2013–14本地ridge；B3=仅用30天校准回执计算 `delta_c = mean[log1p(y)-log1p(B1)]`，然后 `B3=max(0,expm1(log1p(B1)+delta_c))`，不拟合斜率/天气系数，不选择天数。

四城逐城在同一2015对上报原始单位MAE/RMSE。定义 `recovery=(MAE_B0−MAE_B3)/(MAE_B0−MAE_B2)`；仅当四城各自B3较B0改善≥5%，且各自`recovery≥0.8`，才记 `ONE_INTERCEPT_30D_SUFFICIENT_EXPLORATORY`；否则 `ONE_INTERCEPT_30D_INSUFFICIENT_EXPLORATORY`。若分母≤0则直接不足。这个门只比较已暴露测试的工程选择，不产生独立泛化资格；不得根据结果更换校准月份/规则或声称确认。

## 预算和归档

先登记 `EXP053-INTERCEPT-001`；本地只读已存派生原件，CPU≤3分钟，无随机数或网络读取。新状态只存四城各一个`delta`于`CALIBRATION_STATE.json`；新逐时输出仅B3与原键/真值，B0/B1/B2继续路径引用，不复制。保存支持、指标、局部复算、原命令返回、门/报告/关账。若B3不足，下一新ID优先考察低维当地系数而不是直接上Stat-MoE；若足够，保留简单校准并寻未见数据确认。局部验证限本实验原位匹配和算式，不跑全仓门或哈希。
