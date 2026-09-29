# Reproduction guide

[Evidence index](EVIDENCE_INDEX.md) · [Source availability](SOURCE_AVAILABILITY.md)

Run the commands below from the publication directory. The scripts use Python, NumPy and pandas. The publication rerun used Python 3.12.14, NumPy 2.3.5 and pandas 2.2.3; package versions are recorded in `requirements.txt`.

## Gait geometry and robustness

The distributed input is the authored three-decimal 4 × 6 standardized displacement matrix. Its row order is female forward, male forward, female backward, male backward. Column order is foot rotation, stride length, step width, stride time, cadence, velocity.

```bash
python evidence/experiments/INTOX-GAIT-ROBUST-005/recompute_gait_004_005.py   evidence/experiments/INTOX-GAIT-GEO-004/gait_displacement_matrix_soberSD.csv   --outdir gait_recompute --nperm 200000 --seed 20260927
```

The script computes base uncentered SVD metrics, six feature-removal fits, four subgroup-removal fits, row-unit/column-RMS/sign controls, four Hadamard energy components and feature-identity permutation statistics. It also writes the full generated permutation draws to the chosen local output directory. The public evidence includes compact rerun summaries in `evidence/verification/gait_rounded_matrix/`.

| Quantity | Public-matrix rerun |
| --- | --- |
| PC1 energy | 77.7307674386% |
| Top-2 energy | 90.7619363928% |
| Stable rank | 1.2864918654 |
| Participation rank | 1.5921526357 |
| Shared Hadamard energy | 61.4038943933% |
| PC1 permutation upper-tail p | 0.0276948615 |
| Shared-factor permutation upper-tail p | 0.0408947955 |

The empirical upper-tail estimate uses `(exceedances + 1)/(replicates + 1)`. Every permutation independently rearranges the six feature values within each row, preserving row values and their magnitude distribution while breaking shared feature labels. Both tests are evaluated from the generated matrix ensemble in this script. The original report records PC1 p = 0.0275 and shared-factor p = 0.0409 at its working precision. The original rounded-matrix reference CSV agrees with all nine independently checked deterministic quantities.

The main gait script’s outputs are the named calculations above. The report also discusses exhaustive feature subsets, mean-vector alignment, pairwise cosines and residual geometry; the supplied evidence carries recorded summaries for these quantities. The publication verification additionally calculates the mean-vector/PC1 alignment when checking the rounded-matrix reference.

## Acoustic core geometry

Acquire the required KAISD inputs through the source project and prepare a trusted local NPZ with `sober` and `intoxicated` arrays of segments. Each segment has shape 128 × 345 or 345 × 128. Keep the 52/51 condition membership and original segment boundaries explicit. The supplied template accepts object arrays and therefore expects a trusted local NPZ.

```bash
python evidence/experiments/INTOX-SPEECH-GEO-003/recompute_speech_geometry_template.py   /path/to/local_segments.npz --out speech_recomputed
```

The template implements the pooled state and movement spectra and per-segment trajectory measurements: a shared band-wise mean/SD scaler fitted to pooled frames, within-segment differences, covariance spectra, step size, adjacent-direction cosine, tortuosity and channel-energy participation. Source preprocessing uses 22,050 Hz sampling, 2,048 FFT points, 512-sample hops, 128 mel bands and the source project’s per-segment image normalization.

Segment resampling and destructive timing controls are represented by their recorded summaries and report descriptions. Their full generation loops are outside the supplied core template. The report specifies 250 condition-wise 80% segment subsamples and 30 frame-order permutations; the independent-band-shift replicate count and the original speech seeds are unspecified in the supplied record. The publication verification reruns the included gait object and checks the speech summaries against the supplied report; the speech tensors remain with their provider.

## Reading the evidence files

`*_report.csv` and `report_recorded_*.csv` preserve the study’s recorded result precision. `gait_displacement_matrix_soberSD.csv` is the distributed derived matrix. `verification/gait_rounded_matrix/` contains publication rerun outputs. `primary_source_cell_mapping.csv` is a labelled source-verification annotation. The figure map supplies publication captions and the table map distinguishes scientific tables from reader annotations.

SHA-256 checksums cover the distributed files. The snapshot inventory records their sizes and identities; the archive contains no original provider observation files.
