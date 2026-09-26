# Reproduction routes


The repository supports three distinct operations: inspect recorded evidence, recompute retained summaries, and rerun implementations with their original dependencies. Every experiment README identifies its available materials.

## Verify and inspect the archive

From the repository root, with Python 3.9 or newer:

```bash
python scripts/verify_release.py
python scripts/prepare_evidence.py
python audit/recalculate.py
python audit/recalculate_phase2.py
```

Verification checks stored checksums, the recovered bytes of all 512 original artifacts, and links from experiment indices. Restoration expands one compressed per-episode JSONL file and checks its original SHA256. The arithmetic script recomputes author/genre counts, the expected-field summary, three history/transplant aggregates, and optimizer update counts. It writes `audit/summary_recalculation.json`.

## RTG post-training E23

The complete recorded configuration and dependencies are in `evidence/R5_posttraining/configs/phaseA_v1.json`, `environment.txt`, `requirements-train.txt` and `requirements-analysis.txt`. These are the original recorded versions.

The original code imports `RTG_POSTTRAIN_V01`. Stage a working copy under that package name:

```bash
python scripts/prepare_evidence.py
python scripts/stage_posttraining.py work
cd work
python -m RTG_POSTTRAIN_V01.tests.test_contracts
python -m RTG_POSTTRAIN_V01.reproduce --output-root ../reruns/E23_replay_001 --run-id E23-REPLAY-001
```

The replay command performs the original training campaign and requires Torch, NumPy and Matplotlib. It refuses an existing output directory. The restored source archive remains unchanged. For a separate plotting environment, add `--analysis-python /absolute/path/to/plotting/python`. The archived package README documents checkpoint selection, evaluation splits and the phases actually run.

To audit an existing archive in the staged copy without retraining, run from `work/`:

```bash
python -m RTG_POSTTRAIN_V01.audit_completed
```

This command writes derived audit outputs in the working copy. The archived per-episode outputs are the evidence for the reported run; a replay creates a new run.

## Long-run construction E24

Compile the retained C++ implementation and keep new outputs separate:

```bash
mkdir -p reruns/E24
c++ -O2 -std=c++17 evidence/R6_longrun/rtg_longrun.cpp -o reruns/E24/rtg_longrun
./reruns/E24/rtg_longrun > reruns/E24/raw_results.txt
```

The program covers ten 100k-step seeds and one million-step seed in each of three conditions. The original outputs remain in `evidence/R6_longrun/raw_results.txt` and `summary.csv`.

## Fixed-weight pilots E17 and E18

The archives retain training and intervention scripts, checkpoints and saved JSONs. Imports use Torch, NumPy and, in selected analyses, scikit-learn. Scripts retain original `/mnt/data` paths; adapt paths in a new working copy before execution. E17 continuation imports the unarchived `cotstep_500` version. `cotfreedom_upstream.py` in the E18 family imports the E17 `cotstep` model. These dependencies should remain visible when reconstructing a run. E17 multiseed repetitions are sampling repetitions of one checkpoint.

## Tables reports and specifications

E01–E13 retain derived tables, protocols, metric definitions and selected reference functions. E14 retains the original 0.263 measurement and continuation provenance. E15–E16 retain CoT result tables or discussion results. E19 retains a report and figure. E20–E22 retain construction results; the `.py` files in E21–E22 contain prose mechanism specifications. E25–E26 retain protocols and result tables. E27 keeps the 45-step report separate from the available 220-step code.

## Update the findings

The current English text is in `report_text/`; the document editions are in `reports/`. Record substantive edits in `CHANGELOG.md`, preserve stable experiment IDs, and connect changes to their evidence. A new snapshot receives its own version and manifest.

Run `python scripts/refresh_manifest.py` after deliberate release edits, then run `python scripts/verify_release.py`.

## Phase 2: result inspection

Run `python audit/recalculate_phase2.py` to recompute mirror deviation reductions, matched-dose ranges, trajectory means and interval Jaccard. E28–E39 retain protocols, result tables and figures. The script reads paired-bootstrap intervals from the archived result table. Natural LLM experiments and an integrated control loop are the next research stage.
