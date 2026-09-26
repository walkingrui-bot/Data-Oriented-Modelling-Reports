# E15 Relational geometry of visible chain of thought

[Experiment index](../README.md)

R1 had lower recurrence, bridge and repeated n-grams in all 16 prompt sets, and higher burst CV in 14/16. After frequency-preserving shuffles, early-to-late local surplus changed by +0.0504 for R1, −0.0120 for chat and +0.1108 for QwQ. With 48-token windows and 24-token lag, early-to-late speeds were 2.943→2.672, 2.817→2.743 and 2.204→2.551.

## Method

ChainScope supplied 16 matched world-model prompt sets for DeepSeek-R1 and DeepSeek-chat, in two batches of eight. The 64-token window analysis used 400 R1 and 321 chat traces. Fixed-lag analysis required at least 96 content words, retaining 398/50 traces, with 14 long QwQ Putnam traces as a model-family check.

## Interpretation

Visible reasoning redistributes relational scales as it develops. Model and window size shape the observed speed and bridge patterns.

## Artifacts and reproduction

**Report and derived tables**

Compare static geometry, raw trajectory changes and shuffle-controlled changes using the three result CSVs and the accompanying analysis report.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/C_cot/REPORT(20260925-005446).md](../../evidence/C_cot/REPORT%2820260925-005446%29.md) | method_or_report |  |
| [evidence/C_cot/01_static_geometry.csv](../../evidence/C_cot/01_static_geometry.csv) | result_or_record |  |
| [evidence/C_cot/02_raw_trajectory_change.csv](../../evidence/C_cot/02_raw_trajectory_change.csv) | result_or_record |  |
| [evidence/C_cot/03_shuffle_controlled_change.csv](../../evidence/C_cot/03_shuffle_controlled_change.csv) | result_or_record |  |

## Related hypotheses

H20

