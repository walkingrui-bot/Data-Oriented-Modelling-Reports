# HUMAN-SENSORIMOTOR-GEOMETRY-003 Evidence Package

This package records the third experiment in the Human Comfort Geometry line.

## Core question
Do real human movement trajectories and natural-language predictive dynamics share a low-dimensional dominant movement spectrum even when their full state spaces retain many weaker dimensions?

## Real data
- 20 CMU Motion Capture AMC clips from subjects 01, 02 and 03.
- 431,826-character technical-English corpus already used in Chapter 3 Language Mathematics.
- No synthetic dataset is used for the reported cross-domain result.

## Motion preprocessing
- AMC joint angles in degrees.
- Root removed to exclude global translation/orientation.
- Finger/thumb channels removed because CMU documentation states they were not actually captured.
- Angle channels unwrapped before differencing.
- Main raw-amplitude spectra retain physical degree units across joint-angle channels.
- Coordinate-balanced spectra z-score each joint channel and measure potential joint-wise complexity rather than dominant movement energy.
- A 5-frame moving-average sensitivity analysis is retained separately because CMU notes hand/toe channels can be noisy.

## Language preprocessing
- Top 63 characters + UNK, vocabulary 64.
- Bigram teacher field: frequency-weighted P(next|current)-unigram baseline.
- L3 predictive states: empirical next-character distributions for three-character contexts with at least 10 observations.
- L3 movement: weighted differences between successive retained predictive states.

## Main numerical result
Across all 20 motion clips, median raw angular-velocity stable rank = 4.042; after 5-frame smoothing it is 3.295. Natural-language L3 predictive-state movement stable rank = 4.076. The full 95%-energy dimensions remain much larger: motion median d95 = 20.0 and language L3 movement d95 = 20.

The evidence therefore supports a shared low-rank dominant spectrum over a higher-dimensional tail, not a claim that either domain is literally only 3-4 dimensional.

## Files
- motion_trial_geometry.csv
- motion_group_summary.csv
- language_geometry.csv
- motion_language_comparison.csv
- robustness_selected_clips.csv
- source_manifest.csv
- recompute_geometry.py
- figures/
