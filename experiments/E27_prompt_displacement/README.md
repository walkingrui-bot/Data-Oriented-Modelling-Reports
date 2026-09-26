# E27 Prompt conditioning and within-network displacement

[Experiment index](../README.md)

Reported three-seed baseline TV was 0.721. Real-displacement TV after layers 1/2/3/4 was 0.711/0.674/0.472/0.218, versus 0.716/0.709/0.662/0.634 for random directions. At layer four in seed0, forward doses 0/0.5/1/1.5/2 gave P(A)=0.174/0.400/0.691/0.829/0.880; reverse intervention gave 0.868/0.664/0.363/0.204/0.137.

## Method

A four-layer, 24-dimensional, three-head Transformer used 16 content classes, a 52-token vocabulary and four prefix positions. STYLE/NEUTRAL set target A-variant probabilities to 0.9/0.1. Model training included all 16 contents. Displacement estimation used contents 0–7; intervention testing used contents 8–15. Mean final-position STYLE−NEUTRAL displacement was injected and compared with ten norm-matched random directions.

## Interpretation

TV measures the conditional A/B distribution, computed from the correct content’s A/B logits. Layer-four injection occurs after the final block and before the output head. The 45-step campaign supplies the reported layer and dose measurements; the retained 220-step script provides a separate implementation of the layer comparison. Deep displacement exposes a continuously controllable generative factor.

## Artifacts and reproduction

**Reported results and a separate code version**

Use the report for the 45-step results and dose table. archived_code_220steps.py is a separately retained 220-step implementation. The two files record distinct campaign versions.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/P4_prompt/archived_report.md](../../evidence/P4_prompt/archived_report.md) | method_or_report |  |
| [evidence/P4_prompt/archived_code_220steps.py](../../evidence/P4_prompt/archived_code_220steps.py) | code |  |

## Related hypotheses

H19, H20

- C08: TV is conditional on A/B; model training includes all contents, with separate subsets for displacement estimation and intervention testing.
- C09: Report: 45 steps. Available code: 220 steps. Preserve separate version provenance.
- C10: Dose values come from the report; available code emits layer comparisons.
