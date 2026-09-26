# TRACE-CHANNEL-015 — Which teaching traces identify a latent control geometry?

## 1. Question

DISCRETE-TEACHER-DIMENSION-014 established an identifiability gap: a student can learn an autoregressive hard-token CoT/answer map while realizing that map with a continuous control field whose rank or orientation differs from the teacher. TRACE-CHANNEL-015 asks what additional teaching trace is sufficient to shrink that geometric equivalence class.

The underlying teacher, visible vocabulary, six-token prompt, six-token CoT, answer format, student architecture and complete 729-prompt universe remain fixed. This experiment changes only the information channel supplied during training.

The focused pathology panel uses teacher intrinsic dimensions d=2,3,5 with two common student initializations. d=2/3 are the sensitive cases in which hard-token supervision can create extra continuous modes; d=5 is a high-dimensional control in which rank is already usually correct and orientation/subspace recovery remains diagnostic.

## 2. Trace-channel interventions

Seven supervision channels are compared:

1. **hard** — thresholded 0/1 CoT and answer tokens only.
2. **hard_repeat** — the same hard supervision plus additional locally jittered prompt contexts with hard teacher labels. This adds more boundary samples without exposing a graded teacher value.
3. **counterfactual_order** — hard supervision plus local paired counterfactuals that reveal only whether the teacher logit rises or falls between two nearby contexts; magnitude remains hidden.
4. **probability** — hard tokens plus the teacher's continuous sigmoid probability.
5. **quantized_margin4** — hard tokens plus four magnitude bins of the signed pre-threshold margin.
6. **margin** — hard tokens plus the full signed pre-threshold margin.
7. **local_numeric** — full margins on the original discrete universe plus continuous margins in local jittered contexts, supplying both value and local-neighbourhood geometry.

The primary geometry readouts are the global control-field r95, the fraction of student control energy inside the known teacher causal subspace, and principal-angle error to that subspace.

## 3. More hard language is not equivalent to graded geometry

For the d=3 pathology slice, hard-only supervision produces median global r95=4.0 even though the teacher rank is 3. Teacher-subspace energy is 0.9137 and mean principal-angle error is 5.413 degrees.

Adding more local contexts while still exposing only hard labels improves subspace alignment, but rank recovery is not stable across the two initializations: hard_repeat median r95=3.5 (one seed 3, one seed 4). Providing only local counterfactual order is also insufficient here: r95 remains 4.0.

Thus in this controlled case, additional symbolic examples and ordinal 'which way did it move?' information do not by themselves uniquely identify the teacher's continuous field.

## 4. A small graded trace crosses an identifiability threshold

Four-bin signed confidence already changes the geometry sharply. At d=3 it restores r95=3 in both initializations, raises teacher-subspace energy to 0.9818, and reduces mean principal-angle error to 1.293 degrees.

The explicit confidence-quantization ladder makes the threshold more visible. The hard token already supplies the sign. We then quantize only the magnitude of the teacher margin into 1, 2, 4 or 8 levels.

At d=3:

- 1 magnitude level: r95=4, teacher-subspace energy 0.90545;
- 2 magnitude levels: r95=3, teacher-subspace energy 0.9704, mean angle 1.572 degrees;
- 4 levels: r95=3, energy 0.97870;
- 8 levels: r95=3, energy 0.98575.

Because the hard token already carries the sign, moving from one to two magnitude levels adds only one coarse confidence bit. In these two d=3 initializations, that single extra graded bit is enough to restore the correct 95%-energy control rank. Finer quantization then improves orientation and energy concentration progressively rather than causing another discrete rank transition.

The same ladder in d=2 and d=5 shows the same monotonic geometric sharpening even where r95 is already correct: extra graded levels increasingly suppress off-teacher directions.

## 5. Exact numeric traces progressively pin the field down

At d=3, full signed-margin supervision yields teacher-subspace energy 0.9868 and mean angle 0.848 degrees; adding local numeric contexts gives energy 0.9882. At d=5, hard supervision already has the correct r95 but only 0.9880 of energy in the teacher subspace. Full margin raises this to 0.9971 with angle 0.154 degrees.

Probability supervision is intermediate. It contains a continuous value but compresses the teacher logit nonlinearly; in this optimization setting it recovers rank but leaves more orientation error than signed margin. Because probability and margin are mathematically invertible away from exact 0/1 saturation, this contrast should be interpreted as a property of the training signal parameterization and loss, not as a proof that probabilities contain less information in principle.

## 6. Information type matters more than visible task accuracy

Across regimes, visible bit accuracy stays in a relatively narrow high range while control geometry changes substantially. In particular, hard-repeat and counterfactual-order conditions can expose more examples or more relational facts without producing the geometric recovery achieved by a small amount of graded confidence.

This separates two targets:

- **behavioral identification** — reproducing the discrete CoT/answer labels;
- **geometric identification** — recovering the teacher's latent continuous control subspace and rank.

The first can be achieved with hard language traces while the second remains underdetermined.

## 7. Interpretation: tokenization creates a geometric equivalence class

The hard token map partitions the teacher's continuous state into decision regions. Every continuous student field that realizes the same region labels is behaviorally acceptable. TRACE-CHANNEL-015 shows that different teaching traces shrink this equivalence class at different rates.

Repeated hard contexts constrain the location/shape of decision boundaries. Counterfactual ordering constrains some local orientation. Graded confidence constrains distance to the boundary. Full numeric margins constrain both sign and calibrated displacement. Local numeric contexts add neighbourhood geometry.

In this case the largest identifiability jump occurs when the trace first carries even coarse distance-to-boundary information. This provides a concrete mechanism for how a teacher's intrinsic control dimension may or may not survive linguistic discretization.

## 8. Connection to the language and control-field programs

The result sharpens the previous hypothesis that a language model's low-dimensional control field could reflect a human teacher. The dimensionality observed in a student is jointly determined by at least three objects:

`teacher intrinsic geometry -> trace channel -> student/history dynamics -> recovered rotating control field`.

A low-dimensional student field therefore cannot by itself identify the dimensionality of the teacher. The relevant empirical question for natural language becomes: which graded, temporal, relational and repeated-context constraints in real linguistic interaction play the role of the confidence channel in this synthetic experiment?

This gives a direct interface to the parallel linguistic line: linguistic analysis can propose trace features; the current line can intervene on those features and quantify how strongly they reduce control-field non-identifiability.

## 9. Evidence boundary

This experiment uses a synthetic finite teacher and a small tanh autoregressive student. The strongest focused comparison uses d=2,3,5 and two student initializations. The confidence-ladder result directly supports a graded-trace identifiability threshold in this controlled system. It does not establish that natural human language carries margin-like values in the same form, nor that one extra bit will be sufficient in larger language models.

## 10. Files

- `trace_channel_focus_models.csv` — all focused d=2/3/5 model-level results.
- `trace_channel_focus_aggregate.csv` — regime-level summaries.
- `confidence_quantization_ladder_models.csv` — 1/2/4/8 magnitude-level models.
- `confidence_quantization_ladder.csv` — quantization summaries.
- `trace_channel_key_results.csv` — compact main comparison.
- `trace_channel_subspace_recovery.png`
- `trace_channel_principal_angle.png`
- `confidence_quantization_subspace_recovery.png`
- `confidence_quantization_rank.png`
