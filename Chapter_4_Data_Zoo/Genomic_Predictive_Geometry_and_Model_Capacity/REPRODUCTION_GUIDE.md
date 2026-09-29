# Reproduction guide

This guide describes the executable coverage of the supplied evidence. A filename beginning with `reproduce_` does not by itself establish a complete replay path.

| Studies | Available material | Executable scope |
| --- | --- | --- |
| EXP001–EXP010 | Archived summaries, result CSVs where supplied, all figures, source identities and analysis protocol | The exact original supervised bottleneck fitting specification is not fully preserved. Results can be inspected and cross-checked, but this package is not a complete end-to-end refit implementation. |
| EXP011–EXP012 | Direction reliability, capacity results, locked EXP012 record and figures | Derived summaries and the failed capacity-band endpoint can be checked directly. |
| EXP013A | Supplied calibration script, reliability inputs and all result tables | Replay from released derived tables; paths are parameterized. Five output CSVs were compared with the supplied evidence during publication preparation. |
| EXP013B | Supplied estimator/resampling code, direction records, grouped calibration outputs and figures | Requires separately acquired fixed 50-person × 38-SNP observations in the archived order. Embedded provider genotypes were replaced with an explicit input argument. Estimator function bodies are unchanged. |
| EXP013C | Locked design, predictions before reveal, reference-comparison results and supplied code | The script accepts a separately acquired HapMap source. The outer split uses the locked LCG/Fisher–Yates rule; estimator resampling uses NumPy `default_rng` with recorded seeds. |
| EXP013D | Sample-support results, protocol and figures | Despite its joint filename, `reproduce_EXP013C_013D.py` does not execute the complete EXP013D scan. |
| EXP014A | Passport outputs, spectra, distances, figure and matrix-construction code | The supplied script reconstructs input matrices; it does not calculate the full Passport. Provider observations are excluded. |
| EXP014B | Study-design status | No numerical experiment executed. |
| EXP015A/B | Geometry/correlation/operator/control outputs, figures, protocol and seeds | The supplied EXP015 script is a protocol and seed record, not the full analysis implementation. Only the archived top 12 or top 20 singular values are supplied in those spectrum files; they should not be treated as complete spectra. |
| EXP015C | Locked paired genome–transcriptome protocol | No numerical result or executable full analysis is supplied. |

## Checking the released results

From this report directory, with NumPy, pandas and SciPy installed:

```bash
python evidence/scripts/verify_result_tables.py evidence --out numerical_verification.json
```

This performs 50 checks of mapping DOF, exact permutation arithmetic, selected-rank comparisons, stability summaries, estimator errors, and same-gene correlation summaries. It does not download provider observations or rerun original model fitting. The publication run is saved in `evidence/NUMERICAL_VERIFICATION.json`.

## Replaying EXP013A

Place the CSV files from `evidence/experiments/EXP011_PREDICTIVE_DIRECTION_STABILITY/` and `evidence/experiments/EXP012_SMALL_EXTERNAL_BLIND/` in a common local input directory. They are derived results already included in this release. Then run:

```bash
python evidence/scripts/reproduce_EXP013A.py --input-dir /path/to/derived_inputs --out /path/to/replay_outputs
```

The script additionally requires Matplotlib. `evidence/EXP013A_REPLAY_VERIFICATION.json` records numerical agreement with the archived CSVs. Replay does not turn this post hoc study into a new blind validation.

## Separately acquired provider observations

`evidence/SOURCE_MANIFEST.csv` records pinned source identities. The original package contained five observation snapshots and literal genotype dosage strings inside the EXP013B script. None is redistributed. The publication script instead accepts `--genotype-csv` and checks the matrix content/order against an archived digest. No acquisition or upload happens automatically.

```bash
python evidence/scripts/reproduce_EXP013B.py --genotype-csv /path/to/fixed_panel.csv --out /path/to/output
python evidence/scripts/reproduce_EXP013C_013D.py --source /path/to/hapmap.txt --out /path/to/output
python evidence/scripts/reproduce_EXP014A.py --genotype-csv /path/to/fixed_panel.csv --out /path/to/output
```

The fixed panel has 50 rows, one sample-ID column, and the 38 SNP columns in the archived row and feature order. EXP012's marker list and EXP013B's target-grid record specify the selection. EXP014A additionally uses the dataset interfaces in scikit-learn 1.8.0, statsmodels 0.14.6, and NetworkX 3.6.1. Its outputs are provider observation matrices for local use and are not part of this release.

## Documentation and numerical fidelity

The supplied EXP013C script docstring described PCG64 for the outer split, while its implementation and locked record specify LCG/Fisher–Yates. The publication docstring is aligned with the latter; the calculation is unchanged. Protocol-only and partial scripts are labelled according to what they execute. Nonresearch continuation fields were removed. `evidence/FILE_PROVENANCE.csv` records source and publication hashes for included files.

All original result CSV values and figure bytes are preserved. The source Word's maintenance-history table is excluded; its 27 scientific tables and 32 figure placements are retained in the English report. The exact stable50 capacity ratio range is 0.941176–1.60; the source's approximate “1.0–1.6” wording is accompanied by that exact range. The EXP015A r90 entries 25/4/7 are counts out of 81, not fractions. These clarifications do not replace the original numerical results.
