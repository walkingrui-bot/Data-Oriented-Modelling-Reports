# TRAINING-SKY-001 — Four-dimensional training-history reconstruction

- Model: Adam GRU, 897 parameters
- Training history: 48 record events over 6 epochs
- Training-time slices reconstructed: [0, 6, 12, 18, 24, 30, 36, 42]
- Four training coordinates: training time τ × sample identity s × token position j × write channel c
- Write channels: parameters θ, Adam m, Adam v
- Inference axis: 33 CoT tokens
- Local token-write direction is defined by a differentiable embedding-presence scalar at the actual token; a central finite difference estimates its one-step Adam write vector.
- Selected write vectors are injected immediately after the real training event, transported through all later baseline Adam updates, and read out by complete-future CoT likelihood at every cold-start prefix.

## Channel summary

| channel   |   mean_abs_effect |   rms_effect |   max_abs_effect |
|:----------|------------------:|-------------:|-----------------:|
| adam_m    |       0.00106507  |  0.00240367  |       0.0350475  |
| adam_v    |       0.000618252 |  0.00136177  |       0.0179609  |
| theta     |       0.000101898 |  0.000170138 |       0.00166893 |

## Strongest reconstructed events

|   tau |   epoch |   sid |   j | token   | channel   |   rms_effect |   max_abs_effect |
|------:|--------:|------:|----:|:--------|:----------|-------------:|-----------------:|
|     0 |       0 |     0 |  25 | 0       | adam_m    |  0.00767913  |      0.0350475   |
|     0 |       0 |     0 |  13 | A       | adam_m    |  0.00450835  |      0.0174046   |
|     0 |       0 |     0 |  25 | 0       | adam_v    |  0.0043254   |      0.0179609   |
|     0 |       0 |     0 |  13 | A       | adam_v    |  0.0028429   |      0.00758966  |
|     6 |       0 |     6 |  13 | A       | adam_m    |  0.00213568  |      0.00802676  |
|    18 |       2 |     2 |  19 | first   | adam_m    |  0.00124994  |      0.00500679  |
|     6 |       0 |     6 |  13 | A       | adam_v    |  0.00117077  |      0.00178814  |
|    42 |       5 |     2 |   7 | 0       | adam_m    |  0.00111189  |      0.00389417  |
|    12 |       1 |     4 |  19 | first   | adam_m    |  0.00108848  |      0.00405312  |
|    12 |       1 |     4 |  13 | A       | adam_m    |  0.00107847  |      0.00238419  |
|    36 |       4 |     4 |   7 | 1       | adam_m    |  0.0010206   |      0.00230471  |
|     6 |       0 |     6 |  19 | first   | adam_m    |  0.000672004 |      0.00278155  |
|    30 |       3 |     6 |   7 | 1       | adam_m    |  0.000669512 |      0.00309944  |
|    30 |       3 |     6 |   1 | <Q>     | adam_m    |  0.00065581  |      0.00325839  |
|    36 |       4 |     4 |   1 | <Q>     | adam_m    |  0.000651512 |      0.00317891  |
|     6 |       0 |     6 |  31 | result  | adam_v    |  0.000645677 |      0.00278155  |
|    18 |       2 |     2 |  13 | A       | adam_v    |  0.000606512 |      0.00166893  |
|    24 |       3 |     0 |  13 | A       | adam_v    |  0.000560924 |      0.00119209  |
|    42 |       5 |     2 |   1 | <Q>     | adam_m    |  0.000474787 |      0.00230471  |
|    18 |       2 |     2 |   7 | 0       | adam_m    |  0.000440277 |      0.0017484   |
|     6 |       0 |     6 |  13 | A       | theta     |  0.000430733 |      0.00166893  |
|    24 |       3 |     0 |  25 | 0       | adam_m    |  0.000423063 |      0.000953674 |
|    12 |       1 |     4 |  13 | A       | adam_v    |  0.000372075 |      0.000516574 |
|    42 |       5 |     2 |  25 | 0       | theta     |  0.000259319 |      0.00055631  |
|    18 |       2 |     2 |   7 | 0       | adam_v    |  0.000253248 |      0.000675519 |
|    36 |       4 |     4 |   7 | 1       | adam_v    |  0.000243907 |      0.000397364 |
|    36 |       4 |     4 |   7 | 1       | theta     |  0.000215178 |      0.000953674 |
|    24 |       3 |     0 |   7 | 0       | adam_m    |  0.000214854 |      0.000715256 |
|    42 |       5 |     2 |   7 | 0       | adam_v    |  0.000199731 |      0.000874201 |
|    36 |       4 |     4 |   1 | <Q>     | adam_v    |  0.00018638  |      0.000874201 |

## SVD

|   mode |   singular_value |   explained_fraction |   cumulative |
|-------:|-----------------:|---------------------:|-------------:|
|      1 |       0.0537993  |          0.694494    |     0.694494 |
|      2 |       0.0335937  |          0.270789    |     0.965283 |
|      3 |       0.00941296 |          0.0212602   |     0.986543 |
|      4 |       0.00444344 |          0.00473754  |     0.991281 |
|      5 |       0.00356583 |          0.00305095  |     0.994332 |
|      6 |       0.002994   |          0.0021509   |     0.996483 |
|      7 |       0.00237464 |          0.00135304  |     0.997836 |
|      8 |       0.00169813 |          0.000691924 |     0.998528 |
|      9 |       0.00131816 |          0.000416916 |     0.998945 |
|     10 |       0.00117322 |          0.000330271 |     0.999275 |


## Unit-normalized transport efficiency

Raw θ/m/v amplitudes use different state units, so channel magnitude comparisons are interpreted only after normalization by each local write-vector norm.

| channel   |   mean_abs_transport |   rms_transport |   max_abs_transport |
|:----------|---------------------:|----------------:|--------------------:|
| adam_m    |            0.384189  |       0.938288  |            13.5818  |
| adam_v    |          420.846     |     924.413     |          9984.54    |
| theta     |            0.0188335 |       0.0477648 |             0.42295 |

## Event-normalized shape SVD

|   mode |   singular_value |   explained_fraction |   cumulative |
|-------:|-----------------:|---------------------:|-------------:|
|      1 |         4.69569  |           0.459364   |     0.459364 |
|      2 |         3.71106  |           0.286916   |     0.74628  |
|      3 |         1.79142  |           0.0668581  |     0.813138 |
|      4 |         1.56403  |           0.0509626  |     0.864101 |
|      5 |         1.45766  |           0.0442662  |     0.908367 |
|      6 |         1.075    |           0.0240755  |     0.932442 |
|      7 |         0.850168 |           0.015058   |     0.9475   |
|      8 |         0.728079 |           0.0110437  |     0.958544 |
|      9 |         0.598135 |           0.00745346 |     0.965998 |
|     10 |         0.530143 |           0.00585524 |     0.971853 |

## Training-time persistence

|   tau |   mean_abs_effect |   rms_effect |   rms_transport |   epoch |
|------:|------------------:|-------------:|----------------:|--------:|
|     0 |       0.00242879  |  0.00420492  |       1437.82   |       0 |
|     6 |       0.000686817 |  0.00108151  |        352.71   |       0 |
|    12 |       0.000400481 |  0.000652474 |         96.6798 |       1 |
|    18 |       0.000320034 |  0.000608124 |        241.159  |       2 |
|    24 |       0.000205889 |  0.000307054 |         87.3268 |       3 |
|    30 |       0.000169464 |  0.000389932 |         36.6654 |       3 |
|    36 |       0.000307373 |  0.000520023 |         90.6471 |       4 |
|    42 |       0.00024173  |  0.000515786 |         48.3731 |       5 |
