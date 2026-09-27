# DEPENDENCY-ORDER-007 calculation record

Date: 2026-09-27

Data: official test splits from ten Universal Dependencies treebanks; 18,355 sentences.
Predicate contract: identical to RELATIONAL-ARITY-005.

Q1 -> Q4:
- mean tokens: 7.46 -> 38.52;
- predicates/sentence: 1.05 -> 4.76;
- predicate-weighted local arity: 1.17 -> 1.44;
- tree depth: 3.33 -> 7.20;
- mean dependency distance: 1.86 -> 3.76;
- long-arc fraction >=5: 0.067 -> 0.191;
- maximum predicate nesting: 0.30 -> 2.16;
- mean predicate-pair tree distance: 0.35 -> 2.60;
- subordinate predicates/sentence: 0.30 -> 3.18.

All primary nonlocal Q1->Q4 deltas are positive in all ten languages.
Mean local arity rises modestly in 9/10 languages.

Sentence-organization geometry after within-language z-scoring:
stable rank 1.703; participation rank 2.549; PCA95=5; TwoNN=3.079;
top-3 energy=87.15%; mean 10-NN preservation: 62.70% at PCA-4D,
82.58% at PCA-8D.

PC1 explains 58.73% and jointly loads sentence length, predicate count,
mean dependency distance, tree depth and maximum predicate nesting.

Predicate role/order/distance geometry averages stable rank 5.619,
participation rank 7.714 and PCA95=9.1. Its stable rank rises only
3.94 -> 5.06 across length quartiles while predicate count rises
1.05 -> 4.76.
