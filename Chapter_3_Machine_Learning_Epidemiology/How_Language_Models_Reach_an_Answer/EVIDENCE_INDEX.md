# Evidence index

[Report](REPORT_EN.md) · [Figures](FIGURES.md) · [Sources and reproduction](SOURCE_AVAILABILITY.md)

The 18 canonical experiment identities remain the keys for matching report claims to measurements. Later controlled experiments reuse foundations and events; supporting and supplementary summaries overlap the canonical cohorts.

| Experiment | Measured object | Evidence | Figures |
| --- | --- | --- | --- |
| [021](REPORT_EN.md#experiment-021) | Statistical language surrogate; Go documentation-derived transition summaries. | [27 files](evidence/experiments/021) | 3 |
| [022](REPORT_EN.md#experiment-022) | Recorded-agent next-action and visible-text prediction; whole-task holdout. | [8 files](evidence/experiments/022) | 3 |
| [023](REPORT_EN.md#experiment-023) | Authored utterance generation over 124 recorded-state contexts. | [6 files](evidence/experiments/023) | 2 |
| [024](REPORT_EN.md#experiment-024) | Shell-slot prediction and pointer refinement over 124 states. | [5 files](evidence/experiments/024) | 2 |
| [025](REPORT_EN.md#experiment-025) | Object retrieval, source attribution and end-to-end utterance prediction. | [7 files](evidence/experiments/025) | 3 |
| [026A](REPORT_EN.md#experiment-026a) | Archived 24-history control fields and reverse-pair summaries. | [7 files](evidence/experiments/026A) | 3 |
| [026B](REPORT_EN.md#experiment-026b) | New recurrent harness; 17 qualified foundations and matched curricula. | [7 files](evidence/experiments/026B) | 3 |
| [026C](REPORT_EN.md#experiment-026c) | Screening plus 100-microstep protected-update stability runs. | [13 files](evidence/experiments/026C) | 6 |
| [026D](REPORT_EN.md#experiment-026d) | Sparse-anchor screen and 60-microstep confirmation. | [12 files](evidence/experiments/026D) | 5 |
| [026E](REPORT_EN.md#experiment-026e) | Observable anchor selection and controlled training interventions. | [14 files](evidence/experiments/026E) | 4 |
| [026F](REPORT_EN.md#experiment-026f) | 29 static auxiliary settings and six primal–dual settings. | [15 files](evidence/experiments/026F) | 4 |
| [026G](REPORT_EN.md#experiment-026g) | Control-rank, refresh and update-scale sweeps. | [24 files](evidence/experiments/026G) | 4 |
| [027A](REPORT_EN.md#experiment-027a) | 408 correct states, 2,040 candidate edges and 352 canonical transitions. | [10 files](evidence/experiments/027A) | 3 |
| [027B](REPORT_EN.md#experiment-027b) | Bounded recovery on 125 controlled post-exit states. | [5 files](evidence/experiments/027B) | 3 |
| [027C](REPORT_EN.md#experiment-027c) | Context reconstruction, re-entry robustness and contamination stress tests. | [14 files](evidence/experiments/027C) | 4 |
| [027D](REPORT_EN.md#experiment-027d) | Nine development and eight held-out foundations; append-only rescue. | [16 files](evidence/experiments/027D) | 5 |
| [027E](REPORT_EN.md#experiment-027e) | Event-level assembly of the same 125 exit opportunities. | [7 files](evidence/experiments/027E) | 3 |
| [028A](REPORT_EN.md#experiment-028a) | Recorded-agent candidate routing over 300 strong-loop states. | [4 files](evidence/experiments/028A) | 2 |

## Supporting recorded-agent measurements

| Study | Purpose | Evidence |
| --- | --- | --- |
| ASTIG-013A | Cooldown interception, task timing and Submitted control behaviour | [Files](evidence/supporting/ASTIG_013A) |
| ASTIG-013B | Candidate availability, progression roles and rank | [Files](evidence/supporting/ASTIG_013B) |
| ASTIG-013C | Task-phase rules, candidate-role availability and Submit bounds | [Files](evidence/supporting/ASTIG_013C) |

## Supplementary audits

- [Controlled starting-state audit](evidence/supplementary/controlled_starting_state_audit): post-exit 123/2 routing and the separate stop-allowed/forced-continuation counts.
- [Real candidate-scope audit](evidence/supplementary/real_candidate_scope_audit): incremental local/external coverage and phase-role allocation.

These audits use the same source cohorts. Their starting conditions and aggregation explain the different routing counts; they are not additional independent validation samples.

## Result-file precedence

For 026C, the main report uses `final_summary.json` and `stability_100_microsteps*.csv`. The earlier `summary.json`, `raw_protected_update_runs.csv`, `protected_update_summary.csv` and their corresponding figures describe the initial screen. For 026D, `screen_*` and `confirm_*` identify distinct settings. For 026E–026G, retain update scale, selector, rank and refresh interval when comparing rows.

The [recalculation script](checks/recalculate_results.py) checks the report’s numerical comparisons from included local tables. The [file manifest](FILE_MANIFEST.json) and [SHA-256 list](SHA256SUMS.txt) identify the distributed files.
