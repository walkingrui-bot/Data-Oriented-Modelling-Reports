# Frozen-weight reasoning freedom — mechanism pilot 01

Date: 2026-09-25

## Question

Where can task-specific reasoning freedom exist after model weights are frozen?

This pilot isolates the read→transform→write→read loop in a fully observable decoder-only Transformer. Each problem supplies a newly sampled state-transition rule, so the concrete rule varies by episode while model weights remain fixed.

## Controlled task

- Five visible states.
- Each episode samples a new transition permutation.
- The prompt presents the transition table, a start state, and a requested rollout length.
- Training uses rollout lengths 1–5.
- At test time the model generates one intermediate state at a time; every emitted state becomes part of the next forward pass.
- A one-shot control asks what the same frozen network predicts from the initial prompt before any intermediate state has been written back.

Model: 3-layer decoder-only Transformer, d_model=64, 4 attention heads.

## 1. Externalized recurrent computation adds real capability

After training:

| requested steps | iterative rollout final accuracy | one-shot final accuracy |
|---:|---:|---:|
| 1 | 0.908 | 0.908 |
| 3 | 0.883 | 0.350 |
| 5 | 0.858 | 0.450 |
| 8 (beyond training horizon) | 0.667 | 0.150 |

The same fixed weights therefore solve substantially longer compositions when allowed to repeatedly emit a state and read it back.

## 2. Task-specific freedom appears only after contextual reading

At a fixed scratchpad position, examples were grouped so the visible token identity and position were identical across tasks. Effective rank was computed from across-task covariance.

| layer | K effective rank | V effective rank | residual effective rank |
|---:|---:|---:|---:|
| 0 | 0.000 | 0.000 | 3.573 |
| 1 | 3.431 | 2.553 | 5.018 |
| 2 | 4.036 | 3.609 | 5.332 |

Layer-0 K/V are fixed by token identity + position and therefore have zero task-specific freedom. After one contextual block, several independent task-specific K/V directions appear and expand further in the next layer.

## 3. The deep K/V state contains the current transition rule

Five-fold linear probes predicted the next state using only the K/V vector of the same visible scratchpad token.

Token-only baseline: 0.190.

| layer | K probe accuracy | V probe accuracy | residual probe accuracy |
|---:|---:|---:|---:|
| 0 | 0.190 | 0.190 | 0.758 |
| 1 | 0.742 | 0.735 | 0.972 |
| 2 | 0.967 | 0.937 | 0.982 |

Thus identical visible tokens acquire strongly task-specific internal states after contextual reading.

## 4. Causal patching localizes an execution channel

Recipient and donor episodes were selected with the same visible three-token scratchpad prefix but different correct next states. The recipient's visible text was kept unchanged. Only the internal K/V states assigned to those scratchpad positions were replaced by the donor's states.

Results are equal-weighted across 60 distinct visible scratchpad prefixes (300 donor pairs):

| patch (layers 1+2, all 3 scratch tokens) | recipient argmax flips | flips exactly to donor target | Δ recipient-target probability | Δ donor-target probability |
|---|---:|---:|---:|---:|
| K only | 0.133 | 0.107 | -0.123 | +0.105 |
| V only | 0.010 | 0.000 | -0.001 | -0.002 |
| K+V | 0.120 | 0.097 | -0.113 | +0.096 |

A single final scratchpad token was not sufficient to carry this causal effect; replacing the distributed K states across the visible scratchpad produced the effect.

A same-target donor control produced essentially no harmful shift in repeated multi-seed checks, while different-target donor effects were heterogeneous across visible prefixes. A 60-prefix stratified analysis gave an average K-patch flip rate of 0.140 and donor-target flip rate of 0.121.

## 5. Read freedom changes during rollout

The effective number of attended positions in the deepest layer increased from about 2.65 before the first emitted state to roughly 6–7 after several emitted states. Deep-layer attention mass assigned to already-emitted scratchpad positions also rose across the rollout (approximately 0.10 after the first state to about 0.35 late in the 8-step trajectory).

However, raw scratchpad attention mass did not positively predict K-patch causal strength (pair-level correlation approximately -0.23). The causal variable is therefore better described as routing geometry than as simple "amount of attention".

## Current evidence-supported mechanism

For this controlled frozen-weight Transformer:

1. Long rollout adds usable computation through repeated external write/read cycles.
2. The concrete episode-specific transition rule is absent from layer-0 K/V at a fixed token and position.
3. Contextual computation creates several task-specific degrees of freedom in deeper K/V.
4. Deep K states distributed across the scratchpad can causally redirect the next generated state even when the visible scratchpad is held fixed.
5. V replacement has little causal effect in the same intervention, identifying K/routing geometry as the stronger execution channel in this trained system.

This establishes a concrete mechanism by which fixed weights can instantiate a task-specific generative operator in runtime state. It is a controlled proof-of-mechanism, not yet a claim that QwQ/Qwen3 uses the identical internal allocation.

## Next experiment

Move from an explicitly supplied transition table to a latent-rule task where the rule must be inferred from partial evidence. Then repeat the same fixed-token, deep-K/V rank/probe/patch battery. The critical test is whether a rule inferred rather than stated becomes causally instantiated in the same contextual routing degrees of freedom.
