# E07 Single-anchor hops and relational groups

[Experiment index](../README.md)

Single-anchor AUCs at hop 1 were 0.820/0.785/0.799, at hop 2 were 0.534/0.465/0.509, and at hop 5 were 0.215/0.200/0.196. Related three-word groups yielded 0.672/0.664/0.642 and five-word groups 0.582/0.567/0.541. Random three-word groups after five rounds yielded 0.465/0.437/0.437.

## Method

Natural language, Go and Rust were tested with repeated single-anchor backtracking and with related three-word/five-word groups, random groups and position shuffles.

## Interpretation

Short-range backtracking and related groups preserve useful structure. Deep single-anchor hopping rapidly changes the relation between the representation and the original labels.

## Artifacts and reproduction

**Derived tables and reference methods**

Read the linked CSV tables with the shared protocol and metric definitions. The retained reference functions support descriptive geometry and gaze processing. Rebuilding full experiments also requires the source materials, labels and splits described by the protocol.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/L_language/tables/17_multibacktracking.csv](../../evidence/L_language/tables/17_multibacktracking.csv) | result_or_record |  |
| [evidence/L_language/tables/18_related_groups.csv](../../evidence/L_language/tables/18_related_groups.csv) | result_or_record |  |

## Related hypotheses

H01, H20

