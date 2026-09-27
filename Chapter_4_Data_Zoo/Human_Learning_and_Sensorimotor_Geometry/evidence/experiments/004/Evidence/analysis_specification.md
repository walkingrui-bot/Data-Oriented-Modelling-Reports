# HUMAN-EMG-REACHING-GEOMETRY-004 analysis specification

## Source lock
DataSet.csv from `tianshi-yu/UpperLimbReachingData_HRL_Unimelb`, fixed Git blob
`44fa933e7d164aa7279c545047d42d6ee6aae5c4`.

The executed source contained 21,096 processed time windows, 51 columns, 10 subjects,
nine spatial targets and 900 reaches (90 per subject).

## Channels
Kinematic pose: Sfe, Saa, Scpr, Scde, Tfe, Tb.
Kinematic velocity: dSfe, dSaa, dScpr, dScde, dTfe, dTb.
EMG primary: RMS feature streams for BSH, BLH, TLAH, TLH, DA, DM, DP.
EMG sensitivity: corresponding MAV feature streams.

## Two meanings of dimension
**Recruitment / energy breadth.** For non-negative per-channel energies e_j,
breadth = (sum e_j)^2 / sum(e_j^2). This is a participation ratio and asks how
many coordinates or muscles materially share activity.

**Independent temporal spectrum.** Within a reach, each channel is standardized
by its subject-wide mean and SD. Eigenvalues of the channel covariance matrix are
used to compute stable rank = sum(lambda)/lambda_max, participation rank, d90,
d95, and top-k energy retention. This asks how many independent temporal modes
are needed to describe coordinated change.

## Endpoint breadth
For each reach, up to the first three and last three 10-Hz windows are averaged.
The six pose changes are divided by subject-wide channel SD, squared, then entered
into the participation-ratio formula. This produces a continuous realized movement
breadth independent of the EMG calculation.

## Energy breadth
Velocity and EMG channels are divided by their subject-wide RMS scale. Per-channel
mean squared normalized activity is calculated within each reach, then converted
to a participation ratio across the six velocity or seven muscle channels.

## Subject-level inference
Within each subject, Spearman correlations are calculated over 90 reaches. High-vs-low
contrasts compare top and bottom endpoint-breadth tertiles. Across-subject summaries use
the median of ten subject statistics. Intervals are deterministic 20,000-resample
subject-level bootstrap intervals with seed 20260927. Sign counts are retained because
n=10 subjects.

## Sensitivity checks
1. EMG energy breadth repeated with MAV instead of RMS.
2. Main contrasts repeated after excluding reaches with more than 45 processed windows.
3. Covariance spectra repeated after pooling all ten repetitions for each subject×target
   (median 206 windows/cell) and subject×target-row (median 611.5 windows/cell).
