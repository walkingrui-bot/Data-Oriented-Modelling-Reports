# LANGUAGE-HIERARCHICAL-GENERATORS-017

## Question

Experiments 015–016 established two layers of structure in the same English technical corpus:

1. the dominant local language motion field is strongly anisotropic and concentrated in a few high-energy directions;
2. visible language units act as state-dependent, compositional and generally noncommutative transformations of predictive state.

Experiment 017 asks the next hierarchical question:

> **When language is built upward from words into phrases and relational constructions, are higher levels only compositions of lower-level operators, or do they introduce additional generators?**

The experiment separates three possibilities:

- exact composition of lower-level lexical operators;
- predictable phrase-level residual structure;
- relation-level residual generators associated with condition, modality, negation, contrast, conjunction, alternative and relative/complement constructions.

---

## 1. Predictive state space

The same 431,826-character corpus used in 014–016 was tokenized into 102,408 word/punctuation tokens.

A 128-state next-token vocabulary was used. For every usable position, a predictive distribution was estimated from the longest supported 1–4 token suffix and mapped with the Hellinger transform `sqrt(p)`. Frequency-weighted PCA then produced a common 10-dimensional predictive-state coordinate system:

\[
x_t=\Psi(c_{<t})\in\mathbb R^{10}.
\]

A visible token `a_t` therefore produces an empirical state transition

\[
x_t\rightarrow x_{t+1}.
\]

All operator fitting used deterministic held-out context identities, so repeated occurrences of the same suffix were assigned to the same side of the train/test split.

---

## 2. Lexical operator layer

For each sufficiently supported token `a`, an affine state-dependent operator was fitted:

\[
T_a(x)=A_a x+b_a.
\]

All 128 vocabulary states had sufficient support.

Across held-out transitions:

- token-specific reset MSE: **0.142824**
- state-dependent lexical operator MSE: **0.121060**

Thus the word/punctuation layer retains the state-dependent operator effect established in 016.

---

## 3. Phrase operators: composition explains most structure, but not all predictable structure

For every sufficiently frequent exact bigram `(a,b)`, two predictions were compared on held-out contexts.

Sequential lexical composition:

\[
\hat x_{t+2}^{\mathrm{comp}}=T_b(T_a(x_t)).
\]

Direct phrase operator:

\[
\hat x_{t+2}^{\mathrm{phrase}}=T_{ab}(x_t).
\]

A total of **185** exact phrase operators passed the support thresholds.

Weighted held-out errors were:

| Model | MSE |
|---|---:|
| Sequential lexical composition | 0.141692 |
| **Direct phrase operator** | **0.112759** |

The direct phrase operator reduced held-out error by **17.3%** relative to sequential lexical composition.

This establishes that an exact phrase carries predictable transition structure beyond the approximation obtained by repeatedly applying independently fitted lexical operators.

### Residual-operator control

For each phrase, the direct/composed operator difference was compared with a composition-only synthetic target fitted on the identical input states. The high-dimensional spectrum of exact phrase residual operators was similar to the finite-sample synthetic residual spectrum:

- real residual stable rank: **7.73**
- synthetic residual stable rank: **7.38**
- real top-3 residual energy: **29.2%**
- synthetic top-3 residual energy: **34.1%**

Therefore the exact-phrase layer supports **additional predictable transition information**, while the current evidence for new primitive generators is obtained more cleanly at the relation layer below.

---

## 4. Relation layer

Seven operational relation classes were defined by recurrent surface markers:

- condition: `if`, `when`, `unless`, `otherwise`
- contrast: `but`, `however`, `although`
- alternative: `or`
- conjunction: `and`
- negation: `not`
- modality: `must`, `may`, `can`
- relative/complement: `that`, `which`

The purpose of these labels is not to assume a semantic theory. They provide reproducible groups of recurrent constructions whose residual state transformations can be compared.

For an occurrence beginning at position `t`, the lexical prediction over a span of length `h` is

\[
\hat x_{t+h}^{(0)}
=
T_{a_{t+h-1}}\circ\cdots\circ T_{a_t}(x_t).
\]

The observed residual is

\[
r_t^{(h)}=x_{t+h}-\hat x_{t+h}^{(0)}.
\]

A relation-level generator is supported when the mean residual associated with a relation class predicts held-out residual movement better than a relation-independent residual.

---

## 5. Relation identity predicts additional held-out movement

The clearest scale was a three-token horizon.

Across all seven relation classes, a class-specific residual vector reduced held-out error by:

- **5.42%** relative to lexical composition alone;
- **3.29%** relative to a global relation-independent residual correction.

A label-shuffle control repeatedly reassigned the same trajectories to random relation classes. Under 30 shuffles per horizon, the corresponding gain over the global correction had:

- mean: **−0.18%**
- 95th percentile: **+0.13%**

The observed **+3.29%** relation-specific gain is therefore associated with the real relation grouping rather than the availability of an extra class-specific parameter alone.

Examples at the three-token horizon include:

| Relation | Gain vs lexical composition | Gain vs global residual |
|---|---:|---:|
| Modality | 16.2% | 9.84% |
| Condition | 12.5% | 9.47% |
| Contrast | 4.31% | 3.10% |
| Relative/complement | 3.74% | 1.59% |
| Conjunction | 1.37% | 0.66% |

The evidence therefore supports a hierarchical construction:

\[
\text{higher relation movement}
=
\text{lexical composition}
+
\text{small relation-specific residual generator}.
\]

---

## 6. The new relation generators are themselves extremely low-dimensional

The seven held-out-supported relation residual means were centred, frequency weighted and decomposed by SVD.

Their generator space has:

- **stable rank: 1.327**
- participation rank: **1.684**
- top-3 energy: **95.18%**
- 95% energy dimension: **3**

Thus higher-order relational structure does introduce additional systematic movement, but that additional movement is itself concentrated into only a few directions.

The first relation-generator mode strongly separates the operational relation classes. For example, modality and condition occupy opposite sides of this dominant residual axis in the present corpus.

This provides the first direct hierarchical evidence that language grows upward by **composition plus sparse low-dimensional generator insertion**, rather than by constructing a new unrestricted state space at every linguistic level.

---

## 7. Relation generators are not simply the three strongest lexical movement axes

All observed one-token predictive-state displacements were independently decomposed.

The word-level movement field has:

- stable rank: **2.833**
- top-3 movement energy: **63.14%**
- 95% movement dimension: **9**

The relation residual generators were then projected onto this movement basis.

The top three lexical movement axes captured only **22.63%** of relation-generator residual energy.

Principal angles between the top-three relation-generator subspace and the top-three lexical movement subspace were:

\[
19.70^\circ,\quad61.41^\circ,\quad77.97^\circ.
\]

Therefore the hierarchy has a mixed structure:

- one higher-order direction substantially reuses the dominant lower-level movement geometry;
- additional relation directions are largely transverse to the three strongest lexical movement axes.

The evidence supports **reuse plus low-dimensional expansion**.

---

## 8. Hierarchical generator rule

Experiments 015–017 now support the following recursive rule.

Let \(\mathfrak G_\ell\) be the generator family available at linguistic level \(\ell\). Then the next level is formed by composition of the existing family plus a small residual generator space:

\[
\boxed{
\mathfrak G_{\ell+1}
=
\langle\mathfrak G_\ell\rangle_{\circ}
\oplus
\mathfrak R_{\ell+1}
}
\]

where

- \(\langle\mathfrak G_\ell\rangle_{\circ}\) is the state-dependent noncommutative closure of lower-level operators under ordered composition;
- \(\mathfrak R_{\ell+1}\) is the empirically required residual generator space at the higher relation level.

In the current relation-layer experiment,

\[
\operatorname{stable\ rank}(\mathfrak R_{\mathrm{relation}})=1.327,
\]

and three residual modes contain 95.18% of the measured class-level residual energy.

The higher level therefore adds structure economically: most movement is inherited through composition, and the added relation structure occupies a small number of new directions.

---

## 9. Revised mathematical picture of language

The combined experimental picture is now:

\[
\text{surface units}
\rightarrow
\text{state-dependent lexical operators}
\rightarrow
\text{ordered noncommutative composition}
\rightarrow
\text{phrase trajectories}
\rightarrow
\text{small relation-specific residual generators}
\rightarrow
\text{higher linguistic trajectory}.
\]

The dominant movement field remains low-dimensional, while the repertoire of possible language actions grows through operator composition and sparse hierarchical expansion.

This distinguishes three quantities that should no longer be conflated:

1. **state dimension** — the representational space in which predictive/relational states are embedded;
2. **dominant movement dimension** — the few directions carrying most local language motion;
3. **generator-family dimension** — the number of reusable transformation modes available for composing language actions.

Complex language can therefore occupy a large information space while using a small dominant movement geometry and a structured hierarchy of generator families.

---

## 10. Evidence scope

The current evidence is direct for a 102,408-token English technical corpus, using count-derived predictive states rather than neural hidden states. It establishes the hierarchy through held-out lexical transitions, 185 frequent exact phrases, seven recurrent relation classes, shuffle controls and subspace analysis.

Within this scale, the data support the model:

> **language grows by noncommutative composition of state-dependent lower-level operators, with higher relational structure adding small, low-dimensional residual generator spaces.**

This result supplies the missing hierarchical component required to integrate experiments 015–017 into a single mathematical form of language.

---

## Evidence files

- `LANGUAGE-HIERARCHICAL-GENERATORS-017.py`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_lexical.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_phrases.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_relations.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_additive.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_additive_shuffle.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_generators.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_generator_scores.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_relation_generator_modes.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_alignment.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_principal_angles.csv`
- `LANGUAGE-HIERARCHICAL-GENERATORS-017_movement_spectrum.csv`
