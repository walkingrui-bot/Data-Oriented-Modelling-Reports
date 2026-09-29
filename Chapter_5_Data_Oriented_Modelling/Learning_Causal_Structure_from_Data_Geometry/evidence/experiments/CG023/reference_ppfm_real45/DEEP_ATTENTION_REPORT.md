# PPFM REAL45 Deep Context-Attention Probe

Same 45 real PPFM tasks, same task construction, same train/test episodes, two seeds (2101/2102), 450 updates, batch 192. Context order is semantically arbitrary because each token carries its own conditioning coordinate.

| Architecture | Attention depth | Parameter sharing | Params | Two-seed mean MSE | Change vs D1 | Permuted-context MSE |
|---|---:|---|---:|---:|---:|---:|
| D1 | 1 | no | 179,529 | 0.047951 | baseline | 0.047951 |
| D3 | 3 | no | 245,961 | 0.043167 | 9.98% lower | 0.043167 |
| D6 | 6 | no | 345,609 | 0.043102 | 10.11% lower | 0.043102 |
| TIED6 | 6 repeated applications | yes | 179,529 | 0.046460 | 3.11% lower | 0.046460 |

## Main observations

- Untied depth helps: D3 and D6 both beat D1 in both seeds. D3 wins 35/45 tasks; D6 wins 33/45.
- The largest robust step is D1 -> D3. D3 -> D6 is essentially flat in two-seed mean, with seed-specific divergence, suggesting an optimization/depth sweet spot rather than monotonic gains.
- TIED6 has exactly the same parameter count as D1 but a lower two-seed mean MSE (3.11% lower). The effect is modest and not seed-uniform, so this is a suggestive computational-depth signal, not yet a stable latent-CoT result.
- All attention variants remain permutation invariant to evidence-token order within numerical precision.

This probe uses the archived early 45-task real PPFM corpus rather than the current 220-task model. It supports testing a deep context-attention frontend in the current system; it does not by itself establish the optimal depth for the 220-task corpus.
