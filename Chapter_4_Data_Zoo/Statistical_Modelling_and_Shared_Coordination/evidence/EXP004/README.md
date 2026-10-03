# INTERNAL_COORDINATION_004 Evidence

Experiment 004 reproduces Reality Binding on real measured data using the Wisconsin Diagnostic Breast Cancer dataset (UCI DOI: 10.24432/C5DW2B; sklearn `load_breast_cancer`).

Each specimen has 30 nucleus-morphology measurements, partitioned into six non-overlapping five-variable views. Each view is encoded through its own interface into one shared 16-dimensional core. Reality Binding requires a core state inferred from any view to generate all six views for the same specimen. No latent-alignment loss is used.

## Conditions
- `self_only`: six diagonal reconstruction paths only.
- `direct_binding`: all 36 source-view -> target-view paths use the same specimen.
- `switch_binding`: self-only specialization followed by same-specimen Reality Binding without resetting weights.
- `shuffled_pairing`: cross-view targets are assigned to different specimens while view marginals and architecture are preserved.

## Main evidence
Five independent seeds are in `results/all_runs.csv`. The exact fixed train/test split and the 30 published measurements are in `data/wdbc_exact_split.npz`. Seed-0 checkpoints, traces, 6x6 reconstruction matrices, retrieval tables and latent matrices are included for direct inspection. `protocol.json` records the architecture, update budgets and metric definitions.

## Reproduction
Run:

```bash
python code/experiment.py
```

The script uses the local sklearn copy of the dataset and the fixed split in the protocol logic. The supplied NPZ preserves the exact data arrays and split used for this evidence package.

## Primary interpretation
Correct same-specimen binding reduces cross-view prediction error, contracts the six internal states of the same specimen, and raises exact cross-view specimen retrieval. Shuffling specimen correspondence reverses these effects. The remaining cross-view error records view-specific residual structure in real measurements.
