# PROMPT–CoT–ANSWER CONTROL FIELD 007

## Goal
Expand every visible token from the question/prompt through CoT to the final answer into explicit recurrent state, token-code, transfer, control-axis, and control-of-control mathematics. The central hypothesis tested is whether a single mathematical control axis is reused through the sequence by rotation/re-alignment.

## Exact token-level dynamics

For visible token code e_t and recurrent state h_t:

h_t = F_theta(h_{t-1}, e_t)

A_t = dh_t/dh_{t-1},   B_t = dh_t/de_t

For any earlier token s and later state t>=s:

dh_t/de_s = A_t A_{t-1} ... A_{s+1} B_s

For final answer propensity z = logit(1)-logit(0), define lambda_T = dz/dh_T. Then:

lambda_{t-1} = A_t^T lambda_t

g_t = dz/de_t = B_t^T lambda_t

This recursion reproduces direct autograd token gradients with the following closure:

|   q |   bits |   final_answer_propensity |   direct_answer_propensity |   max_token_gradient_closure_error |
|----:|-------:|--------------------------:|---------------------------:|-----------------------------------:|
|   0 |   0000 |                  0.148968 |                   0.148968 |                        1.21471e-08 |
|   1 |   1100 |                  0.148968 |                   0.148968 |                        1.21471e-08 |
|   2 |   0001 |                  0.291342 |                   0.291342 |                        1.10469e-08 |
|   3 |   1110 |                  0.291342 |                   0.291341 |                        1.09836e-08 |
|   4 |   0100 |                  0.291385 |                   0.291385 |                        2.80466e-08 |
|   5 |   1011 |                  0.291385 |                   0.291385 |                        1.65371e-08 |
|   6 |   0110 |                  0.14892  |                   0.14892  |                        8.80333e-09 |
|   7 |   1001 |                  0.14892  |                   0.14892  |                        1.41629e-08 |

## Full-future local control field

To avoid treating prompt tokens as irrelevant merely because a long teacher-forced continuation washes out their direct final-answer gradient, define R_t as all future hidden states plus final answer propensity. J_t = dR_t/de_t. The top right singular vector V_t of J_t is the locally strongest token-code direction for changing the future trajectory.

| phase   |   future_sigma1_mean |   mode1_energy_mean |   top2_cumulative_mean |   rotation_mean_deg |   action_proj1_mean |   action_top2_mean |
|:--------|---------------------:|--------------------:|-----------------------:|--------------------:|--------------------:|-------------------:|
| ANSWER  |             0.661094 |            0.6004   |               0.843261 |             28.3372 |            0.290583 |           0.388303 |
| COT     |             0.780973 |            0.604445 |               0.850619 |             49.2979 |            0.425866 |           0.605259 |
| PROMPT  |             1.08214  |            0.674129 |               0.857635 |             62.8096 |            0.333868 |           0.483317 |

## Static-axis hypothesis

The moving local axis is not representable by one fixed embedding direction. Mean spectra across eight questions:

| axis_object                |   mode1_mean_energy |   top2_mean_cumulative |   top3_mean_cumulative |
|:---------------------------|--------------------:|-----------------------:|-----------------------:|
| final_answer_gradient_g_t  |            0.392935 |               0.663255 |               0.83557  |
| future_trajectory_top1_V_t |            0.560817 |               0.818268 |               0.938404 |

## Phase-to-phase transfer

| source_phase   | target_phase   |   mean_transfer_fro |   median_transfer_fro |   max_transfer_fro |    n |
|:---------------|:---------------|--------------------:|----------------------:|-------------------:|-----:|
| ANSWER         | ANSWER         |         0.642274    |           0.751065    |        0.920785    |   24 |
| COT            | ANSWER         |         0.0116916   |           1.18825e-07 |        0.366018    |  496 |
| COT            | COT            |         0.0922783   |           0.000169772 |        1.84929     | 3968 |
| PROMPT         | ANSWER         |         2.88726e-15 |           2.77807e-16 |        5.72348e-14 |  176 |
| PROMPT         | COT            |         0.00255053  |           8.41785e-10 |        0.375773    | 2728 |
| PROMPT         | PROMPT         |         0.329119    |           0.0766617   |        2.03467     |  528 |

Prompt→final-answer direct transfer is tiny on this fixed long teacher-forced trajectory, while Prompt→CoT transfer remains nonzero. This distinguishes early-state shaping from direct late answer control in this specific GRU trajectory.

## Adjacent control-of-control

For adjacent token actions, define:

M_t = d/de_t (dz/de_{t+1}) = d²z/(de_t de_{t+1}).

Its top singular mode identifies the current token direction that most changes the next token's answer-control vector, and the next-token control direction most affected.

| phase   |   meta_sigma1 |   meta_mode1_energy |   current_action_steer_alignment |
|:--------|--------------:|--------------------:|---------------------------------:|
| ANSWER  |   0.0756385   |           0.924772  |                        0.0756051 |
| COT     |   0.000971293 |           0.788985  |                        0.409522  |
| PROMPT  |   1.16909e-16 |           0.0371462 |                        0.335501  |

## Working result

There is one local answer-control vector g_t at each token position, but not one globally fixed control axis. The axis rotates through a low-dimensional embedding-space field. For the broader future-trajectory axis, one static basis direction explains about 56% of moving-axis energy, two about 82%, and three about 94%. Thus the observed prompt→CoT→answer dynamics are better represented as a low-dimensional rotating control frame than as one immutable axis. Token codes participate by (i) shaping state through B_t, (ii) propagating their effects through ordered A_t products, (iii) aligning or misaligning with the current local control direction, and (iv) through mixed second derivatives, altering the control available to the next token.
