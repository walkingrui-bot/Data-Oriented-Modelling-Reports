# HISTORY-TO-COT-KERNEL-001

- Model: Adam-trained GRU, 5,067 parameters
- Baseline training: 10 epochs × 6 fixed style-batches
- Historical event: swap adjacent batches 2 and 3 in exactly one epoch, then continue identical training
- Three post-event carriers: natural / param-only / optim-only
- Probe CoT length: 59 tokens
- Kernel value: change in mean log probability of the complete remaining canonical continuation at each cold-start prefix

## Immediate Adam two-layer state difference

|   event_epoch |   param_delta_norm_after_swap |   adam_m_delta_norm_after_swap |   adam_v_delta_norm_after_swap |
|--------------:|------------------------------:|-------------------------------:|-------------------------------:|
|             0 |                     0.170241  |                     0.00399917 |                    8.29142e-07 |
|             1 |                     0.068879  |                     0.00540078 |                    1.21227e-06 |
|             2 |                     0.0625908 |                     0.00777168 |                    1.85087e-06 |
|             3 |                     0.0639366 |                     0.00661969 |                    1.39386e-06 |
|             4 |                     0.0522814 |                     0.00638947 |                    1.33344e-06 |
|             5 |                     0.0521893 |                     0.00643627 |                    6.69231e-07 |
|             6 |                     0.0549798 |                     0.00659079 |                    6.37138e-07 |
|             7 |                     0.0566018 |                     0.00665216 |                    5.1673e-07  |
|             8 |                     0.0572474 |                     0.00658491 |                    5.72014e-07 |
|             9 |                     0.057696  |                     0.00660685 |                    4.67419e-07 |

## Kernel SVD

| kind       |   mode |   singular_value |   explained_fraction |   cumulative |
|:-----------|-------:|-----------------:|---------------------:|-------------:|
| natural    |      1 |       0.0316125  |           0.78741    |     0.78741  |
| natural    |      2 |       0.0122803  |           0.118823   |     0.906234 |
| natural    |      3 |       0.00945729 |           0.0704721  |     0.976706 |
| natural    |      4 |       0.00360985 |           0.0102675  |     0.986973 |
| natural    |      5 |       0.00312248 |           0.00768216 |     0.994656 |
| param_only |      1 |       0.0365077  |           0.819954   |     0.819954 |
| param_only |      2 |       0.0148596  |           0.135842   |     0.955796 |
| param_only |      3 |       0.00714731 |           0.0314272  |     0.987223 |
| param_only |      4 |       0.00313781 |           0.00605721 |     0.99328  |
| param_only |      5 |       0.00242593 |           0.00362056 |     0.996901 |
| optim_only |      1 |       0.0197648  |           0.633475   |     0.633475 |
| optim_only |      2 |       0.0116644  |           0.220635   |     0.854109 |
| optim_only |      3 |       0.00840489 |           0.114554   |     0.968663 |
| optim_only |      4 |       0.00332399 |           0.017917   |     0.98658  |
| optim_only |      5 |       0.00235382 |           0.00898445 |     0.995565 |

## Rank reconstruction

| kind       |   rank |   relative_reconstruction_error |
|:-----------|-------:|--------------------------------:|
| natural    |      1 |                       0.461074  |
| natural    |      2 |                       0.306213  |
| natural    |      3 |                       0.152624  |
| natural    |      4 |                       0.114134  |
| natural    |      5 |                       0.0731058 |
| param_only |      1 |                       0.424318  |
| param_only |      2 |                       0.210248  |
| param_only |      3 |                       0.113035  |
| param_only |      4 |                       0.0819742 |
| param_only |      5 |                       0.0556705 |
| optim_only |      1 |                       0.605413  |
| optim_only |      2 |                       0.381956  |
| optim_only |      3 |                       0.177022  |
| optim_only |      4 |                       0.115844  |
| optim_only |      5 |                       0.0665979 |

## Parameter vs optimizer-state carriage

| comparison               |   cosine |   fro_ratio_other_to_natural |
|:-------------------------|---------:|-----------------------------:|
| natural vs param_only    | 0.793832 |                     1.1317   |
| natural vs optim_only    | 0.104096 |                     0.697058 |
| natural vs (param+optim) | 0.999446 |                     0.97148  |
