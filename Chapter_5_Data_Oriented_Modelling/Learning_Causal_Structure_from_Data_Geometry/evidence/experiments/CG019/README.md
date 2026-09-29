# CG-019: Cross-question reuse of generated mechanisms

CG-019 evaluates the six frozen CG-018 mechanism checkpoints on operations absent from training, without further learning. The question is whether generated relations are reusable computational structures beyond the original query.

Mechanism Blank and Feedback, each with seeds 11/22/33, retain the 100 independent test parameter groups and 600 task instances spanning three equivalent worlds and support/no-support conditions. There are no gradient updates, development selection or new checkpoint choices. Final generated matrices B and weights w are reused directly.

## Evidence availability

Synthetic code, checkpoints and results; exact execution requires the recorded dependencies and configured archive paths.

This directory contains 5 CSV result files, 5 Python files and 6 checkpoint files, including reference copies where applicable. See the report section 25 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
