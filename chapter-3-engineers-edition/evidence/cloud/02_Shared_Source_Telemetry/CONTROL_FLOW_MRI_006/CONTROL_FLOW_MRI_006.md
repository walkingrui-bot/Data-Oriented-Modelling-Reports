# CONTROL-FLOW-MRI-006 — Dynamic control-subspace flow along CoT

## Question
Does the locally effective token-control direction remain fixed, or rotate as the realized CoT advances? Do sparse training-history perturbations mainly change control gain or control direction?

## Local future-response map
At each CoT position k, the actual token embedding is treated as the local action. The future response concatenates every subsequent canonical hidden state after that action plus the final answer propensity. J_k = dR_future/de_k is computed by six exact JVP basis probes; its right singular vectors are local embedding-space control modes.

## Exact readable space

The stacked GRU input map has shape (30, 6), numerical rank 6/6, and exact nullity 0. The chosen full future-response Jacobian has functional rank 6–6 across observed positions/questions. Thus this model has no exact fixed silent embedding dimension under this readout, although its control spectrum is often strongly concentrated.

## Overall flow

|   embedding_dim |   stacked_input_rank |   exact_input_nullity |   future_J_functional_rank_min |   future_J_functional_rank_max |   mean_mode1_energy |   mean_mode2_cumulative |   mean_stable_rank |   mean_adjacent_top1_rotation_deg |   median_adjacent_top1_rotation_deg |   max_adjacent_top1_rotation_deg |
|----------------:|---------------------:|----------------------:|-------------------------------:|-------------------------------:|--------------------:|------------------------:|-------------------:|----------------------------------:|------------------------------------:|---------------------------------:|
|               6 |                    6 |                     0 |                              6 |                              6 |            0.604199 |                0.850173 |            1.73284 |                           48.1299 |                             51.9051 |                          82.7989 |

## B vs result

| gate        |   k | token   |   sigma1_mean |   mode1_energy_mean |   stable_rank_mean |   action_projection_v1_mean |   action_projection_top2_mean |   top1_rotation_from_prev_mean_deg |   top2_rotation_from_prev_mean_deg |
|:------------|----:|:--------|--------------:|--------------------:|-------------------:|----------------------------:|------------------------------:|-----------------------------------:|-----------------------------------:|
| B_gate      |   4 | B       |      1.04909  |            0.755923 |            1.32301 |                    0.100392 |                      0.124379 |                            31.6051 |                            50.8567 |
| result_gate |  28 | result  |      0.525068 |            0.538226 |            1.85797 |                    0.665709 |                      0.671989 |                            56.8657 |                            42.3373 |

## Strongest runtime control-frame rotations

|   k |   sigma1_mean |   mode1_energy_mean |   mode2_cumulative_mean |   stable_rank_mean |   functional_rank_min |   functional_rank_max |   action_projection_v1_mean |   action_projection_top2_mean |   top1_rotation_mean_deg |   top1_rotation_max_deg |   top2_rotation_mean_deg | token   |
|----:|--------------:|--------------------:|------------------------:|-------------------:|----------------------:|----------------------:|----------------------------:|------------------------------:|-------------------------:|------------------------:|-------------------------:|:--------|
|  13 |      0.828822 |            0.739803 |                0.932214 |            1.35444 |                     6 |                     6 |                    0.660637 |                      0.709838 |                  79.2549 |                 82.7989 |                  74.9573 | 0/1     |
|   5 |      1.08694  |            0.819344 |                0.96247  |            1.22068 |                     6 |                     6 |                    0.674731 |                      0.763852 |                  75.5309 |                 78.4975 |                  57.5931 | 0/1     |
|  24 |      1.00526  |            0.525767 |                0.788761 |            1.90281 |                     6 |                     6 |                    0.17143  |                      0.211382 |                  74.9053 |                 77.035  |                  66.304  | xor     |
|   8 |      0.555578 |            0.534023 |                0.932362 |            1.87258 |                     6 |                     6 |                    0.716446 |                      0.741123 |                  74.5041 |                 75.4055 |                  74.368  | result  |
|  16 |      0.952778 |            0.803796 |                0.939027 |            1.24411 |                     6 |                     6 |                    0.644721 |                      0.714794 |                  74.4288 |                 77.6146 |                  60.1185 | 0/1     |
|  12 |      1.08832  |            0.649364 |                0.866002 |            1.54004 |                     6 |                     6 |                    0.352757 |                      0.354017 |                  71.0438 |                 71.635  |                  74.5759 | C       |
|   7 |      0.812539 |            0.867513 |                0.933087 |            1.15272 |                     6 |                     6 |                    0.594003 |                      0.909263 |                  70.0235 |                 72.0592 |                  77.5451 | first   |
|  20 |      0.861635 |            0.735213 |                0.906598 |            1.36247 |                     6 |                     6 |                    0.685181 |                      0.745665 |                  67.6462 |                 73.9092 |                  71.3923 | 0/1     |
|  25 |      0.716523 |            0.817753 |                0.937143 |            1.22627 |                     6 |                     6 |                    0.699265 |                      0.732363 |                  66.352  |                 77.5519 |                  65.3656 | 0/1     |
|   9 |      0.776884 |            0.695602 |                0.873923 |            1.4416  |                     6 |                     6 |                    0.674872 |                      0.7442   |                  65.9673 |                 74.9151 |                  69.9484 | 0/1     |
|   2 |      0.663381 |            0.636196 |                0.833469 |            1.57407 |                     6 |                     6 |                    0.638522 |                      0.735259 |                  62.7497 |                 67.5044 |                  71.7516 | 0/1     |
|  18 |      0.343285 |            0.490022 |                0.895717 |            2.04097 |                     6 |                     6 |                    0.3828   |                      0.425247 |                  60.1447 |                 60.9429 |                  88.8849 | second  |

## Natural-scale history perturbations at the two gates

|   k | token   |   mean_top1_direction_change_deg |   max_top1_direction_change_deg |   mean_top2_subspace_change_deg |   mean_abs_sigma1_relative_change |   mean_abs_action_projection_change |
|----:|:--------|---------------------------------:|--------------------------------:|--------------------------------:|----------------------------------:|------------------------------------:|
|   4 | B       |                       0.00191575 |                      0.0110292  |                      0.00423208 |                       2.15737e-05 |                         8.14526e-06 |
|  28 | result  |                       0.00176434 |                      0.00856903 |                      0.002552   |                       1.23479e-05 |                         7.97112e-06 |

## History-amplitude diagnostic
λ=1 is the actual sparse history perturbation. |λ|>1 extrapolates along the realized final parameter-history displacement only as a geometric magnifier; it is not interpreted as a naturally occurring training intervention.

| gate        |   lambda |   parameter_distance |   mean_top1_angle_deg |   max_top1_angle_deg |   mean_top2_angle_deg |   mean_abs_sigma1_relative_change |   mean_action_projection_v1 |   answer_propensity_std |
|:------------|---------:|---------------------:|----------------------:|---------------------:|----------------------:|----------------------------------:|----------------------------:|------------------------:|
| B_gate      |     -100 |          0.110803    |           0.909423    |          0.995188    |           1.90314     |                       0.0119852   |                   0.0959646 |              0.00945092 |
| B_gate      |      -30 |          0.0332408   |           0.275189    |          0.30075     |           0.54692     |                       0.00363329  |                   0.0990431 |              0.0096005  |
| B_gate      |      -10 |          0.0110803   |           0.0919359   |          0.100436    |           0.180081    |                       0.00121469  |                   0.0999407 |              0.00964125 |
| B_gate      |       -3 |          0.00332408  |           0.0276025   |          0.0301473   |           0.0537858   |                       0.000364826 |                   0.100257  |              0.00965533 |
| B_gate      |       -1 |          0.00110803  |           0.00919837  |          0.0100453   |           0.0179228   |                       0.000121615 |                   0.100347  |              0.00965932 |
| B_gate      |        0 |          0           |           5.22827e-07 |          2.09131e-06 |           1.19255e-06 |                       0           |                   0.100392  |              0.00966136 |
| B_gate      |        1 |          0.00110803  |           0.00920537  |          0.0100545   |           0.0178702   |                       0.000121696 |                   0.100438  |              0.0096633  |
| B_gate      |        3 |          0.00332408  |           0.0276219   |          0.0301709   |           0.0535754   |                       0.000365091 |                   0.100528  |              0.00966731 |
| B_gate      |       10 |          0.0110803   |           0.0921452   |          0.100633    |           0.177845    |                       0.00121817  |                   0.100846  |              0.00968114 |
| B_gate      |       30 |          0.0332408   |           0.277009    |          0.302378    |           0.526979    |                       0.00366517  |                   0.10176   |              0.00971998 |
| B_gate      |      100 |          0.110803    |           0.929541    |          1.01309     |           1.68214     |                       0.0123375   |                   0.105016  |              0.00984889 |
| result_gate |     -100 |          0.0732498   |           0.652344    |          0.790667    |           1.0939      |                       0.00737533  |                   0.66264   |              0.00354855 |
| result_gate |      -30 |          0.021975    |           0.205257    |          0.250533    |           0.329069    |                       0.00218341  |                   0.664772  |              0.00354757 |
| result_gate |      -10 |          0.00732498  |           0.0694035   |          0.0848628   |           0.109763    |                       0.000724928 |                   0.665395  |              0.00354749 |
| result_gate |       -3 |          0.0021975   |           0.0209319   |          0.0256103   |           0.0329408   |                       0.000217212 |                   0.665615  |              0.00354752 |
| result_gate |       -1 |          0.000732498 |           0.00698688  |          0.00855101  |           0.0109778   |                       7.24074e-05 |                   0.665677  |              0.00354747 |
| result_gate |        0 |          0           |           2.38637e-07 |          1.9091e-06  |           8.02981e-07 |                       0           |                   0.665709  |              0.00354758 |
| result_gate |        1 |          0.000732498 |           0.00700134  |          0.00856903  |           0.0109903   |                       7.23353e-05 |                   0.66574   |              0.00354743 |
| result_gate |        3 |          0.0021975   |           0.0210285   |          0.0257396   |           0.032957    |                       0.000216901 |                   0.665803  |              0.00354745 |
| result_gate |       10 |          0.00732498  |           0.0704529   |          0.0862984   |           0.109859    |                       0.000722069 |                   0.666024  |              0.00354736 |
| result_gate |       30 |          0.021975    |           0.214567    |          0.263241    |           0.329773    |                       0.00215755  |                   0.66666   |              0.0035473  |
| result_gate |      100 |          0.0732498   |           0.756164    |          0.932223    |           1.10151     |                       0.00708842  |                   0.668943  |              0.00354722 |

## Working interpretation
The local control frame is dynamically reoriented by the running CoT itself: adjacent top-1 control directions often differ by tens of degrees. B has very weak alignment of its realized embedding action with the local top-1 mode, whereas result is strongly aligned. This matches the preceding functional-token-action dissection: B behaves more like a state/history-conditioned routing action, result more like a direct control action. In contrast, the selected sparse Training-Sky history perturbations rotate the already-existing frame only by tiny angles at natural scale. Even a 100x extrapolation of two realized final history-displacement directions produces <1 degree mean top-1 rotation and ~1% control-gain changes. These results support a distinction between history-shaped control geometry and runtime token-by-token control-frame motion.
