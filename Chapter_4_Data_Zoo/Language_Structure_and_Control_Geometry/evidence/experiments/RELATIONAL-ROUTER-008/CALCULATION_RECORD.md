# RELATIONAL-ROUTER-008 calculation record

Date: 27 September 2026

Data: the exact ten pinned Universal Dependencies test blobs already used in RELATIONAL-ARITY-005 and DEPENDENCY-ORDER-007.

Executed comparisons:
1. 80/20 deterministic random split (seed 20260927).
2. Ten leave-one-language-out evaluations.
3. Sentence-length high-complexity stratum.
4. Deterministic shuffled-edge router ablation.

Metric: normalized RMSE across six jointly predicted nonlocal sentence-organization coordinates. Feature and target scaling are fitted on the training partition only.

Parameter/capacity control:
- local composer dimension identical: 8;
- sentence feature dimension identical: 49;
- output head identical: six-output ridge regression;
- flat and hierarchical models differ only in which predicate pairs supply the final 16 message coordinates.

Primary executed results:
- random split flat: 0.67170 NRMSE;
- correct hierarchical router: 0.66969;
- adaptive sparse router: 0.67011 with hierarchy active on 39.225% of test sentences;
- shuffled-edge router: 0.67250.
- leave-one-language-out: correct hierarchy improves over flat in 10/10 languages; mean gain 0.002579 NRMSE, bootstrap 95% CI [0.001313, 0.004106], exact two-sided sign-flip p=0.001953.
- largest target-specific improvement is maximum predicate nesting: 2.90% relative NRMSE reduction.
