# Evidence index

Data-Oriented Modelling · Chapter 5 · Report 03

The research spans twelve named experiments. The early stage is represented by 18 exact report-embedded figures and 21 exported report tables. MDM-KERNEL-002 supplies repeated graph measurements and a protocol sketch. MDM-SOP-BLIND-VALIDATION-003 supplies a precommitment record, three staged analysis scripts, per-split outcomes and the nested Engel comparison.

| Experiment | Question | Report | Evidence |
| --- | --- | --- | --- |
| MDM-ATTN-001 | Label assisted gap occupancy | [Section 3](REPORT_EN.md#3-label-assisted-tests-of-gap-occupancy) | [Figures 1–2](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-ATTN-002 | Unsupervised topology and neighbourhood preservation | [Section 4](REPORT_EN.md#4-unsupervised-tests-of-topological-distortion) | [Figures 3–5](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-SPRING-001 | Candidate screening from local compression | [Section 6](REPORT_EN.md#6-screening-candidates-based-on-local-compression) | [Table 2](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-SPRING-002 | Elastic local scale dissimilarity | [Section 7](REPORT_EN.md#7-the-elastic-local-scale-metric) | [Figures 6–8](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-SPRING-003 | SpringGraph and multiscale relations | [Section 8](REPORT_EN.md#8-springgraph-and-relations-across-scales) | [Figures 9–10](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-ATTN-003 | Geometry constraints around attention | [Section 9](REPORT_EN.md#9-geometry-constraints-around-standard-attention) | [Displayed equations and method](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-ATTN-004 | Aggregation replacement criteria | [Section 10](REPORT_EN.md#10-criteria-for-replacing-the-aggregation-operator) | [Table 3](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-TRAIN-001 | Training coverage and prevalence calibration | [Section 11](REPORT_EN.md#11-training-coverage-and-sampling-density) | [Figures 11–13; sections 11–12](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-SOP-001 | Validation of the modelling procedure | [Section 17](REPORT_EN.md#17-validation-of-the-complete-modelling-procedure) | [Tables 5–8; Figures 14–15](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-KERNEL-001 | Discrete graph state constraints | [Section 18](REPORT_EN.md#18-state-legality-in-discrete-graphs) | [Tables 9–12; Figures 16–18; sections 18–19](evidence/experiments/EARLY_REPORT_RECORDS/README.md) |
| MDM-KERNEL-002 | Selecting operators from graph relations | [Section 20](REPORT_EN.md#20-selecting-operators-from-the-relation-mechanism) | [Tables 13–14; Figures 19–20; per-split CSVs](evidence/experiments/MDM-KERNEL-002/README.md) |
| MDM-SOP-BLIND-VALIDATION-003 | Precommitted validation across four datasets | [Section 21](REPORT_EN.md#21-precommitted-validation-on-additional-datasets) | [Tables 15–19; Figures 21–25; staged scripts and per-split CSVs](evidence/experiments/MDM-SOP-BLIND-VALIDATION-003/README.md) |

## Recorded-result checks

All 81 listed checksums in the supplied collection matched. The precommit record matches its recorded SHA-256. The published Word and table transcriptions preserve 179 original numerical table cells, including the expression of +3.83% as 3.83% higher error. Verification of later experiments recalculates means and win counts from the supplied per-split CSVs.

The [verification script](verification/verify_results.py) supports result reconciliation directly from the published files. The [file map](EVIDENCE_FILE_MAP.csv) records source and publication hashes, including the portable output-path adaptations in the staged scripts.

[Report overview](README.md)
