# RTG 后训练功能验证任务说明 v0.1
## Reproductive Transition Geometry Post-Training Functional Validation

日期：2026-09-25

### 0. 任务定位

本任务不是继续寻找“RTG 是否会产生某种动力学现象”的证据，也不是重新证明 CEG/CE²G 已经建立的历史依赖、几何写回或路径依赖性质。

当前前提是：

1. `繁衍式转移几何 1.0（RTG-1.0）` 已经作为一个完整、可运行的通用推理动力学机制之一被定义；
2. 云端 toy-world 已经完成构造性充分性测试：该机制能够生成与长推理中观察到的多种动力学投影；
3. 下一阶段的唯一核心问题是**功能性验证**：

> 能否把 RTG 做成一个后训练学习器，使一个原本只有局部/一步关系能力的模型，通过 RTG-style post-training 获得真正的多步、历史依赖、可长度外推的推理能力？

因此本任务的评价中心从“动力学统计像不像”切换到：

- 最终任务成功率；
- 长度外推；
- 未见规则迁移；
- 历史依赖推理；
- descendant-geometry rewrite；
- RTG 机制消融后的能力损失；
- 基础模型能力是否保留。

---

# 1. 开工前必须先读的材料

工作区中会提供：

1. `繁衍式转移几何_1.0_机制档案_20260925.docx`
2. 如存在：RTG 第三轮 / 第四轮实验包与报告。

先完整读机制档案，再开工。

不要把 RTG 重写成普通 RNN / GRU hidden state，也不要为了方便把核心机制压缩成一个单一 latent vector 后声称“等价”。

必须保留 RTG 至少以下逻辑区分：

- continuation geometry；
- realized transition；
- rewrite phenotype；
- descendant geometry rewrite；
- inherited / recombined rewrite state；
- bounded write budget；
- projection feedback（在需要的阶段启用）。

工程上允许 low-rank / sparse / factorized 实现，但逻辑对象必须可单独记录和消融。

---

# 2. RTG 最小学习器定义

实现时优先使用 log-capacity / continuation-logit 形式，避免显式 `exp(-S)` 的数值问题。

对当前状态 `a`，定义 continuation geometry：

```text
L_t[a, b]     # continuation log-capacity / logit
P_t[a, :] = softmax(L_t[a, :])
```

这里 `L` 等价于 `-S/Theta` 的数值实现。

每个可实现 transition `a -> b` 有 relation feature：

```text
phi[a, b] in R^d
```

每个活动位置/关系槽维护 inherited rewrite state：

```text
M_t[a] in R^d
```

一次真实 transition `a -> b` 发生时，现场生成 rewrite phenotype：

```text
g_t = normalize(
    W_phi(phi[a,b])
    + gamma * W_M(M_t[a])
    + interaction_term
    + mutation_term
)
```

第一版允许 `interaction_term=0`、`mutation_term=0`，先把基本功能跑通。

`g_t` 不直接要求 child transition 与 parent transition 相似。它用于改写目的状态 `b` 的 descendant continuation law：

```text
score_k = similarity(g_t, phi[b,k])
score_k = score_k - mean_k(score_k)

DeltaL_gene[b,k] = eta_gene * score_k
```

rewrite phenotype 同时部分遗传到目的状态：

```text
M_(t+1)[b] =
    normalize(
        (1-rho) * M_t[b]
        + rho * W_inherit(g_t)
    )
```

所有 geometry rewrite 必须经过 bounded write：

```text
proposed = DeltaL_gene + DeltaL_projection

alpha_t = min(
    1,
    write_budget / (norm(proposed) + eps)
)

L_(t+1) =
    L_ext
    + geometry_retention * (L_t - L_ext)
    + alpha_t * proposed
```

如需保持等价于 CE²G 的符号方向，注意 `L=-S/Theta`，因此“降低 S”对应“提高 L”。

不要在第一版里加入过多复杂器官。先验证核心：

```text
transition
-> rewrite phenotype
-> descendant geometry rewrite
-> inheritance
-> next transition
```

---

# 3. 训练原则

本轮优先坚持：

> **final-answer-only supervision**

训练数据中可以有规则表、环境描述、起始状态、步数等任务输入，但不向学习器提供：

- 正确中间 transition 序列；
- 正确 hidden mode；
- 正确 rewrite phenotype；
- 正确 `M_t`；
- teacher CoT；
- 人工标注的“应该怎样改写 geometry”。

内部过程由模型自己学习。

可以用最终答案 cross-entropy / classification loss。

若训练完全无法启动，可以增加最小的一步能力预训练，但必须与 RTG post-training 分阶段记录，不能把中间答案监督偷偷带进第二阶段。

---

# 4. Phase A：静态规则的组合外推

## 目的

先验证 RTG 学习器能否把“一步关系能力”变成可重复执行的多步组合能力。

这不是最终机制验证，只是最基础的 functional gate。

## Episode 生成

每个 episode 随机生成一个新的 permutation / mapping：

```text
f: {0,...,N-1} -> {0,...,N-1}
```

建议：

```text
N = 8 或 10
```

输入必须包含本 episode 的规则描述，例如完整 rule table 或足以唯一恢复规则的支持集。

再给：

```text
start state x0
step count L
```

目标：

```text
y = f^L(x0)
```

每个 episode 的 `f` 都重新采样。

训练集和测试集不能复用同一个 rule instance。

## 训练

只训练：

```text
L = 1..4
```

只监督最终 `y`。

模型选择 / early stopping 只看训练长度范围内的 validation；不要用 5–20 步测试集调参。

## 测试

独立测试：

```text
L = 1,2,3,4,5,6,8,10,12,16,20
```

同时测试：

- 新 rule；
- 新 start state；
- 规则表顺序随机排列；
- 如是文本输入，替换 symbol 名字 / prompt 表述。

## 必须保存

```text
accuracy_by_length.csv
train_curve.csv
per_episode_predictions.jsonl
```

## 云端 pilot 参考

云端最小实现曾在 1–4 步训练后，对新随机规则外推到 20 步保持 100%。

这个数字只作为 reference，不作为必须复刻的硬编码目标。

本地实验必须独立复现，不允许根据测试长度反复调参直到匹配该数字。

---

# 5. Phase B：历史依赖的规则切换

## 目的

让“同一个当前状态”在不同形成历史下拥有不同下一步 continuation law。

这一阶段必须真正使用 inherited mechanism state。

## Episode

每个 episode 随机生成两套映射：

```text
f_A
f_B
```

再随机生成 trigger set：

```text
T subset of states
```

初始 mode 为 A。

每一步：

```text
x_(t+1) = f_mode(x_t)
```

如果发生预先定义的 trigger event，则 mode 在 A/B 之间切换。

关键要求：

> 对某些相同 `x_t`，其正确下一步必须依赖此前是否已经触发 mode change。

因此只看当前 state 不足以完成任务。

训练数据仍然只给最终答案。

## 训练

```text
L = 1..5
```

## 测试

```text
L = 1,2,3,4,5,6,8,10,12
```

规则实例全部重新采样。

## 必做消融

### B0：完整 RTG

正常运行。

### B1：reset inherited state

每一步以后：

```text
M_t[:] = 0
```

或恢复 baseline。

其他参数完全不变。

### B2：gamma = 0

保留 RTG 结构，但禁止 inherited rewrite state 参与 `g_t`。

### B3：no geometry rewrite

```text
eta_gene = 0
```

只保留基础模型。

## 判定重点

不是单看 full model 绝对 accuracy。

要同时看到：

```text
full model long-horizon accuracy 高
```

并且：

```text
reset M / gamma=0 / no-write
```

对真正需要历史的长任务造成明确能力损失。

## 云端 pilot 参考

此前 toy learner：

```text
full:
8-step  ~99.5%
10-step ~97.7%
12-step ~95.1%

reset inherited mechanism state:
2-step  ~56.3%
3-step  ~36.6%
5-step  ~27.7%
```

同样只作为独立复现参考。

---

# 6. Phase C：真正的 descendant-geometry rewrite

这是本轮最重要的 synthetic functional test。

## Ground-truth world

不再使用“固定 rule + mode switch”。

建立一个世界，其中真实 transition 本身会改写下一步规则。

每个 episode 随机生成：

```text
base continuation geometry L_ext
relation features phi[a,b]
initial M_0
```

世界使用固定但未知于 learner 的 RTG-style generative law：

```text
g_t = normalize(phi[a,b] + gamma_true * M_t[a])

DeltaL_true[b,k]
    = eta_true * centered_similarity(
        g_t,
        phi[b,k]
      )

M_(t+1)[b]
    = normalize(
        (1-rho_true) M_t[b]
        + rho_true g_t
      )

L_(t+1)
    = retention_true * L_t
      + budgeted(DeltaL_true)
```

真实下一 state 可使用：

```text
argmax P_t[a,:]
```

作为第一版确定性任务。

后续再增加 stochastic branch。

## 输入

learner 得到：

- episode 的 initial relation description / base rule；
- 当前 query；
- 起始状态；
- 要运行的步数。

不提供真实中间 trajectory。

## 两阶段训练

### Stage C1：基础一步能力

先把 base model 训练到：

```text
one-step relation accuracy >= 98%
```

这里只教“当前关系如何读”。

保存 checkpoint：

```text
BASE_ONE_STEP.ckpt
```

### Stage C2：RTG post-training

从 `BASE_ONE_STEP.ckpt` 开始。

训练长度：

```text
2..4 steps
```

只给最终答案。

RTG module 可训练。

基础模型不要完全锁死。

允许**很小的 co-adaptation**：

- LoRA；
- 小 residual adapter；
- 或最后少数层小学习率更新。

这一点非常重要。

云端 pilot 中，如果底层表示被故意扭成彼此完全不对齐的随机坐标，再要求一个完全孤立、完全冻结 base 的 RTG head 独自解决所有对齐问题，训练会失败。

因此本轮的真实工程假说是：

> RTG 负责动态推理；base representation 允许少量共同旋转到与 RTG compatible 的关系坐标系。

必须记录 base 参数实际更新比例。

## 测试

```text
2,3,4,5,6,8,10,12 steps
```

### 必做对照

- `full RTG`
- `no geometry write`
- `no inheritance`
- `reset M every step`
- `same trainable parameter count recurrent adapter`
- `base-only`
- 可选：`no write budget`

## 云端 pilot 参考

两阶段版本曾出现：

```text
2–5 step: 100%
6 step:   99.6%
8 step:   93.5%
10 step:  85.4%
12 step:  73.3%
```

关闭 RTG geometry write 后约在 8-class chance level（约 12–16%）。

再次强调：本地独立复现不追求精确重现这些百分比；追求**同一结构性结果**。

---

# 7. Phase D：把 RTG 接到真实小型语言模型

只有 A/B/C 三个 functional gate 全部通过以后再开始。

不要一上来烧大模型。

## Base model

优先选择本机已经可稳定训练 / LoRA 的最小 decoder-only LM。

建议规模：

```text
0.5B – 1.5B
```

若本地已有更合适模型，使用现有模型，不为本任务专门追求更大参数量。

## 总体结构

```text
mostly-frozen LM
    +
small LoRA / residual interface
    +
RTG dynamic state
```

LM 负责：

- token/语言表示；
- 基础语义；
- 局部关系读取；
- 普通语言生成。

RTG 负责：

- continuation geometry；
- rewrite phenotype；
- descendant geometry update；
- inherited rewrite state；
- projection feedback；
- bounded write。

interface 负责把 LM hidden representation 映射到 RTG relation space，再把 RTG update 注回 residual stream / adapter。

## 第一版不要做的事

不要：

- 微调整个 LM；
- 加 teacher CoT；
- 给正确中间步骤；
- 把 RTG 状态直接监督成真实 hidden rule；
- 用最终测试集调长度 curriculum；
- 为了成功偷偷增加一个普通 recurrent controller。

## 文本任务

先把 Phase A/B/C 的任务 textualize。

例如：

```text
Rule A:
red -> blue
blue -> green
...

Rule B:
...

Switch when: yellow, black

Start: red
Apply 8 transitions.
Answer:
```

训练仍然只在 `Answer:` 后监督最终答案。

再做：

- symbol rename；
- prompt paraphrase；
- rule row shuffle；
- novel rule instances；
- longer step count。

这样先回答：

> RTG 能不能在真实语言模型表示之上承担推理动力学？

而不是直接跳到开放数学 benchmark。

---

# 8. Phase E：开放 reasoning 任务（只有 D 成功后）

D 成功以后，再逐步进入：

- modular arithmetic composition；
- state-machine problems；
- graph-path relation composition；
- symbolic equation transformations；
- 小规模 algorithmic planning；
- 最后才是自然语言数学 / logic benchmark。

仍优先 final-answer supervision。

每引入一个新任务族，都必须保留：

```text
base-only
same-parameter adapter
RTG full
RTG ablations
```

避免把“更多参数”误当成 RTG 机制效果。

---

# 9. RTG 必须记录的内部量

即使最终训练只监督答案，也必须把以下 internal diagnostics 存档：

```text
L_t / low-rank geometry summary
M_t norms
g_t rewrite phenotype
alpha_t write budget
||DeltaL_gene||
||DeltaL_projection||
continuation entropy
effective candidate number
top continuation share
transition ancestry ids
```

不要拿这些量参与 target supervision。

它们只用于：

- 机制审计；
- 消融；
- failure diagnosis；
- 后续与真实 CoT projection 对齐。

---

# 10. 关键防作弊规则

1. **数据 split 按 rule instance，不按 sample。**
2. 测试 rule 不得在训练中出现。
3. 长度外推测试长度不得用于 early stopping。
4. 不给中间答案。
5. 不给 hidden mode。
6. 不给正确 genealogy。
7. 不把 step index 映射成答案 shortcut。
8. rule table / text order 随机化。
9. symbol 名称定期随机替换。
10. 每个主要结论至少 3 个独立 seed；synthetic 最好 5 seed。
11. 所有失败 run 保留，不删除。
12. 如果发现 shortcut，修数据生成器，但旧结果保留在 correction log。

---

# 11. Graduation gates

## Gate A — compositional extrapolation

短程训练后，未见规则的长程 accuracy 明显高于 base / 同参数普通 adapter。

目标：

```text
8–12 step >= 90%
```

20-step 能力作为加分，不作为第一版硬门。

## Gate B — history dependence

完整 RTG 在 history-switch 任务明显成功。

`reset M` / `gamma=0` 应出现大幅下降。

目标：

```text
full - resetM >= 30 percentage points
```

在长程任务上成立。

## Gate C — descendant rewrite

两阶段训练后，RTG 对 8–12 步 dynamic-rewrite task 有明显 OOD 能力。

`no-write` 必须显著接近机会水平或至少远低于 full。

## Gate D — real LM integration

文本化任务上：

- full RTG 显著优于 base-only；
- 显著优于相同参数量普通 adapter；
- 长度外推成立；
- inference-time RTG ablation 造成 reasoning accuracy 明显下降；
- 普通一阶语言/关系能力不能严重退化。

## Gate E — open reasoning

至少一个非人工 state-machine 任务族出现稳定收益后，才进入更开放 benchmark。

---

# 12. 输出与归档

每次实验必须带唯一 run id。

建议目录：

```text
RTG_POSTTRAIN_V01/
├── README.md
├── REPORT.md
├── configs/
├── src/
├── checkpoints/
│   ├── BASE_ONE_STEP.*
│   └── RTG_POSTTRAIN_*.*
├── results/
│   ├── phaseA_accuracy_by_length.csv
│   ├── phaseB_history_ablation.csv
│   ├── phaseC_dynamic_rewrite.csv
│   ├── phaseD_lm_results.csv
│   └── seeds_summary.csv
├── traces/
│   ├── failures.jsonl
│   └── internal_diagnostics/
├── figures/
├── correction_log.md
└── environment.txt
```

最终交付：

1. `REPORT.md`
2. 所有 CSV
3. 关键图
4. 训练与评估源码
5. configs
6. checkpoint
7. failure examples
8. correction log
9. 完整可复跑压缩包

---

# 13. REPORT 必须回答的问题

最终报告不要只写“准确率提高”。

必须明确回答：

1. RTG 是否能作为学习器工作？
2. 是否只给 final answer 就能学？
3. 是否能从短程训练外推到更长推理长度？
4. 是否能处理“同当前状态、不同历史、不同 continuation law”？
5. descendant geometry rewrite 是否对能力具有功能必要性？
6. inherited rewrite state 是否对能力具有功能必要性？
7. bounded write 是否影响稳定性 / 锁死？
8. 完全冻结 base 为什么成功或失败？
9. 少量 co-adaptation 是否足够？
10. RTG 相比同参数量普通 recurrent adapter 的增益来自哪里？
11. 哪些任务通过，哪些没有通过？
12. 下一步是否值得进入真实语言 reasoning post-training？

---

# 14. 当前最重要的工程原则

不要为了“像 RTG”而制造复杂代码。

如果最小实现已经能完成：

```text
transition
-> generate rewrite phenotype
-> rewrite descendant continuation geometry
-> inherit/recombine rewrite phenotype
-> bounded update
-> continue
```

就先跑。

也不要为了追求准确率偷偷加入一个真正负责推理的普通 Transformer/GRU controller，把 RTG 变成装饰。

本轮需要验证的是：

> **RTG 本身是否可以承担 post-training 后新增的多步推理动力学。**

如果可以，再逐步扩大模型、任务和自由度。

---

# 15. 开工顺序

严格按：

```text
A. static random-rule composition
↓
B. history-dependent rule switching
↓
C. transition rewrites descendant rule
↓
D. small real language model integration
↓
E. open reasoning
```

任何阶段失败，先定位该阶段，不跳级用大模型掩盖问题。

完成 Phase C 后先提交一次中间报告，再决定 Phase D 的具体 LM 接线。

