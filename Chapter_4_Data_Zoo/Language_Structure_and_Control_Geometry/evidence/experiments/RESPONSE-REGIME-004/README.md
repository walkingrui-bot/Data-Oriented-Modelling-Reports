# RESPONSE-REGIME-004 Evidence Package

Date: 2026-09-27

Controlled paired-response assay comparing three realizations of the same ten algorithms:
1. natural-language procedural response,
2. pseudocode response,
3. executable Python response.

The task and algorithm are fixed across response modes. The experiment therefore measures response-regime realization rather than comparing an unrelated prose corpus with a code corpus.

## Primary measurements

Equal-budget lexical transition geometry (32 most frequent surface symbols plus boundary/UNK):
- Natural-language procedural: stable rank 2.914; top-3 energy 64.1%.
- Pseudocode: stable rank 2.243; top-3 energy 69.9%.
- Executable Python: stable rank 1.659; top-3 energy 83.8%.

Shared six-event procedural geometry (STATE, LOOP, BRANCH, APPEND, CALL, RETURN):
- Natural-language procedural: stable rank 2.101; top-3 97.2%; plan-event F1 0.925.
- Pseudocode: stable rank 2.179; top-3 93.2%; plan-event F1 0.989.
- Executable Python: stable rank 2.179; top-3 93.2%; plan-event F1 0.989.
- Natural-language versus algorithmic top-3 event-subspace overlap: 0.914.

Matched-semantic trajectory control:
- NL / pseudocode: matched 0.829 vs mismatched 0.507; gap 0.322; exact sign-flip p=0.0049.
- Pseudocode / Python: matched 1.000 vs mismatched 0.488; gap 0.512; p=0.0029.
- NL / Python: matched 0.829 vs mismatched 0.507; gap 0.322; p=0.0049.

Surface locality and deletion stress:
- Mean repeated-entity recurrence distance: NL 15.44, pseudocode 8.85, Python 3.35 lexical positions.
- Punctuation/operator density per 100 lexical tokens: NL 14.6, pseudocode 17.4, Python 39.7.
- Under 5% random lexical-token deletion, event-plan F1 remains 0.907 for NL and 0.720 for pseudocode; 8.3% of perturbed Python programs remain parseable. At 10% deletion, Python parseability is 1.15%.

## Artifacts

- `paired_responses.json`: all ten matched response triplets.
- `results.json`: complete metrics, per-task event paths and controls.
- `summary.tsv`: compact regime-level summary.
- `response_regime_004.py`: full reproducible analysis.
- `response_regime_stable_rank.png`: equal-budget lexical/event stable-rank comparison.
- `matched_vs_mismatched_similarity.png`: matched-semantic trajectory control.
- `run_output.txt`: printed experiment summary.

## Evidence boundary

The natural-language side consists of controlled procedural answers. The result establishes a reproducible response-mode comparison over these ten matched algorithms. It supports a shared low-width procedural backbone across natural-language procedural, pseudocode and executable responses while directly measuring different surface constraints. The planned replication broadens the natural-language answer distribution and algorithm families while preserving matched task identity.
