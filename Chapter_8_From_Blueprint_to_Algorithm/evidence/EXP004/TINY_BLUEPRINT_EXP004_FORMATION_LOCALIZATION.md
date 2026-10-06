# Tiny Blueprint EXP004 — Where the Blueprint Forms

This experiment localizes blueprint information across the trained answer-only planner and tests causal transfer from intermediate stages.

## Linear readability by stage

| Stage | Operation | Order | Style | Full 12-state blueprint |
|---|---:|---:|---:|---:|
| goal | 32.90% | 50.08% | 51.10% | 8.03% |
| context_selected | 100.00% | 50.27% | 50.35% | 25.22% |
| planner_input | 100.00% | 100.00% | 66.72% | 66.72% |
| h1 | 100.00% | 100.00% | 100.00% | 100.00% |
| h2 | 100.00% | 100.00% | 100.00% | 100.00% |
| z | 100.00% | 100.00% | 100.00% | 100.00% |

## Causal donor-state transplant

A donor internal state is inserted at a stage, then continued through the remaining planner/executor using a different recipient's numeric payload.

| Stage transplanted | Output follows donor blueprint | Output remains recipient original |
|---|---:|---:|
| planner_input | 100.00% | 12.93% |
| h1 | 100.00% | 12.93% |
| h2 | 100.00% | 12.93% |
| z | 100.00% | 12.93% |

## Raw-component swap control

At planner input, replace exactly one recipient component with the donor component and score against the recipient's original answer.

- swap `goal` only: recipient-answer accuracy **55.77%**
- swap `context_selected` only: recipient-answer accuracy **40.30%**
- swap `order_bit` only: recipient-answer accuracy **55.30%**
- swap `style_bit` only: recipient-answer accuracy **49.83%**

## Interpretation

The earliest stage at which the full 12-state blueprint becomes jointly linearly readable marks the first compact representational formation point under this probe. The earliest stage whose donor transplant makes downstream output follow the donor plan marks the first tested causal control point. These are distinct criteria: readability identifies representational presence; transplant identifies behavioral control.
