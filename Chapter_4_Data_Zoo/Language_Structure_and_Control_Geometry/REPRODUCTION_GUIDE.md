# Reproduction guide

Start with `EVIDENCE_INDEX.md` to identify the study and its recovered code coverage. The report's study identifiers are stable even though publication section, table and figure numbers are sequential.

1. Select the study folder under `evidence/experiments/` and read its source manifest, calculation record and code together.
2. Obtain the external source files from the recorded repositories using the pinned commits or blob identities. Keep those source files outside the publication folder.
3. Supply the dependencies and local paths required by the recovered script. Companion tool-chain studies reuse earlier readers, planners and emitters; inspect those imports before execution.
4. Save a reproduction run to a separate output directory and compare it with the recovered CSV or JSON outputs. The published derived files are the recorded reference outputs.
5. For report-only studies, treat the extracted CSVs as transcriptions and use the retained methods and figures for review. They do not replace the missing analysis archive.

The arity script provides parsing and predicate-vector functions but does not run the full campaign. The dependency-order script is a measurement specification rather than a complete implementation. No full analysis code was recovered for LSP-001, RESPONSE-REGIME-004 or RELATION-COMPRESSION-006.

`RELATIONAL-ROUTER-008/reproduce_relational_router.py` accepts `--ud-dir` and `--out`; its source manifest names the required local UD files. The supplied script uses NumPy and pandas and implements random-split and leave-one-language-out reconstruction. The message-count qualification in `PUBLICATION_NOTES.md` applies to its shuffled-edge comparison.

The report describes the experiments' recorded executions. Preparing this publication package did not rerun the external corpora, retrain the policies or certify exact end-to-end reproduction from every supplied script.
