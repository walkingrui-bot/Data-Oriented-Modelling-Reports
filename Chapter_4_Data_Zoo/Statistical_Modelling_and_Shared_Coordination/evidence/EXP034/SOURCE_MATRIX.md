# EXP034 官方来源与原论文证据矩阵

2026-10-02；`EXP034-SOURCE-001`；限定来源页、格式/人口表和 Ga/Si 所列原始论文，不下载原始力文件或论文副本。原论文方法是相关源研究的**背景**；没有逐文件到原论文受试者的明确映射，故不把论文人数自动当本库有效人数。

| 问题 | 可定位原始来源与观察 | 可下结论 | 缺口 |
| --- | --- | --- | --- |
| 数据集是否列不同研究 | [PhysioNet 数据页](https://physionet.org/content/gaitpdb/1.0.0/) 写总93名PD、73健康、三研究；[format.txt](https://physionet.org/files/gaitpdb/1.0.0/format.txt) 将 `Ga` 指 Yogev 双任务、`Si` 指 Frenkel-Toledo 跑步机研究，`_01` 为普通步行，采样100Hz、18/19列左右足总力 | 有不同**原研究/前缀**，但这不是跨研究受试者排重证据 | 无全库跨研究同人 linkage/排重声明 |
| 人员 ID 语义 | [官方 demographics.txt](https://physionet.org/files/gaitpdb/1.0.0/demographics.txt) 只有 ID、Study、Group、Subjnum、人口/量表/速度字段；`Subjnum` 在各 Study×Group 内重复使用 | 数据可支持研究内人级键 | 无可跨研究连接的全局人 ID；相同或不同人口学值都不能判同人 |
| Ga 原研究纳入 | [Yogev 等 2005 原论文 PDF，方法](https://physionet.org/content/gaitpdb/1.0.0/#references) 写30名PD（H&Y 2–3、服用抗PD药、无运动反应波动）和28名社区便利样本健康，PD来自 Tel-Aviv Sourasky 门诊 | 知道该研究的纳入与招募描述 | 本库 Ga 精确 `_01` 是PD29/健康18；原论文到具体库行的取舍/映射未说明；论文没有说这些人绝不参加 Si |
| Si 原研究纳入 | [Frenkel-Toledo 等 2005 开放原论文，Methods](https://doi.org/10.1186/1743-0003-2-23) 写36名PD（H&Y 2–2.5、无运动反应波动）与30名社区健康，PD同来自 Tel-Aviv Sourasky 门诊 | 知道 Si 的独立研究设计 | 本库 Si 精确 `_01` 为PD35/健康29；原论文到具体库行的取舍/映射未说明；无跨 Ga 排重声明 |
| 普通步行协议 | [Ga 原论文方法同上](https://physionet.org/content/gaitpdb/1.0.0/#references) 描述舒适速度、25m走廊、2分钟、8传感器/足、100Hz；[Si 原论文方法/Protocol/Apparatus](https://doi.org/10.1186/1743-0003-2-23) 描述35m走道、舒适速度普通地面步行为第一条件、每次2分钟、8传感器/足、100Hz | 任务和装置层有相似性，本库格式 `_01` 一致 | 步道长度/原研究任务序列和纳入范围有差异；记录时药物状态、逐文件协议到库行的映射未全部可核，不能宣称完全可交换 |
| 来源表单位一致性 | [官方 demographics](https://physionet.org/files/gaitpdb/1.0.0/demographics.txt) 中 Ga/Si 身高样值约1.x，Ju 样值约160–183 | 提醒跨研究人口字段存在单位解释问题；本轮模型禁入这些字段 | 不据此推断具体人的身份，也不修改 EXP033 输入 |

审计页族：PhysioNet 数据页、format、demographics、Ga 原论文 论文全文/出版摘要、Si 开放论文/原文章摘要，共6类，低于计划≤10。研究前缀、作者重合、同一医院、发表时间、人口学近似、论文与库人数差都不满足事前人员独立性证据。无 `CROSS_STUDY_PERSON_DISJOINTNESS_ESTABLISHED`。
