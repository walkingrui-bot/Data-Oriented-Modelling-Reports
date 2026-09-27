# Generative Control Map — Round 1

## Question

If raw attention is only one implementation-level routing signal, what should an engineer measure instead to observe and control a language model's ongoing generation activity?

This experiment treats the engineering target as three separate questions:

1. **Read state** — what future generation mode is the model already moving toward?
2. **Find sources** — which parts of history actually change that future?
3. **Find leverage** — where can an intervention still causally steer the future?

The combined object is called the **Generative Control Map (GCM)**.

Its main causal component is the **Future Causal Influence field (FCI)**.

For a historical element i and horizon H:

FCI_t(i;H) = divergence between the future continuation distributions with and without a counterfactual change to history element i, accumulated over the chosen future horizon.

This is deliberately architecture-agnostic. Attention weights may help implement the underlying computation, but FCI is defined by what actually changes the future.

## Task

Three independently trained tiny causal Transformers were tested.

Each example contained:
- four binary history cues;
- a query specifying which cue is relevant;
- content;
- four future output positions.

Crucially, the first two future outputs were identical under generation modes A and B. The two modes diverged only at the third and fourth output positions.

Therefore a one-step metric cannot simply read the visible next token and infer which mode is active.

Held-out four-step accuracy was approximately:
- seed 11: 98.8%
- seed 22: 98.0%
- seed 33: 94.1%

## Result 1 — Future causal influence finds the history that actually matters

For every example, each of the four history cues was independently flipped.

The metric then measured how much this counterfactual changed the model's later output distribution at the first delayed A/B divergence.

Top-1 recovery of the truly queried history position, restricted to examples where the model's delayed prediction itself was correct:

| Instrument | Mean top-1 recovery |
|---|---:|
| Mean raw attention over layers | 42.5% |
| Last-layer raw attention | 20.8% |
| Immediate next-step causal effect | 32.9% |
| One-backward linearized future influence | 38.7% |
| **Exact future causal influence (FCI)** | **90.6%** |

Chance is 25%.

Across all examples, including model failures, exact FCI still recovered the queried history in 81.8% of cases, versus 41.1% for mean raw attention.

This makes the practical distinction sharp:

- attention asks how routing mass is allocated;
- next-step effect asks what changes the immediate output;
- FCI asks which history actually changes the **future continuation**.

The delayed-divergence design matters because the relevant generation mode exists before it becomes visible in the next token.

## Result 2 — A model can already be in a future generation mode before the output reveals it

A linear readout was trained on the query-position hidden state to predict the later A/B generation mode.

Mean held-out accuracy across three seeds:

| Layer | Future-mode readout |
|---|---:|
| 1 | 71.9% |
| 2 | 84.4% |
| 3 | 87.0% |
| 4 | 87.0% |

The first two visible future outputs are identical under A and B, yet the internal state becomes increasingly readable as a predictor of the later divergence.

This supports a useful monitoring concept:

**Generation-state readout** = a readout of the future distribution family the current internal state is preparing to generate.

It is an observational instrument, not by itself a causal explanation.

## Result 3 — Readability and controllability are different axes

A generation-mode direction was estimated from training examples as the difference between the mean query state for modes A and B.

On held-out examples, this direction was injected into the query state.

At layer 1, steering B toward A changed future P(A):

0.117 → 0.178 → 0.367 → 0.444 → 0.465
for alpha = 0, 0.5, 1, 1.5, 2.

The reverse intervention moved A toward B:

0.834 → 0.764 → 0.541 → 0.459 → 0.444.

Same-norm random directions were much weaker:
- alpha 1: P(A) ≈ 0.147
- alpha 2: P(A) ≈ 0.189

A second important result emerged: the late query state was easier to read, but changing that same past query position late in the stack had little leverage, because too little downstream routing remained.

Therefore:

**the best place to observe a mode is not necessarily the best place to control it.**

This suggests an engineering dashboard should report at least two distinct layerwise quantities:

- **readability**: how well current state predicts future generation behavior;
- **control gain**: how much a normalized intervention at this site changes the future continuation.

## Result 4 — A cheap local approximation is not yet good enough

A one-backward linearized approximation of future influence improved over some local metrics but recovered the truly relevant history only 38.7% of the time on correct examples.

Therefore this round does **not** justify replacing exact causal rollouts with a simple gradient score.

For engineering use:
- exact/batched counterfactual FCI is the current gold-standard diagnostic;
- efficient Jacobian/JVP or learned surrogate approximations remain an optimization problem.

This negative result is important: the useful upstream concept is established more strongly than a cheap estimator for it.

## Proposed engineering object: Generative Control Map

Instead of one attention heatmap, expose three coordinated views.

### 1. Generation State
"What kind of continuation is the model currently preparing?"

Measured by future-mode / continuation-distribution readouts across layers.

### 2. Future Causal Influence
"Which historical relations are actually shaping that continuation?"

Measured by counterfactual changes to history and divergence of future continuation distributions over a horizon H.

### 3. Control Gain
"Where can we still steer the model effectively?"

Measured by normalized interventions at candidate layers/positions/directions and their effect on future continuation.

The resulting map separates three questions that attention conflates:

**where information is routed, what actually shapes the future, and where an intervention still has leverage.**

## Engineering interpretation

The experiment supports the following replacement for attention-centric instrumentation:

> Do not ask only where the model is looking. Measure what future mode it is forming, which history causally changes that mode, and where the remaining network still provides leverage to redirect it.

In the present toy model:
- raw attention is a weak indicator of the truly relevant history;
- future causal influence is much more discriminative;
- deep states are better for observation;
- earlier states can be better for control;
- a specific learned direction steers future distributions far more than equal-norm random directions.

This is consistent with treating language-model activity as ongoing formation of an effective generation rule rather than as the execution of a single attention map.
