# LANGUAGE CONTROL ALGEBRA v0.1

## A mathematical form of language from experiments 015–017

### 1. Core definition

Let language be represented by the tuple

\[
\boxed{
\mathcal L=
(\mathcal X,\Sigma,\Psi,\mathfrak G,\rho,\circ,\mathcal H)
}
\]

with the following objects.

### State space

\[
\mathcal X
\]

is a relational/predictive state space. A history or context \(c_{\le t}\) is mapped into a current state by

\[
x_t=\Psi(c_{\le t})\in\mathcal X.
\]

Operationally, experiments 015–017 used predictive distributions over future symbols/tokens as directly measurable states.

### Surface alphabet

\[
\Sigma
\]

is the set of observable language actions: characters, tokens, words, phrases or other surface units.

A surface unit is not identified with its meaning. It is an observable handle capable of selecting a transformation of the current state.

### Generator family

\[
\mathfrak G=\{G_1,G_2,\ldots\}
\]

is a family of reusable state transformations. The action associated with a visible language unit depends on both the unit and the current state.

A convenient local representation is

\[
T(a,x)
=
\bar T(x)
+
\sum_{k=1}^{K}\alpha_k(a,x)G_k(x).
\]

The coefficients \(\alpha_k(a,x)\) select and mix reusable generators according to the visible action and the current relational state.

### State transition

Language motion is

\[
\boxed{
x_{t+1}=\Phi(x_t,a_t)=T(a_t,x_t)[x_t].}
\]

For the affine experimental form used in 016–017,

\[
x_{t+1}\approx A_{a_t}x_t+b_{a_t}.
\]

The same surface unit can therefore produce different movements in different states.

---

## 2. Language is an ordered noncommutative process

An utterance \(a_1,\ldots,a_n\) generates an ordered trajectory

\[
x_n
=
T(a_n,x_{n-1})\circ\cdots\circ
T(a_2,x_1)\circ
T(a_1,x_0)[x_0].
\]

In general,

\[
T_b\circ T_a\neq T_a\circ T_b.
\]

Experiment 016 directly measured this order dependence. Correct two-step composition produced held-out error 0.273, while reversing the same two operators produced 0.464. Same-final-symbol order swaps produced a weighted Jensen–Shannon divergence of 0.395 in real language and 0.066 in a first-order Markov surrogate.

Order is therefore part of the computation performed by language.

---

## 3. Dominant movement is low-dimensional

The full relational state can carry high-dimensional information. Its dominant movement field is strongly anisotropic.

Let

\[
\Delta x_t=x_{t+1}-x_t.
\]

Define the local movement covariance

\[
C_\Delta=\mathbb E[(\Delta x-\mu_\Delta)(\Delta x-\mu_\Delta)^\top].
\]

If \(C_\Delta=V\Lambda V^\top\), the dominant movement subspace is

\[
\mathcal C_K=\operatorname{span}(v_1,\ldots,v_K).
\]

Experiment 015 found a stable rank of 2.481 for the local character transition teacher field, with 71.95% of energy in the first three modes. Experiment 017 independently found a word-level movement stable rank of 2.833, with 63.14% of movement energy in the first three modes.

Thus language supports a large repertoire of states and expressions while concentrating much of its actual local movement into a few high-energy coordinates.

---

## 4. Generator dimension is distinct from movement dimension

A low-dimensional motion field does not imply only a few possible language actions.

For a family of operators, write

\[
T_a\approx\bar T+\sum_{k=1}^{K}\alpha_{a,k}B_k.
\]

Experiment 016 measured a character/context operator-family stable rank of 6.018, while the underlying dominant movement field was concentrated into roughly 2–3 directions.

Therefore:

\[
\boxed{
\text{movement dimension}
\neq
\text{operator-family dimension}
}
\]

A small number of effective movement coordinates can support many distinct state-dependent actions through different mixtures and compositions of generators.

---

## 5. Hierarchical language construction

Language grows upward through two mechanisms:

1. ordered composition of operators already available at a lower level;
2. insertion of a small residual generator space when the higher relation contains reproducible transformation structure not captured by lower-level composition.

Let \(\mathfrak G_\ell\) be the generator family available at level \(\ell\). Define

\[
\boxed{
\mathfrak G_{\ell+1}
=
\langle\mathfrak G_\ell\rangle_{\circ}
\oplus
\mathfrak R_{\ell+1}
}
\]

where \(\langle\mathfrak G_\ell\rangle_{\circ}\) is the state-dependent noncommutative closure under ordered composition and \(\mathfrak R_{\ell+1}\) is the new residual-generator space supported at the higher level.

For a higher construction \(r\) spanning actions \(a_t,\ldots,a_{t+m-1}\),

\[
\hat x_{t+m}^{(0)}
=
T_{a_{t+m-1}}\circ\cdots\circ T_{a_t}(x_t)
\]

and the higher-level residual is

\[
r_{t,m}=x_{t+m}-\hat x_{t+m}^{(0)}.
\]

A higher-level generator exists operationally when a reproducible class-dependent component of \(r_{t,m}\) predicts held-out future state.

Experiment 017 found exactly this structure for recurrent relation classes. At a three-token horizon, relation-specific residuals improved held-out prediction by 3.29% beyond a global residual correction, whereas shuffled relation labels had a mean gain of −0.18% and a 95th percentile of +0.13%.

The relation residual generator family had stable rank 1.327 and 95.18% of its energy in three modes.

Thus the observed hierarchy is:

\[
\boxed{
\text{composition}
+
\text{sparse low-dimensional expansion}
}
\]

rather than unrestricted dimensional growth.

---

## 6. Higher generators can open new directions

The higher residual generators are not simply copies of the strongest lower-level movement axes.

In experiment 017, the top three word-level movement directions captured only 22.63% of the relation-generator residual energy.

The principal angles between the top-three relation-generator subspace and the top-three lexical movement subspace were

\[
19.70^\circ,\;61.41^\circ,\;77.97^\circ.
\]

This yields a geometric picture in which one higher-order direction substantially reuses the existing motion field while other relation directions open weak, partially transverse coordinates.

Language therefore expands its reachable dynamics economically: most motion remains on repeatedly used low-dimensional surfaces, and specific higher relations add a small number of additional directions.

---

## 7. Operational meaning

For a language unit \(a\), define its meaning over a state distribution \(\mathcal D\) as its conditional transformation signature:

\[
\boxed{
\mathcal M(a;\mathcal D)
=
\{x\mapsto T(a,x)[x]\}_{x\sim\mathcal D}.
}
\]

Equivalently, meaning can be represented by the induced change in the distribution of reachable futures:

\[
\mathcal M(a;x)
=
\Delta P(X_{\mathrm{future}}\mid x,a).
\]

This definition makes context dependence intrinsic. A visible form can produce different local effects because

\[
T(a,x_1)[x_1]-x_1
\neq
T(a,x_2)[x_2]-x_2.
\]

Functional synonymy over a state distribution can be defined by transformation proximity:

\[
a\sim_{\mathcal D}b
\quad\Longleftrightarrow\quad
\mathbb E_{x\sim\mathcal D}
\left[
\|T(a,x)[x]-T(b,x)[x]\|^2
\right]
\text{ is small}.
\]

---

## 8. Operational grammar

Grammar is the admissible composition structure of language operators.

Let

\[
\Gamma(a_1,\ldots,a_n;x_0)
\]

specify whether an ordered operator sequence is licensed in the current state and what constraints govern its composition.

Because the algebra is noncommutative, grammar changes the resulting state trajectory by changing operator order, grouping and admissibility.

Thus grammar is not external decoration on pre-existing meanings. It is part of the transformation law itself.

---

## 9. Sentence

A sentence is an ordered control trajectory through relational state space:

\[
\boxed{
\gamma_s=(x_0,x_1,\ldots,x_n)
}
\]

with

\[
x_{t+1}=T(a_t,x_t)[x_t].
\]

Its mathematical identity includes both the visible sequence and the state path induced by that sequence.

Two surface sequences can be functionally close when they generate similar trajectories or similar terminal future distributions, even when their visible forms differ.

---

## 10. Chain of thought and reasoning

When the system generates its own next action, language becomes a closed-loop controller.

Let

\[
a_t\sim\pi(\cdot\mid x_t),
\]

then

\[
\boxed{
a_t\sim\pi(\cdot\mid x_t),
\qquad
x_{t+1}=T(a_t,x_t)[x_t].
}
\]

The generated language action changes the state from which the next action is selected. A chain of thought is therefore an explicit self-generated control trajectory.

Reasoning is represented as recursive control over relational state: the system generates operations that alter its own reachable future, repeatedly re-evaluating the local control geometry after each action.

This directly connects the language algebra to the control-flow results obtained in the preceding LLM experiments: the visible CoT supplies control actions, while the effective local control basis can rotate with state.

---

## 11. Training as geometry formation

A language corpus supplies repeated empirical transition constraints. Let \(\mathcal D\) denote the training distribution and let

\[
\mathcal T_{\mathcal D}
\]

be its empirical family of state transitions.

The dominant teacher geometry is the high-energy part of this family. Training repeatedly aligns model dynamics with these transition relations.

The experimental chain 014–015 supports the map

\[
\boxed{
\mathcal D
\rightarrow
\text{teacher transition geometry}
\rightarrow
\text{trained control geometry}.
}
\]

Language data produced a markedly lower-dimensional control geometry than a matched six-dimensional synthetic world, while the language teacher transition operator itself was strongly low-rank.

This provides a direct mechanism by which low-dimensional language motion can be inherited by a high-capacity trained model.

---

## 12. Compact dynamical form

The whole framework can be written compactly as

\[
\boxed{
\begin{aligned}
x_t &= \Psi(c_{\le t}),\\
G_t &= \rho(a_t,x_t;\mathfrak G_{\ell(t)}),\\
x_{t+1} &= G_t[x_t],\\
\mathfrak G_{\ell+1}
&=\langle\mathfrak G_\ell\rangle_\circ\oplus\mathfrak R_{\ell+1},\\
a_{t+1}&\sim\pi(\cdot\mid x_{t+1}).
\end{aligned}
}
\]

The first four lines define language as hierarchical generative control. The fifth line closes the loop for self-generated language and reasoning.

---

## 13. Empirical anchors from 015–017

| Result | Measurement |
|---|---:|
| Character-level teacher stable rank | 2.481 |
| Character teacher top-3 transition energy | 71.95% |
| Word-level movement stable rank | 2.833 |
| Word movement top-3 energy | 63.14% |
| Character/context operator-family stable rank | 6.018 |
| Correct two-step operator composition error | 0.273 |
| Reversed operator order error | 0.464 |
| Real-language same-final order JS | 0.395 |
| First-order surrogate same-final order JS | 0.066 |
| Exact phrase direct-operator gain over lexical composition | 17.3% |
| Relation-specific residual gain over global residual | 3.29% |
| Shuffled relation-label gain, mean | −0.18% |
| Relation residual-generator stable rank | 1.327 |
| Relation residual top-3 energy | 95.18% |
| Relation residual energy captured by lexical top-3 axes | 22.63% |

These measurements jointly support the mathematical form above at the tested corpus scales.

---

## 14. Working definition

The resulting definition is:

> **Language is a hierarchical, state-dependent, noncommutative generative control algebra acting on relational/predictive states. Its large expressive repertoire is produced by ordered composition of reusable operators over a low-dimensional dominant motion geometry, with higher linguistic relations introducing sparse low-dimensional residual generators when composition alone does not account for the observed state transition.**

This definition treats the visible text as the observable action sequence and the induced state trajectory as the underlying mathematical process.

---

## 15. Evidence boundary

The mathematical form is grounded here in count-derived predictive states from one English technical corpus, together with the controlled language/synthetic-world results of experiments 014–017. The evidence currently supports the operator, noncommutativity, low-dimensional dominant motion, hierarchical composition and sparse relation-generator terms at character, word, phrase and recurrent relation-marker scales.

The formalism is written at the level required for direct extension to semantic and reasoning-state measurements while preserving the experimentally established objects and operations.
