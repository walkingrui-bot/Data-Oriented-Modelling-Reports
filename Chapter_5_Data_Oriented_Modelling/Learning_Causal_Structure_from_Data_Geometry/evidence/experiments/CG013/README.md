# CG-013: Two-anchor chart calibration

CG-012 yields 5/10 correct with two stably reversed pairs. CG-013 asks whether two locally known directions can indicate whether to retain or reverse an external operator's sign, without adding a larger model or benchmark.

An anchor supplies polarity: + if the Sachs operator matches its known direction, − if it needs reversal. Test-pair anchors are chosen using direction-free geometry; the test direction never enters neighbour selection. The test concerns local transfer of polarity, not complete retraining.

## Evidence availability

Analysis script and result tables; external observations must be acquired separately.

This directory contains 4 CSV result files, 1 Python files and 0 checkpoint files, including reference copies where applicable. See the report section 18 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
