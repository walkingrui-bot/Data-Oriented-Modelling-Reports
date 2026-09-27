# HUMAN-COMFORT-GEOMETRY-001 evidence package

This package supports the report "Real-Data Screening of Effective Dimensionality and Human Interpretability".

## Measurement rule
All continuous features are standardized feature-wise. Constant columns are removed. The package reports:
- stable rank of covariance: trace(C)/lambda_max(C)
- participation rank: trace(C)^2/trace(C^2)
- entropy rank of the covariance spectrum
- PCA d95: number of PCs required for 95% variance
- first-four-PC variance retention
- local intrinsic dimension: k=10 nearest-neighbor maximum-likelihood estimator (median across samples)
- TwoNN intrinsic-dimension estimate
- 10-nearest-neighbor recall after four-PC projection
- pairwise-distance correlation after four-PC projection

The central comparison distinguishes global dominant rank from local intrinsic dimension. A dataset may have strong global anisotropy while retaining many local degrees of freedom.

## Data
Five datasets are loaded directly from scikit-learn 1.8.0: Iris, Wine, Diabetes, Breast Cancer Wisconsin, and Digits. Two additional public datasets were read directly at their GitHub source identities: Palmer Penguins morphology and a UCI HAR subject-by-activity tidy summary.

## Files
- `analyze_geometry.py`: executed analysis for the five datasets supplied by scikit-learn 1.8.0 plus assembly of externally measured public-data rows.
- `combined_geometry_results.csv`: main table.
- `resampling_stability.csv`: 20 deterministic 80% subsamples for the five scikit-learn datasets.
- `source_manifest.csv`: source identities.
- `local_intrinsic_dimension.png`, `four_dim_variance.png`, `global_vs_local_dimension.png`: report figures.

Input datasets are obtained separately from their providers. Their source identities are recorded in `source_manifest.csv`, including the Palmer Penguins Git blob SHA. This directory contains derived geometry results, analysis code and figures.
