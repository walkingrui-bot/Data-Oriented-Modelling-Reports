# 本机工具选择器

结论及适用条件见[REPORT](REPORT.md)，全过程见[WORKLOG](WORKLOG.md)。这个组件把请求和每个工具的能力说明配对评分，返回原工具的canonical名称；实际参数绑定、授权和执行由调用方另行负责。

## 直接运行

在仓库根目录，使用已有环境和模型缓存。以下命令只读原始题目，不复制实验输入。

```sh
cd '/Users/rui/Documents/ChatGPT/生物圈3号'
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py --case multiple_60
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py --case multiple_60 --method lexical
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py --case multiple_153 --policy research/records/MCD-SELECTION-20260926-002/policy.json
```

第一条用22.7M关系排序器；第二条用无需神经模型推理的TF-IDF基线；第三条展示本次冻结策略如何对所有候选分数都很低的失败题弃权。`--method rerank_description`仅评分工具描述，属于开发阶段比较方案。

真实请求从自己的JSON原件读取：

```sh
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/selector.py /absolute/path/request.json
```

输入对象必须有非空字符串`query`和数组`tools`。每个工具必须有唯一、非空字符串`name`，非空字符串`description`，以及对象`parameters`（该字段承载工具的参数schema）。本轮验证的是英文请求与英文能力说明；中文或其它分布尚未测量。

输出包括`diagnostic`、逐工具`candidate_scores`和`telemetry`。没有候选返回`NO_CANDIDATES`；最高分并列返回`TIED`和空选择；否则返回`RANKED`和唯一名称。分数是模型logit或词面余弦，不是正确概率。默认建议为`RANKING_ONLY_UNCALIBRATED`；显式传入匹配模型版本和评分方法的`--policy`才会返回`CANDIDATE_FOR_BINDING`或`ABSTAIN_UNCERTAIN`，两者均`executes_tools: false`。弃权时`selected`可能仍保留最高分名称供诊断，调用方必须检查`recommendation`。

[policy.json](policy.json)只是在本研究30题及其派生条件上拟合的经验阈值，未获部署风险保证。100题测试覆盖38%；另40题改述后覆盖仅5%。不要把它自动用于其它分布。候选相关但参数缺失时，应进入参数澄清；相关性评分本身不决定参数是否有效。

长文档截断策略为保留query、截断候选文档尾部到512 token，并在telemetry标明；过长query导致无法满足此策略时底层tokenizer会报错。空query、重复名称、非法分数等拒绝处理，不兜底选工具。无匹配识别只做了移除gold的构造条件，尚不等于自然无工具请求验证。

## 环境与原件位置

- Python：仓库`.venv-neural/bin/python`，复用现有torch/transformers；模型默认float32 MPS，可退回CPU，4 CPU线程。
- 神经排序权重：`/Users/rui/.cache/huggingface/hub/models--cross-encoder--ms-marco-MiniLM-L6-v2/snapshots/233902d25c440f23af6f7d6e94d2946bac0bee0a`，仅这一份官方缓存；加载为local-files-only，禁用remote code。
- 原135M比较模型：`/Users/rui/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-135M-Instruct/snapshots/12fd25f77366fa6b3b4b768ec3050bf629380bac`。
- 原BFCL输入及答案：[bfcl_multiple.jsonl](../MCD-ENGINEERING-20260926-001/bfcl_multiple.jsonl)、[bfcl_answers.jsonl](../MCD-ENGINEERING-20260926-001/bfcl_answers.jsonl)。TF-IDF只从原开发题0..29的候选说明计算IDF，因此仍依赖这份原数据。
- 原提示构造器：[pretrained_probe.py](../MCD-ENGINEERING-20260926-001/pretrained_probe.py)，由比较脚本按路径导入。
- 原评估材料仍在用户Downloads中的v0.5 DOCX和COMPLETE ZIP；本研究不重新打包。

## 结果与再分析

开发分为[dev_segments.json](dev_segments.json)引用的两个原始段：首段180条后缓存API兼容失败，接续只完成剩余180条。没有拼接或复制日志。

[FROZEN_PROTOCOL](FROZEN_PROTOCOL.md)记录开发后冻结的四个比较方案、校准网格和最终100题；[test_summary.json](test_summary.json)是主汇总，[control_scores.jsonl](control_scores.jsonl)保留逆序、query替代、移除gold控制。子研究[003报告](../MCD-SEMANTIC-STRESS-20260926-003/REPORT.md)记录另40题改述，不能合并冒充同一预注册确认。

`compare.py`、`study_analysis.py`、`controls.py`保留评分与分析实现。它们的既有结果属于已完成尝试，原输出使用exclusive创建；不要直接重跑覆盖。进一步实验需要新run_id/输出路径和研究登记。单题CLI用于实际调用，不改历史结果。

局部合同检查：

```sh
.venv-neural/bin/python research/records/MCD-SELECTION-20260926-002/test_selector.py
```

原件日志包括[contract_tests.log](contract_tests.log)、[final_contract_tests.log](final_contract_tests.log)。[cli_smoke.log](cli_smoke.log)保留验证器误用基础Python的失败；纠正venv入口后的三个CLI检查见[cli_smoke_r1.log](cli_smoke_r1.log)。只检查本组件，无全仓门或哈希扫描。
