# E13 Genre authors and parallel translations

[Experiment index](../README.md)

Genre explained approximately 55%–62% of author-mean variation in rec/local/mid/long/bridge. Recalculation gives mean window accuracy 52.6786% and 9/14 correct majority predictions; those 14 rows represent 12 unique authors. Hardy and Wilde were approximately 1.22 units from their new-genre centroids. Odyssey translations had recurrence CV 0.5134 and local/long/bridge CVs 0.0556/0.0663/0.0663. The six-style pilot recorded approximately 28%–30% classification with all tokens (reported p=0.033) and 38% with content words (reported p=0.01), against chance 1/6.

## Method

Equal-length English content-word windows compared novels, poetry and drama. Hardy and Wilde supplied same-author cross-genre cases, and human translations of Book I of the Odyssey and Iliad supplied same-source comparisons. Historical six-style pilot tables retain their correction flags.

## Interpretation

Genre and content jointly constrain relational geometry. The author comparison contains 12 unique authors and 14 author-by-genre records, with 9 correct majority predictions.

## Artifacts and reproduction

**Derived tables and reference methods**

Read the linked CSV tables with the shared protocol and metric definitions. The retained reference functions support descriptive geometry and gaze processing. Rebuilding full experiments also requires the source materials, labels and splits described by the protocol.

Paths below are relative to the repository root. The complete file inventory is in [artifacts.csv](artifacts.csv).

| File | Role | Locator |
| --- | --- | --- |
| [evidence/L_language/tables/31_style_pilot_reported_with_flags.csv](../../evidence/L_language/tables/31_style_pilot_reported_with_flags.csv) | result_or_record |  |
| [evidence/L_language/tables/32_style_classifier_reported.csv](../../evidence/L_language/tables/32_style_classifier_reported.csv) | result_or_record |  |
| [evidence/L_language/tables/33_style_bigram_reported.csv](../../evidence/L_language/tables/33_style_bigram_reported.csv) | result_or_record |  |
| [evidence/L_language/tables/34_genre_means_corrected.csv](../../evidence/L_language/tables/34_genre_means_corrected.csv) | result_or_record |  |
| [evidence/L_language/tables/35_genre_variance_decomposition.csv](../../evidence/L_language/tables/35_genre_variance_decomposition.csv) | result_or_record |  |
| [evidence/L_language/tables/36_same_author_cross_style.csv](../../evidence/L_language/tables/36_same_author_cross_style.csv) | result_or_record |  |
| [evidence/L_language/tables/37_author_loo_corrected.csv](../../evidence/L_language/tables/37_author_loo_corrected.csv) | result_or_record |  |
| [evidence/L_language/tables/38_odyssey_translators.csv](../../evidence/L_language/tables/38_odyssey_translators.csv) | result_or_record |  |
| [evidence/L_language/tables/39_iliad_translators.csv](../../evidence/L_language/tables/39_iliad_translators.csv) | result_or_record |  |
| [evidence/L_language/tables/40_translator_metric_CV.csv](../../evidence/L_language/tables/40_translator_metric_CV.csv) | result_or_record |  |

## Related hypotheses

H02, H20

- C01: 9/14 author-by-genre records, 12 unique authors; mean window accuracy 52.6786%.
