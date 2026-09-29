# CG-024 Protocol — Sequential Intervention Execution & Final Acceptance

## Research question
Can the explicit World Program formed in CG-023 continue to produce correct consequences when a new operation arrives *during* rollout, including beyond the training horizon?

## Base world and state
- Same 600 fixed 4D affine worlds from CG-023: `x[t+1] = M x[t] + b`.
- Same whole-world split: 400 train / 100 dev / 100 frozen test.
- Same equilibrium and temporal evidence banks.
- Same 8-candidate explicit World Program; persistent iterative state remains only `(M_k, b_k, logits_k)`.
- No GRU/RNN hidden state and no candidate-selection rule.

## Sequential operations used in training
Each training query contains one event inside the rollout:
1. **Impulse**: add a signed value to one state coordinate at event time.
2. **Clamp**: set one state coordinate to a value at event time.
3. **Persistent force**: add a signed input to one coordinate of `b` from event time onward.

Training final horizons are 4–8 only. The event is placed 1–4 steps before the endpoint. The world object is never supervised with the true `M` or `b`; only consequences and observed evidence are used.

## Training variants
The first pass added event-consequence supervision while preserving passive rollout and equilibrium losses. It established persistent-force execution but revealed that local impulse/clamp effects required sharper transition calibration.

The final model adds two mechanism-consistency objectives without parameter supervision:
- **event-delta consistency**: predicted `(event consequence − passive consequence)` matches the observed event-induced delta;
- **evidence replay**: the generated world must reproduce its own observed one-step temporal transitions and equilibrium forcing-response pairs.

## Frozen acceptance panel
The final model is tested at horizons 8, 16, 32, 64 and 128.

For each trained primitive operation, correct execution is paired against:
- event ignored;
- same operation applied to the wrong variable;
- a shifted event time.

Persistent forcing additionally receives a delayed-onset timing control. An earlier-onset control is retained because longer exposure can partially compensate amplitude bias.

A completely untrained composition is also tested:
- persistent force at `h-4` followed by an impulse at `h-2`;
- correct two-event execution is compared with omitting the second event.

All primary summaries aggregate repeated horizons and two seeds within each of 100 independent frozen test worlds, then bootstrap over worlds.

## Preservation checks
- Passive temporal rollout at horizons 32/64/128 is compared with the frozen CG-023 checkpoint on the same evaluation panel.
- Generated relation distance to the known `M` is measured after training as a diagnostic only; true `M` never enters the training loss.
- Checkpoint reload, matrix constraints and explicit-state serialization/replay are verified.
