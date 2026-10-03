# Reproduction guide

Begin with REPORT_EN.md and EVIDENCE_INDEX.md. Match each claim to its experiment identifier, protocol, aggregate result and recorded gate. EXP089 is a retrospective decision audit of the preceding experiments; it must not be treated as an additional validation sample.

1. Verify CHECKSUMS.sha256 from the report directory. PUBLIC_EVIDENCE_MANIFEST.csv maps each public evidence file to its source-relative path and source hash.
2. Read the experiment-specific protocol, amendments and result interpretation before using its code. Preserve the recorded observation unit, grouping, time definition, training/development/test boundaries, seeds and stopping rules.
3. For EXP001–003, use the supplied controlled simulator and synthetic evidence. For real-source experiments, obtain the stated provider release separately. Source observations, derived row-level tables and real-data checkpoints are not included in this public release.
4. Use the original requirements or protocol/environment records where present. Dependencies vary by experiment. The collection contains NumPy/pandas/scikit-learn and PyTorch research code; there is no single validated environment lock for all 89 experiments.
5. Adapt archived local root paths and mount the separately retrieved source dependencies. The original scripts are retained research implementations, not a newly validated one-command execution package. The native-source integration harness is under evidence/EXP016/training_harness/.
6. Compare reproduced aggregates with the archived outputs. Preserve failed and amended attempts, distinguish simulation from real observations, and distinguish retrospective development from independent confirmation. A conditional test left unscored is not a reported test result.

Publication preparation verified file integrity, report/table/figure preservation and selected aggregate claims. It did not rerun model training, reconstruct external datasets, or certify one-command reproduction across all source environments. This boundary is also stated in VERIFICATION.md.
