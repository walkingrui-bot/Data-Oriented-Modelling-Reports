# INTERNAL_COORDINATION_011 — Public Drug-Development Evidence First Contact

First application of the shared-ganglion / precision architecture to a public drug-development evidence problem.

Public source: `vi-c-ky/Human-genetic-evidence-associated-with-drug-approval`, `data/final_dataset.csv`, Git blob `d7102b1357aaeb780c73d286318fea297d0dbcb4`.

Inputs are six non-clinical evidence channels: literature, somatic mutation, affected pathway, RNA expression, genetic association and animal model. `clinical` and `overall_score` are excluded from inputs. Outcome is Phase 4/approved vs Phase 1/2.

A deterministic Ensembl-target holdout is used so that one target never appears in both training and test sets.

Main result: the polynomial statistical baseline retains the strongest standalone precision in this first pass. The 16×16 ganglion approaches it but has initialization variance. Validation-selected precision fusion brings the strongest ganglion to approximately the polynomial baseline and yields a small log-loss improvement in one strong seed.

Next interface: replace the six coarse evidence classes with the existing 18 native Evidence Data Passport pipelines, add time locking and provenance, and keep the human clinical outcome outside the evidence inputs.
