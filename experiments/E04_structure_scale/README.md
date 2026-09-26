# E04 Structural scale and word-level checks

[Experiment index](../README.md)

For stripped program explanations, bridge AUC at block sizes 1/2/4/8/16/24/32 was 1.000/0.995/0.909/0.754/0.643/0.571/0.551. In the three-language word-level check, mean local AUC was approximately 0.865 and bridge AUC 0.858.

## Method

Contiguous blocks were shuffled as units, preserving within-block order, with block size increasing from 1 to 32. English, Spanish and French were also reanalyzed using word-level units.

## Interpretation

Preserving larger local blocks made original and shuffled materials more similar, locating much of the discriminative signal at local to intermediate scales. Word-level results retain structural signal, with representation-dependent bridge gains.

## Artifacts and reproduction

**Derived tables and reference methods**

Read the linked CSV tables with the shared protocol and metric definitions. The retained reference functions support descriptive geometry and gaze processing. Rebuilding full experiments also requires the source materials, labels and splits described by the protocol.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/L_language/tables/06_multilingual_block_shuffle.csv](../../evidence/L_language/tables/06_multilingual_block_shuffle.csv) | result_or_record |  |
| [evidence/L_language/tables/07_word_level_sanity.csv](../../evidence/L_language/tables/07_word_level_sanity.csv) | result_or_record |  |

## Related hypotheses

H01, H02, H20

