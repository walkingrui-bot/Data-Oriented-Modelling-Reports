# CG-012: A small cross-system transfer test

CG-011 found transferable baseline child information within Sachs. CG-012 tests portability using the same 50 unique baseline relations, including 12 reference children, and 10 external Tübingen pairs from 10 sources. This deliberately small test evaluates transfer without fitting a second large perturbation atlas.

The external sources are DWD meteorology, Abalone, auto-mpg, geysers, concrete, liver function, traffic, UN public-health indicators, housing rent and MOPEX hydrology. Directions come from benchmark metadata and never enter Sachs training. A Tübingen cause–effect pair is not equivalent to a direct molecular edge; the test asks whether a child-feature operator transfers as a broader direction prior across different tasks.

## Evidence availability

Analysis script and result tables; external observations must be acquired separately.

This directory contains 2 CSV result files, 1 Python files and 0 checkpoint files, including reference copies where applicable. See the report section 17 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
