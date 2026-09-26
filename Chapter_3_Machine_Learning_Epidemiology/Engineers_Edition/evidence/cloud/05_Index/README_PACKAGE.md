# Model Control Diagnostics — Complete Engineering Evidence Bundle

Date: 2026-09-26
Current engineering master record: v0.5

## Scope
This archive consolidates the engineering line from WORD-SENSITIVITY-001 through TOOL-CALL-004. It contains the living engineering record, individual experiment reports where they were produced, executable engineering tools, CSV/JSON/NPZ evidence, figures, self-tests, deployment/runbook material, original per-stage artifact ZIPs, and the lower-level telemetry packages used to build the engineering instruments.

## Directory map
- `00_Living_Record/` — v0.1–v0.5 living engineering record; v0.5 is current.
- `01_Experiments/` — expanded evidence for every engineering experiment in chronological order.
- `02_Shared_Source_Telemetry/` — pre-engineering control/Jacobian telemetry directly reused by the scanner/operator experiments.
- `03_Reference_Basis/` — user-provided v1.8 research record used as the theoretical/stopping-geometry reference for later tool-calling work.
- `04_Original_Stage_Bundles/` — original per-stage ZIPs and source telemetry ZIPs, unchanged.
- `05_Index/` — manifest, SHA-256 checksums, public-source provenance, and this README.

## Experiment sequence
1. WORD-SENSITIVITY-001 — Token Control Scanner
2. WORD-SENSITIVITY-002 — Same Token, Different State
3. TOKEN-OPERATOR-ATLAS-001 — Token Operator OS
4. REAL-WORLD-OPERATOR-FAILURES-001 — Public failure-text casebook
5. REAL-WORLD-OPERATOR-TELEMETRY-002 — Failure Axis Guard OS
6. TOOL-CALL-001 — Hybrid Action Geometry / Tool Stability Radius
7. TOOL-CALL-002 — Classic BFCL Case Dissection / Guarded Partial Operators
8. TOOL-CALL-003 — Action Readiness Geometry / Tool stopping & overthinking
9. TOOL-CALL-004 — Semantic Tool Selection Geometry / cross-architecture replication

## Audit note
The current master report v0.5 is the authoritative narrative record. Stage directories preserve the numerical evidence and runnable engineering interfaces. `MANIFEST.csv` and `SHA256SUMS.txt` allow file-level verification.
