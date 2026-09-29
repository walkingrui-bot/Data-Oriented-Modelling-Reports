# Sources and reproducibility

[Report](REPORT_EN.md) · [Evidence index](EVIDENCE_INDEX.md)

## Distributed evidence

The edition is based on the author-supplied 021–028A master report and complete experimental archive dated 29 September 2026. All 328 entries in the supplied source checksum manifest verified against the archive. The report's 19 embedded images match the corresponding source figure files byte for byte.

The release distributes authored experimental results, synthetic measurements, derived summaries, surrogate-generated examples, source identities, code and 78 unchanged standalone research figures. In the 023 example table, the `actual` column contained provider transcript text; the distributed table retains the task/action labels and the authored `free` and `controlled` generations. External raw corpora, original provider trajectories, repeated archive wrappers, document-version copies and operational handover material are outside this distribution.

## Primary source identities

| Evidence line | Input source | Included reconstruction information |
| --- | --- | --- |
| 021 | Locally installed Go HTML documentation, stripped to a technical-language corpus | Four source-dependent scripts and the recorded corpus dimensions, vocabulary, transition counts and result tables; the source Go version and corpus content hash are unspecified |
| 022–025 | [SWE-Xplorer-Experiments](https://github.com/mahirlabibdihan/SWE-Xplorer-Experiments), mini-SWE-agent trajectory collections labelled `gpt-5-mini`, `deepseek-v4-flash` and `qwen-2.5-7b` | Matched task IDs, model summaries, held-out result tables and generated surrogate examples |
| 026A | HISTORY-ALGEBRA-012, described in [Chapter 3, Report 01](https://github.com/walkingrui-bot/Data-Oriented-Modelling-Reports/blob/main/Chapter_3_Machine_Learning_Epidemiology/Research_Report/REPORT_EN.md) | History-pair, swap-context and update-scale summaries |
| 026B–027E | Authored 16-parameter controlled recurrent system | Run-level, state, edge and event tables, measured summaries, figure files and the experimental descriptions |
| 028A / ASTIG | Same public coding-agent collection and task-matched work-state pools | [Thirty trajectory source URLs](evidence/supporting/ASTIG_013C/astig013c_source_manifest.csv), derived task tables and the phase-reconstruction script |

The three public trajectory directory labels were checked against the source repository during publication review. They are retained as dataset model labels. The [mini-SWE-agent project](https://github.com/SWE-agent/mini-swe-agent) and [SWE-bench Verified description](https://www.swebench.com/verified.html) identify the agent and benchmark context. The supplied trajectory URLs point to the provider's `main` branch; an original source commit and per-trajectory content hashes are not specified in the input manifest.

## Recalculate the included results

From the extracted report folder:

```bash
python checks/recalculate_results.py
```

The script reads only the included local tables. It recomputes weighted model summaries, source counts, curriculum contrasts, per-foundation training means, acceptance gates, exit and recovery rates, routing assignments, candidate counts and phase bounds. The saved result is [recalculation_results.json](checks/recalculation_results.json): 100 checks passed.

Publication verification used Python 3.12.14, NumPy 2.3.5 and pandas 2.2.3. Tolerances follow the precision of the source tables. The six-decimal 026A energy table is compared with its higher-precision summary at an absolute tolerance of 0.0000005. This route verifies arithmetic and consistency of saved measurements; it is separate from rerunning model training or obtaining live intervention outcomes.

## Source-dependent code

The four [021 scripts](evidence/experiments/021) implement the language-surrogate analyses. They expect a local Go documentation directory and contain the original output-directory setting. Configure input and output paths in a local working copy before use. Matching the original corpus requires its original Go documentation snapshot.

The [ASTIG-013C script](evidence/supporting/ASTIG_013C/astig013c_reproduce.py) retrieves the identified provider trajectories and reconstructs phase/calibration summaries. That source-dependent retrieval route was not run for this publication. The release's default numerical verification uses the included derived tables.

The supplied 026B file named as a reproduction script consists of two comments, with no executable training implementation. It is therefore not presented as runnable code. Complete executable fit/training/recovery scripts for 022–027E are not contained in the supplied canonical folders. Their provided tables support the local recalculation route above. No new substitute training implementation is asserted as the original experiment.

## Field interpretation

| Supplied field or label | Interpretation in the integrated report |
| --- | --- |
| `external_L3_fallback_needed`, `external_L3_available_for_fallback` | L2b candidate-pool expansion counts. The operation adds available actions while retaining the current history. |
| `local_L2_available_k8` | Candidate availability from local history at width k=8, before any claim of executed task recovery. |
| `Submitted` | Recorded trajectory termination status, separate from benchmark pass/fail. |
| `POST_EDIT_VALIDATED` | Recorded edit followed by a recognised verification action, with the stated failed-test override. It is an operational history rule. |
| `correct`, `survival`, signed answer margin in 026–027 | Known-answer measurements in the controlled task. A deployed agent requires its own validated correctness signal. |
| L3 commitment projection in 027E | Immediate-answer recovery after reconstruction. The 027C neighbourhood-robustness comparison separately favours prompt restart for the two difficult cases. |

Machine-readable field names and numerical values are preserved for compatibility with the supplied evidence. The report applies the operation-based L2b/L3 definitions consistently.

## Figure and comparison notes

`stable_wrong_after_repeated_prompt.png` in 027D has an inconsistent original title. Its numerical bars show future-correct fractions conditional on the present answer remaining wrong. The values 96.0% and 92.1% after repeats two and four support high local recoverability. The integrated text and caption state that reading, and the image bytes are preserved.

The 025 simple-baseline success percentages are compatible with a denominator of 84 under a per-state interpretation, whereas the fitted pointer explicitly uses 93 eligible states. This is an inference from the supplied rates, not a recovered baseline membership list. The original comparison is retained with that qualification.

The 026C screening figures and 100-microstep figures describe different settings. Use the main report's stable tables for the cited eta=0.02 and eta=0.05 outcomes. Figures display point estimates or descriptive summaries, with no uncertainty intervals.

## Interpretation of validation

The canonical study comprises 18 linked experimental units. Its recurrent interventions share the qualified foundations, and later recovery analyses share exit events. Recorded-agent candidate and phase results share the task-matched source cohort. These designs support within-assay comparisons; study counts, states and figures are not counts of independent replications.

The supplied design for executed baseline/controller forks is included in the report as an evaluation protocol. This edition's real-agent outcomes are measured at the recorded-routing and candidate-availability level.
