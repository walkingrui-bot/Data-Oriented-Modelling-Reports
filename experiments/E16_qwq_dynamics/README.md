# E16 QwQ trajectory prediction and movement regimes

[Experiment index](../README.md)

Five-fold one-step MSEs were 0.889 for z, 0.835 for z/v/a and 0.909 for mismatched motion. Free-rollout second-half MSEs were 1.254/1.194/1.260 and endpoint MSEs 1.008/0.956/1.011; the switching model gave endpoint MSE 0.938. Approximately 50.76% of steps approached the endpoint. The rewritten implementation gave K2 centroid-silhouette 0.346, concentrated/diffuse speeds 0.498/0.454 and transition entropies 0.9994/0.9988 bits. State/+v/+v+a MSEs for windows 80/100/120 were 0.759/0.714/0.708, 0.791/0.743/0.737 and 0.830/0.796/0.775; the window100 all-scale values were 0.674/0.656/0.642.

## Method

The extended record contains 115 correct QwQ traces; one analysis used 99 sufficiently long traces and 958 nonoverlapping 100-content-word windows. Existing relational statistics defined z, successive differences defined v, and differences of v defined a. Whole-trace holdouts compared predictors, temporal mismatches and endpoints. A separately rewritten analysis used the longest 90 traces, 2590 windows and 2500 z/v states.

## Interpretation

The motion history adds predictive information to the current relational projection. Reanalysis preserves D/C structure and faster concentrated motion; the measured transition entropies place both regimes close to one bit.

## Artifacts and reproduction

**Archived discussion results**

The numerical record is the retained QwQ discussion archive. Keep its z/v/a comparisons and revised regime interpretation together.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/C_cot/QwQ_后续动力学结果_会话归档.md](../../evidence/C_cot/QwQ_后续动力学结果_会话归档.md) | method_or_report |  |

## Related hypotheses

H05, H06, H07, H20

- C11: Retain recorded D/C and speed replication; retire robust lower-transition-entropy claim.
