# HISTORY-TO-COT-KERNEL-002 — CoT / Answer dual-kernel anatomy

CoT kernel: change in support for the baseline model's own free-generated reasoning path before its final answer marker.

Answer kernel: change in `logit(1)-logit(0)` at the moment each model, from the same cold-start prefix, freely emits its own final answer token.

Flattened cell correlation: **-0.686427**

## Anatomy counts

| class           |   cells |
|:----------------|--------:|
| Weak            |     412 |
| Answer-dominant |      68 |
| CoT-dominant    |      63 |
| Coupled-strong  |      57 |

## Event coupling

|   event_epoch |   cot_kernel_norm |   answer_kernel_norm |   cot_answer_corr_across_k |   mean_full_completion_edit |   answer_flip_points |
|--------------:|------------------:|---------------------:|---------------------------:|----------------------------:|---------------------:|
|             0 |        0.113354   |            0.216988  |                -0.73334    |                 0           |                    0 |
|             1 |        0.0199745  |            0.0294361 |                -0.476886   |                 0           |                    0 |
|             2 |        0.0318224  |            0.0232241 |                 0.873943   |                 0           |                    0 |
|             3 |        0.00507835 |            0.0696751 |                -0.0167545  |                 0.000641026 |                    0 |
|             4 |        0.00430085 |            0.0679641 |                 0.0789018  |                 0.000641026 |                    0 |
|             5 |        0.010431   |            0.011818  |                 0.930162   |                 0           |                    0 |
|             6 |        0.007706   |            0.0723052 |                 0.0694657  |                 0.000641026 |                    0 |
|             7 |        0.0111553  |            0.0725815 |                 0.0195473  |                 0.000641026 |                    0 |
|             8 |        0.0180691  |            0.0256477 |                 0.760707   |                 0           |                    0 |
|             9 |        0.0144421  |            0.0697126 |                 0.00973368 |                 0.000641026 |                    0 |

## SVD top modes

| kernel   |   mode |   singular_value |   explained_fraction |   cumulative |
|:---------|-------:|-----------------:|---------------------:|-------------:|
| CoT      |      1 |       0.120895   |          0.965825    |     0.965825 |
| CoT      |      2 |       0.018428   |          0.0224407   |     0.988265 |
| CoT      |      3 |       0.0124678  |          0.0102721   |     0.998537 |
| CoT      |      4 |       0.00378615 |          0.000947277 |     0.999485 |
| CoT      |      5 |       0.002552   |          0.00043037  |     0.999915 |
| Answer   |      1 |       0.227187   |          0.696387    |     0.696387 |
| Answer   |      2 |       0.149031   |          0.299666    |     0.996053 |
| Answer   |      3 |       0.0168128  |          0.00381387  |     0.999867 |
| Answer   |      4 |       0.00279033 |          0.00010505  |     0.999972 |
| Answer   |      5 |       0.00132227 |          2.359e-05   |     0.999996 |

## CoT/Answer right-subspace overlap

|   rank |   mean_principal_cosine |   min_principal_cosine |   max_principal_cosine |
|-------:|------------------------:|-----------------------:|-----------------------:|
|      1 |                0.935246 |             0.935246   |               0.935246 |
|      2 |                0.492261 |             0.0354642  |               0.949058 |
|      3 |                0.557541 |             0.00599667 |               0.993885 |
|      4 |                0.618324 |             0.0199542  |               0.998496 |
|      5 |                0.626408 |             0.0160884  |               0.999154 |

Strongest lead-lag correlation: lag=0, r=-0.686427

## Root-channel surgery

| kernel   | comparison             |    cosine |   norm_ratio |   relative_residual |
|:---------|:-----------------------|----------:|-------------:|--------------------:|
| CoT      | natural vs param_only  |  0.949543 |     1.16812  |         nan         |
| CoT      | natural vs optim_only  | -0.254096 |     0.375984 |         nan         |
| CoT      | natural vs param+optim |  0.999912 |     1.01373  |           0.0191564 |
| Answer   | natural vs param_only  |  0.876996 |     0.940278 |         nan         |
| Answer   | natural vs optim_only  |  0.403316 |     0.49941  |         nan         |
| Answer   | natural vs param+optim |  0.900027 |     1.14001  |           0.497537  |
