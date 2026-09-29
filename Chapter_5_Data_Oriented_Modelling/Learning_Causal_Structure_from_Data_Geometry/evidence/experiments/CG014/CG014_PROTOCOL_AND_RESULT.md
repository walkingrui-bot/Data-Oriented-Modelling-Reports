# CG-014 One-Intervention Edge Confirmation

## Question
Can one real target intervention improve confirmation of direct causal children beyond observational relation texture alone?

## Data
Small-data design using only the Sachs protein-signaling system:
- one observational condition: cd3cd28;
- five measured intervention targets defined by the public condition manifest:
  Akt, PKC, PIP2, Mek, PKA;
- one intervention condition per target;
- 10 candidate nodes per target, 50 target-node pairs total;
- 12 direct-child pairs in the benchmark GroundTruth graph.

## Features
Observational baseline relation texture:
correlation, nonlinearity gain, heteroscedasticity, input-|residual| dependence,
fibre-width variation, residual skew/kurtosis, and four forward/reverse gaps.

One-intervention response:
robust node-level location, scale, shape and total response, plus within-intervention ranks.

Relation-change features were evaluated separately and in combination.

## Validation
Strict leave-one-target-out: all pairs belonging to the test intervention target are removed from training.

## Main result
Baseline relation AUC = 0.7215.
One-intervention response AUC = 0.7105.
Baseline + matched node response AUC = 0.8838.

Controls:
- shuffling intervention response among nodes within each target: p = 0.017;
- shuffling direct-child labels within each target: p = 0.010.

Interpretation:
observational relation texture and matched intervention response are complementary.
The intervention is useful because the response is attached to the correct node, not merely because an extra condition was added.
