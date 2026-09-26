# FOUNDATION-COT-TERRAIN-002

12 matched autoregressive GRU models, 3,957 parameters each. Same initialization, optimizer, epochs, records processed per epoch and update count.

Training-set sizes: 32, 64, 128 and 256 unique records. For each size, the same record multiset was presented at three genuine interleaving depths: 16-record blocks, 4-record chunks, and 1-record alternation. These schedules change mini-batch composition, not merely order inside a batch.

One valid 24-token CoT was replayed exactly token by token. Each prefix was cold-started and generated a complete continuation. Equality of outputs is only an observation at that prefix.

## Endpoint

|   unique_records |   interleave_chunk |   correct |   accuracy |      predictions |
|-----------------:|-------------------:|----------:|-----------:|-----------------:|
|               32 |                 16 |         8 |        0.5 | 1111111111111111 |
|               32 |                  4 |         8 |        0.5 | 0000000000000000 |
|               32 |                  1 |         8 |        0.5 | 0000000000000000 |
|               64 |                 16 |         8 |        0.5 | 1111111111111111 |
|               64 |                  4 |         8 |        0.5 | 0000000000000000 |
|               64 |                  1 |         8 |        0.5 | 0000000000000000 |
|              128 |                 16 |         8 |        0.5 | 0000000000000000 |
|              128 |                  4 |         8 |        0.5 | 1111111111111111 |
|              128 |                  1 |         8 |        0.5 | 1111111111111111 |
|              256 |                 16 |         8 |        0.5 | 0000000000000000 |
|              256 |                  4 |         8 |        0.5 | 1111111111111111 |
|              256 |                  1 |         8 |        0.5 | 1111111111111111 |

## Aggregate

|   unique_records |   interleave_chunk |   mean_p_correct |   mean_edit |   max_edit |
|-----------------:|-------------------:|-----------------:|------------:|-----------:|
|               32 |                  1 |         0.510417 |    0.140948 |   0.5      |
|               32 |                  4 |         0.510417 |    0.140948 |   0.5      |
|               32 |                 16 |         0.510417 |    0.276529 |   0.5      |
|               64 |                  1 |         0.5      |    0.192739 |   0.521739 |
|               64 |                  4 |         0.5      |    0.192739 |   0.521739 |
|               64 |                 16 |         0.475694 |    0.269996 |   0.73913  |
|              128 |                  1 |         0.461806 |    0.281746 |   1        |
|              128 |                  4 |         0.46875  |    0.357129 |   1        |
|              128 |                 16 |         0.5      |    0.209235 |   0.681818 |
|              256 |                  1 |         0.427083 |    0.277101 |   1        |
|              256 |                  4 |         0.371528 |    0.349876 |   1        |
|              256 |                 16 |         0.489583 |    0.21899  |   0.695652 |

## Strongest within-size interleaving effects

|   unique_records |   k | added_token   |   mean_interleave_effect |   max_interleave_effect |
|-----------------:|----:|:--------------|-------------------------:|------------------------:|
|              128 |  23 | answer        |                 0.666667 |                1        |
|              256 |  23 | answer        |                 0.666667 |                1        |
|              128 |   0 |               |                 0.441339 |                0.5      |
|              256 |   0 |               |                 0.439394 |                0.545455 |
|               64 |  12 | D             |                 0.388889 |                0.583333 |
|              256 |   8 | ;             |                 0.368056 |                0.583333 |
|               64 |   0 |               |                 0.363636 |                0.545455 |
|               64 |  11 | xor           |                 0.358974 |                0.538462 |
|              256 |   7 | 1             |                 0.340875 |                0.538462 |
|              128 |  22 | ;             |                 0.333333 |                0.5      |
|              256 |  22 | ;             |                 0.333333 |                0.5      |
|              256 |   6 | gives         |                 0.31746  |                0.5      |
|              256 |   5 | 0             |                 0.274854 |                0.4      |
|              256 |   1 | B             |                 0.268497 |                0.421053 |
|              256 |   4 | A             |                 0.258333 |                0.375    |
|              256 |   2 | 1             |                 0.249158 |                0.388889 |
|              256 |   3 | xor           |                 0.243697 |                0.352941 |
|              256 |  21 | 0             |                 0.222222 |                0.333333 |
|              256 |  18 | 1             |                 0.222222 |                0.333333 |
|              128 |  21 | 0             |                 0.222222 |                0.333333 |
