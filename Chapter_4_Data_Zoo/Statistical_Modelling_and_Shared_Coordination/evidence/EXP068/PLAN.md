# EXP068 — 真实双惯性传感器跨人活动分类来源门

研究 ID `STAT-PSYMOE-EXP068-20261002-001`；2026-10-02 BST；类型 `EXPLORATORY_REAL_SOURCE_AUDIT`；父阶段 [EXP067](../EXP067/CLOSEOUT.md)。来源为用户在 EXP022 后的研究自治授权和“实践、及时止损”指令，以及 [UCI Human Activity Recognition Using Smartphones 官方页](https://archive.ics.uci.edu/dataset/240/human%2Bactivity%2Brecognition%2B)。当前空气质量自然缺测路线未产生稳定模型增量且2026新损失来源门失败；新问题是：该独立真实活动数据能否支持**按受试者隔离**的加速度计与陀螺仪互补信息测试？若不能，在来源门停止；若能，新实验先比较合适的传统统计，再决定是否有理由测 Stat-MoE / Shared Ganglion。

## 选择和边界

UCI 官方说明：30名受试者，六类活动，腰部手机三轴加速度与三轴角速度，50Hz；发布的惯性信号已滤波并切成128点、50%重叠窗口；官方训练/测试按人划分。真实独立单位为**人**，窗口与重叠窗不是独立人；同一人多个活动和窗口不得跨训练/测试或 bootstrap 当独立人。只用 `total_acc_[x,y,z]` 和 `body_gyro_[x,y,z]` 六个预处理信号文件；不将561维派生特征、body_acc和total_acc双重计作独立传感器。结果只可能说明此协议下的活动识别，不代表医疗诊断、野外自由生活或其他硬件泛化。

UCI 页标 CC BY 4.0，使用时保留作者、数据题名、DOI `10.24432/C54S4K` 与链接。另一个候选 UCI224 气体漂移集网页的 CC BY 与正文“仅研究、排除商业”互相冲突，本次不下载、不使用，避免不清楚的许可风险；其优势是时间漂移，但许可边界阻断。

## 冻结来源门和方法

仅官方 `https://archive.ics.uci.edu/static/public/240/human%2Bactivity%2Brecognition%2Busing%2Bsmartphones.zip` 原件，经内存读取，不落地 ZIP 或原始信号副本。核对官方 train/test 的 `subject_[train,test].txt`、`y_[train,test].txt` 与12个惯性信号文件（两个模态各三轴×两域）：逐窗六信号各128有限数值、每域行数与标签/受试者对齐、标签只在1–6；统计每类每域的人数与窗口数、总人/窗、受试者交集及跨域六信号精确重复窗口数。来源页所说窗口预处理已发生，不能声称是连续原始时序或历史实时采集流；未提供受试者跨数据集身份键。

先定来源门：有效六信号配对窗总数≥9000；train≥20人、test≥8人、合计≥28人，交集0；六类每类 train≥15人且 test≥6人；全部已列六信号每行128有限值，标签/受试者同长，跨域完整六信号精确重复窗数0。任一不满足即 `STOP_REAL_HAR_SOURCE_SUPPORT`，不开模型；全部满足即 `REAL_HAR_PERSON_SPLIT_SOURCE_READY_FOR_STAT_DESIGN`，**仅来源资格**，不是模型改善。精确重复只查两域碰撞，不能证明不同人的动作内容在统计上独立。不得据本次测试标签频数选择模型或门槛。

尝试 `EXP068-SOURCE-001`，脚本 `audit_uci_har_source.py`；官方下载≤70MiB、CPU≤20分钟、内存≤1GiB。保存派生 `SOURCE_MATRIX.json`、`RUN_OUTPUT_001.txt`、`GATE_RESULT.md`、`REPORT.md`、`CLOSEOUT.md`；原始资料只引用URL与成员路径，不保存复制品。只运行本目录的局部校验，无全仓门或非必要哈希。若通过，下一 Experiment ID 才冻结传统模型、受试者级开发/测试、主指标和止损门；此 ID 不训练、不评分。
