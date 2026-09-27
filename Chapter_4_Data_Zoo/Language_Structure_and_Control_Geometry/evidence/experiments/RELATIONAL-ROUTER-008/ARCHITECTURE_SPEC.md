# RELATIONAL-ROUTER-008 architecture specification

## Engineering hypothesis
The prior language campaigns measured a relatively narrow predicate-local relation space, while sentence complexity increased mainly through additional predicates, deeper dependency organization, longer paths and predicate nesting. This validation constructs a two-level representation that mirrors those measurements.

## Shared local composer
Every predicate is represented by the same 21-dimensional measurement used in DEPENDENCY-ORDER-007:
- 7 participant-role counts;
- 7 mean dependency directions;
- 7 log mean dependency distances.

An 8-dimensional PCA composer is fitted only on the training predicates in each split.

## Matched flat control
The flat model uses:
- 8 mean pooled local coordinates;
- 8 standard deviations;
- 8 maxima;
- 8 minima;
- log predicate count;
- 8 mean absolute differences over surface-adjacent predicate pairs;
- 8 mean products over surface-adjacent predicate pairs.

Total: 49 sentence features.

## Hierarchical router
The hierarchical model uses the same local composer, pooling, count, total feature dimension and regression head. The final 16 message coordinates are instead computed over the nearest predicate-ancestor edges in the dependency tree.

## Adaptive sparse router
The adaptive construction uses the flat fast path by default. It activates hierarchical routing when predicate_count >= 3 or maximum predicate nesting >= 2.

## Shuffled-edge control
The shuffled-edge router keeps the same 49-dimensional interface and number of relation-message operations, but replaces true predicate-ancestor connectivity with deterministic incorrect within-sentence pairings.

## Prediction task
Six nonlocal sentence-organization coordinates are jointly predicted:
tree depth, mean dependency distance, maximum predicate nesting, mean predicate-pair tree distance, subordinate predicate count and crossing count.

All models use the same six-output ridge head.
