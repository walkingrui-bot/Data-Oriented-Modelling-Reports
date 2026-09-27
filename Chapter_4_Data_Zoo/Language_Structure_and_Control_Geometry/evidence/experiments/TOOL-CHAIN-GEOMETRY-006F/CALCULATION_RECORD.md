# TOOL-CHAIN-GEOMETRY-006F calculation record

Formal object: end-to-end generated action path consisting of an autoregressive semantic planner followed by the frozen 006E autoregressive JSON emitter, then JSON parse/schema validation and the executable register-world backend.

## Competence gate
The saved checkpoint contains 3 completed training epochs (NLL 1.047148 -> 0.181197). An independent gate required oracle-prefix exact action accuracy >= 0.85 and P1_N1 exact final-state accuracy >= 0.65. Measured gate values were 0.934755 and 0.841667; the checkpoint passed before factorial execution.

## Formal paired factorial
Exactly the same 3 x 200 held-out task panels as final 006D were used. Every task was executed in all four cells: P1_N1, P1_N0, P0_N1, P0_N0. Total = 600 worlds and 2,400 executed trajectories.

Pooled final-state accuracies:
- P1_N1: 0.821667
- P1_N0: 0.806667
- P0_N1: 0.723333
- P0_N0: 0.726667

Task-paired effects:
- provenance main effect: 8.916667 pp; bootstrap 95% CI [6.4166666666666705, 11.499999999999993]
- normalization main effect: 0.583333 pp; bootstrap 95% CI [-1.333333333333342, 2.2500000000000018]
- interaction: 1.833333 pp; bootstrap 95% CI [-1.0000000000000009, 4.833333333333345]

## Oracle-prefix diagnostic on the same 600 formal worlds
10,840 decision contexts were reconstructed under oracle action history and decoded in batch. Overall exact action accuracy = 0.930812. P1_N1/P1_N0/P0_N1/P0_N0 exact = 0.949815, 0.937269, 0.918081, 0.918081. For multi-read WRITE decisions, value accuracy = 0.822148, 0.776846, 0.696309, 0.697987.

The 006F formal result therefore establishes a robust provenance effect under the trained generative planner. Under the matched raw-style distribution included during training, normalization does not show a stable final-state main effect or interaction. This is a training/deployment-distribution result, not a claim that normalization is universally dispensable.
