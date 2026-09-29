#!/usr/bin/env python3
"""
CG-011: Relational Response Operator

Core design:
- Real Sachs perturbation data only.
- Targets come from the public condition_manifest.csv.
- Directed role labels come from the Sachs benchmark GroundTruth.csv.
- For each known intervention target and candidate node, calculate:
  (1) node response geometry,
  (2) baseline target-node relation geometry,
  (3) intervention-induced change in target-node relation geometry.
- Evaluate class-weighted ridge operators with:
  * leave-one-intervention-out (LOIO)
  * leave-one-target-out (LOTO; all interventions sharing a target are held out)
- Primary tasks:
  descendant vs nondescendant,
  direct child vs rest,
  direct child vs farther descendant.
- Validate primary effects with within-intervention / within-target label permutations.
The archived CSVs contain the exact 2026-09-27 numerical results.
"""
print(__doc__)
