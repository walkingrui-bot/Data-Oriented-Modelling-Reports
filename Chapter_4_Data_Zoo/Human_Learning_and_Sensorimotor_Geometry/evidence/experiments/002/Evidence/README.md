# HUMAN-LEARNING-DIMENSION-002 evidence package

This package records the derived evidence used in the report "Human Learning Under One to Three Relevant Dimensions".

## Primary source
Public trial-level data from `mingyus/humans-combine-value-learning-and-hypothesis-testing`, file `data/data_all_wClickInfo.csv`, Git blob SHA `e834ccbbe1e183b7e2c094702b50f2e9ce558441`.

The source contains 57,240 trials from 106 participants, 18 games per participant, 30 trials per game. The design crosses true task complexity (1, 2, or 3 reward-relevant feature dimensions) with whether the dimensionality hint is provided.

## Reanalysis
The report uses the paper's exclusion criterion: overall expected reward probability < 0.468. Four participants (50, 51, 89, 86) meet that rule in the source file, leaving 102 participants and 55,080 trials.

Per-trial expected reward probability is reconstructed from the actual configured stimulus and the true game rule:

`p(reward) = 0.2 + 0.6 * (# rewarding features present / # relevant dimensions)`.

Reaction time is taken from the trial `rt` field. Selected breadth is the `numSelectedFeatures` field. Paired 1D-to-3D effects are participant-level differences with 5,000 deterministic bootstrap resamples (seed family rooted at 20260927).

## Files
- `condition_summary.csv`: reanalysis by true dimension and hint condition.
- `paired_effects.csv`: paired 3D-minus-1D effects with bootstrap intervals.
- `exclusions.csv`: participants matching the source paper exclusion threshold.
- Published comparison: Vong et al. (2019), DOI `10.1111/cogs.12724`, as cited in report Section 2.8 and Figure 7.
- `source_manifest.csv`: source identities.
- `figures/`: report figures showing the derived analysis and cited published comparison.

The Git blob SHA identifies the provider input for separate local retrieval. This directory contains derived analysis outputs, code and report figures.
