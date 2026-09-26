# P05-RTG-POSTTRAIN-20260925-001 关账

2026-09-25；EXPLORATORY；原问题与事前判据见 [PLAN](PLAN.md)，完整结果见 [REPORT](REPORT.md)。

## 三轴结论

- 执行：COMPLETED_CONDITIONAL。唯一正式五种子 Phase A、诊断与本轮交付完成；B/C/D/E 未运行。
- 工程：LOCAL_VALID。9 项局部合同、修正后完整 smoke、563200 原始预测核对、30 组恢复与3600 trace steps 检查通过。
- 科学：MIXED / GATE_A_RELATIVE_ADVANTAGE_FAILED。完整 RTG 1–20 步均 100%，等参数循环模型和纯迭代 reader 也是100%；no-write / reset-M 等消融没有 accuracy 损失。后训练提升 RTG 自身长程可靠性，但相对机制必要性未建立。

## 全部尝试

R-READ-001、A-PREFLIGHT-001（8项通过）、A-SMOKE-001（失败）、R-001（启动前梯度/计数修正）、A-PREFLIGHT-002（9项通过）、A-SMOKE-002（通过）、A-CAMPAIGN-001（5/5完成）、A-ANALYSIS-001（完成）、A-AUDIT-001（通过）、A-DIAG-001（完成），以及交付包检查 A-PACKAGE-001（回执见相应 attempts/ 目录）。

失败 smoke 报 RuntimeError；其已完成 2 次 base 更新，旧 completion 错记0，已显式更正而原件保留。正式任务无运行异常，12970真实 optimizer updates；后训练 RTG无错误，step0 RTG的2726个错误和单次base的41120个错误均在原始输出。

## 证据与状态

- 当前数据、源码、配置、85份正式checkpoint（含selected副本）、全部预测/诊断/图表和来源材料均本地存在；85份不代表85个独立实验。
- `checkpoints/seed_*/BASE_ONE_STEP.ckpt` 与两臂 `SELECTED.ckpt` 可恢复；每个检查点还保留 optimizer、RNG、参数配置、批次编号和选择依据。训练材料全部保存，完整重跑入口 `reproduce.py` 使用全新输出目录及具名run。
- 神经依赖 Python3.12.14/PyTorch2.13.0/NumPy2.5.2；分析依赖 NumPy2.5.3/matplotlib3.10.8。精确依赖清单和原机路径在环境文件，运行时二进制未复制；新机器依赖安装未验证。
- 内部 L/M/g、预算和谱系只记录预定小样本，不假装保存了所有训练episode的内部轨迹。原始最终预测完整保存。
- 本次目录属于 Git 未跟踪工件，登记册/平台入口有局部未提交改动；没有提交、上传或异地备份。

## 边界和停止理由

当前静态任务允许精确一步reader直接迭代；对照已经饱和，未观察到 RTG 比普通循环模型的优势。按事前门槛在 A 停止并交付，未改门救结果。

历史依赖、真实 descendant world、少量 base co-adaptation、联合几何/M预算和真实 LM 接线均未检验。机制档案的云端数字只有来源引用，第三/四轮原始包未定位，不能写成本地复现。

后继可讨论新的阶段门：将A作为基本可执行性检查，将机制优势检验放在真正需要历史与动态规则的任务中。此建议未执行，不撤销当前Gate A失败或擅自启动LM。原始代码和所有负结果保留。

## 验证分类

实际运行、静态检查、未验证项目分别列于 REPORT §8；不追加全仓门、历史重放或非必要哈希。登记册与研究入口按本轮最终状态同步，正式工件包包含对应研究记录索引。
