# INTERNAL_COORDINATION_012 — Statistically Enhanced PsyMoE

This experiment keeps the public drug-development task and target-level holdout from Experiment 011, then changes the modelling architecture rather than the dataset.

The main change is classical statistics **inside** the heterogeneous evidence system:
- each evidence channel receives its own cubic logistic calibration layer;
- its calibrated log-odds joins the native score/presence input;
- the six channels coordinate through one 16x16 ganglion;
- a masked polynomial logistic model is retained as a precision head.

Pipeline unavailability is represented separately from evidence absence. Training exposes the models to random subsets containing 3-6 available pipelines. Evaluation enumerates all combinations with 0-3 unavailable pipelines.

## Main result
Median full-evidence target-holdout log loss:
- Raw PsyMoE: 0.197891
- Stat-PsyMoE: 0.197868
- Stat-PsyMoE + precision: 0.197769
- Masked polynomial: 0.197928
- Original Experiment 011 polynomial without dropout training: 0.197343

The statistical front-end improves Raw PsyMoE in all 12 seed-by-availability comparisons. It also reduces full-evidence seed SD from 0.000981 to 0.000372. The precision hybrid improves Stat-PsyMoE in 11/12 comparisons and further reduces full-evidence seed SD to 0.000253.

The strongest hybrid seed reaches 0.197397 full-evidence log loss, essentially matching the original full-evidence polynomial baseline while retaining explicit pipeline-availability handling.

This is an engineering result about combining reusable coordination with classical statistical precision; it is not evidence that the neural component replaces the statistical model.
