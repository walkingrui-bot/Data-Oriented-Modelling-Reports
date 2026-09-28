# Reproduction guide

The evidence index identifies what can be inspected or executed for each study. Keep new executions in a separate output directory and compare them with the released reference tables.

## Verify the released record

From the report directory, `sha256sum -c CHECKSUMS.sha256` checks the published files. The numerical reconciliation reads the report table transcriptions and experiment outputs:

```bash
python verification/reconcile_tables.py
```

This writes `verification_results/` under the working directory. `B3_OUTPUT_DIR` can choose another directory. The expected record contains 1,301 checks, 1,299 direct-rounding matches and the two Table 42 annotations documented in Publication notes. Python, pandas and their NumPy dependency support this check.

## Simulations and foundational studies

Studies 001–023 supply recorded results, measurements, figures and available design metadata. Study 001 also supplies a synthetic model checkpoint. Full training programs are outside the supplied archives for these studies. Their evidence supports inspection of comparisons, controls and reported summaries. Report-only foundational studies have separately labelled table transcriptions and original figures.

## Active graph measurements: 024

Obtain Email-Eu-core-temporal separately using the recorded source identity and keep it outside the publication directory. The core script accepts the local raw file:

```bash
python evidence/experiments/024/analysis_method.py /path/to/email-Eu-core-temporal.txt
```

It calculates the largest gap, complete primary-segment windows, node/dyad matrices, spectral summaries and consecutive-state cosines. Coverage, degree-stratum, community and bootstrap results are supplied as recorded tables. The script depends on NumPy and pandas.

## Coarse-graining from released summaries: 025

```bash
python evidence/experiments/025/analyze_025.py
```

The default input is the adjacent 024 evidence directory; the default output is `reproduction_025/` under the working directory. `B3_INPUT_DIR` and `B3_OUTPUT_DIR` override them. NumPy, pandas and Matplotlib support this calculation. It reads only `active_neighbour_scale.csv` and `temporal_state_geometry.csv` and calculates the five-scale summaries and figures.

## Frozen corpus calculations: 026–028

The default numeric input directory for these scripts is the included 027 directory. It supplies `do026_X.npz`, `do026_Q.npz` and `do026_balanced_assign8.npy`. Output directories default to `reproduction_026/`, `reproduction_027/` and `reproduction_028/`. The task-specific environment variables `B3_INPUT_DIR` and `B3_OUTPUT_DIR` control the locations. Use Python with NumPy, pandas, SciPy and scikit-learn; plotting also uses Matplotlib. The process scripts were written for a Linux-style multiprocessing environment.

| Script | Calculation and input contract |
| --- | --- |
| `026/run_026.py` | Corpus extraction, placement and full-dimensional routing; set `B3_CORPUS_DOCX` to the separately held frozen source document; python-docx is also required |
| `026/run_026b.py` | Balanced compact routing and frozen numeric state generation; same source-document requirement |
| `026/run_026c.py` | Centralized/broadcast throughput from the included frozen numeric state |
| `026/run_026d.py` | Routed throughput from the included frozen numeric state |
| `027/run_027.py` | Replication, failure, original straggler calculation and concurrent updates |
| `027/run_027b_straggler_light.py` | The precomputed-retrieval orchestration-wait comparison used in Table 91; run after `run_027.py` in the same output directory |
| `027/summarize_027.py` | Summary tables and figures; default input is the released 027 result directory; set `B3_INPUT_DIR` to a reproduction directory to summarize a new run |
| `028/run_028.py` | Persistent workers, plan execution, deferred writes and versioned commit comparisons |

The 134-page source document used to create the frozen corpus is a different snapshot from the publication report. The saved numeric inputs preserve the reference workload for downstream execution. Re-extracting from the publication text defines a new workload and should be reported as a separate run.

Process throughput, latency and write-contention outcomes depend on the host and scheduler. The source tables record the original executions. This publication review reconciled recorded values and reran the 025 derived calculation; it did not retrain the simulation models or rerun the external empirical corpora.

## Code provenance

[CODE_MAP.csv](CODE_MAP.csv) records original and published code hashes. Changes parameterize input/output locations, describe the executable coverage of 024, and separate calculation code from draft-document and ZIP assembly. [EVIDENCE_FILE_MAP.csv](EVIDENCE_FILE_MAP.csv) identifies every published source artifact and its byte-preservation status.
