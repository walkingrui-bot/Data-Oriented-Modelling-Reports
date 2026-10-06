# EXP004C — Pinpointing the Blueprint Birth Operator

| Micro-stage | Operation | Order | Style | Full 12-state blueprint |
|---|---:|---:|---:|---:|
| c0 | 100.00% | 100.00% | 66.72% | 66.72% |
| pre1 | 100.00% | 100.00% | 66.72% | 67.83% |
| h1 | 100.00% | 100.00% | 100.00% | 100.00% |
| pre2 | 100.00% | 100.00% | 100.00% | 100.00% |
| h2 | 100.00% | 100.00% | 100.00% | 100.00% |
| z | 100.00% | 100.00% | 100.00% | 100.00% |

`pre1 = Linear(c0)` and `h1 = tanh(pre1)`. If full-plan readability rises only after `tanh`, the first nonlinearity is the point at which the separate ingredients become a linearly explicit joint plan in this trained network.
