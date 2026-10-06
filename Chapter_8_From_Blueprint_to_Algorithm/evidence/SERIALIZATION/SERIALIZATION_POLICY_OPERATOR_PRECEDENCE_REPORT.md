# Serialization Policy, Operator Precedence, and CoT Front-Loading

## Core question

Does long-run autoregressive supervision of the form

`prompt -> reasoning -> answer`

itself encourage a model to place early-reliable computation before later conditional computation?

A second question is whether the first emitted token must contain the whole early computation. The experiments treat the first reasoning token instead as a possible **branch / commitment token** whose following token span carries the operation result.

## Experiment 1 — Independent branches: serialization alone

Two independent computations were available:

- A: a fixed, highly reusable affine operator;
- B: a context-selected operator.

Both reasoning orders were accepted by the loss:

`A -> B` and `B -> A`.

The same initialization was trained under:

- `reasoning -> answer` (R2A);
- `answer -> reasoning` (A2R).

The first matched seed produced a complete order reversal:
- R2A converged to **100% A-first**;
- A2R converged to **100% B-first**;
- both models reached **100% valid traces and answers**.

A second matched seed reversed the preferred basin:
- R2A converged to **100% B-first**;
- A2R converged to **100% A-first**.

### Supported interpretation

Serialization policy changes the execution-order attractor, but **answer placement alone does not deterministically force the reusable operator to the front** when the two computations are independent. Initialization and later optimization can decide which equally valid order wins.

This is an important boundary condition for the stronger hypothesis.

---

## Experiment 2 — Dependent computation: later work truly requires earlier state

The task was changed so that B was no longer independent.

1. A is computed from the prompt.
2. The result of A determines which B operator is selected.
3. B is then applied to A's result.
4. The final answer equals the B result.

The textual training loss still accepted both descriptions:

`A -> B -> answer`

and

`B -> A -> answer`.

Thus the training target did not explicitly require A to be written first.

### Three R2A replications

Across three independent initializations:

- seed 13101: **100% A-first**, 100% exact, 100% answer;
- seed 13202: **100% A-first**, 100% exact, 100% answer;
- seed 13303: **100% A-first**, 100% exact, 100% answer.

So `reasoning -> answer` consistently selected the causally prior, reusable operation A as the first emitted computation.

### Matched A2R models

With the same initializations but `answer -> reasoning`:

- seed 13101: **100% B-first**;
- seed 13202: **100% A-first**;
- seed 13303: **100% B-first**.

All reached 100% exact valid traces and answers.

The post-answer reasoning order therefore remained basin-dependent rather than consistently respecting the computational prerequisite.

### Supported interpretation

When later computation genuinely depends on earlier state, `reasoning -> answer` creates a stable optimization advantage for the causal order. Once the answer is already emitted, that pressure is substantially weaker: the subsequent reasoning can be organized as a variable explanation path.

---

## Experiment 3 — What does the first reasoning token do?

For the three dependent R2A models, the first reasoning token was treated as a branch marker.

After the prompt:

- forcing `<A>` and asking for the next value produced the correct A result in **100%** of cases for all three seeds;
- forcing `<B>` first produced the correct B result in only **1.96–5.88%** of cases;
- mean B-first immediate readiness: **3.92%**.

Therefore the first token does not need to encode the complete operator. It can act as a **commitment / routing token** that moves the autoregressive state into the computation span for that operator.

A more appropriate unit is:

`branch token -> short token trajectory -> completed operator state`

rather than `one operator = one token`.

---

## Experiment 4 — Front-stable / rear-fragmented structure

Across the three mature R2A models:

- early A-value entropy: **0.02835**;
- later dependent B-value entropy: **0.14210**;
- early A-value logit margin: **6.6383**;
- later B-value logit margin: **4.6926**.

Thus the causally early, repeatedly reusable computation is substantially more confident and sharply committed than the later conditional computation.

This is a controlled instance of:

`stable front -> conditional / finer rear`

without explicitly adding a front-weighted loss.

---

## Experiment 5 — Direction of externalized causal state

In the first dependent R2A model, the emitted A value was replaced with a false value while the original prompt was retained.

The model propagated the counterfactual A state into the B computation and final answer in **40.20%** of cases. This is partial rather than complete dependence because the Transformer can also recover A again from the original context.

In the matched A2R model, the answer was instead corrupted before the reasoning tail.

The later B value copied the false answer in **97.06%** of cases, while the later A value remained correct in **99.02%**.

This exposes a striking serialization asymmetry:

- `reasoning -> answer`: earlier reasoning can become a causal working state for the answer;
- `answer -> reasoning`: the committed answer can become a causal conditioning state for the later explanation.

The latter is a controlled form of post-answer rationalization.

---

## Mechanistic conclusion

The evidence supports a more precise version of the hypothesis:

1. **Autoregressive serialization is not passive display.** Output order can feed back into computation order.
2. **The first token can be a commit token rather than the full computation.** An operator may occupy a multi-token span.
3. **CoT-before-answer preferentially stabilizes causal prerequisites when later computation depends on them.**
4. **This produces a measurable front-to-back confidence gradient:** early reusable computation becomes sharp and immediately executable; later conditional computation remains less sharply committed.
5. **Answer-before-reasoning changes the causal direction.** Once the answer is committed, later reasoning may be organized around that answer rather than constituting the computation that produced it.
6. **Serialization alone is not sufficient to force one universal order.** For independent operations, initialization can determine which valid order wins. The strong front-loading effect appears when the task contains a real dependency structure that CoT can externalize.

A compact computational picture is:

`prompt`
`-> high-support prerequisite becomes executable`
`-> commit token`
`-> operator token span / state externalization`
`-> later operator gains eligibility`
`-> finer conditional computation`
`-> answer`

The experiments therefore support the idea that long-run `reasoning -> answer` supervision can shape not only how a model *reports* reasoning, but also the temporal organization of the computations it learns to execute.
