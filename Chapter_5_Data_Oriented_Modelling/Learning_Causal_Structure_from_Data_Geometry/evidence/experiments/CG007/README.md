# CG-007: Source transfer and atlas-support stress tests

The 18-pair pilot improved weighted accuracy from 61.82% to 84.90%, with selective accuracy near 98.9%. CG-007 changes the holdout unit from pair to source: all pairs from a test source are excluded together. This tests transfer to an unseen generating environment, beyond a previously unseen relationship.

Two independent panels each contain six sources and three scalar pairs per source. Panel A comprises DWD, Abalone, auto-mpg, concrete, liver disorders and Pima Indian diabetes. Panel B comprises UNdata, Moffat, Mahecha, Solly, S. Armagan Tarim and D. Janzing. Across 36 pairs and 12 sources, each outer fold withholds one complete source, including both mirrored orientations of every test pair.

## Evidence availability

Partial recovered results; original execution scripts are not included.

This directory contains 3 CSV result files, 0 Python files and 0 checkpoint files, including reference copies where applicable. See the report section 12 for design, independent units, negative results and limits.

Scientific source scripts retain their recorded runtime paths. Configure these paths in a working copy before execution. Use the release-level reproduction guide for dependencies and data availability. Existing verification JSON files are records supplied with the experiment; current publication checks are under the report-level verification directory.

[Report](../../../REPORT_EN.md) · [Evidence index](../../../EVIDENCE_INDEX.md)
