# Reproduction guide

## Check the prepared records

From this report directory, run:

```bash
python verify_records.py
```

This portable verifier uses Python, NumPy and pandas. It recomputes 24 selected numerical claims from supplied result records and performs independent 10,000-replicate group bootstraps for CG-022 and the four primary CG-024 event contrasts. It writes verification_results locally. It does not download data or train models.

The source-bundle integrity checks were performed before repackaging: 53 supplied SHA-256 entries and all 16 embedded ZIP CRC checks passed. Release integrity is independently described by FILE_MANIFEST.csv and SHA256SUMS.txt.

## Reproduce the redrawn figures

Run `python render_publication_figures.py` from this report directory with NumPy, pandas and Matplotlib installed. It renders Figures 1, 11, 75 and 85 from the conceptual definitions and released result tables. It does not download observations or execute models.

## Re-execute an experiment

Read its protocol, availability entry and Python imports first. Install the experiment's recorded requirements in an isolated environment; later model code requires PyTorch in addition to NumPy, pandas, SciPy and plotting tools. Configure source script paths in a working copy. Original scripts can reference /mnt/data, previous experiment directories and cached provider data, so launching them unchanged from an arbitrary directory is not a supported one-command reproduction path.

Synthetic CG-017–024 records include generating arrays or their referenced copies, model checkpoints and analysis code. Preserve their group/whole-world train, development and test splits. For real analyses, acquire provider observations separately and verify the supplied source hashes where available; use recorded row indices, masks and preprocessing parameters. Do not add those observations to a publication commit or release archive.

Use frozen checkpoints for evaluation when the protocol calls for no retraining. Cross-question studies intentionally reuse earlier models. Aggregate repeated queries and seeds within independent parameter groups/worlds; do not treat rows or seeds as independent worlds. For Sachs transfer, use the intervention target as the holdout unit where specified.

## Verification scope

Publication preparation reaggregated stored results; it did not independently rerun neural training, original permutation tests or wet-lab work. Archived verification.json files describe checks performed in the supplied experimental record. Current verification results are separate under verification/. PyTorch checkpoint containers were inspected structurally as archives without executing pickle payloads; no new checkpoint inference was claimed.
