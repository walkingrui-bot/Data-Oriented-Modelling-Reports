# INTERNAL_COORDINATION_007 Evidence

Final revised Experiment 007 evidence package. The formal training target is distributional: source and target are independent repeat measurements of the same underlying patient state, and output heads predict ordered conditional quantiles rather than exact point reconstructions.

## Final architecture

For each evidence event from channel c:

`current state r -> shared 16x16 M -> + channel input A_c(y_c) -> tanh -> updated current state`

Channel-specific output heads `B_j` map the current shared state to 10%, 25%, 50%, 75%, and 90% quantiles of the current measurement distribution for target channel j.

The same physical M is reused at every evidence event. No future channel is assumed or predicted.

## Main evidence

- `results/recurrent/per_seed_by_evidence.csv`: five-seed comparison of trainable shared M, fixed identity recurrence, and fixed random recurrence after 1/2/3/6 current evidence channels.
- `results/recurrent/ablation.csv`: three-seed post-training matrix replacement and rank lesions.
- `results/onboarding.csv`: three-seed seventh-channel onboarding, frozen M versus adapting M.
- `results/per_seed.csv`: one-pass distributional control showing that a single-use matrix can be absorbed by flexible flanking networks.

## Key checks

- Nominal 80% predictive interval coverage is evaluated on independent held-out repeat measurements.
- Matrix lesions are scored with pinball loss and coverage, not pointwise RMSE.
- New-channel onboarding evaluates both new-route and legacy distributional scores.
- Evidence-order sensitivity is measured explicitly and retained as the next engineering interface.

## Reproduction

The scripts are CPU-compatible and use NumPy, pandas, PyTorch, and scikit-learn. `recurrent_ganglion_distributional.py` reproduces the initial three-seed recurrent experiment; `recurrent_moreseeds.py` extends the main comparison to five seeds. `onboard_distributional_fast.py` reproduces the seventh-channel onboarding control.
