# INTERNAL_COORDINATION_005

Channel Networks for Epidemiologic Measurement Distortion: stable operators, dynamic drift, and reality-core localization.

## What is real and what is controlled

The biological/data backbone is the bundled scikit-learn diabetes dataset (442 patients, 10 baseline variables). The six measurement channels are controlled epidemiology-inspired operators applied to the same patient vector: calibration bias, heaping, lower detection limits, top-coding/saturation, heteroscedastic error, and nonlinear assay response. This semi-synthetic arrangement makes the measurement operator known for audit while preserving real patient covariance.

## Main comparisons

1. Stable channel mechanism: affine channel adapter versus residual neural channel network around the same 16x16 shared reality core.
2. Measurement drift: change only channel 6, then compare local channel adaptation, whole-model adaptation, and a separate 64-parameter dynamic channel state.
3. New-channel onboarding: train the shared world with channels 1-5, freeze it, then attach an unseen nonlinear sixth channel using either an affine or neural channel module.

## Reproduction

Run:

```bash
python code/experiment.py
python code/holdout_channel.py
python code/dynamic_state.py
python code/make_figures.py
```

The scripts use NumPy, pandas, PyTorch, scikit-learn and Matplotlib. `experiment.py` generates the fixed train/test split and controlled channels from the locally bundled scikit-learn dataset.

## Key evidence files

- `results/per_seed.csv`
- `results/summary.csv`
- `results/first_update_gradients.csv`
- `results/holdout_channel.csv`
- `results/dynamic_state.csv`
- `data/diabetes_backbone.npz`
- `data/measurement_channels.npz`
- `figures/fig1_channel_network_and_drift.png`
- `figures/fig2_onboarding_and_localization.png`
- `INTERNAL_COORDINATION_005_Report_v0.1_20261001.docx`
- `INTERNAL_COORDINATION_Living_Report_v0.5_20261001.docx`

`manifest.json` records SHA256 and byte size for packaged files.
