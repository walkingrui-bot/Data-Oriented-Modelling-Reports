# CG-020 protocol

## Question
Can a generated relation system become the persistent computational state of an iterative data model when recurrent hidden state is removed?

## Data
The exact synthetic panel from CG-017—019 is reused: 600 parameter groups, split 400/100/100 for train/dev/test. Each group contains three observationally equivalent linear-Gaussian causal worlds and support/no-support conditions. Test contains 100 independent parameter groups and 600 task instances.

## Persistent state
At world-update step `t`, the only persistent state is:

`O_t = (B_t, logits_t)`

where `B_t` contains three 3×3 candidate relation matrices (zero diagonal, row absolute sum ≤ 0.95), and `logits_t` contains three candidate weights. The fixed observational/support context is re-encoded at every update. Query target is excluded from world generation and is used only to select the final simulated consequence.

No GRU, RNN, recurrent latent vector, KV memory, or parallel hidden state is propagated between world updates.

## Attention variants
All variants use d_model=32, 4 heads, FF=64, zero dropout.

| Variant | Parameters | Attention organization | Explicit world updates |
|---|---:|---|---:|
| onepass1 | 9,286 | 1 block | 1 |
| onepass3 | 26,374 | 3 untied blocks | 1 |
| tied6 | 9,286 | same block repeated 6× | 1 |
| world4_3 | 26,374 | 3 untied blocks shared across updates | 4 |

`onepass3` and `world4_3` therefore have identical parameter count; their principal difference is whether the explicit world object persists across multiple updates.

## Training
Seeds 11 and 22. 450 optimizer updates, batch 64, Adam learning rate 0.0015, gradient clipping at 5. Development NLL checked every 50 steps; best checkpoint retained. Within a seed, all variants use the same RNG rule for batch indices.

Only final mixture NLL is supervised. Intermediate relation matrices receive no direct labels.

## Primary evaluation
Original single-intervention mixture NLL, mean MSE, nearest-candidate MSE, support/no-support NLL and ambiguous-world coverage.

A paired 100-group analysis compares `world4_3` with the parameter-matched `onepass3`; group differences are averaged across the two seeds and bootstrapped 10,000 times over independent parameter groups.

## Cross-question evaluation
The final generated worlds are also evaluated on CG-019-style unseen simultaneous double-do and requested-edge deletion problems. The latter includes ignore-edit and wrong-coordinate controls.

## State sufficiency and interventions
For `world4_3`, the explicit state after update 2 is serialized and then used to continue updates 3–4. Exact replay is compared with uninterrupted execution.

Three interventions are applied at update 2:

1. erase `B` and candidate logits;
2. transplant `B` and logits from a different test group matched on support/query status;
3. flip the largest-magnitude edge in the highest-weight candidate, then continue updates.

The edge-edit prediction displacement is measured immediately and after later world updates.

## Rollout beyond training horizon
The frozen `world4_3` checkpoints are iterated for 20 explicit world updates on a fixed 200-case test probe. NLL, MSE, relation-state RMS change and relation-state RMS norm are recorded. Training supervision ended after update 4.
