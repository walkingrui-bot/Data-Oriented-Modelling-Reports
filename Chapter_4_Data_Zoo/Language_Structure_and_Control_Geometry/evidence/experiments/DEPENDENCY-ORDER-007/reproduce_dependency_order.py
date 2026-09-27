#!/usr/bin/env python3
"""
DEPENDENCY-ORDER-007 reproduction skeleton.

Input:
  Local copies of the exact Universal Dependencies test .conllu blobs listed
  in source_manifest.csv. External treebank text is not bundled.

Primary measurements:
  predicate-local participant arity using the RELATIONAL-ARITY-005 contract;
  tree depth; dependency distance; long-arc fractions; predicate nesting;
  predicate-pair tree distance; crossing dependencies; subordinate predicates;
  and a 21-D predicate realization vector:
  7 role counts + 7 mean directions + 7 log mean dependency distances.

Complexity stratification:
  within each language, sort sentences by token count and split into four
  equal-size empirical quartiles. Aggregate within language and average the
  ten language-specific values.

Statistics:
  Q1->Q4 paired language deltas, 10,000 bootstrap resamples across languages,
  and exact 2^10 sign-flip tests.

See CALCULATION_RECORD.md and the executed CSV/JSON outputs in this package.
"""
ROLES = ["nsubj","csubj","obj","iobj","ccomp","xcomp","obl"]
print("Obtain the exact pinned UD blobs from source_manifest.csv and apply the documented contract.")
