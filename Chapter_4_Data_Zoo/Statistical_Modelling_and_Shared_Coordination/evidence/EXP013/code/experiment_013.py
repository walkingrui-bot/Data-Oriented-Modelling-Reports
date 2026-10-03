#!/usr/bin/env python3
"""
INTERNAL_COORDINATION_013 reproduction scaffold.

Key design:
- public Open Targets x ChEMBL target-disease dataset from Experiment 011;
- deterministic outer target holdout;
- five-fold target-group cross-fitting within outer training;
- traditional masked-polynomial prediction becomes a SEVENTH CHANNEL;
- six biological channels retain their own channel-local statistical calibrators;
- all seven observer states coordinate through one 16x16 ganglion.

The statistical channel is DERIVED evidence, not an independent biological evidence source.
It is cross-fitted to prevent in-sample target leakage.

Damage controls:
1. drop the statistical channel after training;
2. pair each evidence state with another state's statistical result.

See protocol.json and results/results_summary.json for exact fixed settings and results.
"""
print(__doc__)
