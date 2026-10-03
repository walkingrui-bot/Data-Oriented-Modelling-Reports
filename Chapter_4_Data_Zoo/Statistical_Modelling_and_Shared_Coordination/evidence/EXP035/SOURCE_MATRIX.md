# EXP035 八个冻结候选的直接外部资格矩阵

2026-10-02；`EXP035-SEARCH-001`。资格是[计划](PLAN.md)的**联合门**：来源独立、PD≥20/健康≥15人、无双任务普通步行、左右足连续真实垂直力≥50Hz、逐人诊断与原始数值可用、许可清楚。`FAIL` 代表有原始证据与门矛盾；`UNKNOWN` 不当作零，也不当通过。候选顺序冻结于 [CANDIDATE_LIST.md](CANDIDATE_LIST.md)。本轮只读数据页/原始数据论文，没有下载原始信号或运行模型。

| 候选 | 人级 outcome/支持 | 原始双足总力与普通步行 | 来源/许可 | 联合判定及原始证据 |
| --- | --- | --- | --- | --- |
| C1 [GaitNDD](https://physionet.org/content/gaitndd/1.0.0/) | PD15、健康16，**PD<20** | 有左右 force-sensitive resistor 原件 `.let/.rit`，但输出仅粗略比例于足下力，非 GaitPDB 牛顿双足合力；另有衍生 stride `.ts` | PhysioNet ODC Attribution；与 GaitPDB 跨年代/人员排重未见明确 linkage | **FAIL_SUPPORT**，无须用单位假定救门 |
| C2 [Daphnet FoG/UCI](https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait) | PD FoG 事件数据，官方页无健康 cohort | 髋/腿三处加速度，任务含转弯/日常活动，无双足垂直力 | 与当前中心可能关联，但无需裁决 | **FAIL_OUTCOME_AND_MODALITY** |
| C3 [PADS/PhysioNet](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) | 469人真实 PD/鉴别/健康，EXP025 已核 | 双腕智能表的坐位互动运动和问卷；非普通步行双足力 | PhysioNet 独立项目；此处不重新审许可 | **FAIL_MODALITY/TASK**；可支持其本身的新问题，不当同构外部力数据 |
| C4 [Gait in Aging and Disease](https://physionet.org/content/gaitdb/1.0.0/) | PD5、健康10（年轻5、老年5），**两组均<门** | 官方公开的是 2列时间/stride interval；原 force sensor 用于导出事件，不提供12统计所需左右连续垂直力 | PhysioNet 开放 | **FAIL_SUPPORT_AND_RAW_MODALITY** |
| C5 [MyGait/Zenodo](https://zenodo.org/records/15672744) | PD44/健康45，独立西班牙招募，人数足够；有舒适速度10m与6min步行 | 足外侧双 IMU 50Hz 加速度/旋转；`p_...` 压力列官方明确**因可靠性问题未使用**，不等价可信牛顿左右总力 | Zenodo 页面许可字段未显示具体值，本轮不使用原始文件 | **FAIL_FORCE_SEMANTICS**；值得另立双足 IMU 科学问题但需许可先核 |
| C6 [GaitRec 原论文](https://www.nature.com/articles/s41597-020-0481-z) | 211健康与2,084肌骨损伤康复病人，类别为髋/膝/踝/跟骨，**无 PD 类别** | 左右真实垂直 GRF CSV 可用 | 与 GaitPDB 不同机构 | **FAIL_PD_OUTCOME**；不可把“impairment”当 PD |
| C7 [PD full-body kinetics 原论文](https://pmc.ncbi.nlm.nih.gov/articles/PMC9978741/) | **只有26名 PD**，ON/OFF药两次会话，无独立健康组 | 真实力平台 GRF，舒适速度地面步行；不是持续双足鞋底力 | 巴西独立采集；论文 CC BY | **FAIL_HEALTHY_SUPPORT**；不能把药物状态当健康 |
| C8 [Nordic walking 原论文](https://www.nature.com/articles/s41597-025-06209-9) | **最终24名全为 PD**；“Study/Control”是 Nordic walking 与 adapted physical activity 干预组，不是健康对照 | 有原始力平台 `.mot` 及不同步行条件 | 意大利独立采集 | **FAIL_HEALTHY_OUTCOME**；“control”不能误译健康 |

八项中 **0 通过联合门**。未解决的外部世界不由本审计覆盖；本轮只说明上述八项没有 EXP033 直接同构、独立人 PD/健康验证资格。C5 的潜力属于**新问题的双足 IMU**，不证明原双足力模型可迁移。C6/C7/C8 的真实力信号各有不同 scientific outcome，不可借名称凑健康或 PD 人数。
