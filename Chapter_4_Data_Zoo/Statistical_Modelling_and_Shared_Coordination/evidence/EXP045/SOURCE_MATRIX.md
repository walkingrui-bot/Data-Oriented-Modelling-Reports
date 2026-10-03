# EXP045 官方来源矩阵（2026-10-02只读）

| 环节 | 官方原位证据 | 可用语义 | 未决或阻断 |
| --- | --- | --- | --- |
| 2003–04活动 | [CDC/NCHS PAXRAW_C字典](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2003/DataFiles/PAXRAW_C.htm) | 公开 ZIP/XPT，`SEQN`；腰部单轴、每分钟强度，7天至多10080行，`PAXSTAT/PAXCAL/PAXN`；检查后次日才开始佩戴；应使用调查权重 | 不等于原始六轴IMU；真实可用人数/佩戴质量尚未取原件 |
| 2005–06活动 | [CDC/NCHS PAXRAW_D字典](https://wwwn.cdc.gov/Nchs/Data/Nhanes/Public/2005/DataFiles/PAXRAW_D.htm)、[官方数据页](https://wwwn.cdc.gov/Nchs/Nhanes/Search/DataPage.aspx?Component=Examination&CycleBeginYear=2005) | 同类公开单轴分钟记录，`SEQN/PAXSTAT/PAXCAL/PAXN/PAXINTEN/PAXSTEP`；ZIP约449.2 MB | 与C期可设计周期分层，实际人级交集未审 |
| 公开死亡链接 | [NCHS数据页](https://www.cdc.gov/nchs/linked-data/mortality-files/index.html)、[两期原DAT目录](https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/)、[字段字典](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-files-data-dictionary.pdf) | 两期2019公开DAT各在官方目录，`SEQN`可与NHANES合并；成年人`ELIGSTAT=1`才有`MORTSTAT`，`PERMTH_EXM`为检查日起人月；死亡状态未扰动 | 未读个体DAT，交集/事件数未知；2022更新为限制使用，不当作公开数据 |
| 关键事件时间保真 | [NCHS 2019 public-use说明](https://www.cdc.gov/nchs/data/datalinkage/public-use-linked-mortality-file-description.Pdf) | 明确在**部分记录**替换合成随访时间或死因；`MORTSTAT`未扰动 | 无逐记录“未扰动时长”标记可据此排除；不能将`PERMTH_EXM`整体视真实时间到事件。监测始于检查次日，早期死亡与佩戴先后还需独立解决 |
| 使用条件 | [NCHS Data User Agreement](https://www.cdc.gov/nchs/policy/data-user-agreement.html) | 公共数据用于统计分析/报告；禁止识别个人或与可识别个人数据链接 | 本轮只读文档符合范围，未访问个体数据；后继若用公共数据须继续遵守 |

本矩阵仅指本次固定两期、2019公开死亡发布。没有核实际事件支持、可用佩戴日、年龄/调查权重交集，也不把2022限制版当公开。
