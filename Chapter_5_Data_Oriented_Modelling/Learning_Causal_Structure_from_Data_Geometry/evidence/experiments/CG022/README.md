# CG-022: Consequence-supervised executable mechanism models

CG-022 retains explicit state, attention updates and a wide candidate pool while changing supervision: the same generated relations must support several operations and their consequences. The focus is functional reuse of the learned model.

The three-variable system is a restricted test environment. Training randomises internal update length between three and six rounds; frozen evaluation extends to 20. This distinguishes the training window from the evaluated continuation range.

## Evidence availability

Synthetic code, checkpoints and results; exact execution requires the recorded dependencies and configured archive paths.

This directory contains 21 CSV result files, 9 Python files and 8 checkpoint files, including reference copies where applicable. See the report section 28 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
