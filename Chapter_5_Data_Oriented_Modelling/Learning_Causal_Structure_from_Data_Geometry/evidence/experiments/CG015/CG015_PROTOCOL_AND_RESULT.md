# CAUSAL-GEOMETRY-015 — Same Target, Different Perturbation

Small-data design:
- One target only: PKC.
- Ten candidate measured nodes.
- Two real PKC perturbation conditions: CD3/CD28 + G0076 and PMA.
- Baseline relation geometry is computed from the same cd3cd28 reference.
- The edge-confirmation operator is trained only on non-PKC intervention targets.
- Each PKC perturbation is scored independently using baseline relation texture plus matched node response.
- Primary readouts: direct-child AUC, candidate-rank agreement, Top-k overlap, and child-vs-nonchild score separation.
- Exact label control enumerates all C(10,5)=252 possible five-child assignments.
- Node-alignment control tests whether cross-perturbation ranking agreement exceeds random node remapping.

Interpretation boundary:
The experiment tests whether direct-child confirmation survives a change in perturbation method for the same target. It does not claim perturbation-invariant node ranking or universal target-specific response geometry.
