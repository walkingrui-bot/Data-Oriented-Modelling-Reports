# LANGUAGE-TEACHER-GEOMETRY-015

## Question

Why does natural-language training drive a model toward a control geometry dominated by only a few modes?

This experiment moves the analysis from the trained model back into the training sequence itself. The target is not model architecture. The target is the mathematical geometry of language as a teacher.

The central distinction is:

> Language need not be a strictly 2–3 dimensional state space. It may instead possess a **low-dimensional dominant local transition field**, with additional weaker dimensions supplied by longer context and finer structure.

## Corpus

The same 431,826-character English technical corpus used in `LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014` was retained, with the same 64-token character vocabulary.

This keeps the teacher-side analysis directly comparable with the previous GRU control-field measurements.

## 1. Teacher transition operator

Let

\[
P_{ij}=P(x_{t+1}=j\mid x_t=i)
\]

be the empirical one-step transition matrix and let \(\pi\) be the empirical unigram distribution.

The baseline-independent, frequency-weighted teacher transition operator is

\[
A=D_{\pi}^{1/2}\left(P-\mathbf 1\pi^\top\right).
\]

The subtraction removes the no-context baseline. The left weighting gives frequently visited states the appropriate contribution to the training world.

We then compute

\[
A=U\Sigma V^\top.
\]

This gives a language-side spectrum before any neural network is trained.

Equivalently,

\[
P(\cdot\mid i)
\approx
\pi+
\sum_k a_k(i)v_k.
\]

If only a few singular modes dominate, many surface tokens are not producing independent changes in the future distribution. They are reusing a small family of shared transition directions.

## 2. Main teacher-side result

| Sequence world | Stable rank | Participation rank | 95% energy dim | Top-3 energy |
|---|---:|---:|---:|---:|
| Original language | **2.481** | **4.335** | 13 | **71.95%** |
| First-order Markov surrogate | 2.490 | 4.351 | 13 | 71.82% |
| Word-order shuffled | **2.481** | **4.335** | 13 | **71.95%** |
| Within-word letters shuffled | 1.410 | 1.959 | 13 | 80.46% |
| IID with same unigram distribution | 5.406 | 12.719 | 25 | 39.35% |
| Synthetic 2D world | 2.495 | 2.947 | 3 | 99.60% |
| Synthetic 3D world | 4.462 | 6.366 | 7 | 55.65% |
| Synthetic 6D world | 11.402 | 27.918 | 45 | 21.78% |
| Letters only, spaces/punctuation removed | **2.261** | **4.124** | 9 | **69.76%** |

The natural-language one-step transition field is therefore strongly anisotropic before model training. Its stable rank of 2.48 is already close to the low-dimensional regime observed in the trained model's future-control Jacobian.

The same unigram frequencies without linguistic sequential structure do not reproduce this geometry: the IID control has stable rank 5.41 and only 39.35% of transition energy in its top three modes.

Thus frequency imbalance alone does not generate the low-dimensional teacher field.

## 3. Higher-order language is not literally three-dimensional

The conditional next-token distribution was then estimated using progressively longer observed contexts. For every context length, the frequency-weighted variation of the next-token predictive states was decomposed by SVD.

| Context length | Retained contexts | Stable rank | Top-3 energy |
|---:|---:|---:|---:|
| 1 | 64 | **2.481** | **71.95%** |
| 2 | 878 | 3.637 | 51.66% |
| 3 | 2,538 | 4.283 | 45.71% |
| 4 | 6,374 | 4.595 | 43.83% |
| 5 | 7,562 | 4.680 | 43.61% |

This rejects the strongest form of the statement that “language itself is exactly 2–3 dimensional.”

What the data support is more specific:

> **The dominant local motion of language is low-dimensional. Longer context opens additional predictive directions, but these are progressively weaker corrections layered onto a small common backbone.**

This distinction closely matches the control-field measurements: the model has a large available space and multiple residual singular modes, while most effective future-control energy is concentrated into a few dominant directions.

## 4. Where do the dominant modes come from?

The first singular mode of the original teacher operator is overwhelmingly organized around broad symbol classes.

For the first right singular vector, a five-class decomposition (space / vowel / consonant / digit / punctuation-other) explains **94.2%** of its variance.

Its strongest positive coordinate is the space token; its main opposing coordinates are ordinary letters. This identifies a strong segmentation / boundary-versus-continuation direction.

The second mode contrasts major letter-transition classes, with `e`, `a`, `i`, `o`, `h`, `u`, and `y` on one side and common consonantal continuations on the other. The second and third left singular modes retain substantial coarse-class structure (approximately 48% and 44% class-explained variance respectively), while finer orthographic relations add the remaining detail.

When the entire corpus is reduced to only five broad token classes, its transition field has:

- stable rank: **1.535**
- top-2 energy: **92.07%**
- top-3 energy: **99.17%**

So broad class transitions alone already form an extremely low-dimensional skeleton.

However, the low-dimensionality is not solely a whitespace artifact. Removing spaces and punctuation entirely and retaining only the continuous letter stream still gives stable rank **2.261** and top-3 energy **69.76%**.

The strongest interpretation is therefore not “spaces create the two dimensions.” It is:

> **Language repeatedly reuses a small number of relational transition motifs — boundary/continuation, broad orthographic class steering, and finer completion/continuation relations — across a much larger surface vocabulary.**

## 5. Structural interventions

### Word-order shuffle

Non-whitespace chunks were globally shuffled while each chunk and every whitespace span were preserved.

This destroys long-range word order while preserving the complete character-bigram count matrix. As expected mathematically, the one-step teacher spectrum is exactly unchanged:

- stable rank: 2.481 before and after
- top-3 energy: 71.95% before and after

Therefore the observed one-step low-dimensional backbone does not require sentence-level word order.

### First-order Markov surrogate

A new sequence was generated from the empirical language transition matrix itself. Higher-order syntax, semantics, discourse, and fixed lexical sequences were removed while the one-step transition field was retained.

Its teacher spectrum remains essentially identical:

- stable rank: 2.490
- top-3 energy: 71.82%

This shows that the low-dimensional local backbone can exist independently of higher-order linguistic organization.

### Within-word shuffle

Alphabetic characters were randomly permuted inside every word while word lengths, boundaries, punctuation and global character counts were preserved.

This does not expand the teacher field. It makes the dominant backbone even more concentrated:

- stable rank falls to 1.410
- top-3 energy rises to 80.46%
- total structured transition signal decreases substantially

This indicates that real spelling and within-word sequential organization contribute **additional secondary dimensions** rather than causing the original low-dimensional collapse. Destroying those relations removes signal and leaves an even more dominant boundary/class skeleton.

## 6. Proposed mechanism: shared-gradient geometry

The teacher-side result suggests a direct mechanism for the control collapse observed after language training.

For next-token learning, many different surface contexts repeatedly generate error/update directions associated with the same few large transition modes.

If

\[
A=U\Sigma V^\top
\]

has

\[
\sigma_1,\sigma_2,\sigma_3
\gg
\sigma_4,\sigma_5,\ldots,
\]

then training repeatedly reinforces the shared directions \(v_1,v_2,v_3\). Context-specific distinctions still create additional directions, but their gradients are less coherent across the corpus and have lower accumulated energy.

A high-dimensional model can therefore retain large representational capacity while acquiring a much flatter **effective control geometry**.

The working chain is:

\[
\text{repeated language transition motifs}
\rightarrow
\text{anisotropic teacher operator}
\rightarrow
\text{anisotropic accumulated training updates}
\rightarrow
\text{low-dimensional high-gain control field}.
\]

This provides a concrete language-side explanation for `LANGUAGE-CONTROL-DIMENSION-COLLAPSE-014`.

## 7. Revised statement

The evidence now supports the following formulation more strongly than the earlier shorthand “language is 2–3 dimensional”:

> **Natural language contains many dimensions of detail, but its dominant local transition field is concentrated into a small number of repeatedly reused relational modes. Language training therefore acts as a dimensionality-selective teacher: it preferentially engraves these shared high-energy directions into the model's effective control geometry, while higher-order and context-specific distinctions occupy weaker residual modes.**

This also clarifies the relation to human motor control. The relevant analogy is not that the full nervous system or full linguistic state is literally two-dimensional. It is that a high-dimensional substrate may repeatedly express behavior through a small, state-dependent set of dominant control coordinates.

## Evidence files

- `LANGUAGE-TEACHER-GEOMETRY-015_teacher_expansion.csv`
- `LANGUAGE-TEACHER-GEOMETRY-015_context.csv`
- `LANGUAGE-TEACHER-GEOMETRY-015_modes.csv`

