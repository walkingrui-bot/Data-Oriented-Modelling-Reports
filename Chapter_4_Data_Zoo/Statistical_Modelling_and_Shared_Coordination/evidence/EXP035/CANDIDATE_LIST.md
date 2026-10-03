# EXP035 事前固定候选清单

2026-10-02；`EXP035-SEARCH-001` 检索后、逐源资格裁决前固定。固定查询词和≤8候选/≤20页面族预算见 [PLAN.md](PLAN.md)。来源优先选官方数据发布页或原始数据论文；搜索结果可能来自同一 GaitPDB 派生研究，不作为独立候选。以下顺序与八项均冻结，不因资格结果增删。

| 编号 | 候选正式名称与原始资料入口 | 纳入候选原因，尚未裁决 |
| --- | --- | --- |
| C1 | [PhysioNet Gait in Neurodegenerative Disease Database](https://physionet.org/content/gaitndd/1.0.0/) | 已知足部来源、PD/健康真实受试者，检验人数与原始信号语义 |
| C2 | [Daphnet Freezing of Gait Dataset / UCI](https://archive.ics.uci.edu/dataset/245/daphnet+freezing+of+gait) | 已知公开 PD 运动来源，负参照检验健康及足力通道 |
| C3 | [PADS / PhysioNet](https://physionet.org/content/parkinsons-disease-smartwatch/1.0.0/) | 已知真实 PD/健康等与双腕数据，负参照检验足力同构 |
| C4 | [PhysioNet Gait in Aging and Disease Database](https://physionet.org/content/gaitdb/1.0.0/) | 公开足部 force-sensitive 记录、PD/健康，检验真实人数和是否只给 stride interval |
| C5 | [Zenodo MyGait wearable foot IMUs](https://zenodo.org/records/15672744) | 44 PD/45健康、有足部 wearable 和压力字段，检验力可靠性/格式 |
| C6 | [GaitRec 原始研究及数据](https://pmc.ncbi.nlm.nih.gov/articles/PMC7217853/) | 左右垂直地面反作用力真实原件，检验疾病组别 |
| C7 | [PD full-body overground kinetics 原始研究/Figshare](https://pmc.ncbi.nlm.nih.gov/articles/PMC9978741/) | 真实 PD 力平台数据，检验健康对照和可计算时序 |
| C8 | [Parkinsonian Nordic walking 原始数据论文](https://www.nature.com/articles/s41597-025-06209-9) | 新来源的左右地面反作用力文件、study/control，检验真实诊断、人数与普通无任务步行 |

检索中还见仅健康 CAD WALK、仅站立摇摆、只估计而不实测力的 IMU 论文，以及明确重用同一 GaitPDB 的新论文；均未挤占本轮五个新候选。不能把他们的结论倒算成第九个数据集的资格结果。
