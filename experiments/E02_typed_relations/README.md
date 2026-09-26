# E02 Recurrence and typed relational propagation

[Experiment index](../README.md)

AUC was 0.558 for local offsets, 0.570 for multiscale offsets and 0.751 with global recurrence. Bridge rounds 0–5 yielded 0.707/0.782/0.833/0.858/0.881/0.883; the shuffle result was 0.486. Coarse-role probe accuracy rose from 82.7% to 93.8%, and fine-role accuracy from 86.8% to 92.5%. Untyped diffusion was approximately 0.44–0.50.

## Method

Natural L3 compared local offsets, multiscale offsets, global same-identity recurrence and iterative typed bridge propagation. Untyped graph diffusion and position shuffles served as controls; coarse and fine roles were evaluated separately.

## Interpretation

The results support representations that retain the type and direction of relations surrounding recurrence. They provide structural evidence for reconnecting local relational neighborhoods.

## Artifacts and reproduction

**Derived tables and reference methods**

Read the linked CSV tables with the shared protocol and metric definitions. The retained reference functions support descriptive geometry and gaze processing. Rebuilding full experiments also requires the source materials, labels and splits described by the protocol.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/L_language/tables/02_natural_L3_recurrence_bridge.csv](../../evidence/L_language/tables/02_natural_L3_recurrence_bridge.csv) | result_or_record |  |
| [evidence/L_language/tables/03_role_probe_results.csv](../../evidence/L_language/tables/03_role_probe_results.csv) | result_or_record |  |

## Related hypotheses

H01, H20

