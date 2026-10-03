# INTERNAL_COORDINATION_018：冻结核心接入的可识别性预检

研究 ID：`STAT-PSYMOE-EXP018-20261002-001`；日期：2026-10-02（Europe/London）；性质：`EXPLORATORY`；父阶段：[EXP017](../EXP017/REPORT.md)。

**结论：`STOPPED_AFTER_PREFLIGHT / VALID_DIAGNOSTIC_ONLY / NOT_IDENTIFIABLE`。** 三条用户具名新增来源 ClinGen、Gene2Phenotype、Orphanet 的 Open Targets 26.06 原生表都可读，但在沿用 EXP017 的药物终端 cohort 和 target split 时，训练与验证部分没有任何新增来源对应的阳性 pair。因此不能以这组数据有效训练并验证每源统计专家或冻结 ganglion 新接口。本轮没有运行 frozen onboarding、九路 end-to-end 重训或任何 test 性能比较；这是样本/任务配对的阻断，不是模型性能阴性。

## 问题、输入与预先停止条件

计划问的是：新三源能否各自形成 native 统计状态，并只训练新接口接入已保存的六路共享 core，保持旧六路不变；对照为六路原模型和九路完整重训。输入先固定为 EXP017 的 26,235 个 target–disease pair、70/15/15 target split、26.06 官方原表与旧三 seed 检查点。EXP017 的 test 已看过，所以即使完成训练也仅能称回顾性开发诊断。

[PLAN.md](PLAN.md) 在任何 EXP018 性能运行前写明：若新增来源缺少可用于辨识的 train 正负和 validation/test 覆盖，则不把管线接口表现记为可识别，不用改 test 或补标签求阳性。先读原表 schema 和 cohort 词值，后计数，再决定是否训练。

## 实际观察

固定 26.06 历史目录有 `evidence_clingen`、`evidence_gene2phenotype`、`evidence_orphanet` 各一个 Parquet 原件，footer 总行数 4,537、5,050、7,461；三表均含 targetId、diseaseId、score、confidence 和日期字段。EXP017 seeds 101/202/303 的保存点均含六个旧接口、core 和 outcome。这里只做结构检查，**没有**重建六路预测。

| 新增源 | 原 cohort native pair | Train（阳性） | Validation（阳性） | Test（阳性） |
| --- | ---: | ---: | ---: | ---: |
| ClinGen | 10 | 4（0） | 3（0） | 3（0） |
| Gene2Phenotype | 9 | 5（0） | 1（0） | 3（0） |
| Orphanet | 6 | 4（0） | 1（0） | 1（1） |
| 三源并集（去重） | **21** | **11（0）** | **4（0）** | **6（1）** |

并集 train 为 11 个 target，validation 为 4 个，均无新增源对应的阳性；test 只有 4 个 target/6 pair，其中 1 个阳性。即使全 cohort 仍有其他阳性，其来源组合不能提供新增三路在 train/validation 下的正向可识别信号。Orphanet 的 6 个 cohort row score 全为 1，缺乏源内分数梯度。原生类别可能有价值，但在当前 terminal outcome 配对中没有足够独立样本评估。

## 决策与适用范围

依原停止规则，本轮停在诊断。没有生成三份 native pair feature 缓存，也没有训练三源 Stat-MoE、冻结 ganglion、端到端九路、三 seed、对照、图或新检查点。旧 EXP017 的阴性和阳性数值都原样保留。若把 `NOT_IDENTIFIABLE` 写成“冻结接入失败”或“新来源无价值”会越过证据。

下一个可施工问题是重新选定 terminal task/cohort，或调整新增来源组合；两者都会改变科学问题、独立样本和比较资格，必须另立 ID 和冻结切分。尤其不能用 EXP017 已看过的 test 充当新确认集。EXP019–021 依赖九路稳定接入的路线尚未因本预检自动获得执行资格；EXP022 的历史时间锁也未完成。

**本轮实际验证：** 官方固定三表的 schema/footer、cohort 限定聚合词值/分数、原 split 的 pair/target/label 分布、旧检查点参数键存在。**仅静态检查：** Passport 对三源的建模建议和 EXP017 模型结构。**未验证：** 旧六路精确预测重建、九路训练、冻结参数不变、精度/校准/干预结果、point-in-time、独立外部验证。原始聚合见 preflight.json (source asset outside this public snapshot)、native_diagnostics.json (source asset outside this public snapshot)、cohort_support.json (source asset outside this public snapshot)，完整尝试表与原件路径见 [CLOSEOUT.md](CLOSEOUT.md)。
