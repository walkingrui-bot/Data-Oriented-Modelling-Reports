# CAUSAL-GEOMETRY-016 — Executable Data Action Chain

## Question
Can a data-intelligence system use its current evidence state to decide whether to stop or execute another real data operator, instead of applying the same fixed pipeline to every candidate relation?

## Data
The experiment reuses the small real Sachs panel already used in CG-014:
- five unique measured intervention targets;
- ten candidate nodes per target;
- fifty target-node candidate relations;
- leave-one-target-out evaluation.

No new large dataset is introduced.

## Operator library
A0 — BaselineRelation:
compute observational target-node relation texture.

A1 — MatchedResponse:
use the real target intervention and compute the candidate node's matched location / scale / shape response geometry.

A2 — RelationChange:
compute intervention-induced deformation of the target-node relation geometry.

## Reasoning state and stopping
The initial state contains the baseline relation score.
The policy estimates confidence from the absolute baseline score relative to the training-target score distribution.
If baseline evidence is sufficiently strong, it stops.
If not, it executes A1 and updates the candidate score.
The uncertainty quantile is selected only from the non-test targets by inner leave-one-target-out validation.

A2 is evaluated as a deeper fixed continuation control; it is not forced into the adaptive policy because unconditional extra depth reduces performance.

## Main results
Baseline-only AUC = 0.7215.
Always add matched response AUC = 0.8838.
Always add response + relation change AUC = 0.8114.
Strict nested adaptive policy AUC = 0.8553 with matched response invoked for 54% of candidate relations.
Mean operator calls fall from 2.00 for always-response to 1.54 for the adaptive policy.

Among the 27 relations selected for escalation, baseline AUC is 0.5952 and rises to 0.8730 after the matched-response operator.

## Controls
Escalating the most-confident relations instead of the most-uncertain ones gives AUC = 0.7785 at the same operator budget.
Ten thousand random same-budget escalation controls have mean AUC = 0.8238; 11.46% reach or exceed the uncertainty policy.

## Important negative result
All five held-out targets contain at least one candidate relation that triggers escalation.
Therefore this prototype saves pair-level operator computation but does not reduce the number of target-level intervention experiments.
It should not be described as an intervention-selection policy yet.

## Interpretation boundary
CG-016 demonstrates a first executable component of Data Action Chain reasoning:
state-dependent stopping versus continued computation.

It does not yet demonstrate:
- autonomous generation of new hypotheses;
- autonomous invention of new operators;
- target-level experimental design savings;
- general transfer beyond the current small Sachs panel.

The central supported lesson is narrower:
more reasoning depth is not automatically better, and current evidence can be used to route additional computation selectively.
