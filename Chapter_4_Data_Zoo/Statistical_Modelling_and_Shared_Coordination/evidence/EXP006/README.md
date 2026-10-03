# INTERNAL_COORDINATION_006 — Dynamic State Routing

Experiment 006 tests whether a model can separate a changing measurement process from a changing shared reality after stable channel mechanisms and the shared reality core have already been learned.

## Architecture

`measurement -> shared perception -> stable channel net -> frozen 16x16 reality core -> stable target-channel net -> generator`

Experiment 006 adds one 8D recurrent state per channel. A shared GRU receives each channel's deviation from the current cross-channel consensus. Small channel-specific state heads adjust the input/output side of each stable measurement operator. The stable neural channel mechanisms and shared reality core remain frozen during state learning.

## Controlled dynamic episodes

The real `sklearn` diabetes dataset provides the 442-patient, 10-variable biomedical backbone. Six epidemiology-inspired stable measurement channels are inherited exactly from Experiment 005. Every patient contributes four 12-step episodes: no change, channel-6 measurement drift, shared world change, and both changes. Test episodes use a nonlinear drift shape that differs from the training drift shape.

The imposed world-change and measurement-drift coordinates are audit-only. The recurrent state model is trained only from six-channel reconstruction and small state regularization.

## Main five-seed result

See `results/summary.csv` and `results/per_seed.csv`. Key medians:

- world-change readout from shared reality state: R² 0.935
- measurement-drift readout from channel-6 recurrent state: R² 0.646
- drift-state localization to the affected channel: 4.79x other-channel mean
- paired shared-reality movement under world change vs channel-only drift: 4.59x
- channel-6 drift RMSE: 0.206 without dynamic state -> 0.133 with recurrent state
- combined world-change + drift overall RMSE: 0.207 -> 0.143

## Reproduction

From the extracted evidence directory:

```bash
python code/experiment.py --seed 0
python code/make_figures.py
python code/build_report.py
```

Dependencies: Python 3, NumPy, pandas, PyTorch, scikit-learn, matplotlib, python-docx.

`results/seed0_frozen_base.pt` and `results/seed0_dynamic_state.pt` contain the recorded seed-0 stable model and dynamic state module. `results/seed0_dynamic_arrays.npz` contains the held-out episode observations, audit coordinates, predictions, reality trajectories and channel states.
