# MDM-SOP-BLIND-VALIDATION-003

The staged comparison records mechanism-guided decisions before downstream evaluation on ModeChoice, Engel, RAND HIE and Les Misérables. blind_precommit.json and its recorded SHA-256 identify the original decision record. phase1_precommit.py calculates design and feature diagnostics; phase2_reveal.py calculates repeated evaluation metrics; phase3_nested_probe.py compares ordinary and coverage-balanced Engel training through nested validation.

The results are available per split: 60 ModeChoice comparisons, 120 Engel comparisons, 25 RAND HIE comparisons, 100 Les Misérables graph comparisons and 80 outer splits for the Engel nested probe. The graph design diagnostics use the full original topology before edge removal. The recorded hash supplies file-integrity evidence for the precommit record.

The published scripts retain statistical calculations and direct new outputs to MDM_OUTPUT_DIR, or to mdm_validation_results in the current directory. The supplied original result files remain the reference for this edition.

[Report section 21](../../../REPORT_EN.md#21-precommitted-validation-on-additional-datasets) · [Reproduction guide](../../../REPRODUCTION_GUIDE.md)
