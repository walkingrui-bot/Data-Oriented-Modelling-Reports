# NATURAL-REASONING-FINDER-024 | 怎样在模型里找到类似自然推理的内部过程？

## 研究触发

023 已经证明：可见 CoT 完全固定时，模型仍可在 hidden state 中完成任务；同时也出现一个更重要的问题——内部可解码的变量是否都属于“真正推理过程”？本轮因此把 **decodability** 与 **functional reasoning state** 分开。

## 1. Label-free future-control tomography

在每个 layer/time checkpoint 真正停机，只从 hidden activation cloud 本身取 PCA 扰动方向；沿这些方向做 ±ε state perturbation，再继续完全相同的 visible suffix。将 baseline answer logits 与局部 finite-difference future responses 拼成 future-control signature。发现阶段不使用 main/branch/comparison 标签。

输出只按最终答案训练的 023 模型中，post-hoc audit 得到：

- answer：best AMI = 0.9707
- branch：best AMI = 0.2577
- comparison：best AMI = -0.0109

这说明 Finder 很容易恢复最终 answer state，也能看到部分 branch structure，但没有恢复出独立 comparison gate。

## 2. 一个关键反例：可解码 ≠ 功能性 reasoning state

为排除“Finder 太弱”的解释，另训一个正对照：visible CoT 仍严格固定，但在 hidden state 上增加辅助 supervision，使 THINK state 中 main/branch、CHECK state 中 comparison 都可被专门 auxiliary head 100% 解码；最终 answer 同样 100% 正确。

然而在这个模型上，仅使用未来控制几何的 label-free tomography，comparison 的最佳 AMI 仍只有 0.0356。也就是说，**一个变量可以在 hidden activation 中被完美读出，却没有作为一个独立 predictive/causal state 参与未来控制。**

这给出本系列非常重要的方法学修正：probe accuracy 不能单独定义“模型在这里推理”。

## 3. 与 reference reasoning algebra 的对照

REASONING-BRANCH-021 中的 COMPARE 则满足功能性判据：COMPARE 当前 committed answer 不变，却改变 future-response state；把 COMPARE/CORRECT 反序会改变结果，强制错误 comparison signal 会在 72.0% 病例改变最终输出。这里 comparison 是 **被后续 CORRECT 实际读取的 gate**，因此属于 future-equivalence quotient 的真实 reasoning state。

于是三类对象被区分：

1. **surface token**：可见但可能不携带完整状态；
2. **decodable hidden feature**：能从 activation 读出，但可能只是伴随表征；
3. **functional reasoning state**：能区分未来、改变局部 control geometry，并能通过 transplant/intervention 搬运后续行为。

## 4. Natural Reasoning Finder 的正式判据

一个内部变量/子空间升级为 reasoning-state candidate，至少需要三条同时成立：

1. **Recoverability**：在 layer×time 停机点可稳定恢复；
2. **Future relevance**：不同取值对应不同 standardized future-control signature / future-equivalence class；
3. **Causal transport**：activation transplant、low-rank patch 或定向扰动可以把后续行为按 donor/candidate state 重定向。

只有第 1 条成立时，只能称为 representation；三条同时成立，才称为 functional reasoning state。

## 5. 怎样在真实 LLM 中寻找“像自然推理”的过程

1. 收集 surface-equivalent checkpoints：当前 token/CoT/answer propensity 相同或近似，但历史不同。
2. 在 layer×time 网格暂停模型，保存 residual stream / KV cache / recurrent memory 等内部 state。
3. 对每个停机点做 standardized future-control tomography：同一 suffix、多方向 state perturbation、future logits/Jacobian。
4. 按 future-control signature 建 quotient / cluster；不要按词义或 CoT 文本聚类。
5. 找 **silent branch fiber**：当前 readout 不变但 future signature 改变的内部方向。
6. 找 **comparison gate**：future-control geometry 出现分区、方向突变或 conditional switch 的内部状态。
7. 找 **conditional correction**：同一后续 token/action 在不同 gate state 下产生不同 state rewrite。
8. 做 hidden transplant / low-rank subspace patch；验证这些内部状态能否因果搬运未来轨迹。
9. 最后拟合 operator algebra，检查模型内部是否出现 retained commitment、re-entry、branch、compare、correct 等与自然推理 reference algebra 功能同构的结构。

## 6. “像自然推理”的数学定义

设模型内部 predictive-state quotient 为 H/~future，自然而言的 reasoning reference algebra 为 R。若存在一个映射 phi: H/~future -> R，使一组模型内部算子 T_a 与 reasoning operators G_a 在相关状态上近似满足

phi(T_a([h])) ≈ G_a(phi([h])),

并且这些算子通过因果干预可复现 branch/re-entry/compare/correct 的未来行为，则称该内部过程与自然推理代数 **功能同构/近似同态**。它不要求模型输出人类式 CoT，也不要求 hidden coordinate 与人类语言标签一一对应。

## 7. 当前实验给出的结论

023 的 output-only LM 已经能 100% 解题，但 Finder 没有找到独立 comparison gate；因此正确答案本身不证明模型内部执行了 natural branch→compare→correct 算法。相反，真正的“自然推理过程”必须通过 future-equivalence 与因果控制结构来识别。
