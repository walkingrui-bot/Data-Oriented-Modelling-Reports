# FOUNDATION-COT-TERRAIN-004

36 matched autoregressive GRU models; 3,023 parameters/model; 59-token replay trajectory.

Factors: 32/64/128/256 unique-record training pools × chunk16/chunk4/chunk1 interleaving × 3 temporal order seeds. Same initialization, optimizer, epochs, processed-record count and update count.

Every CoT point is a cold start from the original prompt plus the exact first k tokens. Each point produces a complete greedy continuation. Matching output is recorded only as observable equality, never as process merging.

## Endpoint signature counts

|        signature |   models |
|-----------------:|---------:|
| 0000000000000000 |       23 |
| 1111111111111111 |       13 |

Dominant exact naked-endpoint signature: `0000000000000000` (23/36 models)

## Foundation summary

|   unique_records |   chunk |   mean_deformation |    seed_sd |   max_seen |
|-----------------:|--------:|-------------------:|-----------:|-----------:|
|               32 |       1 |           0.759647 | 0          |   1        |
|               32 |       4 |           0.759647 | 0          |   1        |
|               32 |      16 |           0.759647 | 0          |   1        |
|               64 |       1 |           0.754099 | 0.0282182  |   1        |
|               64 |       4 |           0.784349 | 0.00379083 |   0.974684 |
|               64 |      16 |           0.809597 | 0.00853956 |   1        |
|              128 |       1 |           0.790397 | 0.00372404 |   1        |
|              128 |       4 |           0.765163 | 0.0180786  |   1        |
|              128 |      16 |           0.78555  | 0.121086   |   1        |
|              256 |       1 |           0.761274 | 0.0240878  |   1        |
|              256 |       4 |           0.790981 | 0.0670584  |   1        |
|              256 |      16 |           0.899699 | 0.065542   |   1        |

## Strongest order-seed dispersion within a fixed foundation

|   unique_records |   chunk |   k |   mean_seed_distance |   max_seed_distance |   output_classes |
|-----------------:|--------:|----:|---------------------:|--------------------:|-----------------:|
|              256 |       4 |  59 |             0.967871 |            1        |                3 |
|              128 |      16 |  58 |             0.872514 |            0.974684 |                3 |
|              128 |      16 |  56 |             0.833333 |            1        |                3 |
|              256 |       4 |  58 |             0.812182 |            0.974684 |                3 |
|              128 |      16 |  57 |             0.803813 |            0.95     |                3 |
|              256 |       4 |  57 |             0.795726 |            0.95     |                3 |
|              128 |      16 |  42 |             0.778134 |            0.954023 |                3 |
|              256 |       4 |  42 |             0.772566 |            0.902439 |                3 |
|              128 |      16 |  18 |             0.766226 |            0.954023 |                3 |
|              256 |       4 |   1 |             0.763566 |            0.930233 |                3 |
|              256 |       4 |   8 |             0.759746 |            0.902439 |                3 |
|              256 |       4 |  25 |             0.759746 |            0.902439 |                3 |
|              256 |       4 |  53 |             0.759746 |            0.902439 |                3 |
|              256 |       4 |  34 |             0.759746 |            0.902439 |                3 |
|              256 |       4 |  18 |             0.759746 |            0.902439 |                3 |
|              256 |       4 |  17 |             0.759746 |            0.902439 |                3 |
|              256 |       4 |  19 |             0.752497 |            0.903614 |                3 |
|              128 |      16 |  41 |             0.74513  |            0.931818 |                3 |
|              256 |       4 |   7 |             0.740192 |            0.879518 |                3 |
|              256 |       4 |  16 |             0.740192 |            0.879518 |                3 |
|              256 |       4 |  21 |             0.740192 |            0.879518 |                3 |
|              256 |       4 |   4 |             0.740192 |            0.879518 |                3 |
|              256 |       4 |  41 |             0.740192 |            0.879518 |                3 |
|              256 |       4 |  52 |             0.740192 |            0.879518 |                3 |
|              256 |       4 |  33 |             0.740192 |            0.879518 |                3 |
