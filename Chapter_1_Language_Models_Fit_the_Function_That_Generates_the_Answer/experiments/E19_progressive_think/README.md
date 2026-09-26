# E19 Progressive THINK with noisy evidence

[Experiment index](../README.md)

At 0 THINK, accuracies were 35.01/36.69/49.93%; at 8 THINK they were 35.01/37.26/49.80%, a mean gain of 0.146 percentage points. The 1218 intervention conditions × 256 pairs × three seeds produced 935424 condition outputs. Seed43 had nine exploratory whole-evidence positives, increasing operator probability by approximately 0.100–0.205.

## Method

An independently implemented ten-symbol, 64-dimensional, three-layer, four-head pre-LN Transformer had 155456 parameters. Each episode supplied eight evidence items with 0.3 corruption probability, using final-answer supervision after ANS. Seeds 41/42/43 each received 24000 updates at batch 128, totaling 9216000 online episodes. THINK counts were 0/1/2/3/4/6/8. Each seed used 256 algebraically selected pairs with distinct recipient, donor and operator answers.

## Interpretation

Across three independently trained models, additional THINK left mean accuracy nearly unchanged. The intervention sweep exposed local causal control in the evidence region, supplying a route for studying how further computation could develop a rule.

## Artifacts and reproduction

**Report and figure**

The formal report and mechanism figure present the progressive-THINK methods and outcomes.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/P3_progressive/REPORT(20260925-042904).md](../../evidence/P3_progressive/REPORT%2820260925-042904%29.md) | method_or_report |  |

## Related hypotheses

H13, H20

