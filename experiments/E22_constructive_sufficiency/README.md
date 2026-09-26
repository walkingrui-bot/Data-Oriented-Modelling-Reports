# E22 Constructive sufficiency of RTG dynamics

[Experiment index](../README.md)

State/+v/+v+a/mismatched MSEs were 0.8792/0.8655/0.8553/0.8848. K2 silhouette was 0.2632, concentrated/diffuse speed ratio 1.1048, progress difference 0.0589 and endpoint-approach fraction 0.5233. Deleting one projection produced divergence in 141/400 pairs within 60 steps. Nineteen of 27 neighboring parameter points passed the joint criteria.

## Method

The complete RTG world combines continuation geometry, inherited local rewriting, recombination, mutation, projection events and write budgets. Seven low-bandwidth statistic families define z. Sixty independent trajectories support five-fold trace-level prediction; 400 pairs test projection deletion. A neighborhood scan spans gamma=1.2/1.4/1.6, rho=0.26/0.32/0.38 and genealogy write=0.5/0.6/0.7, totaling 27 points.

## Interpretation

RTG generates temporal predictive structure, recurring movement regimes and causal projection effects in one mechanism. Nineteen successful neighboring parameter settings place these properties in a region of the parameter space. The resulting movement has directional correspondences with the observed CoT trajectories.

## Artifacts and reproduction

**Results and mechanism specification**

round4_full_mechanism_sketch.py records the mechanism as a prose specification. The CSVs and report contain parameter-neighborhood and sufficiency results.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/R4_sufficiency/ROUND4_REPORT.md](../../evidence/R4_sufficiency/ROUND4_REPORT.md) | method_or_report |  |
| [evidence/R4_sufficiency/01_parameter_neighborhood_scan.csv](../../evidence/R4_sufficiency/01_parameter_neighborhood_scan.csv) | result_or_record |  |
| [evidence/R4_sufficiency/02_robust_full_mechanism_summary.csv](../../evidence/R4_sufficiency/02_robust_full_mechanism_summary.csv) | result_or_record |  |
| [evidence/R4_sufficiency/round4_full_mechanism_sketch.py](../../evidence/R4_sufficiency/round4_full_mechanism_sketch.py) | mechanism_specification |  |

## Related hypotheses

H05, H14, H18, H20

- C13: Sufficiency refers to specified properties and tasks; RTG is an implemented mechanism instance.
