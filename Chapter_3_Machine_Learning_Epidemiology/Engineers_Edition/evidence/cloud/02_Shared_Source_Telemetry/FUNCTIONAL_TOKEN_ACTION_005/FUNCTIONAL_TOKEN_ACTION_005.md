# FUNCTIONAL-TOKEN-ACTION-005 — B / result crystallization-gate dissection

## Objective
Dissect the two crystallization gates identified in TRAINING-SKY-004 using the microscope line's separation of visible token identity, actual recurrent action, continuous carried state, local Jacobian geometry, and downstream response.

The GRU uses learned 6-D embeddings, so the actual token action is the embedding vector supplied to the recurrent transition. A standardized reference action is the model's mean vocabulary embedding; it is only a within-model reference and is not assigned semantic neutrality.

## Gates

- `B_gate`: k=4, visible token `B`
- `result_gate`: k=28, visible token `result`

## Baseline state geometry

| gate        | token   |   pre_hidden_pair_mean |   post_actual_hidden_pair_mean |   post_reference_hidden_pair_mean |   actual_hidden_multiplier |   reference_hidden_multiplier |   answer_propensity_std_actual |   answer_propensity_std_reference |
|:------------|:--------|-----------------------:|-------------------------------:|----------------------------------:|---------------------------:|------------------------------:|-------------------------------:|----------------------------------:|
| B_gate      | B       |              0.0871723 |                      0.0428193 |                         0.0473889 |                   0.491202 |                      0.543623 |                     0.00903737 |                         0.0227048 |
| result_gate | result  |              0.0287208 |                      0.0175186 |                         0.0134652 |                   0.609961 |                      0.46883  |                     0.00331846 |                         0.0027922 |

## Local Jacobian geometry

| gate        |   Jh_sigma1 |   Jh_fro |   Je_sigma1 |   Je_fro |   answer_state_gain |   answer_action_gain |
|:------------|------------:|---------:|------------:|---------:|--------------------:|---------------------:|
| B_gate      |    0.641415 | 0.922078 |    0.830064 | 1.00889  |            0.186586 |             0.205624 |
| result_gate |    1.13097  | 1.60924  |    0.499492 | 0.652721 |            0.39385  |             0.260479 |

## State × action interaction

| gate        |   mean_abs_state_action_interaction |   max_abs_state_action_interaction |   rms_state_action_interaction |   std_question_state_effect_actual_action |   std_question_state_effect_reference_action |
|:------------|------------------------------------:|-----------------------------------:|-------------------------------:|------------------------------------------:|---------------------------------------------:|
| B_gate      |                         0.0136673   |                        0.0139151   |                     0.0136688  |                                0.00903737 |                                    0.0227048 |
| result_gate |                         0.000524968 |                        0.000581264 |                     0.00052775 |                                0.00331846 |                                    0.0027922 |

## Action-path integral closure

| gate        |   mean_finite_answer_action |   mean_abs_finite_answer_action |   mean_hidden_action_norm |   max_abs_answer_closure |   max_hidden_closure |
|:------------|----------------------------:|--------------------------------:|--------------------------:|-------------------------:|---------------------:|
| B_gate      |                  -0.0345917 |                       0.0345917 |                  0.942892 |              3.8455e-07  |          1.83194e-07 |
| result_gate |                  -0.294012  |                       0.294012  |                  1.15341  |              4.74009e-07 |          1.41867e-07 |

## High-gain-band position

| gate        |   peak_alpha_mean |   peak_abs_gain_mean |   actual_gain_mean |   actual_to_peak_ratio_mean |
|:------------|------------------:|---------------------:|-------------------:|----------------------------:|
| B_gate      |            -1     |             0.798566 |          0.0366297 |                   0.0457733 |
| result_gate |             0.675 |             0.333301 |         -0.321692  |                   0.965166  |

## Training-sky code closure

| gate        |   max_error |    min_error |   max_abs_error |
|:------------|------------:|-------------:|----------------:|
| B_gate      | 1.43051e-06 | -8.34465e-07 |     1.43051e-06 |
| result_gate | 9.53674e-07 | -1.90735e-06 |     1.90735e-06 |

For the answer axis, the TRAINING-SKY-004 token code equals the history-induced change in the token's finite immediate answer action, up to float32 numerical error.

## Strongest code ↔ geometry relations

| gate        | target      | geometry_feature              |   pearson_r |
|:------------|:------------|:------------------------------|------------:|
| B_gate      | answer_code | delta_state_displacement_norm |    0.333369 |
| B_gate      | answer_code | delta_answer_state_gain       |   -0.268155 |
| B_gate      | answer_code | delta_Je_sigma1               |   -0.199153 |
| B_gate      | cot_code    | delta_state_displacement_norm |   -0.847646 |
| B_gate      | cot_code    | delta_answer_action_gain      |   -0.654419 |
| B_gate      | cot_code    | delta_answer_state_gain       |    0.639351 |
| result_gate | answer_code | delta_Je_fro                  |   -0.726565 |
| result_gate | answer_code | delta_Je_sigma1               |   -0.687623 |
| result_gate | answer_code | delta_state_displacement_norm |    0.431053 |
| result_gate | cot_code    | delta_Jh_sigma1               |   -0.669583 |
| result_gate | cot_code    | delta_Jh_fro                  |   -0.660294 |
| result_gate | cot_code    | delta_Je_fro                  |   -0.205941 |

## Historical carrier channels

| gate        | train_channel   |   cot_code_rms |   answer_code_rms |   delta_state_displacement_rms |   delta_Jh_sigma1_rms |   delta_Je_sigma1_rms |   delta_answer_action_gain_rms |
|:------------|:----------------|---------------:|------------------:|-------------------------------:|----------------------:|----------------------:|-------------------------------:|
| B_gate      | adam_m          |    6.87152e-07 |       2.04748e-05 |                    3.75102e-05 |           3.5347e-05  |           3.00039e-05 |                    8.67173e-06 |
| B_gate      | adam_v          |    6.69392e-07 |       1.12457e-05 |                    2.73966e-05 |           1.41592e-05 |           1.70496e-05 |                    4.44991e-06 |
| B_gate      | theta           |    1.75682e-07 |       1.29666e-06 |                    4.46254e-06 |           2.54755e-06 |           2.11392e-06 |                    1.12893e-06 |
| result_gate | adam_m          |    1.60234e-06 |       1.76218e-05 |                    9.71403e-06 |           1.21037e-05 |           9.85195e-06 |                    5.0558e-06  |
| result_gate | adam_v          |    6.2113e-07  |       6.45028e-06 |                    7.75603e-06 |           4.15926e-06 |           7.45105e-06 |                    6.79e-06    |
| result_gate | theta           |    2.53539e-07 |       1.19998e-06 |                    9.87493e-07 |           1.08485e-06 |           4.62956e-07 |                    7.33934e-07 |

## Working interpretation

`B` and `result` are two different kinds of crystallization gate. `B` is not located near the high-gain region of the tested action path and shows strong state×action interaction; its training-sky CoT code is tightly associated with changes in state-displacement geometry. `result` lies near a high-gain action band and its answer token code is strongly associated with changes in the token→state Jacobian. Crystallization therefore does not denote one fixed token mechanism.
