# INTERNAL_COORDINATION_010 — Shared Ganglion + Precision Residual

Experiment 010 upgrades the mixed numeric-language architecture from Experiment 009 by separating shared cross-data coordination from channel-specific precision.

## Design

The 16D mixed ganglion is trained first and then frozen. Numeric and language precision experts are trained outside the ganglion. A precision expert activates only when its own native evidence is present. Final outputs use a residual blend: `shared + alpha * (local - shared)`, with alpha selected on an internal validation subset and capped at 0.75.

## Main evidence

Across three matched seeds, long precision training reduced median numeric same-channel pinball from 0.0793 to 0.0745; the numeric specialist reference was 0.0742. Language same-channel semantic accuracy rose from 80.0% to 83.7%; the specialist reference was 85.2%. With both evidence types available, numeric pinball reached 0.0745 and language semantic accuracy reached 90.1%.

Text→numeric and numeric→language outputs were unchanged exactly, because the local expert is inactive when its native evidence is absent. After precision recovery, removing the first two learned ganglion directions still degraded combined and cross-modal performance, so the precision paths did not replace the shared ganglion.

## Files

- `code/experiment_010.py`: full experimental definitions and original all-in-one runner.
- `code/run_seed010.py`: short capacity screen by seed.
- `code/run_precision_long.py`: long precision training by seed.
- `code/ganglion_retention_010.py`: ganglion lesion after precision recovery.
- `code/build_report_010.py`: report and Living Record builder.
- `results/`: base checkpoints, precision expert checkpoints, per-seed tables, aggregate summary and lesion results.
- `figures/`: report figures.
- `documents/`: standalone report and Living Report v0.11.
- `protocol.json`: fixed experiment settings.
- `manifest.json`: SHA256 and byte count for every packaged file.

The package is self-contained apart from standard Python dependencies: PyTorch, NumPy, pandas, scikit-learn, matplotlib and python-docx.
