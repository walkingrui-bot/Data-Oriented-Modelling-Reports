# E05 Diachronic rewriting and multilingual relay

[Experiment index](../README.md)

Across the four texts, local/recurrence/bridge summary AUCs were 0.592/0.586/0.842. The nine-version bridge result was 0.806±0.012. Effects varied by text and direction; Tao Hua Yuan Ji yielded 0.809 and 0.615 in the two directions. At block sizes 1/2/4/8/16, diachronic bridge AUCs were 0.842/0.692/0.604/0.553/0.486; relay values were 0.807/0.684/0.536/0.482/0.497.

## Method

Four classical/modern Chinese pairs were tested in both directions: Shi Shuo, Lanting Ji Xu, Zuiweng Ting Ji and Tao Hua Yuan Ji. A nine-version relay of Tao Hua Yuan Ji held the event sequence fixed and used leave-one-version-out evaluation, with additional external English and Japanese versions.

## Interpretation

Preserving the event sequence preserves part of the relational geometry across rewriting and translation. The variation by text and direction shows how this continuity interacts with expression.

## Artifacts and reproduction

**Derived tables and reference methods**

Read the linked CSV tables with the shared protocol and metric definitions. The retained reference functions support descriptive geometry and gaze processing. Rebuilding full experiments also requires the source materials, labels and splits described by the protocol.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/L_language/tables/08_cross_era_bridge.csv](../../evidence/L_language/tables/08_cross_era_bridge.csv) | result_or_record |  |
| [evidence/L_language/tables/09_cross_era_summary.csv](../../evidence/L_language/tables/09_cross_era_summary.csv) | result_or_record |  |
| [evidence/L_language/tables/11_story_relay.csv](../../evidence/L_language/tables/11_story_relay.csv) | result_or_record |  |
| [evidence/L_language/tables/12_story_external_versions.csv](../../evidence/L_language/tables/12_story_external_versions.csv) | result_or_record |  |
| [evidence/L_language/tables/10_cross_era_block_shuffle.csv](../../evidence/L_language/tables/10_cross_era_block_shuffle.csv) | result_or_record |  |
| [evidence/L_language/tables/13_story_block_shuffle.csv](../../evidence/L_language/tables/13_story_block_shuffle.csv) | result_or_record |  |

## Related hypotheses

H01, H02, H20

