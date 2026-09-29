# CG-023: Observation coordinates and executable dynamics

CG-023 tests whether one generated mechanism can integrate different observation coordinates and produce states beyond the training horizon, extending the operation-based evaluation of CG-022.

Container order and generating order are separated. Permuting evidence rows should not change their meaning; temporal direction, forcing-to-equilibrium response and forecast horizon are semantic coordinates that the model must retain.

## Evidence availability

Synthetic code, checkpoints and results; exact execution requires the recorded dependencies and configured archive paths.

This directory contains 15 CSV result files, 3 Python files and 2 checkpoint files, including reference copies where applicable. See the report section 29 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
