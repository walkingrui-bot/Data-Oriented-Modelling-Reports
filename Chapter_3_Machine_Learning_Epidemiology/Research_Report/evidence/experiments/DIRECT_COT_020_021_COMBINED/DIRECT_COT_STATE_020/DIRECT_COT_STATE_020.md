# DIRECT-vs-CoT-STATE-020

## Question

What is different between a model that answers directly and the same model when it is allowed to generate a chain of thought? Does CoT provide information that is strictly necessary for correctness, merely add computation depth, or reorganize the state into a different answer-ready representation?

## Controlled three-mode world

One 32-hidden-state GRU is trained jointly on all 16 four-bit XOR problems in three modes:

- DIRECT: answer immediately.
- BLANK-THINK: traverse the same number of intermediate recurrent steps as CoT but feed blank `X` values instead of relation values.
- CoT: explicitly generate and re-inject `r1=A xor B`, `r2=C xor D`, `r3=r1 xor r2`, then answer.

All three modes freely generate their complete target sequences exactly correctly on all 16 problems. The comparison therefore does not conflate mechanism with task failure.

## Different internal endpoints despite identical answers

At the answer marker, mean hidden-state L2 distances are approximately:

- Direct vs CoT: 2.76
- Direct vs Blank: 2.53
- Blank vs CoT: 2.08

Mean absolute final answer margin is about 8.86 for Direct, 11.12 for Blank and 11.97 for CoT.

Thus identical correct hard answers can be implemented by different state organizations.

## Relation-state decodability

Leave-one-out linear probes show a strong distinction.

Direct:
- prompt end: r1≈56%, r2≈56%, final answer=100%
- answer state: r1≈50%, r2≈50%, final answer=100%

CoT:
- prompt end: r1=100%, r2≈94%, answer≈69%
- after the first relation value: r1=r2=answer=100%
- relation variables remain linearly readable through the rest of the trajectory.

Blank-think eventually makes the final answer fully readable but does not preserve r1/r2 as stable explicit variables; their decodability decays toward chance.

The result separates:
- Direct: early answer-compression.
- Blank: extra recurrent computation without explicit relation re-injection.
- CoT: extra computation plus persistent relation-state organization.

## Immediate answer-gate surgery

From each intermediate hidden state the normal future trajectory is discarded and the common `answer` token is fed immediately.

Direct is already 100% answer-ready at prompt end.

Blank:
- prompt end 50%
- first blank stage 50%
- second ≈56%
- third 100%

CoT:
- prompt end 50%
- after r1 50%
- after r2 ≈69%
- after r3 100%

A further distinction appears: in CoT the final answer is linearly decodable much earlier than the state is ready for the model's normal answer gate. Information availability is therefore not the same object as action/readout readiness.

## Working interpretation

In this controlled problem, CoT is not necessary for correctness because the Direct route has learned a direct answer map. Extra recurrent depth is independently useful, as shown by Blank-think. Relation-bearing CoT additionally reorganizes the state so intermediate variables remain explicit and reusable.

The next experiment therefore asks a different question: for one particular problem and model state, how can the amount and type of additional reasoning needed before answer-readiness be calculated mathematically?
