# Reproduction guide

Run commands from this report directory. The release has two practical entry points: reconcile the recorded CSV results, and execute the supplied staged validation using separately installed provider datasets.

## Check the released results

```bash
sha256sum -c CHECKSUMS.sha256
python verification/verify_results.py
```

The result check recalculates mean metrics, the Engel selection count and the precommit digest from the published files. It prints a JSON summary. The English table CSVs and the figure map support direct comparison with the report.

## Run the staged validation

The recorded environment is Python 3.13.5, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0, scikit-learn 1.8.0, statsmodels 0.14.6 and NetworkX 3.6.1. Matplotlib is used for plotting; its version is identified by the reproduction environment used by the reader. The data loaders use the corresponding installed provider packages.

Choose a fresh output directory and run the stages in order:

```bash
export MDM_OUTPUT_DIR="$PWD/reproduction_results"
python evidence/experiments/MDM-SOP-BLIND-VALIDATION-003/phase1_precommit.py
python evidence/experiments/MDM-SOP-BLIND-VALIDATION-003/phase2_reveal.py
python evidence/experiments/MDM-SOP-BLIND-VALIDATION-003/phase3_nested_probe.py
```

The first stage records a new timestamp and a corresponding digest for that execution. The supplied blind_precommit.json and blind_precommit.sha256 identify the archived decision record for this edition. The file map gives hashes for the source scripts and their portable publication versions; their calculation logic is retained.

The final-stage scripts produce derived result tables and figures. The provider records are accessed by the installed statsmodels and NetworkX loaders. The graph kernel directory supplies a protocol sketch and its recorded 100-split results. The early-stage directory supports report-level comparison through the recovered figures and tables.

## Recreate the English figures

The figure script renders Figures 1–13 from the transcribed reported values and diagram operations. It writes to mdm_english_figures in the current directory, or to MDM_FIGURE_OUTPUT_DIR.

```bash
python figures/reproduce_english_figures.py
```
