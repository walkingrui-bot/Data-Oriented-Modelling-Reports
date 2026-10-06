# Tiny Blueprint EXP001 — Explicit Blueprint Calibration

**Seed:** 20261006  
**Model parameters:** 11,323  
**Dataset:** 2,880 synthetic contexts; 80/10/10 train/validation/test  
**Blueprint space:** 3 operations × 2 argument orders × 2 styles = **12 exact plans**

## Goal

Establish the smallest controllable system in which a context is compiled into an explicit blueprint before answer execution. The blueprint is a discrete executable plan, so its full probability distribution can be enumerated exactly.

## Synthetic context mechanism

Each context contains goal `G`, rule `R`, order bit `O`, style bit `S`, numeric payload `X,Y`, and distractor `D`. Presentation order is randomly shuffled.

The true blueprint is composed from multiple context variables:

- `operation = permutation_R(G)`
- `argument_order = O XOR parity(R)`
- `style = S XOR [G==2]`

This prevents the blueprint from being a copy of any single context token.

## Model

Order-invariant token encoder → compact context state → autoregressive three-slot blueprint decoder:

`context -> OP -> ARG_ORDER -> STYLE`

The model has **11,323 parameters**.

## Results

- Test slot accuracy — OP: **100.00%**
- Test slot accuracy — ARG_ORDER: **100.00%**
- Test slot accuracy — STYLE: **100.00%**
- Test exact whole-blueprint accuracy: **100.00%**
- 100 random presentation-order shuffles, same semantic context: **100.00%** retained the same correct top blueprint.

For one held-out example:

- True blueprint: `SUB | YX | LONG`
- Top predicted blueprint: `SUB | YX | LONG`
- Exact probability of true blueprint: **0.98328805**
- Blueprint posterior entropy: **0.141668 bits**
- Executed true blueprint answer: `RESULT=-3`
- Executed top blueprint answer: `RESULT=-3`

Top-5 exact blueprint probabilities:

- 1. `SUB | YX | LONG`: p=0.98328805
- 2. `MAX | YX | LONG`: p=0.01128036
- 3. `ADD | YX | LONG`: p=0.00475468
- 4. `SUB | YX | SHORT`: p=0.00038716
- 5. `SUB | XY | LONG`: p=0.00021547

## Evidence supported by EXP001

The tiny network learned a context-to-blueprint mapping whose output is a discrete executable object. Because the blueprint space has only 12 states, `p(B|C)` is exactly enumerable rather than approximated by sampling. Presentation-order shuffling leaves the semantic plan stable by construction of the encoder.

This establishes the calibration platform for the next experiment: remove explicit blueprint supervision and test whether a hidden state acquires the same plan structure when trained only through downstream answer likelihood.
