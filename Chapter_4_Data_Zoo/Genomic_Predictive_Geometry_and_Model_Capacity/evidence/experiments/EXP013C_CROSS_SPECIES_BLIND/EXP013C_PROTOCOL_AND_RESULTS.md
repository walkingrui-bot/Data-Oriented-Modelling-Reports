# CROSS-SPECIES-ESTIMATOR-BLIND-013C

This is a preregistered external estimator-transfer test. The source is the public MVP maize HapMap demo matrix, locked at Git blob `b8120641d506cd1ee55e46d8c345f313501c21ae`. Before independent reference genotypes were used, the experiment fixed the 30/60/60/129 sample split, four chromosome tasks, train-only marker filters, 38-marker panels, q=9 target grid, missing-value rule, EXP013B affine coefficients, and primary/secondary endpoints. The complete locked object is `EXP013C_preregistration_locked.json`.

Primary result: the locked whole-training bootstrap calibration achieved lower direction-level MAE against the independent 129-person maize operator than the locked split-mean calibration. The corresponding MAEs were 0.1466 and 0.1728. Raw direction ordering also favored bootstrap (Spearman 0.5453 vs 0.5413). The preregistered stable-count comparison also held: power-debias mean task-level count error was 1.0 versus 1.5 for bootstrap.

The external result separates ordering transfer from absolute-scale transfer. The locked human-panel calibrations preserve useful relative direction information in maize, but absolute reliability magnitudes shift by task; maize chromosome 4 is the clearest example, where the independent reference contains four directions above 0.5 while the locked bootstrap calibration predicts zero and power-debias predicts one. This motivates EXP013D as a post-hoc decomposition of sample-resolution and calibration shift.

Evidence boundary: this experiment validates estimator transfer across species on four tasks from one maize panel. It does not test model-capacity selection.

## Machine-readable summary

```json
{
  "experiment": "CROSS-SPECIES-ESTIMATOR-BLIND-013C",
  "status": "external cross-species blind estimator transfer; preregistration written before independent reference genotypes were opened",
  "source": "shanwai1234/MVP demo.data/hapmap/hapmap.txt",
  "source_blob_sha": "b8120641d506cd1ee55e46d8c345f313501c21ae",
  "tasks": 4,
  "directions": 36,
  "n_train": 30,
  "n_independent_reference": 129,
  "primary_endpoint_bootstrap_MAE_lower_than_split_mean": true,
  "secondary_raw_bootstrap_spearman_higher_than_split_mean": true,
  "secondary_power_count_MAE_no_larger_than_bootstrap": true,
  "metrics": {
    "split_mean": {
      "direction_MAE": 0.17281535128259512,
      "direction_RMSE": 0.19585532070070977,
      "raw_spearman": 0.5412711617894204,
      "cal_spearman": 0.5412711617894204,
      "stable50_accuracy": 0.75
    },
    "split_power_rel": {
      "direction_MAE": 0.15890220528617133,
      "direction_RMSE": 0.19532845639361146,
      "raw_spearman": 0.5188854010229753,
      "cal_spearman": 0.5188854010229753,
      "stable50_accuracy": 0.8333333333333334
    },
    "bootstrap": {
      "direction_MAE": 0.14659777150652079,
      "direction_RMSE": 0.18154400843772592,
      "raw_spearman": 0.5453141272399766,
      "cal_spearman": 0.5453141272399766,
      "stable50_accuracy": 0.7777777777777778
    }
  },
  "mean_task_stable_count_abs_error": {
    "split_mean": 2.25,
    "split_power_rel": 1.0,
    "bootstrap": 1.5
  },
  "mean_reference_stable50": 2.25,
  "mean_reference_effective_support": 2.902032582861613,
  "finding": "The locked human-panel bootstrap calibration transferred poorly in absolute scale to maize but still preserved more of the direction ordering than the split-mean baseline. Power-debias and bootstrap stable-count errors were similar, with power not worse on the preregistered count endpoint. The external result therefore supports the ordering advantage more strongly than universal calibration of reliability magnitude.",
  "evidence_boundary": "This is a cross-species estimator-transfer result on four tasks derived from one public maize HapMap panel. It tests reliability estimators, not model-capacity selection."
}
```
