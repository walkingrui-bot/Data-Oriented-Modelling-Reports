# HUMAN-EMG-REACHING-GEOMETRY-004 Evidence Package

This package accompanies the standalone experimental report.

**Executed source:** 21,096 processed windows from 900 real reaches by 10 participants, fixed to Git blob `44fa933e7d164aa7279c545047d42d6ee6aae5c4`.

**Primary result:** realized endpoint movement breadth robustly tracks broader kinematic recruitment, but the independent temporal covariance spectrum does not expand. High-breadth reaches show a median **+0.522** increase in kinematic energy breadth (95% bootstrap interval **+0.373 to +0.741**, 10/10 participants positive) while kinematic covariance stable rank changes by **−0.244** (**−0.343 to −0.137**). EMG recruitment broadens more modestly.

**Dominant spectrum:** within single reaches, the first three covariance modes carry a median **95.8%** of standardized kinematic variation and **95.6%** of EMG-RMS variation. After pooling ten repetitions for each participant × target, four modes still carry **94.8%** of kinematic and **94.0%** of EMG variation; d90=4 and d95=5 in both domains.

Files:
- `source_manifest.csv` — immutable source identity and dataset counts.
- `analysis_specification.md` — exact operational definitions.
- `reproduce_004.py` — reproduction script for the fixed public source.
- `subject_level_results.csv` — within-participant coupling and high/low contrasts.
- `key_results.csv` — primary estimates, bootstrap intervals and sign counts.
- `target_row_summary.csv` — descriptive target-row geometry.
- `spectrum_summary.csv` — single-trial and pooled covariance-spectrum checks.
- `long_trial_sensitivity.csv` — sensitivity excluding reaches longer than 45 processed windows.
- `figures/` — report figures.

The public source file itself is not duplicated in this ZIP; the Git blob SHA fixes the exact input bytes and the reproduction script downloads that blob.
