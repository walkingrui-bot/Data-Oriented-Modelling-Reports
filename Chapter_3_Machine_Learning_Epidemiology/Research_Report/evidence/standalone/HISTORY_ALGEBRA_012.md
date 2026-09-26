# HISTORY-ALGEBRA-012 — Whole-history permutation algebra → Prompt–CoT–Answer control field

## Question

Treat the entire training history as an ordered mathematical object rather than attributing effects to individual epochs. With the training multiset fixed exactly, which algebraic features of the whole ordering generate differences in the later Prompt–CoT–Answer control field?

## Design

A common 16-parameter 2D recurrent foundation is first trained with a fully symmetric objective over four training groups A–D. Each group corresponds to one of the four 2-bit questions and contains both chain variants, so the diagnostic history has exactly the same training multiset under every condition.

Starting from the identical common foundation, apply exactly one SGD update from each group. All **4! = 24** permutations are exhausted. No training example is added or removed; only the operator composition order changes.

For each final model, evaluate a fixed canonical Prompt→CoT→Answer trajectory for all four questions and compute every token's 4D final-answer control vector `g_t = ∂z_final/∂e_t`. The four questions × seven visible positions × four embedding dimensions form a **112-dimensional control-field fingerprint G(H)** for each history H.

Common foundation natural chain: `00|00|11|00`; answer signature: `0011`. Diagnostic main learning rate η=0.002. At this η the 24 histories produce 1 distinct natural chain signatures and 1 answer signatures; the control-field comparison itself is made on the same fixed canonical trajectories so every coordinate is aligned across all 24 histories.

## Whole-history algebra

Let each group define an SGD operator `U_a(θ)=θ−ηg_a(θ)`. For a permutation H=(s1,s2,s3,s4):

`Θ(H)=U_s4 ∘ U_s3 ∘ U_s2 ∘ U_s1 (θ0)`.

The first-order term `−η Σ_a g_a` is identical for all 24 histories. The leading order-sensitive term is second order:

`δθ_H^(2) = (η²/2) Σ_(a<b) x_ab(H) [H_b g_a − H_a g_b]`,

where `x_ab=+1` when a precedes b and −1 otherwise. Thus the first nontrivial whole-history coordinates are the six pairwise order/commutator coordinates AB, AC, AD, BC, BD, CD.

## Main result 1 — pairwise order is the leading history algebra

A linear projection of the 24 centered control fields onto the six pairwise order coordinates explains **98.792%** of the total history-conditioned control-field energy at η=0.002. Permutation parity alone explains only **0.000%**.

The exact second-order commutator formula predicts the 24 centered final parameter vectors with cosine **0.977626** and relative Frobenius error **24.807%**. Passing these second-order parameter predictions through the exact nonlinear control-field readout gives field cosine **0.982958** and relative error **33.745%**. The fully linearized `history commutator → parameter → control-field Jacobian` prediction has cosine **0.983015** and relative error **33.734%**.

Across the small-η scan, the absolute residual of the second-order parameter expansion scales approximately as **η^3.173**, directly matching the expected emergence of third- and higher-order history-composition terms beyond the pairwise commutator layer.

## Main result 2 — S4 Fourier anatomy of the whole history

The 24 histories form the permutation group S4. The centered function `H ↦ G(H)` was decomposed exactly with character projectors into S4 isotypic components. Energy fractions are:

- standard_31: **91.5635%**
- two_dim_22: **0.1849%**
- standard_sign_211: **8.2516%**
- sign: **0.0000%**

This is a basis-independent decomposition of the entire history effect by permutation symmetry. It distinguishes genuine order structure from arbitrary epoch numbering. The corresponding CSV also records how much of each irrep is already captured by the six pairwise-order coordinates and where the higher-order residual lives.

## Main result 3 — the control field itself is low dimensional

SVD of the 24×112 centered history-conditioned control-field matrix gives mode-1 energy **97.366%**, top-2 **99.967%**, and top-3 **99.998%**. Thus the 24 possible histories do not create 24 unrelated geometries; the observable control-field displacement occupies a small set of coupled response modes.

## Where the whole-history algebra manifests

The fraction of total history-conditioned control-field variation carried by each aligned visible position is:

- Q_A: **67.317%**
- Q_B: **8.547%**
- ROUTE_MARK: **2.087%**
- ROUTE_BIT: **11.912%**
- CODE_MARK: **8.662%**
- CODE_BIT: **1.301%**
- ANSWER_MARK: **0.174%**

These values refer to the same canonical Prompt→CoT→Answer trajectories. They therefore measure where the algebra of the past becomes visible in the later control geometry, rather than mixing in different strings.

## Mathematical interpretation

The experiment supports a hierarchy:

`fixed training multiset`
`→ ordered product of noncommuting training operators`
`→ pairwise Lie-bracket layer (leading order)`
`→ higher-order composition residuals with cubic-and-higher scaling`
`→ final parameter displacement`
`→ token-wise Prompt–CoT–Answer control-field displacement`.

The causal object is therefore not an isolated historical event. A training item acquires its effect through its ordered relations with the rest of the history. At leading order those relations are six antisymmetric pairwise coordinates; higher-order residuals quantify genuinely multi-event composition that is not reducible to a sum of isolated events.

## Evidence boundary

This experiment establishes the history-algebra decomposition in a completely enumerated four-group diagnostic history on a small recurrent model. All 24 permutations are observed, so no permutation class is extrapolated. The η-scaling audit identifies the pairwise commutator layer as the leading order-sensitive term and measures the remaining higher-order contribution directly. The resulting objects are designed to be carried forward to larger histories using log-signature / Lie-basis approximations rather than epoch-wise attribution.

## Files

- `all_24_history_permutations.csv`
- `all_24_final_parameters.csv`
- `all_24_control_fields.csv`
- `pairwise_commutator_parameter_basis.csv`
- `pairwise_commutator_control_field_basis.csv`
- `pairwise_history_relation_strength.csv`
- `learning_rate_hierarchy_scan.csv`
- `S4_irrep_control_field_decomposition.csv`
- `history_control_field_svd.csv`
- `control_field_parameter_jacobian.csv`
- `control_field_variation_by_token_position.csv`
- `history_order_hierarchy_scaling.png`
- `S4_irrep_control_field_energy.png`
- `pairwise_order_relation_strength.png`
- `history_algebra_by_sequence_position.png`
- `all_24_history_control_mode_scores.png`

## Extended hierarchy audit

The full learning-rate sweep was extended from the perturbative regime into a deliberately non-perturbative range. At η=0.0005, the six pairwise order coordinates explain 99.9109% of control-field history energy and the second-order parameter prediction has cosine 0.998777. At η=0.001 the corresponding values are 99.6612% and 0.994890. At η=0.002 all 24 histories still retain the same natural CoT and answer signatures while pairwise order explains 98.7921%.

The second-order parameter residual scales approximately as η^3.173 over the small-η regime. At η=0.012, pairwise field energy explained falls to 28.0042% and four natural CoT signatures appear; by η=0.048 there are 12 distinct joint CoT/answer signatures. This directly separates a pairwise Lie/commutator regime from a higher-order history-composition regime.

For each unordered pair, the empirical pairwise control-field basis was also compared with the local theoretical basis `(η²/2)(∂G/∂θ)(H_b g_a-H_a g_b)` at η=0.002. Direction cosines are AB=0.997586, AC=0.928870, AD=0.812965, BC=0.972461, BD=0.992899, CD=0.992972. The remaining magnitude error is consistent with the measurable higher-order terms already present at this η.

Additional files:

- `learning_rate_hierarchy_scan_wide.csv`
- `pairwise_commutator_field_basis_closure.csv`
- `history_algebra_regime_transition.png`
