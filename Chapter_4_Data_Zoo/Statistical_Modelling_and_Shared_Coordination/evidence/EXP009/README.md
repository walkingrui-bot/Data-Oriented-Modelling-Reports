# INTERNAL_COORDINATION_009 — Mixed Language–Statistical Ganglion Training

Date: 2026-10-02

## Research question
Can one shared 16×16 ganglion support a statistical measurement channel and a natural-language semantic channel that refer to the same underlying patient state, while developing shared parameter directions that causally support both modalities?

## Data
- Real scaffold: `sklearn.datasets.load_diabetes`, 442 × 10 patient measurements.
- Fixed train/test split: 353 / 89.
- Statistical observation channel: six controlled nonlinear measurement coordinates with independent remeasurement noise, heaping, lower-detection censoring and top-coding.
- Language observation channel: six three-level patient concepts rendered through four stochastic natural-language paraphrases per patient. The training target is semantic class, not exact sentence reproduction.

The standardized 10-dimensional patient state is used only for post-training audit probes.

## Model
- Numeric perception: 6 → 32 → 16.
- Text perception: learned 24-dimensional token embedding, masked pooling, 24 → 32 → 16.
- Shared ganglion: one trainable 16×16 matrix plus bias.
- Numeric head: q10/q25/q50/q75/q90 for six independent remeasurement coordinates; pinball loss.
- Language head: six three-class semantic outputs; cross-entropy.

Three matched branches start from the same initialization in each seed:
1. numeric specialist;
2. language specialist;
3. mixed coordination, cycling numeric-only evidence, text-only evidence and joint evidence while always optimizing both target types.

Seeds: 0, 1, 2. Main budget: 800 updates. Seed 0 is checkpointed at 0/25/50/100/200/400/800.

## Key evidence files
- `results/final_branch_metrics.csv` — three-seed endpoint metrics.
- `results/seed0_training_history.csv` — checkpointed mixed/specialist dynamics.
- `results/ganglion_delta_geometry.csv` — ganglion displacement geometry across branches.
- `results/freeze_after_200.csv` — shared-ganglion freeze control.
- `results/modality_stress.csv` — 200-update specialist continuation after mixed training.
- `results/ganglion_lesions.csv` — singular-direction lesion and matched-random perturbation controls.
- `results/data_arrays.npz` — audit arrays, split indices, semantic labels and statistical-channel parameters.
- `results/seed0_*_final.pt` — seed-0 final model state dictionaries.
- `figures/` — report figures.
- `documents/` — standalone report and updated Living Report.

## Reproduction
From the evidence-package root:

```bash
python code/experiment_009.py
python code/analyze_009.py
python code/build_report_009.py
```

The experiment uses Python 3, NumPy, pandas, PyTorch, scikit-learn, Matplotlib and python-docx. The report builder expects the previous Living Report when regenerating the merged document; the standalone experiment report and all numerical evidence are independently reproducible from this package.

## Main measured results
Across three seeds, the mixed ganglion reached median numerical pinball 0.0859 and language semantic accuracy 84.3% with both evidence types. Numeric-only evidence supported 72.5% language accuracy; text-only evidence supported numerical pinball 0.1530. The mixed current state linearly audited the ten-dimensional patient scaffold at R² ≈ 0.704.

Seed 0 showed early positive numerical/language gradient cosine on the ganglion (0.511 at step 25; 0.665 at step 50) while paired cross-modal state correspondence formed. Freezing the ganglion after step 200 retained endpoint performance. Removing the first two singular directions of the learned mixed ganglion displacement produced larger damage to both numerical and language performance than a matched-norm random matrix perturbation.

## Evidence scope
The patient-state scaffold is real. Statistical observation noise/processes and language surface descriptions are controlled constructions. The language pathway is a compact neural text perception model rather than a pretrained language model. This experiment tests the mixed-data coordination mechanism at controlled scale.
