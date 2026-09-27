# RELATION-COMPRESSION-006 Calculation Record

Date: 27 September 2026

## Question
How does human Chinese sentence simplification act on predicate-local relation structure as a matched sentence trajectory shortens? The executed assay separates predicate-count reduction, source-branch non-recovery, within-retained-branch slot loss, and role-preserving realization recoding.

## Data
Official MCTS dev/test original sentences plus five human simplifications per source, identified by exact Git blob SHAs in `source_manifest.csv`.
UD Chinese GSDSimp train/dev/test provides the supervised predicate-role assay and exact source identity.

## Matched path construction
A UD-derived longest-match lexicon segments MCTS text. Sources with at least three references shorter than the original are retained (N=507). For each source:
- mild = longest shorter reference
- medium = median shorter reference
- strong = shortest reference
Mean target/source token ratios are 0.9220, 0.8345, and 0.6563.

## Predicate-role model
A hashed linear multi-label classifier is trained on UD Chinese GSDSimp train, with thresholds selected on dev. Held-out test:
- micro-F1 = 0.591
- local-arity correlation r = 0.582
- arity MAE = 0.525 slot
- SUBJ F1 = 0.628
- OBJ F1 = 0.728
The aggregate trajectory, predicate count, local arity, and SUBJ/OBJ-supported structure are primary evidence coordinates. OBL/COMP measurements are retained as secondary components.

## Primary trajectory
Original -> Strong:
- mean tokens: 35.73 -> 23.05
- mean predicates: 7.23 -> 5.05
- mean local arity: 1.060 -> 1.041
- role stable rank: 2.088 -> 2.041
- predicate density: 20.25 -> 21.90 per 100 tokens

## Alignment-based operation decomposition
Primary monotonic branch alignment threshold = 0.80; thresholds 0.65, 0.95, and 1.10 are retained in `alignment_threshold_sensitivity.csv`.
At strong compression:
- source-branch non-recovery = 47.14%
- net predicate-count reduction = 30.23%
- lower-bound replacement share of source-branch non-recovery = 35.86%
- net-pruning share = 64.14%
- within-retained slot loss = 25.04%
- role-signature-preserving realization recoding = 53.18%
- 76.60% of measured lost source slots are carried by non-recovered source branches.

## Length-matched random deletion
Random controls delete source tokens to the same target token counts while preserving order.
Human minus random source-branch non-recovery is positive at all three compression levels; bootstrap 95% intervals are stored in `random_control_bootstrap_ci.csv`.
Within-retained slot-loss differences are strongest at mild compression and converge toward the random control at medium/strong compression.

## Interpretation supported by the executed assay
Human simplification preserves a bounded local relation width while surface length and predicate count decline. The operation mix changes with compression depth: mild simplification contains substantial branch replacement/re-expression, whereas strong simplification contains substantially more net predicate pruning. The retained surface becomes more predicate-dense as compression strengthens.
