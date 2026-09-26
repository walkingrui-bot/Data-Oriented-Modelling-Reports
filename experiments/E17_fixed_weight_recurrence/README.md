# E17 External recurrence and K V intervention with fixed weights

[Experiment index](../README.md)

At horizons 1/3/5/8, rollout final accuracy was 90.8/88.3/85.8/66.7%. Scoring the first initial-prompt prediction against the final label gave 90.8/35.0/45.0/15.0%. At fixed token/position, K effective rank rose 0→3.431→4.036 and V rank 0→2.553→3.609. Deep K/V/KV patch flip rates were 13.3/1.0/12.0%, with exact donor-target rates 10.7/0/9.7%.

## Method

Pilot 01 used a three-layer, 64-dimensional, four-head decoder-only Transformer. Each episode sampled a five-state permutation; prompts gave its table, start and horizon. Training covered lengths 1–5. Frozen evaluation emitted and reread states, with 120 cases per reported horizon. K/V interventions selected baseline-correct donor/recipient episodes with identical three-token prefixes but different successors, aggregating approximately 300 pairs equally across 60 prefixes.

## Interpretation

This establishes use of external serial computation and deep routing states in the trained network. Its first prediction was trained as the next intermediate state, so the one-shot comparison measures this network’s immediate output. Separately trained direct-answer models are assessed in E26. The multiseed script changes sampling seeds and loads one checkpoint; it supplies intervention-sampling repetitions.

## Artifacts and reproduction

**Code checkpoint and intervention outputs**

Read the pilot report, final checkpoint and intervention JSONs. Scripts retain /mnt/data paths; adapt them in a working copy. cotstep_continue.py imports cotstep_500, which is absent. The multiseed script resamples one checkpoint. See docs/REPRODUCTION.md.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/P1_fixed_weights/cotstep.py](../../evidence/P1_fixed_weights/cotstep.py) | code |  |
| [evidence/P1_fixed_weights/cotstep_continue.py](../../evidence/P1_fixed_weights/cotstep_continue.py) | code |  |
| [evidence/P1_fixed_weights/cotstep_eval2.json](../../evidence/P1_fixed_weights/cotstep_eval2.json) | result_or_record |  |
| [evidence/P1_fixed_weights/cotfreedom_mechanism.json](../../evidence/P1_fixed_weights/cotfreedom_mechanism.json) | result_or_record |  |
| [evidence/P1_fixed_weights/cotfreedom_kv_control.json](../../evidence/P1_fixed_weights/cotfreedom_kv_control.json) | result_or_record |  |
| [evidence/P1_fixed_weights/cotfreedom_stratified.json](../../evidence/P1_fixed_weights/cotfreedom_stratified.json) | result_or_record |  |
| [evidence/P1_fixed_weights/cotfreedom_multiseed.py](../../evidence/P1_fixed_weights/cotfreedom_multiseed.py) | code |  |
| [evidence/P1_fixed_weights/cotstep.pt](../../evidence/P1_fixed_weights/cotstep.pt) | checkpoint |  |

## Related hypotheses

H20

- C04: Pilot 01 multiseed repetitions resample one checkpoint.
- C05: Pilot 01 one-shot scores the first output of the same step-trained model.
