# 语言推理研究专线：阶段性收敛报告与证据归档

**归档日期：2026-09-25**  
**状态：研究专线收敛；后续进入独立复现实验/NN实现，不再继续无边界扩展语言现象。**

## 核心结论

这条研究线从一个非常朴素的问题开始：如果把语义标签拿掉，仅保留 identity、位置、复现和局部顺序，语言内部是否仍然存在可用于区分关系角色的结构？连续实验给出的答案是：**有，但它不是“某个词重复了”这么简单。**

当前最稳的计算候选是：**一个旧 identity / relational state 再次进入活动时，与它绑定的一小团局部关系也部分恢复；远距离 recurrence 的价值主要在于把局部关系团重新接上，而不是形成一根孤立的长程连线。**

进一步的跨语言、古今改写、多轮转译、程序↔自然语言往返、眼动和作者/文体实验把这个命题压得更精确：

1. 关系几何能跨语言和跨表达形式保存，但最强的不变量位于局部—中尺度；
2. 表面 token recurrence 不是最终 identity，必须升级为 learned relational-state correspondence；
3. 人类阅读回跳的“什么时候启动”和“回哪里”应拆开：前者像低负荷动作门，后者更像语义/关系吸引场；
4. 回访不是旧眼动轨迹的机械 replay；如果存在 packet reinstatement，它更可能发生在内部关系状态层；
5. 文体改变的是同一关系系统的时间尺度/衰减/刷新策略；作者改变更多的是表面实现；同一源内容会约束一个允许的关系几何流形，而不是锁死几个固定标量；
6. 这些结果支持“推理可能是内部化的感觉—动作协调/重新定向动力学”的研究假说，但目前**不能**据此声称神经机制已经被证明等同。

## 证据主线

### 1. 匿名 identity 仍携带结构角色
Natural L1/L2/L3 identity-only AUC 为 1.000 / 0.873 / 0.642；L3 局部几何只有约 0.558–0.570，加上全局同 identity recurrence 后升至 0.751，结构 bridge 迭代可至 0.883。频率保持的位置打乱降到约 0.49–0.51。普通未分型 graph diffusion 只有约 0.44–0.50。

这意味着：**token identity ≠ occurrence role；但 identity 的复现历史与带方向的局部关系，可以恢复 role geometry。**

### 2. 跨语言稳定，但不是“神秘全局结构”
五语言（英/中/日/西/法）leave-one-language-out 中，形式文本 local→recurrence→bridge 平均 AUC 0.851→0.909→0.979；程序自然语言解释为 0.902→0.966→0.990。删除共享代码词后仍为 0.871→0.950→0.989。

关键控制改变了解释：字符 bigram 的巨大 bridge 增益部分来自短语/形态复现。word-level 复跑仍约 0.86 AUC，但 bridge 不再巨大。block shuffle 从 1.000 随保留块增大降至 0.551（block=32），说明最强信号在**局部—中尺度**。

### 3. 换时代、换语言、换表示仍能保留关系桥
四篇古文→现代汉语的跨时代留文测试：local 0.592、recurrence 0.586、bridge 0.842。多语言《桃花源记》反复改写链：bridge 0.806±0.012；外部英文译本 0.929，日文训读 0.852。

代码↔自然语言往返用执行测试锁死语义：4个程序、3个重构版本，总计 229,014 次等价性比较，229,014/229,014 一致。其英/中/日自然语言解释仍有 local/recurrence/bridge = 0.697/0.712/0.803。

### 4. 真人眼动：表面 bridge 失败，关系层才是 selector
OneStop demo（2读者、3209 fixation）中，188次 ≥5词位长回跳。字面复现、局部词袋、表面有序 bridge 对真实 target 的选择都约在随机附近（0.43–0.50）。这是一条重要负证据：**文本表面 bridge 不能直接等同于 human gaze target selector。**

但回跳启动存在明显低负荷门控迹象：175个可匹配事件的 source fixation trial-equal percentile=0.364，95% bootstrap 0.300–0.428；相对 forward 局部基线短约22 ms。回跳前三个 fixation 接近 0.5，source 突然降至约0.378。

Target 方面，真实目标此前被看过的比例 74.5%，距离匹配期望为 66.1%；但在“都看过”的候选中，prior count/dwell/max/recency 的排名全部约0.48–0.51。也就是说：**memory availability 有作用，memory strength 不是 selector。**

旧位置之后的4步眼动 packet 也没有被重新走一遍：set/sequence/delta 与距离匹配 null 无优势。因此 packet reinstatement 若存在，不能定义成 scanpath replay。

Wilcox 2024 与 Rego 2026 的独立文献与此收敛：positive PMI / semantic reactivation 能解释 targeted regressions；较低 surprisal 的当前位置更容易启动 regression，更 salient/更 surprising 的旧词更容易成为 target。

### 5. 分布式 expected relation field
从 Wilcox 公开六语 MECO predictor 文件抽样，expected PPMI 对旧候选形成的场通常比 direct PPMI 更宽。三个句子位置批次（18个语言×位置样本）中，约83.1%的 source state 出现 expected effective-candidate number > direct；中位扩张约1.41×；direct 与 expected 的 top target 一致率只有约59%。

这个结果最适合映射到新 NN：**不是 address lookup，而是 distributed attraction → competition/settling → reinstatement。**

### 6. 文体、作者与“同源文本换表达者”
六文体初步结果提示诗歌、对话、科研、新闻、小说、正式文件在 recurrence horizon 上有细微但系统的偏移；不过该 pilot 有两处口头报告不一致，已经在 correction log 中降级，需重跑后再用于论文。

更干净的作者实验（小说/诗歌/戏剧）显示：在作者均值层面，genre 对 recurrence/local/mid/long/bridge/burst 的 η² 大约 0.55–0.62。Hardy 从小说换诗歌、Wilde 从诗歌换戏剧时，几何明显向新文体质心移动，说明它不是纯作者指纹。

同一源文本的独立人类翻译更关键。《奥德赛》第一卷三译本中，总 recurrence density 可以从10.8%变到3.5%，但 local、long、bridge 的跨译者 CV 只有约0.056/0.066/0.066。《伊利亚特》第一卷则稳定在另一组维度（recurrence/mid/gap CV/burst CV）。共同结论是：**同一内容约束一个关系几何流形，但具体稳定轴依赖内容；n-gram 实现最不稳定。**

## 统一机制假说

当前最精确的工作模型不是“语言里有一个逻辑模块”，而是：

**unresolved relational trace → low-cost revisit gate → distributed expected-affinity field over old packets → sparse competition/settling → one or several relational packets reinstated → current/old packet coordination → delayed episode credit**

这也解释了为什么新 NN 不应该使用 teacher address、hard top-k 或 “memory[37]” 式精确检索。exact-token identity 可以作为廉价低层证据，但最终 address 必须是 learned relational-state correspondence。

## 对 NN 架构的直接约束

- 保留大而冗余的 Packet Field，允许稀疏活动；不要过早压成低维 summary/pointer。
- recurrence 不等于 exact token equality；应允许代词、同义表达、省略、跨语言表达映射到同一或相近 relational state。
- 把 revisit opportunity 与 reinstatement affinity 分开学习，但不必增加独立器官。
- gate 更像“什么时候允许活动离开当前流”；selector 更像分布式关系吸引场。
- eligibility trace 记录的是一次 reinstatement episode（source state × old packet × interaction consequence），不是“这个 packet 最近活过”。
- credit 应基于 conditional/relative contribution，避免高频 packet 仅因常见而自我繁殖。
- next-token loss 可以是外显后果之一，不能成为整个系统唯一的价值定义。

## 明确保留的负结果

- ordinary untyped graph diffusion 不能替代 typed structural bridges；
- directional STDP 可把分布学得很强，但不自动保存 occurrence role；
- TRF-v0.1R 修复了 temporal persistence，却没有通过结构语言资格；
- surface bridge 不能预测人类 gaze target；
- prior dwell/count/recency 不能在已访问候选之间选中 regression target；
- revisit 后不会机械 replay 原 scanpath；
- 六文体 pilot 中两个数字存在口头记录冲突，不能直接发表。

## 研究结论的证据等级

**当前可以作为内部强结论：**
1. 频率之外存在 identity/order/recurrence geometry；
2. recurrence 最有价值时会重新连接局部关系结构；
3. 该结构可以跨语言/改写/表示形式部分保存；
4. strongest invariant 位于 local–mesoscale，而非简单 global recurrence；
5. 人类 gaze regression 的启动与目标选择至少表现为不同计算问题；
6. target selector 需要关系/语义层，不是 surface similarity 或 memory-strength heuristic；
7. 同一内容与文体都会约束关系几何，但作者主要改变实现轨迹。

**仍然是假说、需要独立实验：**
1. relational packet reinstatement 是否就是人类抽象推理的通用 primitive；
2. 推理是否与感觉—动作协调共享同一神经动力学；
3. expected affinity field 是否能在不依赖语言模型语义表示的 NN 中自发学习；
4. neural reinstatement 是否可在 EEG/MEG/颅内记录中直接观察。

## 归档说明

ZIP 内包含全部保留下来的数值表、纠错记录、方法定义、来源索引和可复现脚本骨架。大体积/受版权约束的原始数据不再分发，改为保留精确来源和获取入口。`tables/00_evidence_ledger.csv` 是最适合作为后续写论文/搭实验的总账。
