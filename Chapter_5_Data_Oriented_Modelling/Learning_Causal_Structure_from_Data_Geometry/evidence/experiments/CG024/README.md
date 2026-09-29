# CG-024: Sequential intervention execution

CG-024 asks whether an inferred dynamical model can receive a new event during rollout and propagate its consequences. It extends CG-023's passive execution with explicit event tests.

The same 600 stable four-variable affine worlds are used. Eight (Mₖ,bₖ,logitₖ) candidates remain the only persistent state, without recurrent hidden memory, pruning or direct M,b supervision. New training targets concern event consequences.

## Evidence availability

Synthetic code, checkpoints and results; exact execution requires the recorded dependencies and configured archive paths.

This directory contains 15 CSV result files, 6 Python files and 6 checkpoint files, including reference copies where applicable. See the report section 30 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
