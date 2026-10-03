#!/usr/bin/env python3
"""
INTERNAL_COORDINATION_015 reproduction scaffold.

Core idea:
1. Fit three strict target-group cross-fitted statistical experts:
   additive, interaction, empirical-Bayes.
2. Do NOT train a neural router.
3. Estimate convex expert weights directly from OOF weighted log loss.
4. Condition routing first on available-pipeline count, then on
   available-pipeline count x observed evidence density when supported.
5. The resulting Stat-MoE may be used as a derived observer channel
   inside the shared ganglion, but routing itself remains statistical.

See protocol.json and results/*.csv for the fixed reported run.
"""
print(__doc__)
