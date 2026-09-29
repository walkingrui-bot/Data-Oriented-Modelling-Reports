# Evidence index

[Report](REPORT_EN.md) · [Sources](SOURCE_AVAILABILITY.md) · [Reproduction guide](REPRODUCTION_GUIDE.md)

| Study | Measured object and evidence level | Available evidence |
| --- | --- | --- |
| [LM-BASE-001](evidence/experiments/LM-BASE-001/) | Prior language and human-motion reference calculations | Baseline geometry summary; Figure 1; source identities |
| [INTOX-SPEECH-CAL-002](evidence/experiments/INTOX-SPEECH-CAL-002/) | Published 150-speaker ALC disfluency calibration | Original study transcription; three-cell primary-source mapping annotation |
| [INTOX-SPEECH-GEO-003](evidence/experiments/INTOX-SPEECH-GEO-003/) | Recorded direct acoustic calculation: 103 segments from two recordings | Pooled geometry, segment medians, resampling and timing-control summaries; preprocessing specification; core geometry script; Figures 2–5 |
| [INTOX-GAIT-GEO-004](evidence/experiments/INTOX-GAIT-GEO-004/) | Aggregate reanalysis of a published 100-participant study | Four-by-six standardized displacement matrix; recorded SVD, loading, cosine and residual summaries; Figures 6–8 |
| [INTOX-GAIT-ROBUST-005](evidence/experiments/INTOX-GAIT-ROBUST-005/) | Robustness and orthogonal factorization of the same aggregate object | Feature/subgroup removal, scaling controls, recorded permutation summaries, Hadamard decomposition, executable gait script; Figures 9–13 |

The integrated interpretation appears in report Section 8 under the working nickname “The Magical Hypothesis.” Its evidential basis is the combination of the distinct speech and gait objects above.

[Publication verification](evidence/verification/VERIFICATION.json) · [Public-matrix rerun outputs](evidence/verification/gait_rounded_matrix/) · [File provenance](evidence/FILE_PROVENANCE.csv) · [Source registry](evidence/records/source_registry.csv)

All thirteen supplied figures are preserved byte-for-byte. Numeric evidence CSVs retain the supplied values. The original ALC table is accompanied by [verified cell mappings](evidence/experiments/INTOX-SPEECH-CAL-002/primary_source_cell_mapping.csv). Report table extractions are available in [report_tables](evidence/report_tables/); these are transcriptions and reader annotations, with their roles listed in [TABLE_MAP.csv](TABLE_MAP.csv).
