# LM-vs-NATURAL-REASONING-MATH-022 | 语言模型与自然推理的纯数学比较

## 定位
本节不比较“谁更像人”，也不把合成 reasoning world 当作真实神经科学证据。这里把“自然推理”定义成一种最低限度的 reference algebra：它必须允许 retained commitment、re-entry、branch、counterfactual manipulation、comparison 与 conditional correction。然后把它与 autoregressive language model 的一般动力学形式比较。

## 1. 两边首先属于同一个大类：受状态条件化的动力系统
Autoregressive language model 可以写为：

    h_{t+1}=F_theta(h_t,e(a_t)),     a_{t+1}~pi_theta(.|h_{t+1})

Reasoning control algebra 写为：

    r_{t+1}=G_{a_t}(r_t),           y_t=O(r_t)

因此数学上不存在“一个是神秘思考、一个只是机器”的二分。两者都可以是状态、算子、读出与反馈组成的动力控制系统。真正值得比较的是 state 怎样因子化、哪些 operator 是 primitive、什么信息被外显。

## 2. 核心差别不是可计算性，而是状态因子化与原生控制接口
标准 autoregressive LM 每一时刻只实现一条 realized token path；任何尚未外显的候选、回退点、比较结果，都必须编码在 hidden state h_t 中，或者通过更多 token 序列化出来。021 的 natural-reasoning reference algebra 则把 committed main、counterfactual branch 与 comparison state 分成显式状态坐标。

这不是说 LM 不能实现 reasoning。恰恰相反：只要 hidden state 足够，LM 可以模拟整个 reasoning algebra。区别是：如果它真的完成同一个 reasoning task，它的 h_t 内部必须携带一个与 augmented reasoning state 等价的预测信息。

## 3. 一个精确的 serial-emulation 下界
021 有 173 个 future-response 不等价的 reasoning states，但可见 committed surface 只有 goal×main=25 种。每个 visible surface 平均折叠 11.0 个不同内部 reasoning states；同一 surface 内 state pairs 的 future-response 不等价比例为 89.89%。

由 deterministic predictive-state / Myhill–Nerode 型下界，任何要精确实现全部未来控制行为的串行系统，必须至少具有与 future-response equivalence classes 一样多的可区分 hidden states。

    |H_min| >= |R / ~future| = 173
    hidden bits >= ceil(log2 173) = 8 bits
    visible (goal,main) projection only needs ceil(log2 25) = 5 bits
    extra predictive information lower bound = log2(173/25) = 2.791 bits

所以“只看当前语言表面”必然不足；但“LLM 隐状态也只是当前表面”同样是错误的。一个能精确做这类 reasoning 的 autoregressive model 必须在 hidden dynamics 中恢复这些额外 predictive distinctions。

## 4. 自然推理 reference algebra 比普通语言运动新增什么？
语言实验已经给出：局部 teacher motion stable rank≈2.481；35 个字符生成算子族 stable rank≈6.018；算子组合非交换。020/021 显示 reasoning 并不是抛弃这套结构，而是在其上增加新的 factor/control primitives：retained commitment、re-entry、branch fiber、comparison state、conditional correction。

因此可以写成：

    G_reason = closure_o(G_language) ⊕ R_memory ⊕ R_reentry ⊕ R_branch ⊕ R_compare ⊕ R_correct ...

这里“⊕”表示实验上可分离的新 generator component，不要求线性正交。

## 5. 两边共享“高维状态 + 低维实际运动”结构
语言局部 teacher motion stable rank=2.481；language operator family stable rank=6.018。020 reasoning state stable rank=8.758，但合法 reasoning trajectory movement stable rank=3.118。021 加入 branch/correction 后 state stable rank=6.996，实际 branch-loop movement stable rank=5.589。

所以最稳妥的纯数学比较不是“语言模型低维、自然推理高维”。更像是：两者都允许高维 predictive state，但一次真实运行只调用较低维的局部控制方向；自然推理的新增特征是能够把多个关系位置/承诺同时保存在增广 state 中，并用高层 operator 对这些 state factors 做比较和重写。

## 6. 一个重要等价命题
**Finite emulation proposition.** 对任何有限 reasoning control algebra (R,A,G,O)，存在一个 autoregressive hidden-state dynamical system whose hidden state can encode R exactly and reproduce the same operator/output behavior. 反过来，如果把 autoregressive system 限制到只保存 surface projection P(r)，而存在 r1!=r2、P(r1)=P(r2) 且 r1 not~_future r2，则它不可能精确实现全部 reasoning behavior。

因此“语言模型 vs 自然推理”的数学分界不是能不能计算，而是：**模型是否在内部建立了与 reasoning algebra 同构/同态的增广 predictive state，以及其 token 控制是否真正实现 branch、compare、correct 等闭环 operator。**

## 7. 当前纯数学结论
1. LM 与 reasoning 都属于状态依赖动力控制系统；“机制化”不会把其中一方降级。
2. Autoregressive serialization 不是 reasoning 的反面；它是一种实现接口。若要精确支持 reasoning，它必须在 hidden state 中携带被文本表面折叠掉的 branch/commitment/comparison 信息。
3. Natural-reasoning reference algebra 的新增数学对象不是“更多词义”，而是对多个关系状态及其比较结果进行控制的高层 generators。
4. 文本输出是 reasoning state 的投影；同一可见输出可以对应 future-response 不等价的内部状态。
5. 真正需要在真实 LLM 上检验的问题因此被压缩为：hidden-state control field 中是否存在可识别的 branch fiber、comparison gate、conditional correction operator，以及它们是否具有与 020/021 相同的 future-response algebra。

## 证据边界
“自然推理”在本节中是一个形式化 reference algebra，而不是对人脑神经实现的经验断言。现有自然语言实验与合成 reasoning experiments 支持的是一套可施工的数学比较框架；真实人类推理是否采用同样的状态因子化，需要独立行为/神经数据。