# Tiny Blueprint EXP002 — Context-Built Blueprint

**Seed:** 20261007  
**Parameters:** 14,587  
**Training rule permutations:** 0,1,2,3  
**Validation permutation:** 4  
**Held-out test permutation:** 5 = `(2, 1, 0)`

## Why EXP002

EXP001 proved that a small network can emit an explicit executable blueprint. EXP002 removes the fixed rule-ID lookup shortcut. The current rule is supplied as three `(goal -> operation)` facts inside each context, shuffled on every example. The model must read the current context to determine the requested operation.

## Architecture

A query goal attends over the three current rule facts. The attended context representation is compiled into the three-slot blueprint:

`context facts + query -> OP -> ARG_ORDER -> STYLE`

The 12-state blueprint probability distribution remains exactly enumerable.

## Held-out-rule result

The test set uses a rule permutation never used for training.

- OP accuracy: **100.00%**
- ARG_ORDER accuracy: **100.00%**
- STYLE accuracy: **100.00%**
- Exact whole-blueprint accuracy: **100.00%**
- Mean attention mass on the context fact matching the queried goal: **0.9999**
- Example held-out-context true-blueprint probability: **0.97670686**
- Example blueprint entropy: **0.195706 bits**

## Evidence supported

A tiny network can compile an explicit blueprint from rule relations supplied in the current context and apply that mechanism to an unseen rule permutation. The blueprint is therefore context-built in this calibration task rather than selected from a memorized rule ID.

The next mechanistic step is to train the same task **without blueprint labels**, using only final-answer likelihood, then test whether a latent state recovers the explicit blueprint geometry found here.
