# REASONING-GENERATOR-019

## Question

Apply the closure/residual/surgery assay from REASONING-GENERATOR-018 to a genuinely trained self-generated autoregressive model, without inserting any reasoning-specific hidden update by construction.

The competing empirical question is whether a trained model recruits a reproducible low-dimensional effective generator during multistep integration that is absent from matched non-integrative language composition.

## Paired autoregressive world

A single GRU language model is trained jointly on 32 finite tasks:

- 16 `PARALLEL` cases
- 16 `REASON` cases

Each prompt contains the same four bits A,B,C,D and each target contains exactly 21 generated tokens.

The first two visible CoT blocks are identical in both tasks:

1. A xor B gives r1
2. C xor D gives r2

The third block is matched in length and vocabulary but differs functionally:

- PARALLEL repeats A xor B and answers r1.
- REASON computes r1 xor r2 and answers the integrated result.

Thus sequence length, vocabulary, two preceding computations, answer format and autoregressive mechanism are matched.

The trained model has embedding dimension 16 and hidden dimension 48.

Three independent training initializations were retained. Every model generated all 32 complete CoT+answer sequences exactly correctly in free autoregressive generation: 32/32 exact sequences and 32/32 correct answers for every seed.

## A theoretical boundary: exact microdynamics is already closure

For a standard recurrent language model define the exact token-conditioned transition

T_a(h) = F_theta(h, E(a)).

Every autoregressive trajectory then satisfies

h_(t+1) = T_(a_t)(h_t)

exactly.

Reapplying the trained recurrence to every recorded generated transition gives maximum closure error **0.0e+00** across all three models.

Therefore a genuinely new dynamical update law cannot appear at the complete raw-hidden-state level of this architecture. At that level, reasoning is necessarily in the closure of the same state-dependent token transition family.

A separate "reasoning generator" can only be an *effective* object induced by coarse-graining, restricted operator families or higher-level semantic/relation coordinates.

This distinction is essential when interpreting REASONING-GENERATOR-018: its positive controlled case validated the assay by explicitly adding dynamics outside the language closure. A normal GRU does not possess such an extra microscopic update channel.

## Coarse effective closure assay

To test whether reasoning nevertheless creates a low-dimensional *effective* residual, a deliberately restricted language closure is estimated.

A shared affine state-dependent transition plus token-specific offset is learned only from the first two XOR blocks, pooling PARALLEL and REASON trajectories. These blocks are visibly identical computations in both task modes.

The fitted closure is then evaluated only on the matched third segment.

Across the three exact-generating models:

 seed  parallel_RMSE  reasoning_RMSE  R_over_P  paired_diff_RMS  paired_mode1_energy  paired_top2_energy  paired_top3_energy  paired_r95  paired_stable_rank
19020       0.637389        0.649718  1.019343         0.406563             0.330570            0.538979            0.619412          17            3.025076
19021       0.814104        0.826548  1.015285         0.381595             0.298422            0.474109            0.594618          13            3.350956
19022       0.838997        0.853206  1.016936         0.324582             0.387708            0.545923            0.673422          11            2.579258

The reasoning/parallel residual ratio is only **1.0153–1.0193** (mean **1.0172**).

Thus the genuine integration step does not show a selective jump in closure error relative to the matched-length PARALLEL control.

## Matched excess residual

For each bit pattern and aligned third-segment position, define

d(bits,t) = r_REASON(bits,t) - r_PARALLEL(bits,t),

where both residuals are measured against the same lower-level closure.

If reasoning introduced a shared small generator, D should collapse onto a reproducible low-dimensional subspace.

Instead:

- r95 across the three seeds = **[17, 13, 11]**
- stable rank = **[3.025, 3.351, 2.579]**
- mode-1 energy ranges only about 0.30–0.39
- top-2 energy ranges about 0.47–0.55

The excess therefore does not display the two-mode collapse seen in the controlled 018 positive case.

## Cross-seed reproducibility

The top-2 candidate residual plane is independently estimated in each initialization.

Pairwise mean principal angles are approximately 76–83 degrees, with an overall mean of **80.33°**.

The candidate directions therefore fail the cross-seed reproducibility criterion. Their orientation is largely initialization-specific.

## Candidate functional surgery

For each model, candidate top-2 excess modes are estimated on half of the bit patterns and removed from closure residuals on the held-out half during free generation.

The intervention is not reasoning-selective. Even a 25% attenuation destroys held-out answers in both PARALLEL and REASON tasks across all three models. Full removal likewise destroys both.

This indicates that these coarse residual directions contain generic transition structure required by both task families rather than a reasoning-specific functional module.

## Result

This trained autoregressive case supports the null hypothesis at the level tested:

**No reproducible low-dimensional reasoning generator was detected outside the matched language-composition closure.**

The result is stronger than simply "SVD found no axis":

1. the model freely generates every reasoning chain and answer correctly;
2. matched non-reasoning sequences have the same length, vocabulary and first two computations;
3. reasoning closure error is almost identical to matched parallel closure error;
4. the matched excess residual is relatively high-dimensional;
5. leading residual directions do not align across initializations;
6. residual surgery is nonselective.

## Interpretation

The experiment changes the meaning of the question.

At full microscopic state resolution, a standard autoregressive network cannot literally acquire a second hidden update law during reasoning: every token is processed by the same state-dependent network transition.

Thus the scientifically meaningful question is not:

"Does reasoning add a new microscopic generator?"

but:

"At what coarse-grained relational/semantic representation does the closure of lower-level language operators cease to explain the observed trajectory, and does the remaining effective residual define a reproducible functional generator?"

LANGUAGE-HIERARCHICAL-GENERATORS-017 already operates at such a higher-level relation-state abstraction. The correct next assay should therefore apply closure/residual/surgery to an explicitly learned **semantic/relation state** rather than to complete GRU hidden state.

In other words, 019 provides a negative anatomical control and a boundary theorem: apparent new reasoning generators are representation-level claims. They must be defined relative to a coarse-graining Psi(h), not relative to the complete microscopic recurrence F_theta itself.
