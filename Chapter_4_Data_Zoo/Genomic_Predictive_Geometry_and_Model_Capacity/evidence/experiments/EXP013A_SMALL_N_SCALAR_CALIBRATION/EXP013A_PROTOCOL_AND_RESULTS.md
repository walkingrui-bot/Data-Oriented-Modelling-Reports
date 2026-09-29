# SMALL-N-RELIABILITY-CALIBRATION-013A

This is a post-hoc calibration/diagnostic experiment using archived real-data outputs from EXP011 and EXP012. No synthetic dataset is used. EXP012 capacity outcomes were already revealed before this experiment, so they are used only as a stress target, not as blind validation.

Calibration: six fixed scalar summaries plus an exploratory hard-threshold sweep are fit only on the eight medium-n EXP011 tasks using scale-only regression and leave-one-task-out MAE. The chosen threshold is then applied unchanged to the four locked EXP012 reliability runs.

Resolution diagnostic: repeated-split relative gap = |E1-E2| / mean(E1,E2), where E is continuous effective support. Four chr21 tasks provide two archived split estimates; EXP012 provides two partitions for each of two target grids.


```json
{
  "experiment": "SMALL-N-RELIABILITY-CALIBRATION-013A",
  "status": "post-hoc estimator calibration using archived real-data operator outputs; not a blind validation",
  "calibration_tasks": "8 real medium-n chr21/chr22 tasks from EXP011",
  "stress_task": "EXP012 real 50-sample 1000 Genomes task; train n=30; revealed near-optimal rank=5",
  "best_medium_threshold_tau": 0.59,
  "best_medium_threshold_LOO_MAE_rank": 2.578294676943035,
  "best_medium_threshold_EXP012_prediction_continuous": 1.1296966323406625,
  "best_medium_threshold_EXP012_prediction_rounded": 1,
  "best_fixed_soft_EXP012_prediction": {
    "estimator": "sqrt_support",
    "continuous": 2.9246623804040213,
    "rounded": 3,
    "medium_LOO_MAE_rank": 4.920954720579207
  },
  "EXP012_actual_nearopt_rank_005": 5,
  "medium_chr21_relative_split_gap_mean": 0.012204834098859951,
  "medium_chr21_relative_split_gap_max": 0.024276897160597815,
  "EXP012_relative_split_gap_mean": 0.2048333535948037,
  "EXP012_relative_split_gap_min": 0.1161129188644028,
  "split_gap_mean_ratio_small_over_medium": 16.782969103524078,
  "finding": "Re-thresholding or scalar soft transforms of archived reliability spectra do not recover the small-n near-optimal rank. Repeated-split effective support is far less stable in EXP012, providing a direct resolution-warning observable."
}
```
