# CHAIN_ANSWER_DECOMP_005

## Aim

Separate causes of generated chain differences from causes of final-answer differences in an exactly 10-parameter recurrent network.

## Network and training histories

- Exactly 10 trainable parameters: W(2x2), u(2), b(2), v(2). Fixed scalar token encodings.
- Question Q=(A,B), target endpoint y=A.
- Each Q has two teacher-forced chain codings: route r in {0,1}, code c=A xor r, endpoint y=c xor r=A.
- Same initialization, same eight records per epoch, same optimizer, learning rate, epochs and update count.
- History A orders each pair r0 then r1; history B orders the same pair r1 then r0.
- Seed=14, lr=0.01, epochs=60, answer loss weight=3.0.

## Endpoint and generated-chain observation

|   A |   B |   gold_y |   A_r |   A_c |   A_y |   B_r |   B_c |   B_y |   A_route_p1 |   B_route_p1 |   A_code_p1_generated_branch |   B_code_p1_generated_branch |   A_answer_p1_generated_branch |   B_answer_p1_generated_branch | chain_equal   | answer_equal   |
|----:|----:|---------:|------:|------:|------:|------:|------:|------:|-------------:|-------------:|-----------------------------:|-----------------------------:|-------------------------------:|-------------------------------:|:--------------|:---------------|
|   0 |   0 |        0 |     1 |     0 |     0 |     0 |     0 |     0 |     0.611795 |     0.311109 |                     0.375347 |                     0.208369 |                       0.441005 |                       0.185494 | False         | True           |
|   0 |   1 |        0 |     0 |     0 |     0 |     0 |     0 |     0 |     0.227635 |     0.202954 |                     0.199206 |                     0.179881 |                       0.228502 |                       0.182462 | True          | True           |
|   1 |   0 |        1 |     1 |     1 |     1 |     1 |     1 |     1 |     0.833936 |     0.781234 |                     0.820719 |                     0.812123 |                       0.829277 |                       0.819677 | True          | True           |
|   1 |   1 |        1 |     1 |     1 |     1 |     1 |     1 |     1 |     0.790019 |     0.618879 |                     0.806428 |                     0.723198 |                       0.826431 |                       0.808191 | True          | True           |

Both histories produce the correct hard endpoint vector `0011`. The selected chain-only case is Q=(0,0): history A generates chain (1, 0), history B generates chain (0, 0), and both generate endpoint y=0.

Observed equality of final answers is only equality under the final hard-label observation; the parameter states and generated paths remain distinct.

## Autoregressive factorization

For this two-token chain, the model defines

P_theta(r,c,y|Q) = P_theta(r|Q) P_theta(c|Q,r) P_theta(y|Q,r,c).

The generated chain is therefore both an output and a re-entered input: changing r or c changes the future recurrent state before the answer is emitted.

## Model x chain cross-feed

| model     | forced_chain   |   r |   c |   answer_logit |   answer_p1 |   answer_pred |
|:----------|:---------------|----:|----:|---------------:|------------:|--------------:|
| history_A | chain_A        |   1 |   0 |      -0.237086 |    0.441005 |             0 |
| history_A | chain_B        |   0 |   0 |       1.65022  |    0.838921 |             1 |
| history_B | chain_A        |   1 |   0 |      -1.49757  |    0.182789 |             0 |
| history_B | chain_B        |   0 |   0 |      -1.47956  |    0.185494 |             0 |

### Exact logit decomposition

| quantity                                   |      value | definition                              |
|:-------------------------------------------|-----------:|:----------------------------------------|
| total_generated_logit_difference_A_minus_B |  1.24248   | z_A(C_A)-z_B(C_B)                       |
| direct_parameter_effect_holding_chain_B    |  3.12978   | z_A(C_B)-z_B(C_B)                       |
| chain_effect_within_model_A                | -1.88731   | z_A(C_A)-z_A(C_B)                       |
| direct_parameter_effect_holding_chain_A    |  1.26048   | z_A(C_A)-z_B(C_A)                       |
| chain_effect_within_model_B                | -0.0180037 | z_B(C_A)-z_B(C_B)                       |
| model_x_chain_interaction                  | -1.8693    | [z_A(C_A)-z_A(C_B)]-[z_B(C_A)-z_B(C_B)] |

The total generated-answer logit difference admits two exact reference decompositions: direct parameter effect with one chain held fixed plus within-model chain effect. Their difference is the model-by-chain interaction.

## Discrete chain interventions on the answer

| model     | intervention   | held_token   |   answer_logit_effect |
|:----------|:---------------|:-------------|----------------------:|
| history_A | route_0_to_1   | c=0          |           -1.88731    |
| history_A | route_0_to_1   | c=1          |           -2.74448    |
| history_A | code_0_to_1    | r=0          |           -0.0890506  |
| history_A | code_0_to_1    | r=1          |           -0.946224   |
| history_B | route_0_to_1   | c=0          |           -0.0180037  |
| history_B | route_0_to_1   | c=1          |           -0.00632792 |
| history_B | code_0_to_1    | r=0          |           -0.0367757  |
| history_B | code_0_to_1    | r=1          |           -0.0251     |

## History-to-function parameter decomposition

For any smooth functional f(theta), the finite difference between the two trained models is exactly the line integral

f(theta_A)-f(theta_B) = integral_0^1 grad_theta f(theta_B+s Delta theta)^T Delta theta ds.

Gauss-Legendre integration was used to split this finite difference across the ten parameters.

| function     |   actual_logit_A_minus_B |   integrated_gradient_sum |   closure_error |   jacobian_norm_lineavg |   delta_theta_projection |
|:-------------|-------------------------:|--------------------------:|----------------:|------------------------:|-------------------------:|
| route        |                 1.24981  |                  1.24981  |    -8.88178e-16 |                 3.36661 |                 1.24981  |
| code_r0      |                 2.77093  |                  2.77093  |     3.10862e-15 |                 6.35315 |                 2.77093  |
| code_r1      |                 0.98548  |                  0.98548  |     1.11022e-16 |                 3.92259 |                 0.98548  |
| answer_r0_c0 |                 3.12978  |                  3.12978  |    -2.58448e-09 |                 6.62728 |                 3.12978  |
| answer_r0_c1 |                 3.07751  |                  3.07751  |     3.42061e-10 |                 7.35113 |                 3.07751  |
| answer_r1_c0 |                 1.26048  |                  1.26048  |    -2.44249e-15 |                 3.80989 |                 1.26048  |
| answer_r1_c1 |                 0.339355 |                  0.339355 |    -5.55112e-17 |                 1.5142  |                 0.339355 |

Top route-logit parameter contributions:

| parameter   |   finite_difference_contribution |
|:------------|---------------------------------:|
| b2          |                        1.2713    |
| b1          |                        0.432465  |
| u2          |                       -0.392219  |
| u1          |                       -0.0960176 |
| W22         |                        0.0254753 |

Top answer-logit contributions for forced chain (0, 0):

| parameter   |   finite_difference_contribution |
|:------------|---------------------------------:|
| b2          |                         2.73827  |
| b1          |                         0.741303 |
| u2          |                        -0.392279 |
| u1          |                        -0.093261 |
| W22         |                         0.084749 |

## Observational visibility

| observable                 |   jacobian_rank |   J_delta_theta_L2 |   delta_theta_rowspace_fraction |   delta_theta_nullspace_fraction |   top_singular_value |
|:---------------------------|----------------:|-------------------:|--------------------------------:|---------------------------------:|---------------------:|
| route_logits_4Q            |               4 |            1.50426 |                        0.856978 |                         0.515353 |              3.79906 |
| canonical_answer_logits_4Q |               4 |           10.9356  |                        0.782332 |                         0.622861 |             23.6191  |

This measures how strongly the same trained parameter-history difference Delta theta is visible to a chain readout versus a canonical fixed-chain answer readout.

## Evidence-supported interpretation

In this controlled case, training order changes the generated chain while preserving the correct hard answer vector. The autoregressive chain is mathematically a mediator that is emitted, discretized, and fed back into the recurrent dynamics. Cross-feeding separates changes in chain generation from changes in how a fixed chain is interpreted. The parameter line integral then attributes both kinds of functional differences back to the same finite trained parameter displacement.


## Replication scan: 100 initializations

The exact hyperparameters were held fixed (lr=0.01, 60 epochs, answer-loss weight 3); only the common initialization seed was varied from 1 to 100.

- 4/100 seeds produced the strict correct and identical endpoint vector `0011` in both training histories.
- 2/4 of those strict-endpoint seeds also produced at least one different self-generated chain.
- In both chain-difference cases, cross-feeding the alternative chain caused a hard answer flip in exactly one of the two models, while the other model was insensitive at the hard-label level.
- The two cases were mirror-like: seed 14 had strong chain control in history A; seed 25 had strong chain control in history B.

These counts are descriptive for this fixed tiny architecture and hyperparameter setting. They establish a reproduced causal pattern within the scan rather than a population frequency estimate.

## Four causal components exposed by the cross-feed design

For two trained parameter states theta_A and theta_B with self-generated chains C_A and C_B, the observed answer difference can be separated into four experimentally addressable objects:

1. **Chain-generation effect:** the histories change `P(C|Q)`. In the selected case, the route probability crosses the greedy threshold: P_A(r=1|Q)=0.612 versus P_B(r=1|Q)=0.311.
2. **Fixed-chain model effect:** holding the chain fixed, `P(Y|Q,C,theta)` differs across parameter histories. With chain B fixed, the answer-logit difference is +3.130.
3. **Within-model chain effect:** holding the model fixed, intervening on the generated chain changes the answer. In history A, replacing chain B by chain A changes the answer logit by -1.887 and changes the hard answer from 1 to 0.
4. **Model-by-chain interaction:** the same chain intervention has different causal strength in the two trained models. The interaction is -1.869 logit units; history B has only -0.018 logit units of route-chain effect for the corresponding intervention.

Thus identical endpoint answers can be produced by different causal organizations. In the selected case, history A uses its generated route token as a compensatory control signal: under chain B it would answer 1, whereas its own generated chain moves the logit back to the correct side of the boundary. History B produces the same endpoint with little dependence on that route token.

## CoT as a hybrid dynamical mediator

In this autoregressive toy system, a chain token has a dual mathematical role. It is first an output selected from the current state, then it is converted back to a token encoding and injected into the next recurrent transition. With greedy decoding,

`r = H(z_r(theta,Q))`, followed by `h_next = F_theta(h, x(r))`.

The Heaviside decision `H` makes the end-to-end map piecewise smooth. A continuous training-history displacement in parameter space can move a chain logit across zero; the discrete token change then creates a finite state intervention on the next step. This gives a concrete mechanism by which small continuous historical differences can become large downstream chain differences.

For seed 14, at the self-generated history-A branch `(r=1,c=0)`, the local answer sensitivity to the re-fed route-token encoding is `dz_answer/dx_route = -3.350`; for history B at the same forced branch it is only `-0.003`. The same symbolic route token therefore acts as a high-gain control coordinate in one trained system and an almost inert coordinate in the other.

## Working interpretation for the larger programme

The evidence from this case supports treating CoT as a model-dependent causal mediator rather than only as a textual explanation. The token sequence is generated by the current parameter state, discretized, and re-entered as future input. Its causal role therefore depends jointly on (i) how training history shapes the probability of emitting each token and (ii) how the same trained history shapes the downstream transition induced by that token.
