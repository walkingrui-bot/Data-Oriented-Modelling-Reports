# INTERNAL_COORDINATION_008 — Time-Aligned Evidence Coordination

This experiment extends the recurrent shared-ganglion architecture with an explicit temporal hierarchy. Measurements sharing a timestamp are coordinated as an unordered evidence set. Distinct timestamps update the same ganglion recurrently. The training target is an independent repeat-measurement distribution at the current timestamp; no future prediction target is used.

Reproduce:
```bash
python code/time_aligned_coordination.py
python code/build_assets.py
```

Key outputs: `results/per_seed.csv`, four figures, standalone report, and Living Report v0.8. `data/diabetes_backbone.npz` is the fixed real-patient scaffold inherited from the previous experiments.
