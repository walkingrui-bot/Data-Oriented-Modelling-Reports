# CG-022 protocol — Consequence-Supervised World Program

## Engineering target
Construct an explicit world-state model that can use one generated candidate population to produce correct consequences under a broad family of interventions and relation edits. The experiment reuses earlier design conclusions rather than re-testing hypothesis ecology.

## Data
The exact synthetic panel from CG-017—021 is reused: 600 independent parameter groups, split 400/100/100 into train/dev/test. Each group contains three observationally equivalent linear-Gaussian SCMs, each with support-present and support-absent instances. The test set contains 100 independent parameter groups and 600 task instances.

The three-variable context and finite rollout length are local mechanistic probes. They are not treated as the temporal or structural boundary of the generative problem.

## Architecture
All new variants use:

- 8 persistent candidate worlds;
- explicit state `(B_t, logits_t)` only across world updates;
- three untied attention blocks per update, token width 32, 4 heads, FF width 64;
- zero diagonal and row absolute sum <= 0.95 for every generated 3×3 relation matrix;
- no GRU/RNN state;
- no KEEP/DROP/BRANCH action, top-k pruning, winner rule, candidate-to-world assignment, sparsity target or relation-matrix supervision.

Support evidence is hidden during updates 1–2 and becomes visible from update 3.

## Training operators
The model never receives true `B` as input or intermediate supervision. True SCMs are used only to compute consequence labels.

Training bank (21 operators):

- 6 single-node interventions: each target at -1 and +1;
- 9 double-node interventions: all three unordered target pairs with value patterns (+1,+1), (+1,-1), (-1,+1);
- 6 coordinate deletion operations: delete each directed off-diagonal relation coordinate, then intervene on its source at +1.

At each optimization update, six operators are sampled from this bank. The same generated world population must answer all six.

The local rollout horizon is randomly sampled from 3–6 world updates during training.

## Held-out operator bank
The frozen model is evaluated on 30 operations not used during training:

- 12 single-node interventions at ±0.5 and ±1.5;
- 6 double-node interventions using held-out value combinations;
- 6 relation-halving operations followed by source intervention;
- 6 relation-sign-flip operations followed by source intervention.

## Construction iterations

### Broad
450 updates. Objective: sampled operator-bank consequence NLL only.

### Balanced
500 updates. Objective combines original-query NLL, operator-bank NLL, support-observation likelihood, and a support-vs-masked evidence-use margin.

### Evidence-coupled
500 updates. Objective combines original-query NLL, operator-bank NLL, support-observation likelihood, and a downstream operator-gain margin requiring support-conditioned consequences to improve relative to a matched support-masked run.

Seeds: 11 and 22. Adam learning rate 0.0015, batch 64, gradient clipping 5.

## Evaluation

- original-query NLL;
- full training-bank NLL;
- held-out-bank NLL;
- family-specific held-out NLL/MSE;
- paired 100-group bootstrap comparisons (10,000 resamples);
- support-observation and downstream-operator gain;
- wrong-support transplant;
- exact state-sufficiency replay from saved update-2 object state;
- frozen rollout to 20 world updates;
- relation-matrix distance to true SCM for evaluation only.
