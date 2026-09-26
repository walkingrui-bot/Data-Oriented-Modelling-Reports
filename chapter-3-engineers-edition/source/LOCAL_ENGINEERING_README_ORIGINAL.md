# Model Control Diagnostics — 本机工程延伸

本目录是 v0.5 的增量工程研究记录；原始 Word、ZIP 和权重保持原位，不重打包。先读 [评估与结果](REPORT.md)，再按下面入口使用。标准库即可运行 `mcd.py`；真实模型实验使用仓库现有 `.venv-neural`，没有修改共享依赖。

## 直接查看实际模型病例

```bash
cd '/Users/rui/Documents/ChatGPT/生物圈3号'
.venv-neural/bin/python research/records/MCD-ENGINEERING-20260926-001/inspect_case.py --case multiple_23 --posthoc
```

去掉 `--posthoc` 就是未知正确答案时的诊断输出。它从唯一的原始推理记录读取分数，不复制日志。已知答案只补事故评价，不能影响候选选择。

## 接入自己的遥测

```bash
python3 mcd.py diagnose incident.json
python3 mcd.py radius telemetry.json
python3 mcd.py guard domain.json
```

以上三条在本目录执行。输入错误输出 `INVALID_INPUT` 且退出码2；正常诊断退出码0，但0不代表允许执行工具。组件不连接任何真实执行器。

`diagnose` 输入：`score_unit`、`candidates`。每个候选必须有唯一 `id` 和四个有限分数 `full/name_neutral/description_neutral/schema_neutral`。分数由同一模型/评分约定产生；本例是等长度候选标签的 next-token log-probability。可选 `correct_id` 只用于事后分析。输出同时保存各视图并列赢家、每个竞争者的分数变化以及真正的全候选top1。缺字段、NaN、重复ID拒收；不把敏感通道自动命名为唯一病因。

`radius` 输入：`model_revision/checkpoint/score_unit/coordinate_system` 与 `actions`。每个动作有 `id/score/gradient/admissible`，同维梯度和显式可信可执行域状态。对全部可选竞争者取最小一阶距离。可选 `calibration` 包含相同四项来源、`n` 和 `warning_floor`；模型、读出、坐标不匹配即拒收。不校准就返回 `UNCALIBRATED`；零梯度标一阶不可识别，所有结果均 `certified:false`。没有 `EXECUTE` 指令。

`guard` 输入：`registry/context/proposal`。registry 每个工具含 `schema` 和权限需求 `permissions`；context 由可信宿主提供 `snapshot_id/permissions/preconditions`，并行需 `parallel_independent:true`。proposal 含相同snapshot、`mode`、`calls`，每个call含 `name/arguments`。检查注册、参数、权限回执、前置回执、状态版本、空CALL、无操作携带调用、重复调用和并行条件。

支持的schema子集为显式type的closed object、array及其items、string、boolean、null、number、integer、enum、minimum/maximum、minItems/maxItems。未知关键词或类型拒收；这不是完整JSON Schema实现，整数使用严格Python/JSON整数值，`2.0`不当作integer。description仅作注释。schema转换必须由宿主明确完成，不自动把BFCL的dict/float等类型含糊放行。

宿主仍负责真实环境核查、用户意图与作用域、原子执行时的重新校验、认证与审计。本组件接收可信宿主的回执，不能靠输入中的一个true证明外部世界状态，也不能从调用数判断语义目标覆盖。`hard_domain_admissible:true`只说明本次输入满足上述局部合同。

## 原件和复现入口

- [原始证据复算脚本](audit_original.py)：读取用户ZIP成员，不解包复制；[复算结果](original_audit.json)。
- [真实模型协议](PRETRAINED_PROTOCOL.md)、[运行脚本](pretrained_probe.py)、[原始分数](pretrained_scores.jsonl)、[汇总](pretrained_assessment.json)、[干预结果](patch_results.json)、[唯一新状态遥测](patch_states.npz)。
- [最小合同测试](test_mcd.py)、[全过程](WORKLOG.md)、[关账](CLOSEOUT.md)。
- 主干权重：`/Users/rui/.cache/huggingface/hub/models--HuggingFaceTB--SmolLM2-135M-Instruct/snapshots/12fd25f77366fa6b3b4b768ec3050bf629380bac`，仅官方缓存一份，134,515,008参数；新下载的权重约269MB。

重算汇总可以运行 `analyze_probe.py`；不需要再次推理。`pretrained_probe.py --phase main` 故意用独占创建原始结果文件，现有结果存在时拒绝覆盖。需要新实验时必须新run目录/ID并更新运行路径；不要删除旧结果来重跑。patch脚本同样拒绝覆盖既有结果。

局部验证：在仓库根运行 `.venv-neural/bin/python -m unittest discover -s research/records/MCD-ENGINEERING-20260926-001 -p test_mcd.py -v`。只发现此具名文件，不运行全仓测试。
