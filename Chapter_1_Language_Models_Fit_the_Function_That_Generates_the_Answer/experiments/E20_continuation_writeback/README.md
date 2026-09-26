# E20 Decomposing writes to continuation geometry

[Experiment index](../README.md)

Median immediate successor-law TV across 20 seeds was 0 for static and same-edge, 0.0202 for genealogy and 0.0173 for genealogy+projection. At projection strength 0.08, unbudgeted entropy/replay was 0.513/0.455, versus 0.816/0.220 at budget 0.15. Across 80 synchronized pairs, 60-step divergence after deletion was 46.25% in the unbudgeted condition, 38.75% at 0.15 and 48.75% at 0.25.

## Method

A CE²G-inspired synthetic relational world compared static, same-edge, signed-local, genealogy, delay, projection and combined variants. A phenotype scan used 16 parameter points with three seeds each. Fixed-condition comparisons used 20/30 seeds for successor-row distributions, revisits and adjacent-edge similarity, followed by write-budget and single-projection deletion controls.

## Interpretation

Strengthening an executed edge and rewriting successors of its destination produce different dynamics. Several update rules generate dynamic phenotypes, and bounded writes retain the causal effect of projection.

## Artifacts and reproduction

**Report and decomposition tables**

Compare static, same-edge, genealogy and projection conditions in the archived tables. This experiment marks the move to constructing observable rules.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/R2_writeback/ROUND2_REPORT.md](../../evidence/R2_writeback/ROUND2_REPORT.md) | method_or_report |  |
| [evidence/R2_writeback/01_ablation_diagnostics.csv](../../evidence/R2_writeback/01_ablation_diagnostics.csv) | result_or_record |  |
| [evidence/R2_writeback/04_write_budget_sweep.csv](../../evidence/R2_writeback/04_write_budget_sweep.csv) | result_or_record |  |
| [evidence/R2_writeback/05_dynamic_writeback_gate_summary.csv](../../evidence/R2_writeback/05_dynamic_writeback_gate_summary.csv) | result_or_record |  |

## Related hypotheses

H14, H18, H20

- C13: Sufficiency refers to specified properties and tasks; RTG is an implemented mechanism instance.

The second research turning point was to construct a generative rule, making its operation and rewriting of successors directly observable and intervenable.
