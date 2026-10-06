# EXP005 — Neural Network → Explicit Algorithm

## Result

The trained answer-only network contains **20,454 parameters**. Its valid-domain behavior was decompiled into a short explicit program with:

1. a complement-based relation rule,
2. six modular arithmetic coefficient pairs,
3. one XOR formatting rule.

The explicit program was compared against the original neural network over the complete valid finite state space, including all six presentation orders of the three context facts.

- exhaustive cases: **52,272**
- exact two-token agreement: **52,272/52,272 = 100.0000%**

## Causal identification of the planner algorithm

The network's attention strongly suppresses the queried fact and mixes the other two. This was tested by intervening on context facts:

- mutate the queried/target fact: **0.00%** of interventions changed downstream behavior;
- mutate a non-target fact: **97.92%** changed downstream behavior;
- mean fraction of payload outputs changed after target-fact mutation: **0.00%**;
- mean fraction changed after non-target-fact mutation: **73.28%**.

Across valid permutation contexts, the two non-target operation identities uniquely determine the missing target operation. The extracted planner therefore implements a complement rule.

## Extracted executor programs

The executor was probed over all 121 `(x,y)` payload pairs for each planner state. Without using blueprint labels, the outputs fit exactly six modular linear forms, each with two formatting states:

- operation 0, order 0: `(x + 2y) mod 11`
- operation 0, order 1: `(2x + y) mod 11`
- operation 1, order 0: `(2x + 3y) mod 11`
- operation 1, order 1: `(3x + 2y) mod 11`
- operation 2, order 0: `(4x + y) mod 11`
- operation 2, order 1: `(x + 4y) mod 11`

The output-format state follows the inferred truth table `style_bit XOR [goal==2]`.

## Matrix-level formation operator

The first planner affine map has shape **(64, 72)**, numerical rank **64**, and bias norm **0.771366**.

Its singular spectrum is concentrated but not low-rank in the strict sense:
- 90% Frobenius energy: first **18** singular directions
- 95%: first **28**
- 99%: first **44**

The full 12-state plan is not linearly explicit before the first nonlinearity, but becomes 100% linearly readable immediately after the first `tanh`. The local operator at a concrete input is:

`J(x) = diag(1 - tanh^2(W1 x + b1)) @ W1`

so the plan-closing step is an input-dependent gain transformation applied after the shared affine transport.

## Decompiled program

The standalone file `decompiled_tiny_blueprint_algorithm.py` contains the recovered algorithm and no neural-network weights.

## Evidence boundary

The exact equivalence result applies to the complete **valid finite domain defined by this synthetic task**. It establishes that, for this trained network and domain, parameterized neural behavior can be replaced by an explicit recovered algorithm with identical outputs.
