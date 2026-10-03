# EXP070 — WISDM 独立人群双手机传感器三活动来源门

研究 ID `STAT-PSYMOE-EXP070-20261002-001`；2026-10-02 BST；`EXPLORATORY_EXTERNAL_COHORT_SOURCE_AUDIT`；父阶段 [EXP069](../EXP069/CLOSEOUT.md)统计开发门未过。新科学问题：独立于 UCI240 的真实采集，能否找到足够多**逐人同活动、同手机加速度与陀螺仪时段重叠**的记录，以在更多独立人上重新考察第二传感器价值？这检验下一实验的可识别性，不把EXP069失败改称成功。

## 数据、理由与预先边界

[UCI507 WISDM 官方页](https://archive.ics.uci.edu/dataset/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdata)称51人、18活动、20Hz、手机/手表各加速度与陀螺仪，逐人原始行含 ID、活动码、timestamp、xyz；官方 DOI `10.24432/C5HK59`、CC BY 4.0。只审**手机**加速度与陀螺仪；手表另设备不混入，预制滑动窗特征也不计原始记录。预先选官方活动码 `A` walking、`D` sitting、`E` standing（这些与 UCI240 的三项语义相近），但设备位置手机口袋对 UCI240腰部不同；未来即使建模，也不是同任务模型原封外部确认。真实独立单位是人；多样本、多秒及两路同步片段不扩大独立人计数。

原件：`https://archive.ics.uci.edu/static/public/507/wisdm%2Bsmartphone%2Band%2Bsmartwatch%2Bactivity%2Band%2Bbiometrics%2Bdataset.zip`；仅内存下载/按成员流式读，不保存 ZIP、PDF、原始行副本。先核包内 `activity_key.txt` 对 A/D/E 的实际英文名称；若与预先映射不符停止，不改选标签。逐人每传感器×活动统计：格式合法、ID对应文件、timestamp可作整数、xyz有限、行数、首尾时间、非递减时间比例和在两传感器间**不依赖单位的时间跨度交叠率** `max(0,min(maxA,maxG)-max(minA,minG))/min(spanA,spanG)`。比例只用于来源资格，不把任意相近时间行冒充精确同步样本；真正配窗需后继实验明确规则。每组若时间戳非单调可先用 min/max审来源，但留数/比例；不得暗示原文件严格有序。

冻结来源门：官方活动键三项精确匹配；至少40个不同人同时在 A/D/E 的手机 acc 与 gyro 各有≥1000行有效 xyz、非零 timestamp 跨度、两路各活动交叠率≥0.5；这40人各活动有两个传感器，不允许从不同人/活动凑。低于任一门即 `STOP_WISDM_PAIRED_PERSON_SUPPORT`，不训练；通过才 `WISDM_THREE_ACTIVITY_PAIRED_SOURCE_READY_FOR_DESIGN`。同时报所有51人的缺口、无效/非有限、各活动来源分布与具体身份支持，避免缺失=0。仅审来源，0模型拟合、0 UCI240旧test评分。

候选取舍：继续 UCI240同21人调C或改门槛不会提供新的独立证据；WISDM新增不同人、手机口袋场景与原始双传感器，可将人级不稳定与跨场景差异分开研究。PAMAP2仅9人，UCI341与UCI240为同30人衍生，不提供同等独立人增量；UCI224气体集许可陈述冲突而暂存。WISDM仍受受控活动、参与者/设备配置与三类任务限制。

尝试 `EXP070-SOURCE-001`，命令 `python3 audit_wisdm_source.py`；网络≤330MiB、内存≤2GiB、CPU≤20分钟。输出 `SOURCE_MATRIX.json`、`RUN_OUTPUT_001.txt`、门/报告/关账；只保存来源元数据和计数，不复制原始材料。必要时按实际包结构作解析修订，保留失败尝试和先前已看内容；不能改冻结科学门。局部验证只核本目录派生计数与门裁决；不运行全仓或哈希审计。若通过，下一实验另ID冻结人级训练/测试、配窗规则、适当统计模型与实用门；本ID不看成绩。
