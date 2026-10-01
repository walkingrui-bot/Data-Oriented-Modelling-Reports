# Evidence index

This edition connects each reported experiment to the recovered numerical outputs, figures and method records. Report tables transcribe the supplied manuscript; their presence does not imply recovery of the original observations.

| Experiments | Evidence included | Coverage |
| --- | --- | --- |
| ASTIG-001–010 | Report tables 2–26 and Figures 1–19 | Reported measurements and manuscript figures; original row-level outputs and early analysis scripts not recovered |
| ASTIG-011 | Table 27 and Figures 20–22 | Reported matched-task comparison; original experiment files not recovered |
| ASTIG-012A | [Gate outcomes, threshold sweep and summary](evidence/ASTIG_012A/) | Recovered numerical files |
| ASTIG-012B | [Model comparison, parameter sweep and summary](evidence/ASTIG_012B/) | Recovered numerical files |
| ASTIG-013A | [Cooldown, task results, controls, source manifest and script](evidence/ASTIG_013A/) | Recovered outputs; summary scope wording updated |
| ASTIG-013B | [Candidate availability and progression results](evidence/ASTIG_013B/) | The archive matching the reported 131/142/178 local candidates and 139/64/97 roles |
| ASTIG-013C | [Phase calibration, availability, bounds and script](evidence/ASTIG_013C/) | Recovered numerical outputs and method script |
| ASTIG-013D | [Controlled replay, persistence, horizons and script](evidence/ASTIG_013D/) | Recorded-continuation replay outputs |
| ASTIG-013E | [Eight-command execution matrix and summary](evidence/ASTIG_013E/) | Recovered derived outcomes; raw execution logs and source-code diffs excluded |
| MODE-COLLISION-001 | [Geometry, spectra, training, three-seed curves and scripts](evidence/MODE_COLLISION_001/) | Recovered numerical outputs; external request pairs excluded |
| MODE-CONTROL preliminary run | [Prompt metrics and summary](evidence/MODE_CONTROL/) | Four-prompt engineering checks, separate from the original cohort |
| MODE-CONTROL RUN-1 | [140-prompt baseline metrics](evidence/MODE_CONTROL/RUN1_baseline_metrics.csv) | Scalar measurements and mode labels; generated strings and encoded text excluded |
| MODE-CONTROL FINAL | [Final summary](evidence/MODE_CONTROL/MODE_CONTROL_FINAL_summary.json), Tables 55–56 and Figures 53–56 | Recovered final summary and manuscript aggregates; original intervention, control, generation and reversal row files not recovered |

The [57 report tables](evidence/report_tables/) and [56-figure catalogue](FIGURES.md) provide a consistent route back to the English report. Table 1 is the hypothesis register, Table 56 the synthesis and Table 57 the source map.

## Provenance and calculation checks

[SOURCE_MANIFEST.json](SOURCE_MANIFEST.json) identifies original archive hashes, file hashes and publication transformations. [SHA256SUMS](SHA256SUMS) checks the released files. The included verification script checks baseline counts, selected arithmetic and the three-seed aggregation using only these derived measurements. It does not retrain a model or repeat the intervention campaign.

Two recovered archives carrying ASTIG-013B in their names describe a separate radius/similarity-floor analysis. This edition uses the candidate-expansion archive whose numerical results match the report. It does not substitute one analysis for the other.

## Reproduction interfaces

ASTIG-013A, 013C and 013D scripts fetch public trajectory sources when run by a reader. Run each from its own directory in a separate working copy. Those URLs refer to the source repository's main branch and are not an immutable raw-data snapshot. No external trajectories are stored in this publication.

MODE-COLLISION-001 scripts require numpy, pandas, scipy, scikit-learn, torch and matplotlib, plus the separately obtained 70-pair JSON with the manifest hash. Run run_mode_geometry.py, run_mode_geometry_seed11.py, run_mode_geometry_seed19.py and then mode_collision_finalize.py from that directory. Publication edits make paths relative and align the seed-19 output filename with the finalizer. Seed 7's saved training curve reaches epoch 50; the other two scripts run 40 epochs. These recovered scripts are provided as method records and were inspected, not retrained for this publication.
