# RELATIONAL-ARITY-005 calculation record

Date: 2026-09-27

## Question
Does natural-language sentence complexity primarily arise by widening each local predicate-participant relation, or by composing more locally narrow predicate relations?

## Data
Ten Universal Dependencies test treebanks:
English-EWT, Chinese-GSDSimp, Japanese-GSD, Turkish-IMST, Arabic-PADT,
Russian-SynTagRus, Finnish-TDT, Hindi-HDTB, Spanish-GSD and Korean-GSD.

Exact Git blob SHAs are recorded in `source_manifest.csv`. Raw external corpora are not duplicated in this package.

## Predicate definition
A local predicate head is:
- a VERB; or
- a copular ADJ/NOUN/PROPN with a `cop` child; or
- an AUX with an explicit participant child.

Explicit local participant dependencies are direct children with base UD relations:
`nsubj`, `csubj`, `obj`, `iobj`, `ccomp`, `xcomp`, `obl`.

Arity is the count of these direct participant dependents. It is therefore an
explicit UD-dependency arity measure; implicit arguments are outside this assay.

## Complexity analysis
Sentences are split into within-language token-length quartiles.
For every quartile, the assay measures:
- predicate heads per sentence;
- mean participant arity per predicate;
- 95th-percentile arity;
- stable rank and top-3 energy of the seven-role count vector.

Sentence-level Spearman measurements relate token length and tree depth to:
predicate count, participant total, mean predicate arity and maximum arity.

## Geometry
Abstract relation geometry uses a seven-coordinate role-count vector.
Realization geometry appends seven mean signed dependency-offset coordinates,
producing a 14-coordinate role-plus-order vector.
Reported diagnostics: stable rank, participation rank, PCA-95 dimension,
top-3 energy, TwoNN (where non-degenerate) and pairwise-distance CV.

## Primary measured results
- 18,355 sentences; 41,223 predicate-local structures.
- Predicate-weighted mean explicit arity: 1.508.
- 85.52% of predicates have <=2 explicit participants.
- 97.36% have <=3; 2.64% have >=4.
- Mean across-language Spearman(sentence length, predicate count): 0.744.
- Mean Spearman(sentence length, mean predicate arity): 0.282.
- Across within-language length quartiles, predicates/sentence rise 1.09 -> 4.82.
- Mean arity rises 1.19 -> 1.44.
- Seven-role stable rank rises 4.30 -> 4.94 and is essentially flat from Q3 to Q4.
- Abstract role-count stable rank averages 4.99; adding direction/order raises it to 6.26.
