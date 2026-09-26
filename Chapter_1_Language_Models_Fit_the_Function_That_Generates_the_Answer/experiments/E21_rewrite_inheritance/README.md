# E21 Lineage inheritance of rewrite behavior

[Experiment index](../README.md)

Across 30 seeds, inherited-code lag1–4 similarities were 0.4247/0.2439/0.2051/0.2021, versus 0.0292/0.0175/0.0120/0.0141 for fixed updates. Across 40 seeds, real-minus-shuffled differences were +0.2754/+0.0826/+0.0447/+0.0386. In 750 M transplants, gamma=1 gave median successor TV 0.0099 and 13.9% divergence over 25 steps; gamma=0 gave zero effect.

## Method

Each node carries local rewrite state M. The executed transition’s relation feature combines with source M to form a rewrite code, modifying destination successors and M. Fixed, inherited, shuffled-ancestry and no-inheritance conditions were compared. A transplant held geometry, node and current action fixed and exchanged history-produced M.

## Interpretation

This establishes an inherited state controlling how an action rewrites its successors, with a causal effect in the constructed system. Systems sharing geometry can diverge because M differs; the complete state includes both geometry and M.

## Artifacts and reproduction

**Results and mechanism specification**

round3_minimal_model.py records the mechanism as a prose specification. The CSVs contain the swap and lineage-sweep results.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/R3_genealogy/ROUND3_REPORT.md](../../evidence/R3_genealogy/ROUND3_REPORT.md) | method_or_report |  |
| [evidence/R3_genealogy/round3_minimal_model.py](../../evidence/R3_genealogy/round3_minimal_model.py) | mechanism_specification |  |
| [evidence/R3_genealogy/02_paired_ancestry_effects.csv](../../evidence/R3_genealogy/02_paired_ancestry_effects.csv) | result_or_record |  |
| [evidence/R3_genealogy/04_mechanism_swap_interventions_gamma1.csv](../../evidence/R3_genealogy/04_mechanism_swap_interventions_gamma1.csv) | result_or_record |  |

## Related hypotheses

H14, H18, H20

- C13: Sufficiency refers to specified properties and tasks; RTG is an implemented mechanism instance.
