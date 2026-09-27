# Evidence index

Study identifiers 001–004 link the merged report to the four original investigations. Figure and table numbers below refer to the merged English edition.

| Study | Question and analysis unit | Report location | Primary evidence |
| --- | --- | --- | --- |
| 001 · Human Comfort Geometry | Geometry of seven public datasets; dataset-level spectra and local neighborhoods | Section 1; Tables 1–5; Figures 1–3 | [Geometry results](evidence/experiments/001/Evidence/combined_geometry_results.csv) · [Subsampling](evidence/experiments/001/Evidence/resampling_stability.csv) |
| 002 · Human Learning Dimension | Learning under one to three reward-relevant dimensions; 102 retained participants and 55,080 trials | Section 2; Tables 6–9; Figures 4–7 | [Conditions](evidence/experiments/002/Evidence/condition_summary.csv) · [Paired effects](evidence/experiments/002/Evidence/paired_effects.csv) · [Exclusions](evidence/experiments/002/Evidence/exclusions.csv) · Published comparison: report Section 2.8 and Figure 7 |
| 003 · Human Sensorimotor Geometry | Twenty motion clips from three subjects and a technical-English corpus, measured in specified representations | Section 3; Tables 10–17; Figures 8–11; supplementary Figure 17 | [Clip results](evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/motion_trial_geometry.csv) · [Group summaries](evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/motion_group_summary.csv) · [Language results](evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/language_geometry.csv) · [Comparison](evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/motion_language_comparison.csv) |
| 004 · Human EMG Reaching Geometry | Effector recruitment and temporal covariance in 900 reaches by ten participants | Section 4; Tables 18–21; Figures 12–16 | [Key results](evidence/experiments/004/Evidence/key_results.csv) · [Participant results](evidence/experiments/004/Evidence/subject_level_results.csv) · [Target rows](evidence/experiments/004/Evidence/target_row_summary.csv) · [Spectra](evidence/experiments/004/Evidence/spectrum_summary.csv) · [Longer-window sensitivity](evidence/experiments/004/Evidence/long_trial_sensitivity.csv) |

## Analysis files

| Study | Browse analysis outputs, figures and code |
| --- | --- |
| 001 | [Files](evidence/experiments/001/Evidence/) |
| 002 | [Files](evidence/experiments/002/Evidence/) |
| 003 | [Files](evidence/experiments/003/Evidence/human_sensorimotor_geometry_003/) |
| 004 | [Files](evidence/experiments/004/Evidence/) |

## Figure and table correspondence

[FIGURE_MAP.csv](FIGURE_MAP.csv) identifies every displayed image, its source evidence path, complete caption, and SHA-256. The 16 images embedded in the four source reports retain their original bytes. Figure 17 adds the pose-versus-velocity image supplied with Study 003. Study 004 source Figure 4 uses `fig5_emg_recruitment_sensitivity.png`; source Figure 5 uses `fig4_dominant_mode_retention.png`. The map follows the report order.

[TABLE_MAP.csv](TABLE_MAP.csv) maps the 21 numbered study tables to their source numbers. The three additional reader tables provide the research map, terminology, and source index.

[EVIDENCE_MANIFEST.csv](EVIDENCE_MANIFEST.csv) maps the included authored evidence to its study source and records current file hashes. Original scientific outputs retain their source bytes; packaging notes and checksum lists describe this public edition. [CHECKSUMS.sha256](CHECKSUMS.sha256) verifies the current component relative to this directory. [Source availability](SOURCE_AVAILABILITY.md) distinguishes research provenance from the files included in the public package.
