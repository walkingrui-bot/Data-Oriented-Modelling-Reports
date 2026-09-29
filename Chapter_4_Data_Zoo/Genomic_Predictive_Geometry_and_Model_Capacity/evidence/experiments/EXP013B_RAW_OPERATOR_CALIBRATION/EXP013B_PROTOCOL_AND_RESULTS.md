# SMALL-N-RELIABILITY-CALIBRATION-013B

EXP013B returns to the raw real genotype operator. It uses the exact 50-person BioNumPy/1000 Genomes panel and the 38-SNP panel already archived by EXP012. No synthetic data are used. The original EXP012 blind result is not re-run; this is post-hoc measurement calibration.

For each of 128 deterministic outer resamples, 30 people form the estimator sample and 20 different people form an independent operator reference. Two fixed non-overlapping 9-SNP target grids are evaluated. The right singular directions are defined from the 30-person operator. The independent target for each direction is the symmetric operator agreement R_hold = clip(2 a·b/(||a||²+||b||²),0,1), with a=C_train v_k and b=C_holdout v_k.

Estimator comparison: (i) one 15/15 split, (ii) mean of 30 15/15 splits, (iii) median of 30 splits, (iv) power-domain debias using mean split noise power, and (v) 200 whole-training bootstrap resamples of size 30. Affine calibration is evaluated with grouped leave-one-outer-split-out folds, so all 18 directions from the held-out people split are absent while the calibration line is fit.


```json
{
  "experiment": "SMALL-N-RELIABILITY-CALIBRATION-013B",
  "status": "post-hoc raw-operator estimator calibration on one real 50-person 1000 Genomes panel; repeated outer resampling; not external blind validation",
  "source": "bionumpy/bionumpy example_data/thousand_genomes.vcf",
  "source_blob_sha": "5faa223e61eb3b301ebc397eab1df22e4f105f8d",
  "fixed_panel": "38 SNPs archived from EXP012; no SNP reselection in EXP013B",
  "outer_design": "128 deterministic 30-train/20-independent-holdout splits x 2 fixed non-overlapping 9-SNP target grids",
  "direction_evaluations": 2304,
  "split_half": "30 random 15/15 partitions per task, all evaluated on full-training singular directions",
  "bootstrap": "200 size-30 resamples per task, all evaluated on full-training singular directions",
  "independent_reproducibility": "clip(2 a·b / (||a||^2+||b||^2),0,1), where a=C_train v_k and b=C_holdout v_k",
  "raw_direction_spearman": {
    "split_one": 0.4315143754843608,
    "split_mean": 0.518308964646912,
    "split_median": 0.5035989690426267,
    "split_power_rel": 0.7154532948744666,
    "bootstrap": 0.7676898239129254
  },
  "grouped_LOO_calibrated_direction_MAE": {
    "split_one": 0.18901653476952104,
    "split_mean": 0.18071155145869544,
    "split_median": 0.17942500637071246,
    "split_power_rel": 0.13563632979826507,
    "bootstrap": 0.12696619569312595
  },
  "grouped_LOO_calibrated_stable50_accuracy": {
    "split_one": 0.734375,
    "split_mean": 0.734375,
    "split_median": 0.734375,
    "split_power_rel": 0.8719618055555556,
    "bootstrap": 0.8784722222222222
  },
  "grouped_LOO_stable_count_MAE": {
    "split_one": 1.5546875,
    "split_mean": 1.5546875,
    "split_median": 1.5546875,
    "split_power_rel": 0.94140625,
    "bootstrap": 1.0390625
  },
  "bootstrap_vs_split_mean": {
    "raw_spearman_bootstrap": 0.7676898239129254,
    "raw_spearman_split_mean": 0.518308964646912,
    "calibrated_direction_MAE_bootstrap": 0.12696619569312595,
    "calibrated_direction_MAE_split_mean": 0.18071155145869544,
    "calibrated_stable50_accuracy_bootstrap": 0.8784722222222222,
    "calibrated_stable50_accuracy_split_mean": 0.734375,
    "stable_count_MAE_bootstrap": 1.0390625,
    "stable_count_MAE_split_mean": 1.5546875
  },
  "finding": "Using all 30 training individuals in bootstrap resamples preserves the ordering of directions that reproduce in independent people much better than 15/15 split-half estimates. A simple grouped-LOO affine calibration turns that ordering advantage into lower direction-level error and better stable-direction classification/counting. However the number of stable directions remains under-resolved: even the bootstrap count is not an exact capacity estimator.",
  "evidence_boundary": "All calibration and evaluation come from repeated resampling of the same 50-person real panel. The candidate coefficients are therefore calibration artifacts to be locked before a new external blind dataset, not a universal law."
}
```
