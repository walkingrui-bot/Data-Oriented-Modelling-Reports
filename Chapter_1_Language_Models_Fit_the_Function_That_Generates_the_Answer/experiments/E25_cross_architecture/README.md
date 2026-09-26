# E25 History-conditioned continuation in three architectures

[Experiment index](../README.md)

GRU/SSM/Transformer state MSEs were 0.959/1.812/1.593, falling to 0.729/1.367/1.197 with v/a and rising to 0.964/1.819/1.603 after mismatch. On the first 300 of 449 pairs sharing visible state and rule tables but differing in history, TV was 0.365/0.324/0.361 and mean accuracy 0.652/0.633/0.654. D/C clustering varied by architecture. Initial trigger/neutral intervention TV ratios were 1.022/1.040/1.058.

## Method

Episodes sampled A/B permutations and a trigger that switched mode when encountered. GRU, simplified SSM and one-layer causal Transformer used 24 dimensions; Transformer had four heads. Each architecture used seeds 11/22/33 and training length six. Each model supplied 320 sixteen-step trajectories; standardized hidden states were projected onto eight PCA components for five-fold trace-level Ridge prediction.

## Interpretation

Motion adds order-related predictive information to eight-dimensional state projections. Different histories also produce different outputs at the same visible input. E26 follows this result into selective historical participation.

## Artifacts and reproduction

**Report tables and figures**

Inspect the per-architecture and per-seed result tables, protocols, and eight-dimensional projection analysis.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/X1_cross_architecture/REPORT.md](../../evidence/X1_cross_architecture/REPORT.md) | method_or_report |  |
| [evidence/X1_cross_architecture/02_trajectory_prediction.csv](../../evidence/X1_cross_architecture/02_trajectory_prediction.csv) | result_or_record |  |
| [evidence/X1_cross_architecture/03_same_visible_state_different_history.csv](../../evidence/X1_cross_architecture/03_same_visible_state_different_history.csv) | result_or_record |  |
| [evidence/X1_cross_architecture/05_history_intervention_diagnostic.csv](../../evidence/X1_cross_architecture/05_history_intervention_diagnostic.csv) | result_or_record |  |

## Related hypotheses

H05, H06, H18, H20

- C03: Interpret predictive gains as added information relative to the selected PCA projection.
