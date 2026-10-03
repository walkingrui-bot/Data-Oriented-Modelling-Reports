#!/usr/bin/env python3
"""
INTERNAL_COORDINATION_012 reproduction scaffold.

Uses the same public source and deterministic target split as Experiment 011:
https://raw.githubusercontent.com/vi-c-ky/Human-genetic-evidence-associated-with-drug-approval/main/data/final_dataset.csv

Core comparison:
1. masked polynomial logistic model;
2. raw PsyMoE;
3. Stat-PsyMoE with one weighted cubic logistic calibrator per evidence channel;
4. Stat-PsyMoE + validation-selected polynomial precision head.

Pipeline absence is distinct from biological evidence absence.
Training uses random availability masks with 3-6 available pipelines.
Evaluation enumerates every mask with 0,1,2,3 unavailable pipelines.

See protocol.json and results/*.csv for the exact fixed result tables.
"""
print(__doc__)
