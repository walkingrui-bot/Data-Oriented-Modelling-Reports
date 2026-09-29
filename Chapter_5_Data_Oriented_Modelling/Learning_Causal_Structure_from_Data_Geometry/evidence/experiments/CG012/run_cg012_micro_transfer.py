#!/usr/bin/env python3
"""
CG-012 Micro Cross-System Transfer Test

Small-data design:
- Train a class-weighted ridge "direct-child texture" operator on 50 unique
  Sachs target-node relations from the cd3cd28 reference condition.
- Baseline relation features: correlation, nonlinear gain, heteroscedasticity,
  input-|residual| dependence, fibre-width variation, residual skew/kurtosis,
  and forward/reverse directional gaps.
- External test: 10 scalar Tübingen cause-effect pairs from 10 different real
  data sources only.
- For each pair, compute the Sachs child-texture score in both orientations;
  predict the orientation with the larger score.
- Run only 20 bootstrap resamples per external pair.

This intentionally small experiment tests transfer of relation texture, not a
large benchmark leaderboard.
"""
print(__doc__)
