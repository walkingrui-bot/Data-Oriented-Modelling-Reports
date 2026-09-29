# CG-011: Relational response operators—adjacency and downstream propagation

CG-010 showed that low-rank compression can preserve energy while impairing role prediction. CG-011 therefore models a target–node relation using three observations: its baseline geometry, its intervention-induced change and the candidate node's response.

Direct-child inference asks whether a pair resembles a local causal channel; response-cone inference asks how intervention effects extend downstream. A single combined score can mistake shared response for direct coupling.

## Evidence availability

Analysis script and result tables; external observations must be acquired separately.

This directory contains 6 CSV result files, 1 Python files and 0 checkpoint files, including reference copies where applicable. See the report section 16 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
