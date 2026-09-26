# E12 Candidate distributions in an expected relation field

[Experiment index](../README.md)

The 18 language-by-batch rows report 290 source observations. Weighting by these counts gives 83.104% with larger expected effective candidate count. The median of the 18 batch-level median ratios is 1.4139; the archived report gives approximately 59% top-target agreement.

## Method

Public Wilcox predictors were used to compare direct and expected PPMI over old candidates. Nonnegative weights were normalized and exponentiated entropy measured effective candidate count. Six languages and three positional batches were examined for field width and top-target choice.

## Interpretation

Expected relation fields spread weight over more historical candidates, motivating a distributed representation of possible return targets.

## Artifacts and reproduction

**Derived tables and reference methods**

Read the linked CSV tables with the shared protocol and metric definitions. The retained reference functions support descriptive geometry and gaze processing. Rebuilding full experiments also requires the source materials, labels and splits described by the protocol.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/L_language/tables/29_expected_ppmi_mid_probe.csv](../../evidence/L_language/tables/29_expected_ppmi_mid_probe.csv) | result_or_record |  |
| [evidence/L_language/tables/30_expected_ppmi_three_batches.csv](../../evidence/L_language/tables/30_expected_ppmi_three_batches.csv) | result_or_record |  |
| [audit/summary_recalculation.json](../../audit/summary_recalculation.json) | result_or_record |  |

## Related hypotheses

H20

