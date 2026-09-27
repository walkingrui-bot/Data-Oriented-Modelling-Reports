# RESPONSE-REGIME-004B1 calculation record

Date: 2026-09-27

## Executed source set

ParaphraseBench test rows were read from the public GitHub repository `DataManagementLab/ParaphraseBench`, pinned in this package to commit `9c77daa11c7fa1fa16bbb2e314303b4017fb2220`. The experiment used 57 aligned SQL targets and six curated natural-language variants per target: naive, syntactic, morphological, lexical, semantic and missing-information, for 342 natural-language rows. File-level Git blob identities are in `SOURCE_MANIFEST.json`.

## Transition-geometry calculation

Natural-language tokenization lowercased the rows and retained alphabetic tokens, numeric tokens and punctuation. A shared top-64 surface vocabulary was built across the six NL variants, with BOS/EOS/UNK states. For each current token a, the centered conditional future code was `C(a)=P(next|a)-P(next)`. The visitation-weighted covariance was `M=sum_a p(a) C(a) C(a)^T`. Stable rank was `trace(M)/lambda_max(M)`; participation rank was `trace(M)^2/||M||_F^2`; top-3 energy used the three leading eigenvalues. Top-3 subspace overlap used `||U_naive^T U_variant||_F^2/3`.

SQL used a separate top-64 token vocabulary with SQL operators and punctuation retained and the table name normalized to a generic table token. Its stable rank was 3.5449 and top-3 energy 54.85%.

Across the six NL variant fields, stable rank ranged from 5.1162 to 8.0956. Top-3 overlap with the naive field ranged from 0.6049 to 0.9424. These values establish the local surface geometry for this benchmark construction.

## Target-identity calculation

Each NL row was mapped to hashed character 3-5-gram TF-IDF features in 4,096 bins. For one held-out paraphrase style at a time, each SQL target prototype was the normalized sum of its five non-held-out variants. The held-out row was matched to the most similar of the 57 target prototypes by cosine similarity.

Mean Top-1 across the six held-out styles was 74.56%; mean MRR was 0.8351; mean matched-minus-mismatched cosine gap was 0.3437. Random target identity is 1/57 = 1.75%. A 1,000-permutation label control produced means of 1.68-1.82% and a common empirical 95th percentile of 5.26%. All six held-out Top-1 counts have exact binomial upper-tail p < 1e-28 against p=1/57.

## Evidence statement

This campaign establishes a request-side paraphrase-invariance coordinate: local NL surface transition fields change in width and orientation across curated paraphrase families, while the identity of the fixed executable SQL target remains strongly recoverable from a held-out style. It complements the existing procedural-response triplet assay and supplies a separate request-to-executable-target measurement interface.
