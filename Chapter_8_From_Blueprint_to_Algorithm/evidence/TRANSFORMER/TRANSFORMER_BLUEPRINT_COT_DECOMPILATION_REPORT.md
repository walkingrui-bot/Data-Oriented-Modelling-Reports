# Transformer Blueprint, Output Order, and Chain-of-Thought Decompilation

## System

A 3-block causal Transformer with **116,512 parameters** was trained on a controlled three-operation program task.

Each input supplies:
- three operation facts in random presentation order,
- one payload value,
- an output-mode cue.

The logical program is always an ordered three-slot object:

`E0 -> E1 -> E2`

Two output modes were studied:
- **Direct:** emit only the final answer.
- **Forward trace / CoT:** emit `S1, operation1, state1, S2, operation2, state2, S3, operation3, state3, final answer`.

A reverse-trace control contains the same intermediate information but emits `S3 -> S2 -> S1`.

Sixteen operation programs with `E2=O0` were held out compositionally; the remaining 48 programs were used for training.

## 1. Blueprint formation is separable from answer execution

After the three facts and payload are read, the hidden state at the `SEP` position contains the full three-slot operation program.

For the **direct-only** model, final-layer SEP readout:
- E0: **100.00%**
- E1: **99.82%**
- E2: **100.00%**

For the **trace-only** model:
- E0/E1/E2: **100/100/100%**

The first Transformer block is already sufficient for 100% three-slot readout in the phase-1 curriculum models.

Yet after the Direct-first phase, autoregressive final-answer accuracy was only **15.999%**, while the Trace-first phase produced **100% exact traces and answers**.

Thus, in this controlled Transformer, formation of a readable operation blueprint occurs before successful execution of that blueprint into the final answer.

## 2. The readable SEP blueprint is not the sole causal store

Causal activation patching used donor and recipient problems that differed in exactly one operation slot.

At the embedding/earliest layer:
- replacing the changed fact with the donor fact caused the corresponding CoT operation slot to follow the donor: **100%**
- the other two slots remained recipient slots: **100%**
- the entire donor trace and final answer followed: **100%**

Replacing only the `SEP` state did not transfer the donor operation.

Therefore, the Transformer keeps the causally used program information distributed in the context/fact stream. `SEP` contains an accurate summary/readout of the whole blueprint, but execution does not use SEP as a single recurrent bottleneck.

This differs from the earlier GRU system, where the context-final recurrent state served as the primary blueprint store.

## 3. Output order is an execution scheduler over the distributed blueprint

In the forward-CoT model, first-block attention from the three execution markers routes to the matching logical fact.

Average Layer-1 attention mass to `(E0,E1,E2)`:

- `S1`: **(0.472, 0.159, 0.038)**
- `S2`: **(0.016, 0.274, 0.027)**
- `S3`: **(0.046, 0.032, 0.436)**

At each marker the next operation token is emitted with **100% accuracy**.

Thus the recovered execution schedule is:

`S1 -> retrieve E0 -> execute`
`S2 -> retrieve E1 -> execute`
`S3 -> retrieve E2 -> execute`

The complete program remains linearly readable while individual operations are selectively activated according to output position.

## 4. CoT intermediate tokens are causal computational state

The strongest causal test directly edited intermediate value tokens.

When the correct `V1` was replaced with a different value, while keeping the original context and program:

- next counterfactual `V2`: **97.83%**
- downstream counterfactual `V3`: **97.25%**
- final counterfactual answer: **97.42%**
- full downstream counterfactual trace: **97.25%**

When `V2` was replaced:

- counterfactual `V3`: **98.33%**
- final counterfactual answer: **98.50%**
- complete remaining trace: **98.08%**

The emitted intermediate value is therefore read back as the state for the next computation. In this system the chain-of-thought sequence acts as an external execution tape / working state.

## 5. Why forward CoT is much easier than reverse CoT

Forward and reverse traces contain the same operation identities and intermediate values and use the same number of supervised output tokens.

With the same **14-epoch, batch-512** training schedule:

### Forward trace
- training exact trace: **100%**
- final answer: **100%**

### Reverse trace
- exact trace: **7.29%**
- final answer: **9.75%**
- mean correct step pairs: **0.633 / 3**

The reverse model nevertheless retrieved every operation identity correctly:
- S3 operation: **100%**
- S2 operation: **100%**
- S1 operation: **100%**

Its value accuracy showed the computational problem:
- first-emitted `V3`: **9.75%**
- then `V2`: **15.41%**
- last-emitted `V1`: **38.11%**

Layer-1 attention also reversed its routing schedule:
- first `S3` primarily routes to **E2**
- then `S2` routes to **E1**
- then `S1` routes to **E0**

This supports a precise mechanism: output order can successfully schedule *which operator* is retrieved, but forward execution order is valuable because each emitted intermediate result becomes available to the next causal step. Reverse order requires the model to compute deep future states before their causal prerequisites have been externalized.

## 6. Direct generation versus CoT

The direct-only model eventually reached **98.29%** seen-domain answer accuracy when given approximately the same optimizer-update budget as the curriculum systems.

Therefore direct computation is learnable in this task.

The optimization path is very different:
- a complete program blueprint is readable early,
- direct training then has to learn to collapse all three operations into the hidden computation before emitting one value,
- forward CoT rapidly learns local one-step transitions and writes each resulting state back into the autoregressive context.

At the Direct answer position, attention is not organized as the clean sequential `E0 -> E1 -> E2` routing seen in CoT. The model instead builds a compressed multi-operation computation before the final value token.

## 7. Training-order experiment

Three balanced mixed-training curricula were run after correcting for the longer number of CoT tokens by giving each example equal total loss weight.

Seen-domain generation after the mixed phase:

- **Trace-first:** trace exact **100%**; direct **78.50%**
- **Direct-first:** trace exact **99.23%**; direct **71.74%**
- **Joint from scratch:** trace exact **99.76%** and direct **89.77%** after approximately equalized update budget
- **Direct-only:** direct **98.29%** after approximately equalized update budget

Internal blueprint readout was already essentially complete after the first block in both Trace-first and Direct-first phase-1 models.

Thus the training-order effect observed here acts mainly on the **execution/scheduling circuit**, rather than on whether the three operation facts can be represented at all. Trace supervision installs the sequential retrieve–execute–write-back loop very quickly; direct supervision eventually learns a compressed execution path with more optimization.

## 8. Compositional holdout exposes the exact missing blueprint component

The held-out programs placed operation `O0` in logical slot E2, a combination never shown during training.

Forward-CoT models still emitted approximately **2 of 3** step pairs correctly on these programs: the first two learned operation slots were executed, and failure appeared at the unseen third-slot composition.

The controlled holdout therefore exposes failure at the operation-schedule level rather than only as a wrong final token.

## Recovered Transformer execution algorithm

The evidence supports the following program for the forward-CoT Transformer:

1. keep operation facts as distributed context-resident program components;
2. maintain a globally readable summary of the operation sequence;
3. at output marker `S1`, retrieve the E0 operator;
4. apply E0 to the current value and emit the new value;
5. read that emitted value back as the current computational state;
6. at `S2`, retrieve E1 and repeat;
7. at `S3`, retrieve E2 and repeat;
8. emit the final state as the answer.

This is a sequence of **retrieve -> transform -> externalize state -> retrieve next operator**.

## Evidence scope

These results come from a controlled finite-domain, three-block causal Transformer trained on one explicit compositional computation family. They establish a concrete mechanistic example in which a Transformer forms a readable operation blueprint, keeps its causal components distributed in context, and uses autoregressive output order as an execution schedule and external state tape.
