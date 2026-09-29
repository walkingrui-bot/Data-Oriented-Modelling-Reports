# Analysis Protocol Notes

## Geometry
- Genotypes are encoded as diploid alternate-allele dosage 0/1/2.
- SNP columns are standardized using the relevant training sample where prediction is evaluated.
- Global effective dimension uses the participation ratio of the standardized covariance spectrum.
- Local intrinsic dimension uses a TWO-NN nearest-neighbour estimator.
- Predictive geometry is calculated from the observed→target cross-covariance matrix.
- `r90` is the number of singular directions required for 90% cross-covariance spectral energy.
- Predictive energy is the mean squared standardized cross-covariance energy per target.

## Predictive model
- Supervised low-rank linear bottleneck.
- Rank is scanned over a predetermined grid.
- Capacity selection uses validation or held-out test according to the experiment design stated in the report.
- External chr22 experiment locks the geometry-derived rank before the capacity sweep is opened.

## Exact permutation validation added during report consolidation
For EXP006C, the 19-window q=48 experiment has 8 rank-48 and 11 rank-40 labels. All C(19,8)=75,582 label allocations were enumerated while preserving this class count. The two-feature leave-one-window-out rule reached 18/19 exact matches with exact tail probability 3/75,582 = 3.9692e-5. Four contiguous genomic blocks (5,5,5,4 windows) yielded 15/19 matches; exact permutation tail probability = 576/75,582 = 0.00762086.


## PREDICTIVE-DIRECTION-STABILITY-011
Split the training individuals into stratified halves A/B. Estimate observed-to-target cross-covariance operators C_A and C_B. Define S=(C_A+C_B)/2 and N=(C_A-C_B)/2. Along each right singular direction v_k of S, define reliability r_k=clip(1-||N v_k||^2/||S v_k||^2,0,1). stable50 is the number of directions with r_k>=0.5. Capacity is also summarized by the smallest rank within 0.005 or 0.010 validation R^2 of the task maximum. Controls shuffle target individuals globally or within super-population before constructing the operator.


### EXP012 small-data blind test
Before any capacity scan, the source, split, MAF filter, stability protocol, stable50, center rule and rank band were written to `EXP012_preregistration_locked.json`. Primary success required the validation minimal rank within 0.005 R2 of the validation maximum to fall inside the locked band. Test data were never used to select rank. The endpoint failed (predicted [1,1], revealed near-optimal rank 5).


## SMALL-N-RELIABILITY-CALIBRATION-013A
Uses only archived real-data operator outputs from EXP011 and EXP012. Six fixed scalar summaries are calibrated by a scale-only map on the eight medium-n EXP011 tasks and assessed by leave-one-task-out MAE. An exploratory reliability threshold sweep (0.05–0.80 in 0.01 increments) is selected only by medium-n LOO MAE, then applied unchanged to EXP012. Because EXP012 capacity results were already revealed, this is estimator calibration/diagnosis rather than blind validation.

Resolution warning is measured by the relative repeated-split gap in continuous effective support: |E1-E2| / mean(E1,E2). Archived chr21 medium-n duplicate splits are compared with the two locked partitions for each of the two EXP012 target grids.


### EXP013B raw-operator small-n calibration
Uses the exact real BioNumPy/1000 Genomes source and the 38-SNP panel archived by EXP012. The panel is held fixed; no new SNP selection is performed. For each of 128 deterministic outer resamples, 30 individuals form the estimator sample and 20 different individuals form an independent operator reference. Two fixed non-overlapping 9-SNP target grids are evaluated. Right singular directions are defined from the 30-person operator. Independent direction reproducibility is `clip(2 a·b/(||a||^2+||b||^2),0,1)` with `a=C_train v_k` and `b=C_holdout v_k`. Estimators are one 15/15 split, mean/median over 30 15/15 splits, power-domain debias using mean split noise power, and 200 whole-training bootstraps of size 30. Affine calibration is evaluated by grouped leave-one-outer-split-out folds so all 18 directions from the held-out people split are absent while the calibration line is fit. EXP013B is calibration on one real source, not external blind validation.


## EXP013C–EXP014A
EXP013C freezes all estimator coefficients and sample/task rules before independent maize reference genotypes are opened. EXP013D is explicitly post-hoc. EXP014A measures four real data structures with a shared passport interface and makes no architecture-routing claim.
