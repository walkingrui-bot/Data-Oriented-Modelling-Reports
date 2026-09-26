# STOPPING-GEOMETRY-022 — CoT as a state-space optimal stopping problem

## Question

Can "how much CoT this particular question needs" be calculated from the trained model itself rather than assigned from task labels or a fixed token budget?

COT-BUDGET-GEOMETRY-021 showed that equal token lengths can correspond to very different state transitions and that the set of correct budgets may be non-contiguous. STOPPING-GEOMETRY-022 turns this observation into an explicit stopping problem and tests a learned state-based stopping function.

## Exact 6-bit autoregressive system

One 48-state GRU is trained on the complete 64-question six-bit hierarchical XOR universe in three modes:

- Direct
- Blank-think
- relation-bearing CoT

The CoT path has five genuine intermediate relations. Two independent initializations (22022 and 22023) achieve 64/64 exact free generation and 64/64 correct answers in every mode. A third attempted initialization did not meet this exact-generation inclusion criterion and is excluded from stopping analysis.

All stopping results below are therefore measured on models that already possess the complete trained CoT behavior.

## State-space formulation

Let h be the current model state and pi(a|h) its thought-action policy.

Stopping now incurs a risk L_stop(h). Continuing incurs compute cost lambda and expected future value.

The optimal value function is

V(h) = min[
    L_stop(h),
    lambda + E_(a~pi(.|h)) V(F_theta(h,a))
].

The optimal stopping region is

S* = {h : L_stop(h) <= lambda + E V(F_theta(h,a))}.

A CoT length is therefore not fundamental. It is the first hitting time of this stopping region along one particular thought trajectory.

For a fixed trained CoT trajectory, define the answer-readiness set

A(q) = {k : the immediate answer from h_k agrees with the model's correct full-CoT answer}.

In this experiment the full-CoT answer is correct on all 64 questions, so agreement with full-CoT and gold correctness coincide.

## Oracle result: one model, same formal task, radically different minimum depths

Seed 22022:
- 32/64 questions are already answer-ready at the prompt (k=0).
- 6 first become answer-ready at k=1.
- 11 first become ready at k=2.
- 13 first become ready at k=3.
- only 2 require the full k=5 path.

Mean oracle first-ready depth = 1.203/5, corresponding to 75.94% compute saving relative to always running all five relations.

Seed 22023:
- 36/64 are ready at k=0.
- 12 first at k=1.
- 8 first at k=2.
- 8 first at k=3.
- none require k=4 or k=5 as their first correct point.

Mean oracle depth = 0.813/5, a potential 83.75% saving.

The required depth is therefore a property of the exact model-question state, not merely formal task depth.

## The readiness set is usually not an interval

For seed 22022, 39/64 questions have more than one connected component in A(q).
For seed 22023, 43/64 do.

Example (seed 22022):

question `000101` is answer-ready at

A(q) = {0, 2, 4, 5}.

The same genuine relation trajectory can therefore move the model:

ready -> not ready -> ready -> not ready -> ready.

This reproduces the non-monotonic blank-compute behavior from 021 without using blank tokens. Even correct semantic reasoning actions can move the immediate answer readout across its decision surface multiple times before the final state.

Thus "minimum needed CoT", "maximum safe CoT" and "optimal fixed length" are three different objects.

## Fixed-depth policies

For seed 22022, fixed depth accuracy is:

k=0: 50.0%
k=1: 34.4%
k=2: 50.0%
k=3: 59.4%
k=4: 75.0%
k=5: 100%.

No fixed depth below five preserves full accuracy, despite an oracle average requirement of only 1.20 steps.

The gap is produced entirely by problem-conditioned state geometry.

## Observable stopping signals

At every state k the following quantities are computed without using the gold answer:

- answer logit and absolute margin
- answer confidence / entropy
- gradient norm of the answer logit with respect to hidden state
- local distance proxy |margin| / ||grad||
- hidden-state norm
- movement since the previous thought step
- change in answer logit
- current relation depth

A state-geometry stopper additionally receives the complete current hidden state.

The stopping classifier is trained to predict whether the current immediate answer is already the same as the known correct full-CoT answer. Evaluation uses eight-fold question-grouped cross-validation: all six states from each held-out question remain outside stopper training.

## Learned stopping results

Seed 22022:
- full fixed CoT: 100% accuracy, mean 5.00 steps
- state-geometry stopper: 96.875% accuracy, mean 2.813 steps
- compute saving: 43.75%
- oracle: 100%, mean 1.203 steps

Seed 22023:
- full fixed CoT: 100% accuracy, mean 5.00 steps
- state-geometry stopper: 95.313% accuracy, mean 2.891 steps
- compute saving: 42.19%
- oracle: 100%, mean 0.813 steps

The learned state-value approximation captures substantial adaptive structure but remains far from the oracle boundary.

## Why confidence alone is insufficient

Conservative scalar threshold policies save little compute at high accuracy.

Seed 22022:
- confidence/absolute-margin threshold: 98.44% accuracy, mean 4.92 steps
- local boundary-radius threshold: 100%, mean 5.00 steps

Seed 22023:
- confidence/absolute-margin: 96.88%, mean 4.45
- boundary radius: 100%, mean 4.61

A state can be confidently wrong with respect to its eventual full-CoT answer. Therefore local confidence is not a complete stopping statistic.

The state-based stopper improves substantially because the decision depends on where the model is in its learned relational dynamics, not only on distance from the current answer hyperplane.

## Relationship to 020 and 021

DIRECT-vs-CoT-STATE-020 separated three mechanisms:

1. Direct answer compression.
2. Extra recurrent computation depth.
3. Relation-bearing CoT that explicitly re-injects and preserves intermediate variables.

COT-BUDGET-GEOMETRY-021 then showed that per-problem thought value is a finite state-space path integral and that equal budgets can have different effects depending on thought-action identity.

STOPPING-GEOMETRY-022 closes the chain: choosing when to stop is an optimal stopping problem over this state/action geometry.

## Working definition

A scalar "reasonable CoT length" exists only after fixing:

- a model theta,
- a question q,
- a thought policy pi,
- an answer-readout rule,
- a correctness/risk criterion,
- and a compute cost.

The fundamental object is the stopping set S* in state space.

For one realized trajectory gamma=(h_0,h_1,...), the familiar token budget is merely the sequence of times at which gamma enters or leaves S*.

Because gamma can cross the stopping boundary repeatedly, the induced set of acceptable lengths can be non-contiguous.

## Final implication

"What answers need CoT?" is more precisely:

Which prompt states lie outside the model's acceptable answer region but possess a learned thought trajectory that reaches it at acceptable cost?

A problem needs no additional CoT when its prompt state is already in the stopping region.

It needs CoT when the prompt state is outside and learned thought actions perform enough state-space work to enter the region.

Additional CoT becomes harmful when later thought actions move the state back out of the region or add more expected error/cost than future improvement.

The unresolved engineering problem is not to discover one universal optimal length, but to learn an accurate value/stopping function over the model's relational state geometry. The approximately 42-44% compute saving obtained here with a simple held-out state classifier, compared with a 76-84% oracle opportunity, measures the remaining gap.
