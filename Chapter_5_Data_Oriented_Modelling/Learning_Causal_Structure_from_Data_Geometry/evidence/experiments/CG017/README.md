# CG-017: Generated intermediate objects in iterative data models

This experiment transfers Chapter 3's feedback questions to data modelling and causal inference. A model encodes input, generates an intermediate object, feeds it into subsequent computation and produces further candidates. The tests examine prediction, multiple possible consequences and task-dependent value of different representations.

Two generated-object formats are studied: continuous feedback states and numerical prediction candidates. Both are returned to later recurrent states.

## Evidence availability

Code, checkpoints, synthetic records and aggregate real-data outputs; per-cell real predictions excluded.

This directory contains 7 CSV result files, 4 Python files and 72 checkpoint files, including reference copies where applicable. See the report section 23 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
