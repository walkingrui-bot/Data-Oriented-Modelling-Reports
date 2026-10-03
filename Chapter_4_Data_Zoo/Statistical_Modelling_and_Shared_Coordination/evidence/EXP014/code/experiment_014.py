#!/usr/bin/env python3
"""Reproduction scaffold for INTERNAL_COORDINATION_014.

The fixed experiment uses the same public Open Targets x ChEMBL object and target-level split as Experiments 011-013.
Three strict cross-fitted model observers are constructed: additive logistic, pairwise-interaction logistic, and a beta-binomial empirical-Bayes evidence-state observer.
A naive committee and a softmax-routed committee are then trained with the six biological evidence channels and one shared 16x16 ganglion.
See protocol.json and results/results_summary.json for the fixed design and reported values.
"""
print(__doc__)
