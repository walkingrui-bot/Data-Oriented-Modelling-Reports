# NATLANG-COMPAT-004B evidence package

This package supports the **Joint Script-Language Disentanglement Campaign** integrated into *Chapter 3 - The Language Edition, Living Language Record v1.4*.

## What is included
- `source_manifest.csv`: exact pinned FLORES-200 source identities (Git blob SHA, URL, row count).
- `pairwise_surface_results.csv`: 74 evaluated pair conditions across the three pair classes.
- `same_language_script_swap_results.csv`: the eight primary same-language/different-script interventions and controls.
- `pair_class_surface_summary.csv` and `pair_class_script_neutral_summary.csv`: aggregate class results.
- `surface_geometry_primary_variants.csv`: stable/participation rank, PCA-95, TwoNN, distance concentration and resampling statistics for the 16 primary script variants.
- `low_dimensional_knn_preservation.csv`: 10-NN retention after 4D/8D PCA projections.
- `statistical_summary.json`: primary aggregate statistics and uncertainty intervals.
- Figures 4.37-4.42 used in the report.
- `CALCULATION_RECORD.md`: executed construction and key results.
- `reproduce_natlang_compat_004b.py`: standalone reproduction script using the pinned external corpus sources.

## External data convention
Raw FLORES-200 text is **not duplicated** in this ZIP. The reproduction script retrieves the exact pinned Git revision recorded in `source_manifest.csv` and verifies each Git blob identity before computation.

## Primary measured statements
The surface assay gives 5.36% direct and 9.61% learned Top-1 for the eight same-language/different-script pairs; different-language/same-script controls give 7.53% direct and 6.25% learned. The permuted alignment control for the primary interventions averages 0.51%, approximately the 1/197 retrieval chance level. After glyph identity is removed, same-language/different-script direct and learned structural retrieval rise to 28.78% and 33.53%. Script-change displacement stable rank averages 14.96 in the surface representation and 4.39 after script identity is erased.
