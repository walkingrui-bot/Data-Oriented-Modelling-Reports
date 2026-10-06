# Training Order and Blueprint Front-Loading

## Question

Can early training history move a repeatedly trained operation toward the front of a later execution blueprint, even when the final task accepts multiple equally valid execution orders?

## Controlled setup

A causal Transformer was trained on a task with two independent computational branches:

- **A**: one highly reusable fixed affine operator.
- **B**: one context-selected affine operator from a four-operator family.

The final answer combines the two branch results. During the final training phase, both traces are accepted by the loss:

- `A -> B -> answer`
- `B -> A -> answer`

The final phase therefore does **not** prescribe which branch must be emitted first.

All dose-response conditions start from the **same model initialization** and receive the same 300-step flexible-order final training phase. Only the amount and identity of early subtask training changes.

## Dose-response: early A training

| A-only pretraining steps | A-first after final training | B-first | Exact valid trace | Final answer |
|---:|---:|---:|---:|---:|
| 0 | 32.35% | 67.65% | 100% | 100% |
| 10 | 72.06% | 27.94% | 100% | 100% |
| 30 | 100.00% | 0.00% | 100% | 100% |
| 70 | 100.00% | 0.00% | 100% | 100% |

The preference crosses from a baseline B-first majority to complete A-first commitment after 30 early A-only steps.

## Symmetric dose-response: early B training

| B-only pretraining steps | A-first after final training | B-first | Exact valid trace | Final answer |
|---:|---:|---:|---:|---:|
| 0 | 32.35% | 67.65% | 100% | 100% |
| 10 | 0.00% | 100.00% | 100% | 100% |
| 30 | 0.00% | 100.00% | 100% | 100% |
| 70 | 0.00% | 100.00% | 100% | 100% |

Ten B-only pretraining steps are already sufficient to produce complete B-first commitment in this initialization.

## What changes internally?

The effect is stronger than a small first-token preference.

When the model is forced to begin with the *non-preferred* branch marker, it often cannot immediately produce that branch value.

After 30 A-only pretraining steps:
- A value is executable first: **100.00%**
- B value is executable first: **5.88%**

After 30 B-only steps:
- A value is executable first: **17.65%**
- B value is executable first: **100.00%**

Thus early training alters the organization of the initial execution state: one branch becomes immediately executable while the other is deferred until later in the generated trajectory.

## Replication / basin dependence

Independent seeds show that curriculum is a strong bias rather than a deterministic law.

Stable-A-first pretraining produced A-first behavior in all three tested seeds, with one seed retaining a mixed 70.6/29.4 split. Variable-B-first pretraining produced B-first commitment in two of three tested seeds; one seed later fell into the A-first basin.

This supports a path-dependent attractor interpretation: early training changes the probability of entering a particular execution-order basin, while later task statistics can still compete with that history.

## CoT externalization: separate mechanism

A separate intervention distinguishes **schedule front-loading** from **external working-state use**.

In this free-order task A and B are computationally independent. Editing the first externally emitted branch value did not reliably force the final answer to use that edited value. The model could often recover from the original context.

By contrast, in the earlier sequential Transformer task, where step 2 genuinely depended on step 1, editing the emitted intermediate state propagated through later computation with about 97–98% fidelity.

Therefore:

1. **Training order can front-load an operation into the execution schedule.**
2. **Externalization becomes a computational tape when later computation causally depends on the externalized state.**
3. These are related but distinct mechanisms.

## Interpretation

The controlled evidence supports a model in which early training can establish an execution habit:

`early repeated computation -> early executable state -> preferred first blueprint step -> later computations are organized after it`

The final task can preserve this schedule even when another execution order is equally valid and receives the same final training objective.

This provides a concrete mechanism by which curriculum order can become internal computation order.
