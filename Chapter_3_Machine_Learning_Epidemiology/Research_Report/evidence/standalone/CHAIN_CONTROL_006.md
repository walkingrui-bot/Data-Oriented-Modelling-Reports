# CHAIN_CONTROL_006

## Aim

Separate the visible identity of a chain token from its re-fed numerical action, continuous recurrent-state carry, and downstream answer control in the exact 10-parameter autoregressive RNN.

## Structural equation view

For Q=(A,B), the generated route label R and code label C are discrete readouts, while their causal feedback values x_R and x_C enter later recurrent transitions. The answer logit is a smooth control surface

Z_theta(x_R,x_C|Q)=v^T F_theta(F_theta(F_theta(F_theta(h_R,x_R),M_CODE),x_C),M_ANS),

with h_R obtained from Q followed by the route marker. Normal autoregression chooses R=H(z_R), feeds x_R=BIT[R], then chooses C=H(z_C), feeds x_C=BIT[C], and finally emits Y=H(Z_theta).

## Selected case

Seed 14, Q=(0,0); history A generates chain (1, 0), history B generates chain (0, 0); both hard answers are 0.

### Visible identity versus feedback action

| model     | condition                                | visible_route   | visible_code   |   route_action |   code_action |   answer_logit |   answer_p1 |   answer_pred |   delta_logit_vs_normal |
|:----------|:-----------------------------------------|:----------------|:---------------|---------------:|--------------:|---------------:|------------:|--------------:|------------------------:|
| history_A | normal                                   | 1               | 0              |              1 |            -1 |      -0.237086 |    0.441005 |             0 |               0         |
| history_A | silent_surface_same_action               | ∅               | ∅              |              1 |            -1 |      -0.237086 |    0.441005 |             0 |               0         |
| history_A | renamed_surface_same_action              | 0               | 1              |              1 |            -1 |      -0.237086 |    0.441005 |             0 |               0         |
| history_A | same_surface_neutral_action              | 1               | 0              |              0 |             0 |       1.5338   |    0.822561 |             1 |               1.77089   |
| history_A | same_surface_opposite_action             | 1               | 0              |             -1 |             1 |       1.56117  |    0.826521 |             1 |               1.79826   |
| history_A | renamed_surface_matching_opposite_action | 0               | 1              |             -1 |             1 |       1.56117  |    0.826521 |             1 |               1.79826   |
| history_B | normal                                   | 0               | 0              |             -1 |            -1 |      -1.47956  |    0.185494 |             0 |               0         |
| history_B | silent_surface_same_action               | ∅               | ∅              |             -1 |            -1 |      -1.47956  |    0.185494 |             0 |               0         |
| history_B | renamed_surface_same_action              | 1               | 1              |             -1 |            -1 |      -1.47956  |    0.185494 |             0 |               0         |
| history_B | same_surface_neutral_action              | 0               | 0              |              0 |             0 |      -1.51123  |    0.180757 |             0 |              -0.0316647 |
| history_B | same_surface_opposite_action             | 0               | 0              |              1 |             1 |      -1.52267  |    0.179069 |             0 |              -0.0431036 |
| history_B | renamed_surface_matching_opposite_action | 1               | 1              |              1 |             1 |      -1.52267  |    0.179069 |             0 |              -0.0431036 |

Renaming or suppressing the visible token label while preserving the numerical feedback action changes the answer logit by at most 0.000e+00 in the all-question audit. Holding the visible label fixed while neutralizing or reversing its feedback value changes the recurrent computation and can change the hard answer.

### All-question audit

| model     |   A |   B |   natural_r |   natural_c |   natural_answer |   natural_logit |   renamed_surface_same_action_logit |   renamed_surface_invariance_error |   neutral_feedback_answer |   neutral_feedback_logit |   neutral_feedback_hard_flip |   opposite_feedback_answer |   opposite_feedback_logit |   opposite_feedback_hard_flip |
|:----------|----:|----:|------------:|------------:|-----------------:|----------------:|------------------------------------:|-----------------------------------:|--------------------------:|-------------------------:|-----------------------------:|---------------------------:|--------------------------:|------------------------------:|
| history_A |   0 |   0 |           1 |           0 |                0 |       -0.237086 |                           -0.237086 |                                  0 |                         1 |                  1.5338  |                            1 |                          1 |                   1.56117 |                             1 |
| history_A |   0 |   1 |           0 |           0 |                0 |       -1.21679  |                           -1.21679  |                                  0 |                         0 |                 -1.28388 |                            0 |                          0 |                  -1.30701 |                             0 |
| history_A |   1 |   0 |           1 |           1 |                1 |        1.58051  |                            1.58051  |                                  0 |                         1 |                  1.63929 |                            0 |                          1 |                   1.65318 |                             0 |
| history_A |   1 |   1 |           1 |           1 |                1 |        1.56054  |                            1.56054  |                                  0 |                         1 |                  1.63831 |                            0 |                          1 |                   1.65307 |                             0 |
| history_B |   0 |   0 |           0 |           0 |                0 |       -1.47956  |                           -1.47956  |                                  0 |                         0 |                 -1.51123 |                            0 |                          0 |                  -1.52267 |                             0 |
| history_B |   0 |   1 |           0 |           0 |                0 |       -1.49975  |                           -1.49975  |                                  0 |                         0 |                 -1.51607 |                            0 |                          0 |                  -1.5243  |                             0 |
| history_B |   1 |   0 |           1 |           1 |                1 |        1.51416  |                            1.51416  |                                  0 |                         1 |                  1.52647 |                            0 |                          1 |                   1.5326  |                             0 |
| history_B |   1 |   1 |           1 |           1 |                1 |        1.4383   |                            1.4383   |                                  0 |                         1 |                  1.51397 |                            0 |                          1 |                   1.52905 |                             0 |

## Downstream regeneration after route-feedback intervention

| model     | condition      |   visible_route |   actual_route_action |   regenerated_code |   code_logit |   answer_logit |   answer_pred |   code_changed |   answer_changed |
|:----------|:---------------|----------------:|----------------------:|-------------------:|-------------:|---------------:|--------------:|---------------:|-----------------:|
| history_A | normal         |               1 |                     1 |                  0 |    -0.509347 |      -0.237086 |             0 |              0 |                0 |
| history_A | route_neutral  |               1 |                     0 |                  1 |     0.867209 |       1.15218  |             1 |              1 |                1 |
| history_A | route_opposite |               1 |                    -1 |                  1 |     1.43615  |       1.56117  |             1 |              1 |                1 |
| history_B | normal         |               0 |                    -1 |                  0 |    -1.33478  |      -1.47956  |             0 |              0 |                0 |
| history_B | route_neutral  |               0 |                     0 |                  0 |    -1.44444  |      -1.49277  |             0 |              0 |                0 |
| history_B | route_opposite |               0 |                     1 |                  0 |    -1.49483  |      -1.49757  |             0 |              0 |                0 |

This intervention keeps the emitted route label fixed but changes the value re-entered into the network, then lets the code token regenerate from the modified state.

## Continuous state and discrete feedback are separable channels

| model     |   carry_state |   discrete_feedback |   route_label |   code_label |   answer_logit |   answer_p1 |   answer_pred |
|:----------|--------------:|--------------------:|--------------:|-------------:|---------------:|------------:|--------------:|
| history_A |             0 |                   0 |             1 |            0 |    -0.00781748 |    0.498046 |             0 |
| history_A |             0 |                   1 |             1 |            0 |     1.14171    |    0.757993 |             1 |
| history_A |             1 |                   0 |             1 |            0 |     1.5338     |    0.822561 |             1 |
| history_A |             1 |                   1 |             1 |            0 |    -0.237086   |    0.441005 |             0 |
| history_B |             0 |                   0 |             0 |            0 |     0.330435   |    0.581865 |             1 |
| history_B |             0 |                   1 |             0 |            0 |     0.931818   |    0.717444 |             1 |
| history_B |             1 |                   0 |             0 |            0 |    -1.51123    |    0.180757 |             0 |
| history_B |             1 |                   1 |             0 |            0 |    -1.47956    |    0.185494 |             0 |

| model     |      full |   state_carry_neutral_feedback |   reset_state_with_feedback |   reset_state_neutral_feedback |   carry_x_feedback_interaction |
|:----------|----------:|-------------------------------:|----------------------------:|-------------------------------:|-------------------------------:|
| history_A | -0.237086 |                        1.5338  |                    1.14171  |                    -0.00781748 |                      -2.92041  |
| history_B | -1.47956  |                       -1.51123 |                    0.931818 |                     0.330435   |                      -0.569718 |

Boundary-specific ablations:

| model     | condition                   |   answer_logit |   answer_pred |   delta_logit_vs_full |
|:----------|:----------------------------|---------------:|--------------:|----------------------:|
| history_A | full                        |      -0.237086 |             0 |             0         |
| history_A | neutralize_route_feedback   |       1.6226   |             1 |             1.85969   |
| history_A | neutralize_code_feedback    |      -0.973107 |             0 |            -0.736021  |
| history_A | neutralize_both_feedback    |       1.5338   |             1 |             1.77089   |
| history_A | reset_before_route_feedback |      -1.16922  |             0 |            -0.932136  |
| history_A | reset_before_code_feedback  |       1.14171  |             1 |             1.3788    |
| history_A | reset_both_boundaries       |       1.14171  |             1 |             1.3788    |
| history_B | full                        |      -1.47956  |             0 |             0         |
| history_B | neutralize_route_feedback   |      -1.49277  |             0 |            -0.0132126 |
| history_B | neutralize_code_feedback    |      -1.50383  |             0 |            -0.0242666 |
| history_B | neutralize_both_feedback    |      -1.51123  |             0 |            -0.0316647 |
| history_B | reset_before_route_feedback |       1.47406  |             1 |             2.95363   |
| history_B | reset_before_code_feedback  |       0.931818 |             1 |             2.41138   |
| history_B | reset_both_boundaries       |       0.931818 |             1 |             2.41138   |

## Continuous chain-control surface

Across the sampled (x_R,x_C) control plane, the two trained histories disagree on the hard answer over 75.40% of grid points. The relative Frobenius difference between their answer-logit surfaces is 1.7116.

### Decision thresholds

| model     | surface                        | held       |   roots_in_range |
|:----------|:-------------------------------|:-----------|-----------------:|
| history_A | code_logit_vs_route_feedback   | none       |         0.628539 |
| history_A | answer_logit_vs_route_feedback | x_code=-1  |         0.935237 |
| history_A | answer_logit_vs_route_feedback | x_code=+1  |         0.358182 |
| history_A | answer_logit_vs_code_feedback  | x_route=-1 |                  |
| history_A | answer_logit_vs_code_feedback  | x_route=+1 |        -1.18635  |
| history_B | code_logit_vs_route_feedback   | none       |                  |
| history_B | answer_logit_vs_route_feedback | x_code=-1  |                  |
| history_B | answer_logit_vs_route_feedback | x_code=+1  |                  |
| history_B | answer_logit_vs_code_feedback  | x_route=-1 |                  |
| history_B | answer_logit_vs_code_feedback  | x_route=+1 |                  |

## Finite token control equals integrated local gain

For a fixed held coordinate, a discrete feedback change from -1 to +1 is exactly the line integral of the local derivative along that feedback coordinate:

Z(+1,c)-Z(-1,c)=integral_{-1}^{+1} partial Z(x,c)/partial x dx.

| model     | control        | held     |   finite_logit_effect |   integrated_local_gain |   closure_error |
|:----------|:---------------|:---------|----------------------:|------------------------:|----------------:|
| history_A | route_-1_to_+1 | code=-1  |           -1.88731    |             -1.88731    |     3.9968e-15  |
| history_A | route_-1_to_+1 | code=+1  |           -2.74448    |             -2.74448    |    -7.99361e-15 |
| history_A | code_-1_to_+1  | route=-1 |           -0.0890506  |             -0.0890506  |     2.08167e-16 |
| history_A | code_-1_to_+1  | route=+1 |           -0.946224   |             -0.946224   |     2.44249e-15 |
| history_B | route_-1_to_+1 | code=-1  |           -0.0180037  |             -0.0180037  |     9.02056e-17 |
| history_B | route_-1_to_+1 | code=+1  |           -0.00632792 |             -0.00632792 |    -1.73472e-18 |
| history_B | code_-1_to_+1  | route=-1 |           -0.0367757  |             -0.0367757  |     1.8735e-16  |
| history_B | code_-1_to_+1  | route=+1 |           -0.0251     |             -0.0251     |     9.02056e-17 |

Maximum numerical closure error: 7.994e-15.

## Mirror-case replication

|   seed | model     |   A |   B | generated_chain   |   normal_logit |   route_action_opposite_logit |   route_action_opposite_effect |   route_action_neutral_logit |   route_action_neutral_effect |
|-------:|:----------|----:|----:|:------------------|---------------:|------------------------------:|-------------------------------:|-----------------------------:|------------------------------:|
|     14 | history_A |   0 |   0 | (1, 0)            |      -0.237086 |                       1.65022 |                     1.88731    |                      1.6226  |                    1.85969    |
|     14 | history_B |   0 |   0 | (0, 0)            |      -1.47956  |                      -1.49757 |                    -0.0180037  |                     -1.49277 |                   -0.0132126  |
|     25 | history_A |   0 |   0 | (0, 0)            |      -1.35955  |                      -1.36642 |                    -0.00687301 |                     -1.36556 |                   -0.00600547 |
|     25 | history_B |   0 |   0 | (1, 0)            |      -0.264824 |                       1.12948 |                     1.3943     |                      1.09528 |                    1.3601     |

## Evidence-supported interpretation

In this controlled autoregressive system, a chain token has at least three distinguishable objects: an externally visible label, a numerical feedback action applied to the recurrent dynamics, and a continuous hidden state carried across the token boundary. The visible label alone is absent from the state equation; relabeling it while preserving the re-fed numerical action leaves the answer unchanged. Changing the feedback action while preserving the displayed label changes the control point on Z_theta(x_R,x_C|Q), and the same action coordinate can have very different gain and decision geometry after different training histories. The self-generated CoT therefore selects discrete points on a model-dependent continuous control surface.


## Regenerated-chain route-control sweep

The route feedback coordinate was varied continuously while the route label was held conceptually fixed; the code token was then regenerated from the modified recurrent state and fed normally into the answer stage. This exposes whether the first chain token controls later chain construction, not only a fixed answer readout.

| model     | observable       | switch_locations           |   n_switches |
|:----------|:-----------------|:---------------------------|-------------:|
| history_A | regenerated_code | 0.628750                   |            1 |
| history_A | answer_pred      | 0.358750;0.628750;0.936250 |            3 |
| history_B | regenerated_code |                            |            0 |
| history_B | answer_pred      |                            |            0 |

