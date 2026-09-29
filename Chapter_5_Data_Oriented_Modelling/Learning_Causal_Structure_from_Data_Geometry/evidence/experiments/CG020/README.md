# CG-020: Explicit object-state iteration

CG-018 retained a 48-dimensional GRU hidden state alongside relation feedback. CG-020 removes that parallel memory: only three matrices B and three candidate logits persist across updates. Fixed observation/support context is re-encoded each round; there is no recurrent hidden state or other cross-round latent cache.

The same three-variable worlds permit exact do-consequences. Four training updates define the scoring window, while the object transition is separately tested for continuation, saving, editing and longer rollout.

## Evidence availability

Synthetic code, checkpoints and results; exact execution requires the recorded dependencies and configured archive paths.

This directory contains 9 CSV result files, 5 Python files and 8 checkpoint files, including reference copies where applicable. See the report section 26 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
