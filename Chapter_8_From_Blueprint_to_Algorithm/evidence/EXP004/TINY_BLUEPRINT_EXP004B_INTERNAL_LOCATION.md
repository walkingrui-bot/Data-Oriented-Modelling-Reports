# EXP004B — Internal Location of the Learned Blueprint

## Attention routing matrix

Rows are queried goals; columns are semantic fact-goal identities after undoing shuffle.

| query \\ fact | G0 | G1 | G2 |
|---|---:|---:|---:|
| G0 | 0.0286 | 0.4745 | 0.4969 |
| G1 | 0.4693 | 0.0362 | 0.4945 |
| G2 | 0.4621 | 0.5021 | 0.0358 |

## z-coordinate ablation

Baseline exact answer accuracy: **100.00%**

| z dim | Accuracy after mean-ablation | eta² operation | eta² order | eta² style | One-dim donor swap changes output | One-dim swap reaches donor full-plan answer |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 61.22% | 0.016 | 0.004 | 0.939 | 43.70% | 14.53% |
| 1 | 91.55% | 0.052 | 0.289 | 0.634 | 17.57% | 12.83% |
| 2 | 68.62% | 0.505 | 0.116 | 0.334 | 39.77% | 16.70% |
| 3 | 78.72% | 0.184 | 0.789 | 0.011 | 28.67% | 15.03% |
| 4 | 88.60% | 0.915 | 0.000 | 0.056 | 20.93% | 15.33% |
| 5 | 64.45% | 0.020 | 0.035 | 0.892 | 40.63% | 13.67% |
| 6 | 87.37% | 0.302 | 0.258 | 0.209 | 22.43% | 14.57% |
| 7 | 96.57% | 0.156 | 0.646 | 0.143 | 10.87% | 12.77% |

## Reading

Layer localization and coordinate localization are different. The full blueprint first becomes jointly linearly readable at h1, then h2 preserves/remaps it, and z compresses it to eight coordinates. The coordinate analyses show how distributed the final compressed code is; single z coordinates are not assumed to correspond one-to-one with semantic blueprint factors.
