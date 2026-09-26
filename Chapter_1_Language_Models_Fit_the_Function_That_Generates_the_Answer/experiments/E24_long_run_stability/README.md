# E24 Long-run stability of a single-step feedback loop

[Experiment index](../README.md)

Across ten seeds, free/mask-only/constrained violation rates were 31.39/0/0%, late entropies 0.065/0.158/1.582 nats and late coverage 43.1/49.7/100%. In the million-step representative run, mask-only late entropy/coverage was 0.000015/12.5%, versus 1.577/100% when constrained. Constrained entropy before perturbation, during the first 1000 subsequent steps and during steps 4000–5000 was 1.5771/1.5666/1.5777.

## Method

A C++ world had 32 states, five allowed successors per state and 12-dimensional transition features. Free self-writing, support-mask-only and support-plus-budget-plus-reference-relaxation conditions were compared. Each used ten seeds for 100000 steps and seed101 for 1000000 steps, with geometry perturbations at one-quarter, one-half and three-quarters of the run. The constrained version used budget 0.12 and retention 0.98, versus 0.9995 in controls.

## Interpretation

The combined configuration stabilizes a finite symbolic graph: the support mask enforces valid moves, and the full mechanism sustains path diversity and recovery after shocks.

## Artifacts and reproduction

**C++ implementation and saved results**

The archived C++ program runs the three conditions over ten 100k-step seeds and a one-million-step run. Compile to a new output directory; save the new results separately. See docs/REPRODUCTION.md.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/R6_longrun/rtg_longrun.cpp](../../evidence/R6_longrun/rtg_longrun.cpp) | code |  |
| [evidence/R6_longrun/raw_results.txt](../../evidence/R6_longrun/raw_results.txt) | result_or_record |  |
| [evidence/R6_longrun/summary.csv](../../evidence/R6_longrun/summary.csv) | result_or_record |  |
| [evidence/R6_longrun/REPORT.md](../../evidence/R6_longrun/REPORT.md) | method_or_report |  |

## Related hypotheses

H17, H18, H20

- C12: Zero violations reflect masking; multipath stability is assessed for the combined configuration.
- C13: Sufficiency refers to specified properties and tasks; RTG is an implemented mechanism instance.
