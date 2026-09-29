#!/usr/bin/env python3
"""
CG-010: Variable Decomposition & Machine Learning for Causal Transmission

Reproduction outline:
- Download the real Sachs conditions cd3cd28, aktinhib, g0076, psitect,
  u0126, pma and b2camp from MLAI-Yonsei/FANS.
- Read intervention targets from saezlab/corneto/datasets/sachs/v1/condition_manifest.csv.
- Read the benchmark directed graph from MLAI-Yonsei/FANS/data/sachs/GroundTruth.csv.
- Compute robust response components relative to cd3cd28:
  location shift, log-IQR scale shift, centered/scaled quantile-shape distance.
- Label each node by directed graph distance from the measured intervention target.
- Form the 6 x 11 x 3 tensor, RMS-normalize components, run uncentered SVD
  and NMF, then evaluate regularized logistic models with leave-one-intervention-out CV.
- Run within-intervention role-label permutation controls.
The CSVs archived with this script contain the exact numerical results from the
2026-09-27 run.
"""
print(__doc__)
